#!/usr/bin/env python3
"""
会話ログインポーター v5（新シート対応版）

変更点:
- task_execution_log → conversation_tasks
- retry_log → conversation_errors
- context_log → conversation_insights
"""

import sys
import os
import re
import time
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from dotenv import load_dotenv
load_dotenv('.env')

from tools.sheets_manager import GoogleSheetsManager

# 新シート名
TASK_SHEET = 'conversation_tasks'
ERROR_SHEET = 'conversation_errors'
INSIGHT_SHEET = 'conversation_insights'

class QualityFilter:
    """品質フィルター（v4と同じ）"""
    
    @staticmethod
    def is_code_fragment(text: str) -> bool:
        code_indicators = [
            r'def\s+\w+\s*\(',
            r'class\s+\w+',
            r'import\s+\w+',
            r'from\s+\w+\s+import',
            r'[\{\}\[\]\(\)].*[\{\}\[\]\(\)]',
            r'^\s*[#/\*]',
            r'\.py["\']?$',
            r'^[-=]{3,}$',
            r'^\s*$',
        ]
        
        for pattern in code_indicators:
            if re.search(pattern, text):
                return True
        
        return False
    
    @staticmethod
    def is_meaningful(text: str, min_length: int = 10) -> bool:
        if len(text.strip()) < min_length:
            return False
        
        alphanumeric = re.sub(r'[^\w\s]', '', text)
        if len(alphanumeric) < min_length // 2:
            return False
        
        if QualityFilter.is_code_fragment(text):
            return False
        
        return True
    
    @staticmethod
    def extract_meaningful_part(text: str, max_length: int = 200) -> str:
        lines = text.split('\n')
        
        meaningful_lines = []
        for line in lines:
            line = line.strip()
            if QualityFilter.is_meaningful(line, min_length=5):
                meaningful_lines.append(line)
        
        result = ' '.join(meaningful_lines[:3])
        return result[:max_length]

