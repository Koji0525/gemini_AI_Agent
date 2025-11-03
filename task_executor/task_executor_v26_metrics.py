"""
TaskExecutor v26 - 計測機能付き
作成日: 2025-11-03
"""

import time
import asyncio
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskExecutor:
    def __init__(self, sheets_manager, browser_controller=None):
        self.sheets = sheets_manager
        self.browser = browser_controller
        self.execution_stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "total_execution_time": 0,
        }

    async def execute_single_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_start = time.time()
        task_id = task.get("task_id", "unknown")
        retry_count = task.get("retry_count", 0)

        result = {
            "task_id": task_id,
            "task_name": task.get("task_name", "unknown"),
            "status": "failed",
            "output": None,
            "elapsed_time": 0,
            "retry_count": retry_count,
            "error_type": None,
            "fix_applied": False,
        }

        try:
            output = await self._call_agent(task)
            elapsed = time.time() - task_start

            result.update(
                {"status": "completed", "output": output, "elapsed_time": round(elapsed, 2)}
            )

            self.execution_stats["successful_tasks"] += 1
            self.execution_stats["total_execution_time"] += elapsed

        except Exception as e:
            elapsed = time.time() - task_start
            result.update({"elapsed_time": round(elapsed, 2), "error_type": type(e).__name__})
            self.execution_stats["failed_tasks"] += 1

        finally:
            self.execution_stats["total_tasks"] += 1
            await self._save_execution_log(task, result)

        return result

    async def _call_agent(self, task):
        await asyncio.sleep(0.1)
        return f"Task completed: {task.get('task_name')}"

    async def _save_execution_log(self, task, result):
        log_entry = [
            task.get("task_id", ""),
            task.get("task_name", ""),
            task.get("assigned_agent", ""),
            result["status"],
            str(result.get("output", "")),
            "",
            "",
            "",
            "",  # 既存カラム
            result["elapsed_time"],
            result["retry_count"],
            result.get("error_type", ""),
            result.get("fix_applied", False),
        ]
        try:
            await self.sheets.append_row("task_execution_log", log_entry)
        except Exception as e:
            logger.error(f"ログ記録失敗: {str(e)}")

    def get_stats(self):
        total = self.execution_stats["total_tasks"]
        if total == 0:
            return {"success_rate": 0, "avg_execution_time": 0, **self.execution_stats}
        return {
            "success_rate": round(self.execution_stats["successful_tasks"] / total * 100, 2),
            "avg_execution_time": round(self.execution_stats["total_execution_time"] / total, 2),
            **self.execution_stats,
        }
