#!/usr/bin/env python3
"""
修正版データ統合パイプライン - テスト環境対応
"""
import logging
import os
from typing import Any, Dict

logger = logging.getLogger(__name__)


class DataIntegrationPipeline:
    def __init__(self):
        self.is_test_mode = os.getenv("TEST_MODE", "False").lower() == "true"
        self.sheets_manager = None

        if not self.is_test_mode:
            try:
                from tools.sheets_manager_fixed import GoogleSheetsManager

                self.sheets_manager = GoogleSheetsManager()
            except ImportError as e:
                logger.warning(f"⚠️ スプレッドシートマネージャーのインポートに失敗: {e}")
                self.is_test_mode = True

    def run_pipeline(self) -> Dict[str, Any]:
        """パイプラインを実行（テスト対応版）"""
        logger.info("🚀 データ統合パイプライン開始")

        results = {
            "conversation_logs": self._process_conversation_logs(),
            "spreadsheet_logs": self._process_spreadsheet_logs(),
            "test_mode": self.is_test_mode,
        }

        logger.info("✅ データ統合パイプライン完了")
        return results

    def _process_conversation_logs(self) -> Dict[str, Any]:
        """会話ログを処理（テスト対応版）"""
        logger.info("📝 会話ログを処理中...")

        if self.is_test_mode:
            # テスト用のダミーデータ
            dummy_data = [
                ["2024-01-01", "ユーザー", "テストメッセージ"],
                ["2024-01-01", "AI", "テスト応答"],
            ]
            logger.info(f"🧪 テストモード: 会話ログ {len(dummy_data)}件 処理完了")
            return {"count": len(dummy_data), "data": dummy_data}

        try:
            # 実際の会話ログ処理
            conversation_data = self.sheets_manager.read_range(
                "会話ログ!A2:C100", [["2024-01-01", "ユーザー", "テストメッセージ"]]
            )
            logger.info(f"✅ 会話ログ: {len(conversation_data)}件 処理完了")
            return {"count": len(conversation_data), "data": conversation_data}

        except Exception as e:
            logger.error(f"❌ 会話ログ処理エラー: {e}")
            return {"count": 0, "data": [], "error": str(e)}

    def _process_spreadsheet_logs(self) -> Dict[str, Any]:
        """スプレッドシートログを処理（テスト対応版）"""
        logger.info("📊 スプレッドシートログを処理中...")

        if self.is_test_mode:
            # テスト用のダミーデータ
            dummy_data = [["タスク1", "完了", "2024-01-01"]]
            logger.info(f"🧪 テストモード: タスクログ {len(dummy_data)}件 処理完了")
            return {"count": len(dummy_data), "data": dummy_data}

        try:
            # 実際のスプレッドシートログ処理
            task_data = self.sheets_manager.read_range(
                "タスクログ!A2:C100", [["タスク1", "完了", "2024-01-01"]]
            )
            logger.info(f"✅ タスクログ: {len(task_data)}件 処理完了")
            return {"count": len(task_data), "data": task_data}

        except Exception as e:
            logger.error(f"❌ スプレッドシートログ処理エラー: {e}")
            return {"count": 0, "data": [], "error": str(e)}


# テスト用
if __name__ == "__main__":
    pipeline = DataIntegrationPipeline()
    results = pipeline.run_pipeline()
    print(f"パイプライン実行結果: {results}")
