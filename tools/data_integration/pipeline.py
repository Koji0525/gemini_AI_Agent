#!/usr/bin/env python3
"""
データ統合パイプライン - 修正版

統一初期化パターンを適用
"""

import os
from typing import List, Dict, Any
from datetime import datetime

from tools.data_integration.models import UnifiedLogEntry
from tools.data_integration.sources import DataSourceRegistry
from tools.data_integration.extractors import PatternExtractor, PatternResult
from tools.sheets_manager import GoogleSheetsManager
from tools.unified_initializer import init


class DataIntegrationPipeline:
    """データ統合パイプライン - 統一初期化適用"""

    def __init__(self, config: Dict[str, Any]):
        """
        パイプライン初期化 - 統一パターン適用

        Args:
            config: 設定ファイルの内容
        """
        self.config = config

        # 統一初期化パターンでリソースを初期化
        self.sheets_manager = GoogleSheetsManager(
            spreadsheet_id=os.getenv("SPREADSHEET_ID"), service_account_file="config/service_account.json"
        )

        self.source_registry = DataSourceRegistry(config, self.sheets_manager)
        self.pattern_extractor = PatternExtractor(config.get("pattern_extraction", {}))

    def run(self) -> Dict[str, Any]:
        """パイプライン実行"""
        print("🔄 データ統合パイプライン開始")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # STEP 1: データ抽出
        print("📥 STEP 1: データ抽出")
        all_entries = self._extract_data()
        print(f"   合計: {len(all_entries)}件")

        # STEP 2: パターン抽出
        print("🔍 STEP 2: パターン抽出")
        patterns = self._extract_patterns(all_entries)

        # STEP 3: knowledge_base保存
        print("💾 STEP 3: knowledge_base保存")
        saved_count = self._save_to_knowledge_base(all_entries, patterns)

        # メトリクス集計
        metrics = {
            "total_entries": len(all_entries),
            "saved_count": saved_count,
            "patterns_found": sum(len(p) for p in patterns.values()),
            "timestamp": datetime.now(),
        }

        print("✅ パイプライン完了")
        return metrics

    def _extract_data(self) -> List[UnifiedLogEntry]:
        """全データソースからデータ抽出"""
        all_entries = []

        for source in self.source_registry.get_all_sources():
            source_name = source.__class__.__name__
            print(f"   🔍 {source_name}...", end="")

            if source.validate():
                entries = source.extract()
                print(f" ✅ {len(entries)}件")
                all_entries.extend(entries)
            else:
                print(" ❌ 検証失敗")

        return all_entries

    def _extract_patterns(self, entries: List[UnifiedLogEntry]) -> Dict[str, List[PatternResult]]:
        """パターン抽出"""
        patterns = self.pattern_extractor.extract_all_patterns(entries)

        # 結果表示
        for pattern_type, pattern_list in patterns.items():
            print(f"   📊 {pattern_type}: {len(pattern_list)}パターン")
            for pattern in pattern_list:
                print(f"      • {pattern.name} (信頼度: {pattern.confidence:.2f}, 件数: {pattern.count})")

        return patterns

    def _save_to_knowledge_base(self, entries: List[UnifiedLogEntry], patterns: Dict[str, List[PatternResult]]) -> int:
        """knowledge_baseに保存"""
        kb_config = self.config.get("knowledge_base", {})
        sheet_name = kb_config.get("sheet_name", "knowledge_base")
        max_entries = kb_config.get("max_entries_per_run", 1000)
        deduplicate = kb_config.get("deduplicate", True)

        try:
            # シート取得または作成
            spreadsheet = self.sheets_manager.gc.open_by_key(os.getenv("SPREADSHEET_ID"))

            try:
                sheet = spreadsheet.worksheet(sheet_name)
                existing_data = sheet.get_all_values()
            except:
                # シートが存在しない場合は作成
                sheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
                existing_data = []

            # 保存対象エントリを選択
            entries_to_save = entries[:max_entries]

            if deduplicate and existing_data:
                # 簡易的な重複除去
                existing_ids = set()
                if len(existing_data) > 1:
                    headers = existing_data[0]
                    if "source_id" in headers:
                        id_index = headers.index("source_id")
                        existing_ids = {row[id_index] for row in existing_data[1:] if len(row) > id_index}

                entries_to_save = [entry for entry in entries_to_save if entry.source_id not in existing_ids]

            # 保存用データ作成
            if not existing_data:
                headers = ["timestamp", "source_type", "source_id", "content_type", "content", "metadata"]
                data_to_save = [headers]
            else:
                data_to_save = []

            for entry in entries_to_save:
                row = [
                    entry.timestamp.isoformat(),
                    entry.source_type.value,
                    entry.source_id,
                    entry.content_type.value,
                    entry.content[:500],
                    str(entry.metadata),
                ]
                data_to_save.append(row)

            # 保存実行
            if len(data_to_save) > (1 if not existing_data else 0):
                if not existing_data:
                    sheet.update("A1", data_to_save)
                else:
                    sheet.append_rows(data_to_save[1:] if len(data_to_save) > 1 else [])

                print(f"   💾 {len(entries_to_save)}件を{sheet_name}に保存")
                return len(entries_to_save)
            else:
                print("   ⏭️  新しいデータなし（スキップ）")
                return 0

        except Exception as e:
            print(f"   ❌ 保存失敗: {e}")
            return 0


# 統一初期化パターンを使用した代替ファクトリ
def create_pipeline(config: Dict[str, Any]) -> DataIntegrationPipeline:
    """パイプライン作成ファクトリ - 統一パターン"""
    return DataIntegrationPipeline(config)


if __name__ == "__main__":
    # テスト実行
    config = {"sources": {"conversation_logs": {"enabled": True}, "spreadsheet_logs": {"enabled": True}}}

    pipeline = create_pipeline(config)
    results = pipeline.run()
    print(f"実行結果: {results}")
