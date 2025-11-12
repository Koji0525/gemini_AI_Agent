"""
QualityFeedbackLoop修正版
append_rows使用
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict

project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.sheets_manager import GoogleSheetsManager

logger = logging.getLogger(__name__)


class QualityFeedbackLoopFixed:
    """品質フィードバックループ修正版"""

    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = sheets_manager
        logger.info("✅ QualityFeedbackLoopFixed 初期化完了")

    async def process_task_result(self, task: Dict[str, Any], result: Dict[str, Any]):
        """タスク結果を処理"""
        try:
            task_id = task.get("task_id", "UNKNOWN")
            logger.info(f"📊 品質判定: {task_id} → スコア {result.get('quality_score', 0)}/10")

            # 品質スコアが7未満の場合、代替案を生成
            if result.get("quality_score", 0) < 7:
                logger.info(f"  🔄 代替案生成: 代替案: 別の方法で実装を試みる")

                # フィードバックを記録
                feedback_row = [
                    [
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        task_id,
                        task.get("description", ""),
                        str(result.get("quality_score", 0)),
                        "品質改善が必要",
                        "代替アプローチを検討",
                    ]
                ]

                # ✅ 修正: append_rows を使用
                try:
                    self.sheets.append_rows("quality_feedback", feedback_row)
                    logger.info("  ✅ フィードバック記録完了")
                except Exception as e:
                    logger.warning(f"  ⚠️ フィードバック記録エラー（シートなし）: {e}")

        except Exception as e:
            logger.error(f"❌ 品質処理エラー: {e}")


if __name__ == "__main__":
    import asyncio

    async def test():
        sheets = GoogleSheetsManager()
        loop = QualityFeedbackLoopFixed(sheets)

        task = {"task_id": "TEST_001", "description": "テストタスク"}
        result = {"quality_score": 5}

        await loop.process_task_result(task, result)

    asyncio.run(test())
