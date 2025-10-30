#!/usr/bin/env python3
"""
データ統合パイプライン - 複数ソースからデータを統合
変更理由: 新規作成 - ダッシュボードから呼び出される統合処理
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

# プロジェクトルート設定
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.sheets_manager import GoogleSheetsManager
except ImportError:
    # フォールバック
    import importlib.util

    spec = importlib.util.spec_from_file_location("sheets_manager", project_root / "tools" / "sheets_manager.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    GoogleSheetsManager = module.GoogleSheetsManager


class DataIntegrationPipeline:
    """データ統合パイプライン"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.sheets_manager = GoogleSheetsManager()
        self.results = {"total_entries": 0, "sources_processed": [], "errors": []}

    def run(self) -> Dict[str, Any]:
        """パイプライン実行"""
        self.logger.info("🚀 データ統合パイプライン開始")

        # 各ソースからデータを取得
        sources = self.config.get("sources", {})

        if sources.get("conversation_logs", {}).get("enabled"):
            self._process_conversation_logs()

        if sources.get("spreadsheet_logs", {}).get("enabled"):
            self._process_spreadsheet_logs()

        self.logger.info("✅ データ統合パイプライン完了")
        return self.results

    def _process_conversation_logs(self):
        """会話ログを処理"""
        try:
            self.logger.info("📝 会話ログを処理中...")

            # knowledge_baseシートからデータ取得
            kb_data = self.sheets_manager.read_range("knowledge_base")

            if kb_data and len(kb_data) > 1:
                entries = len(kb_data) - 1  # ヘッダー除く
                self.results["total_entries"] += entries
                self.results["sources_processed"].append("conversation_logs")
                self.logger.info(f"✅ 会話ログ: {entries}件 処理完了")
            else:
                self.logger.warning("⚠️ 会話ログが見つかりません")

        except Exception as e:
            error_msg = f"会話ログ処理エラー: {e}"
            self.logger.error(f"❌ {error_msg}")
            self.results["errors"].append(error_msg)

    def _process_spreadsheet_logs(self):
        """スプレッドシートログを処理"""
        try:
            self.logger.info("📊 スプレッドシートログを処理中...")

            # task_execution_logシートからデータ取得
            task_data = self.sheets_manager.read_range("task_execution_log")

            if task_data and len(task_data) > 1:
                entries = len(task_data) - 1  # ヘッダー除く
                self.results["total_entries"] += entries
                self.results["sources_processed"].append("spreadsheet_logs")
                self.logger.info(f"✅ タスクログ: {entries}件 処理完了")
            else:
                self.logger.warning("⚠️ タスクログが見つかりません")

        except Exception as e:
            error_msg = f"スプレッドシートログ処理エラー: {e}"
            self.logger.error(f"❌ {error_msg}")
            self.results["errors"].append(error_msg)


def create_pipeline(config: Dict[str, Any]) -> DataIntegrationPipeline:
    """パイプラインを作成"""
    return DataIntegrationPipeline(config)


if __name__ == "__main__":
    # テスト実行
    logging.basicConfig(level=logging.INFO)

    test_config = {"sources": {"conversation_logs": {"enabled": True}, "spreadsheet_logs": {"enabled": True}}}

    pipeline = create_pipeline(test_config)
    results = pipeline.run()

    print("\n📊 パイプライン実行結果:")
    print(f"   処理データ数: {results['total_entries']}件")
    print(f"   処理ソース: {', '.join(results['sources_processed'])}")
    if results["errors"]:
        print(f"   エラー: {len(results['errors'])}件")