class ConversationLogImporterV5:
    def __init__(self, sheets_manager, source_file: str):
        self.sheets_manager = sheets_manager
        self.spreadsheet = sheets_manager.gc.open_by_key(os.getenv("SPREADSHEET_ID"))
        self.source_file = source_file
        self.quality_filter = QualityFilter()
    
    def parse_conversation_log(self, file_path: str) -> Dict[str, List[Dict]]:
        """会話ログをパース（v5 - 新シート対応）"""
        
        print(f"📄 パース中: {file_path}")
        print(f"   出力先: {TASK_SHEET}, {ERROR_SHEET}, {INSIGHT_SHEET}")
        print()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parsed_data = {
            'tasks': [],
            'errors': [],
            'insights': []
        }
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # エラーと解決策を抽出
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        error_pattern = r'❌\s*(.+?)(?=\n\n|\n✅|\Z)'
        solution_pattern = r'✅\s*(.+?)(?=\n\n|\n❌|\Z)'
        
        error_matches = list(re.finditer(error_pattern, content, re.DOTALL))
        solution_matches = list(re.finditer(solution_pattern, content, re.DOTALL))
        
        for error_match in error_matches:
            error_text = error_match.group(1).strip()
            
            if not self.quality_filter.is_meaningful(error_text, min_length=15):
                continue
            
            error_clean = self.quality_filter.extract_meaningful_part(error_text, max_length=500)
            
            solution = None
            for sol_match in solution_matches:
                if 0 < sol_match.start() - error_match.end() < 500:
                    solution_text = sol_match.group(1).strip()
                    if self.quality_filter.is_meaningful(solution_text, min_length=10):
                        solution = self.quality_filter.extract_meaningful_part(solution_text, max_length=500)
                        break
            
            parsed_data['errors'].append({
                'conversation_id': f'CONV_{datetime.now().strftime("%Y%m%d")}_{len(parsed_data["errors"])}',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source_file': self.source_file,
                'error_description': error_clean,
                'solution': solution if solution else '未解決',
                'success': solution is not None,
                'extracted_from': f'line {error_match.start()}',
                'confidence': 0.8 if solution else 0.5,
                'error_category': 'imported',
                'notes': ''
            })
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # タスクを抽出
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        task_pattern1 = r'(?:タスク|Task)[:：]\s*(.+?)(?:\n\n|\Z)'
        task_pattern2 = r'(?:^|\n)(?:\d+\.|\-|\*)\s+(.+?)(?:\n|$)'
        
        task_matches = []
        task_matches.extend(re.finditer(task_pattern1, content, re.IGNORECASE | re.DOTALL))
        task_matches.extend(re.finditer(task_pattern2, content, re.MULTILINE))
        
        for match in task_matches:
            task_desc = match.group(1).strip()
            
            if not self.quality_filter.is_meaningful(task_desc, min_length=20):
                continue
            
            task_clean = self.quality_filter.extract_meaningful_part(task_desc, max_length=200)
            
            status = 'completed'
            quality_score = 7
            
            if any(x in task_clean.lower() for x in ['error', 'failed', 'エラー', '失敗']):
                status = 'failed'
                quality_score = 4
            elif any(x in task_clean.lower() for x in ['✅', '成功', 'success', '完了']):
                status = 'completed'
                quality_score = 9
            
            parsed_data['tasks'].append({
                'conversation_id': f'CONV_{datetime.now().strftime("%Y%m%d")}_{len(parsed_data["tasks"])}',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source_file': self.source_file,
                'task_description': task_clean,
                'status': status,
                'quality_score': quality_score,
                'extracted_from': f'line {match.start()}',
                'confidence': 0.7,
                'category': 'imported',
                'notes': ''
            })
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 判断プロセスを抽出
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        for i, error in enumerate(parsed_data['errors'][:50]):
            if error['success']:
                parsed_data['insights'].append({
                    'conversation_id': error['conversation_id'],
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'source_file': self.source_file,
                    'insight_type': 'error_resolution',
                    'description': f"エラー解決: {error['error_description'][:100]}",
                    'context': error['error_description'],
                    'decision': 'fix',
                    'reasoning': error['solution'],
                    'confidence': 0.8,
                    'tags': 'imported,error_resolution'
                })
        
        print(f"   タスク: {len(parsed_data['tasks'])}件")
        print(f"   エラー: {len(parsed_data['errors'])}件")
        print(f"   判断: {len(parsed_data['insights'])}件")
        
        return parsed_data
    
    def import_to_sheets(self, parsed_data: Dict[str, List[Dict]]):
        """新シートにインポート"""
        
        print()
        print("📊 スプレッドシートにインポート中...")
        print()
        
        BATCH_SIZE = 100
        SLEEP_TIME = 2
        
        # タスク
        if parsed_data['tasks']:
            print(f"【{TASK_SHEET}】 {len(parsed_data['tasks'])}件")
            
            task_sheet = self.spreadsheet.worksheet(TASK_SHEET)
            
            rows = []
            for task in parsed_data['tasks']:
                row = [
                    task['conversation_id'],
                    task['timestamp'],
                    task['source_file'],
                    task['task_description'],
                    task['status'],
                    task['quality_score'],
                    task['extracted_from'],
                    task['confidence'],
                    task['category'],
                    task['notes']
                ]
                rows.append(row)
            
            for i in range(0, len(rows), BATCH_SIZE):
                batch = rows[i:i+BATCH_SIZE]
                task_sheet.append_rows(batch)
                print(f"   ✅ {i+len(batch)}/{len(rows)}件")
                if i + BATCH_SIZE < len(rows):
                    time.sleep(SLEEP_TIME)
        
        # エラー
        if parsed_data['errors']:
            print(f"【{ERROR_SHEET}】 {len(parsed_data['errors'])}件")
            
            error_sheet = self.spreadsheet.worksheet(ERROR_SHEET)
            
            rows = []
            for error in parsed_data['errors']:
                row = [
                    error['conversation_id'],
                    error['timestamp'],
                    error['source_file'],
                    error['error_description'],
                    error['solution'],
                    error['success'],
                    error['extracted_from'],
                    error['confidence'],
                    error['error_category'],
                    error['notes']
                ]
                rows.append(row)
            
            for i in range(0, len(rows), BATCH_SIZE):
                batch = rows[i:i+BATCH_SIZE]
                error_sheet.append_rows(batch)
                print(f"   ✅ {i+len(batch)}/{len(rows)}件")
                if i + BATCH_SIZE < len(rows):
                    time.sleep(SLEEP_TIME)
        
        # 判断
        if parsed_data['insights']:
            print(f"【{INSIGHT_SHEET}】 {len(parsed_data['insights'])}件")
            
            insight_sheet = self.spreadsheet.worksheet(INSIGHT_SHEET)
            
            rows = []
            for insight in parsed_data['insights']:
                row = [
                    insight['conversation_id'],
                    insight['timestamp'],
                    insight['source_file'],
                    insight['insight_type'],
                    insight['description'],
                    insight['context'],
                    insight['decision'],
                    insight['reasoning'],
                    insight['confidence'],
                    insight['tags']
                ]
                rows.append(row)
            
            for i in range(0, len(rows), BATCH_SIZE):
                batch = rows[i:i+BATCH_SIZE]
                insight_sheet.append_rows(batch)
                print(f"   ✅ {i+len(batch)}/{len(rows)}件")
                if i + BATCH_SIZE < len(rows):
                    time.sleep(SLEEP_TIME)
        
        print()
        print("✅ インポート完了")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='会話ログインポーター v5')
    parser.add_argument('files', nargs='+', help='.txtファイルのパス')
    parser.add_argument('--dry-run', action='store_true', help='パース結果のみ表示')
    
    args = parser.parse_args()
    
    sheets = GoogleSheetsManager(
        spreadsheet_id=os.getenv("SPREADSHEET_ID"),
        service_account_file="configuration/service_account.json"
    )
    
    all_parsed_data = {
        'tasks': [],
        'errors': [],
        'insights': []
    }
    
    for file_path in args.files:
        importer = ConversationLogImporterV5(sheets, os.path.basename(file_path))
        parsed = importer.parse_conversation_log(file_path)
        
        all_parsed_data['tasks'].extend(parsed['tasks'])
        all_parsed_data['errors'].extend(parsed['errors'])
        all_parsed_data['insights'].extend(parsed['insights'])
    
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 最終結果:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"   タスク: {len(all_parsed_data['tasks'])}件")
    print(f"   エラー: {len(all_parsed_data['errors'])}件")
    print(f"   判断: {len(all_parsed_data['insights'])}件")
    print()
    
    if not args.dry_run:
        # 最初のファイルのインポーターを使用
        importer = ConversationLogImporterV5(sheets, '')
        importer.import_to_sheets(all_parsed_data)
