"""
QualityFeedbackLoop - 品質フィードバックループ
作成日: 2025-11-03
"""

import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QualityFeedbackLoop:
    def __init__(self, sheets_manager, task_executor, gemini_client=None):
        self.sheets = sheets_manager
        self.executor = task_executor
        self.gemini = gemini_client
        self.stats = {
            "accepted_high": 0,
            "accepted_ok": 0,
            "retry_improvement": 0,
            "retry_alternative": 0,
        }

    async def process_task_result(
        self, task: Dict[str, Any], result: Dict[str, Any]
    ) -> Dict[str, Any]:
        quality_score = result.get("quality_score", 0)

        if quality_score >= 9:
            await self._mark_as_completed(task, result)
            self.stats["accepted_high"] += 1
            return {"action": "accepted", "reason": "high_quality"}

        elif quality_score >= 7:
            await self._mark_as_completed(task, result)
            self.stats["accepted_ok"] += 1
            return {"action": "accepted_with_notes", "reason": "acceptable"}

        elif quality_score >= 5:
            self.stats["retry_improvement"] += 1
            return {"action": "retry_with_improvement", "reason": "needs_improvement"}

        else:
            self.stats["retry_alternative"] += 1
            return {"action": "retry_with_alternative", "reason": "unacceptable"}

    async def _mark_as_completed(self, task, result):
        logger.info(f"✅ タスク完了: {task.get('task_name')}")

    def get_stats(self):
        total = sum(self.stats.values())
        if total == 0:
            return {**self.stats, "acceptance_rate": 0, "retry_rate": 0}
        return {
            **self.stats,
            "acceptance_rate": round(
                (self.stats["accepted_high"] + self.stats["accepted_ok"]) / total * 100, 2
            ),
            "retry_rate": round(
                (self.stats["retry_improvement"] + self.stats["retry_alternative"]) / total * 100, 2
            ),
        }
