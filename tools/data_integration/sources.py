#!/usr/bin/env python3
"""
データソース抽象化

各種ログソースからUnifiedLogEntryを生成
"""

import os
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from datetime import datetime

from tools.data_integration.models import (
    UnifiedLogEntry, 
    SourceType, 
    ContentType
)
from tools.sheets_manager import GoogleSheetsManager

class DataSource(ABC):
    """データソース基底クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    def extract(self) -> List[UnifiedLogEntry]:
        """データを抽出"""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """ソースが利用可能かチェック"""
        pass

class ConversationLogsSource(DataSource):
    """会話ログソース（conversation_*シート）"""
    
    def __init__(self, config: Dict[str, Any], sheets_manager: GoogleSheetsManager):
        super().__init__(config)
        self.sheets_manager = sheets_manager
        self.spreadsheet = sheets_manager.gc.open_by_key(os.getenv("SPREADSHEET_ID"))
    
    def validate(self) -> bool:
        """シートが存在するか確認"""
        try:
            sheets = [ws.title for ws in self.spreadsheet.worksheets()]
            required = self.config['sheets']
            return all(sheet in sheets for sheet in required)
        except Exception:
            return False
    
    def extract(self) -> List[UnifiedLogEntry]:
        """会話ログを抽出"""
        entries = []
        
        for sheet_name in self.config['sheets']:
            try:
                sheet = self.spreadsheet.worksheet(sheet_name)
                data = sheet.get_all_values()
                
                if len(data) <= 1:
                    continue
                
                headers = data[0]
                rows = data[1:]
                
                for row in rows:
                    if len(row) < len(headers):
                        continue
                    
                    row_dict = dict(zip(headers, row))
                    
                    # タイプ判定
                    if 'tasks' in sheet_name:
                        content_type = ContentType.TASK
                    elif 'errors' in sheet_name:
                        content_type = ContentType.ERROR
                    elif 'insights' in sheet_name:
                        content_type = ContentType.INSIGHT
                    else:
                        content_type = ContentType.TASK
                    
                    entry = UnifiedLogEntry(
                        timestamp=self._parse_timestamp(row_dict.get('timestamp')),
                        source_type=SourceType.CONVERSATION,
                        source_id=f"{sheet_name}_{row_dict.get('conversation_id', 'unknown')}",
                        content_type=content_type,
                        content=row_dict.get('content', ''),
                        metadata={
                            'sheet_name': sheet_name,
                            'conversation_id': row_dict.get('conversation_id', ''),
                            'task_type': row_dict.get('task_type', ''),
                            'status': row_dict.get('status', '')
                        }
                    )
                    
                    entries.append(entry)
            
            except Exception as e:
                print(f"   ⚠️  {sheet_name}: スキップ - {e}")
                continue
        
        return entries
    
    def _parse_timestamp(self, ts_str: str) -> datetime:
        """タイムスタンプをパース"""
        try:
            return datetime.fromisoformat(ts_str)
        except:
            return datetime.now()

class SpreadsheetLogsSource(DataSource):
    """スプレッドシートログソース（task_execution_log等）"""
    
    def __init__(self, config: Dict[str, Any], sheets_manager: GoogleSheetsManager):
        super().__init__(config)
        self.sheets_manager = sheets_manager
        self.spreadsheet = sheets_manager.gc.open_by_key(os.getenv("SPREADSHEET_ID"))
        self.column_mapping = config.get('column_mapping', {})
    
    def validate(self) -> bool:
        """シートが存在するか確認"""
        try:
            sheets = [ws.title for ws in self.spreadsheet.worksheets()]
            required = self.config['sheets']
            return all(sheet in sheets for sheet in required)
        except Exception:
            return False
    
    def extract(self) -> List[UnifiedLogEntry]:
        """スプレッドシートログを抽出"""
        entries = []
        
        for sheet_name in self.config['sheets']:
            try:
                sheet = self.spreadsheet.worksheet(sheet_name)
                data = sheet.get_all_values()
                
                if len(data) <= 1:
                    continue
                
                headers = data[0]
                rows = data[1:]
                
                for row in rows:
                    if len(row) < len(headers):
                        continue
                    
                    row_dict = dict(zip(headers, row))
                    
                    # 柔軟な列マッピング
                    timestamp_val = self._find_column_value(row_dict, 'timestamp')
                    content_val = self._find_column_value(row_dict, 'content')
                    error_val = self._find_column_value(row_dict, 'error')
                    status_val = self._find_column_value(row_dict, 'status')
                    agent_val = self._find_column_value(row_dict, 'agent')
                    
                    # コンテンツタイプ判定
                    if error_val or 'error' in sheet_name.lower():
                        content_type = ContentType.ERROR
                    elif 'retry' in sheet_name.lower():
                        content_type = ContentType.ERROR
                    else:
                        content_type = ContentType.TASK
                    
                    # コンテンツ構築（エラーがあればそれを優先）
                    content = error_val if error_val else content_val
                    
                    entry = UnifiedLogEntry(
                        timestamp=self._parse_timestamp(timestamp_val),
                        source_type=SourceType.SPREADSHEET,
                        source_id=f"{sheet_name}_{row_dict.get('log_id', row_dict.get('id', 'unknown'))}",
                        content_type=content_type,
                        content=content,
                        metadata={
                            'sheet_name': sheet_name,
                            'status': status_val,
                            'agent': agent_val,
                            'raw_data': row_dict
                        }
                    )
                    
                    entries.append(entry)
            
            except Exception as e:
                print(f"   ⚠️  {sheet_name}: スキップ - {e}")
                continue
        
        return entries
    
    def _find_column_value(self, row_dict: Dict[str, str], key: str) -> str:
        """
        柔軟な列検索
        
        設定ファイルのcolumn_mappingを使って、
        複数の候補列から値を取得
        """
        candidates = self.column_mapping.get(key, [key])
        
        for candidate in candidates:
            if candidate in row_dict and row_dict[candidate]:
                return row_dict[candidate]
        
        return ''
    
    def _parse_timestamp(self, ts_str: str) -> datetime:
        """タイムスタンプをパース"""
        try:
            # ISO形式
            return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        except:
            try:
                # 日本語形式など
                return datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
            except:
                return datetime.now()

class DataSourceRegistry:
    """データソース管理"""
    
    def __init__(self, config: Dict[str, Any], sheets_manager: GoogleSheetsManager):
        self.config = config
        self.sheets_manager = sheets_manager
        self.sources = []
        
        self._register_sources()
    
    def _register_sources(self):
        """ソース登録"""
        
        sources_config = self.config.get('sources', {})
        
        # ConversationLogsSource
        if sources_config.get('conversation_logs', {}).get('enabled', False):
            self.sources.append(
                ConversationLogsSource(
                    sources_config['conversation_logs'],
                    self.sheets_manager
                )
            )
        
        # SpreadsheetLogsSource
        if sources_config.get('spreadsheet_logs', {}).get('enabled', False):
            self.sources.append(
                SpreadsheetLogsSource(
                    sources_config['spreadsheet_logs'],
                    self.sheets_manager
                )
            )
    
    def get_all_sources(self) -> List[DataSource]:
        """全ソース取得"""
        return self.sources
