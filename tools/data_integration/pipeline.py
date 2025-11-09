#!/usr/bin/env python3
"""
モック対応版データ統合パイプライン
"""
import logging
import os
from typing import Any, Dict

logger = logging.getLogger(__name__)


class DataIntegrationPipeline:
    def __init__(self):
        self.is_test_mode = os.getenv("TEST_MODE", "False").lower() == "true"
        logger.info(
            f"🧪 データ統合パイプライン - モード: {'テスト' if self.is_test_mode else '本番'}"
        )

    def run_pipeline(self) -> Dict[str, Any]:
        """パイプラインを実行（モック対応版）"""
        logger.info("🚀 データ統合パイプライン開始")

        results = {
            "conversation_logs": self._process_conversation_logs(),
            "spreadsheet_logs": self._process_spreadsheet_logs(),
            "test_mode": self.is_test_mode,
            "status": "success",
        }

        total_processed = (
            results["conversation_logs"]["count"] + results["spreadsheet_logs"]["count"]
        )
        logger.info(f"✅ データ統合パイプライン完了 - 合計 {total_processed} 件処理")

        return results

    def _process_conversation_logs(self) -> Dict[str, Any]:
        """会話ログを処理（モック対応版）"""
        logger.info("📝 会話ログを処理中...")

        try:
            from tools.sheets_manager import GoogleSheetsManager

            manager = GoogleSheetsManager()

            conversation_data = manager.read_range("会話ログ!A2:C100", [])

            if self.is_test_mode:
                logger.info(f"🧪 テストモード: 会話ログ {len(conversation_data)}件 処理完了")
            else:
                logger.info(f"✅ 会話ログ: {len(conversation_data)}件 処理完了")

            return {"count": len(conversation_data), "data": conversation_data, "source": "sheets"}

        except Exception as e:
            logger.error(f"❌ 会話ログ処理エラー: {e}")
            return {"count": 0, "data": [], "error": str(e), "source": "error"}

    def _process_spreadsheet_logs(self) -> Dict[str, Any]:
        """スプレッドシートログを処理（モック対応版）"""
        logger.info("📊 スプレッドシートログを処理中...")

        try:
            from tools.sheets_manager import GoogleSheetsManager

            manager = GoogleSheetsManager()

            task_data = manager.read_range("タスクログ!A2:C100", [])

            if self.is_test_mode:
                logger.info(f"�� テストモード: タスクログ {len(task_data)}件 処理完了")
            else:
                logger.info(f"✅ タスクログ: {len(task_data)}件 処理完了")

            return {"count": len(task_data), "data": task_data, "source": "sheets"}

        except Exception as e:
            logger.error(f"❌ スプレッドシートログ処理エラー: {e}")
            return {"count": 0, "data": [], "error": str(e), "source": "error"}


# テスト用
if __name__ == "__main__":
    # テストモードで実行
    import os

    os.environ["TEST_MODE"] = "true"

    pipeline = DataIntegrationPipeline()
    results = pipeline.run_pipeline()
    print(f"パイプライン実行結果: {results}")
