#!/usr/bin/env python3
"""
タスク完了ハンドラー
タスク完了時に次のタスクを自動生成
"""
import logging
from typing import Dict, List
import sys

sys.path.insert(0, ".")

from tools.sheets_manager_v02_mapped import GoogleSheetsManager

logger = logging.getLogger(__name__)


class TaskCompletionHandler:
    """タスク完了後の処理を担当"""

    def __init__(self, sheets: GoogleSheetsManager):
        self.sheets = sheets
        self.logger = logger

    async def on_task_completed(self, task: Dict, result: Dict) -> None:
        """
        タスク完了時の処理

        Args:
            task: 完了したタスク
            result: 実行結果
        """
        try:
            self.logger.info(f"🎯 タスク完了処理開始: {task.get('task_id', 'unknown')}")

            # 1. 目標達成度を評価
            progress = await self.evaluate_progress(task)
            self.logger.info(f"📊 進捗評価: {progress}%")

            # 2. 次のタスクが必要か判断
            if progress < 100:
                # 3. 次のタスクを生成
                next_tasks = await self.generate_next_tasks(task, progress, result)

                if next_tasks:
                    # 4. pm_tasksに追加
                    await self.add_tasks_to_queue(next_tasks)
                    self.logger.info(f"✅ 次のタスク{len(next_tasks)}件を追加")
            else:
                self.logger.info("🎉 目標達成！")

        except Exception as e:
            self.logger.error(f"❌ タスク完了処理エラー: {e}")

    async def evaluate_progress(self, completed_task: Dict) -> float:
        """
        目標達成度を評価

        Returns:
            進捗率（0-100）
        """
        try:
            # project_goalから目標取得
            goals = self.sheets.get_data("project_goal")
            if not goals:
                return 0.0

            # 完了タスク数をカウント
            all_tasks = self.sheets.get_data("pm_tasks")
            if not all_tasks:
                return 0.0

            completed_count = sum(1 for t in all_tasks if t.get("status") == "completed")
            total_count = len(all_tasks)

            if total_count == 0:
                return 0.0

            progress = (completed_count / total_count) * 100
            return round(progress, 2)

        except Exception as e:
            self.logger.error(f"進捗評価エラー: {e}")
            return 0.0

    async def generate_next_tasks(
        self, completed_task: Dict, progress: float, result: Dict
    ) -> List[Dict]:
        """
        次のタスクを生成

        Returns:
            新しいタスクのリスト
        """
        next_tasks = []

        try:
            # 完了したタスクの結果を分析
            task_type = completed_task.get("required_role", "unknown")

            # 簡易的な次タスク生成ロジック
            if "design" in task_type.lower():
                # デザインタスク完了 → 実装タスク生成
                next_tasks.append(
                    {
                        "task_id": f"auto_{completed_task.get('task_id', 'unknown')}_impl",
                        "description": f"{completed_task.get('description', '')}の実装",
                        "required_role": "dev_agent",
                        "status": "pending",
                        "parent_task": completed_task.get("task_id"),
                        "auto_generated": True,
                    }
                )

            elif "dev" in task_type.lower() or "implementation" in task_type.lower():
                # 実装タスク完了 → テストタスク生成
                next_tasks.append(
                    {
                        "task_id": f"auto_{completed_task.get('task_id', 'unknown')}_test",
                        "description": f"{completed_task.get('description', '')}のテスト",
                        "required_role": "review_agent",
                        "status": "pending",
                        "parent_task": completed_task.get("task_id"),
                        "auto_generated": True,
                    }
                )

            # より高度な生成ロジックはPM Agentに委譲（将来実装）

        except Exception as e:
            self.logger.error(f"次タスク生成エラー: {e}")

        return next_tasks

    async def add_tasks_to_queue(self, tasks: List[Dict]) -> bool:
        """
        タスクをpm_tasksに追加

        Args:
            tasks: 追加するタスクのリスト

        Returns:
            成功したらTrue
        """
        try:
            for task in tasks:
                self.sheets.append_row("pm_tasks", task)
                self.logger.info(f"✅ タスク追加: {task.get('task_id')}")

            return True

        except Exception as e:
            self.logger.error(f"タスク追加エラー: {e}")
            return False
