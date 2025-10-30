#!/usr/bin/env python3
"""
データ統合パイプライン（レート制限対策版）

全てのログソースからナレッジを抽出し、
knowledge_baseに統合する
"""

import sys
import os
import time
from typing import List, Dict, Any
from datetime import datetime

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from dotenv import load_dotenv
load_dotenv('.env')

from tools.data_integration.models import UnifiedLogEntry, IntegrationMetrics
from tools.data_integration.sources import DataSourceRegistry
from tools.data_integration.extractors import PatternExtractor
from tools.data_integration.rate_limiter import RateLimiter, batch_write
from tools.sheets_manager import GoogleSheetsManager

class DataIntegrationPipeline:
    """データ統合パイプライン"""
    
    def __init__(self, config: Dict[str, Any], sheets_manager: GoogleSheetsManager):
        self.config = config
        self.sheets_manager = sheets_manager
        self.spreadsheet = sheets_manager.gc.open_by_key(os.getenv("SPREADSHEET_ID"))
        
        # コンポーネント初期化
        self.source_registry = DataSourceRegistry(config, sheets_manager)
        self.pattern_extractor = PatternExtractor(config)
        self.rate_limiter = RateLimiter(max_retries=5, base_delay=3.0)
        
        # バッチサイズ（設定ファイルから取得）
        self.batch_size = config.get('global', {}).get('batch_size', 50)
        
        # メトリクス
        self.metrics = IntegrationMetrics()
    
    def run(self) -> IntegrationMetrics:
        """パイプライン実行"""
        
        start_time = time.time()
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔄 データ統合パイプライン開始")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()
        
        # STEP 1: データ抽出
        print("📥 STEP 1: データ抽出")
        all_entries = self._extract_all_data()
        print(f"   合計: {len(all_entries)}件")
        print()
        
        # STEP 2: パターン抽出
        print("🔍 STEP 2: パターン抽出")
        patterns = self._extract_patterns(all_entries)
        print(f"   失敗パターン: {len(patterns['failure_patterns'])}件")
        print(f"   修正レシピ: {len(patterns['fix_recipes'])}件")
        print(f"   成功パターン: {len(patterns['success_patterns'])}件")
        print()
        
        # STEP 3: knowledge_base に保存（バッチ書き込み）
        print("💾 STEP 3: knowledge_base に保存（バッチ処理）")
        saved_count = self._save_to_knowledge_base_batch(patterns)
        print(f"   保存完了: {saved_count}件")
        print()
        
        # メトリクス計算
        self.metrics.execution_time = time.time() - start_time
        self.metrics.total_entries = len(all_entries)
        self.metrics.patterns_extracted = {
            'failure_patterns': len(patterns['failure_patterns']),
            'fix_recipes': len(patterns['fix_recipes']),
            'success_patterns': len(patterns['success_patterns'])
        }
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("✅ 統合完了")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        self._print_summary()
        
        return self.metrics
    
    def _extract_all_data(self) -> List[UnifiedLogEntry]:
        """全データソースから抽出"""
        
        all_entries = []
        sources = self.source_registry.get_all_sources()
        
        for source in sources:
            source_name = source.__class__.__name__
            
            if not source.validate():
                print(f"   ⚠️  {source_name}: 利用不可")
                continue
            
            try:
                entries = source.extract()
                all_entries.extend(entries)
                
                # メトリクス更新
                self.metrics.entries_by_source[source_name] = len(entries)
                
                print(f"   ✅ {source_name}: {len(entries)}件")
            except Exception as e:
                print(f"   ❌ {source_name}: エラー - {e}")
                self.metrics.errors.append(f"{source_name}: {e}")
        
        return all_entries
    
    def _extract_patterns(self, entries: List[UnifiedLogEntry]) -> Dict[str, List[Dict]]:
        """パターン抽出"""
        
        return self.pattern_extractor.extract_all_patterns(entries)
    
    def _save_to_knowledge_base_batch(self, patterns: Dict[str, List[Dict]]) -> int:
        """
        knowledge_baseに保存（バッチ書き込み版）
        
        レート制限対策:
        - バッチサイズ単位で書き込み
        - Exponential Backoff
        - 自動リトライ
        """
        
        kb_sheet = self.spreadsheet.worksheet('knowledge_base')
        
        # 全パターンを1つのリストにまとめる
        all_rows = []
        row_counter = 0
        
        for pattern_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                kb_id = f"KB_{pattern_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{row_counter}"
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                row = [
                    kb_id,
                    timestamp,
                    pattern['knowledge_type'],
                    pattern.get('source', 'data_integration'),
                    str(pattern),
                    pattern.get('context', ''),
                    '',
                    pattern.get('confidence', 0.8),
                    0,
                    0,
                    '',
                    ','.join(pattern.get('tags', [])) if isinstance(pattern.get('tags', []), list) else '',
                    ''
                ]
                
                all_rows.append(row)
                row_counter += 1
        
        # バッチ書き込み（レート制限対策付き）
        if all_rows:
            print(f"   総件数: {len(all_rows)}件")
            print(f"   バッチサイズ: {self.batch_size}件")
            print()
            
            batch_write(
                data=all_rows,
                sheet=kb_sheet,
                batch_size=self.batch_size,
                rate_limiter=self.rate_limiter
            )
        
        return len(all_rows)
    
    def _print_summary(self):
        """サマリー表示"""
        
        print()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📊 統合サマリー")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()
        
        print("データソース別:")
        for source, count in self.metrics.entries_by_source.items():
            print(f"   {source}: {count}件")
        
        print()
        print("パターン抽出:")
        for pattern_type, count in self.metrics.patterns_extracted.items():
            print(f"   {pattern_type}: {count}件")
        
        print()
        print(f"実行時間: {self.metrics.execution_time:.2f}秒")
        
        if self.metrics.errors:
            print()
            print("エラー:")
            for error in self.metrics.errors:
                print(f"   ⚠️  {error}")
