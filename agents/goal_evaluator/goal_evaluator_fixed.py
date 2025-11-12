"""
GoalEvaluator修正版 - リスト→辞書変換 + safe_get_data修正
"""

import asyncio
import logging
import os
import sys
from typing import Any, Dict, List, Optional

project_root = os.path.abspath(os.path.dirname(__file__) + "/../..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.safe_sheets_wrapper import SafeSheetsWrapper
from tools.sheets_manager import GoogleSheetsManager

logger = logging.getLogger(__name__)


class GoalEvaluatorFixed:
    """GoalEvaluator修正版"""

    GOAL_SCHEMA = ["goal_id", "status", "description"]
    TASK_SCHEMA = [
        "task_id",
        "parent_goal_id",
        "description",
        "required_role",
        "status",
        "priority",
        "estimated_time",
        "dependencies",
    ]

    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = GoogleSheetsManager()
        self.safe_sheets = SafeSheetsWrapper(self.sheets)
        logger.info("✅ GoalEvaluatorFixed 初期化完了")

    def _convert_row_to_dict(self, row: List[Any], schema: List[str]) -> Dict[str, Any]:
        """行データを辞書に変換"""
        result = {}
        for i, col_name in enumerate(schema):
            if i < len(row):
                result[col_name] = row[i]
            else:
                result[col_name] = ""
        return result

    async def _load_goal(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """
        ゴール読み込み（修正版）

        Args:
            goal_id: ゴールID

        Returns:
            ゴール情報（辞書形式）
        """
        try:
            # ✅ safe_readを使用（safe_get_dataは存在しない）
            goals_list = self.safe_sheets.safe_read("project_goal!A2:C100", default=[])

            if not goals_list:
                return None

            # ✅ リスト→辞書変換
            goals = [self._convert_row_to_dict(row, self.GOAL_SCHEMA) for row in goals_list]

            # goal_idで検索
            for goal in goals:
                if goal.get("goal_id") == goal_id:
                    return goal

            return None

        except Exception as e:
            logger.error(f"❌ ゴール読み込みエラー: {e}")
            return None

    async def _load_tasks_for_goal(self, goal_id: str) -> List[Dict[str, Any]]:
        """ゴールに紐づくタスク読み込み（修正版）"""
        try:
            # ✅ safe_readを使用
            tasks_list = self.safe_sheets.safe_read("pm_tasks!A2:H100", default=[])

            if not tasks_list:
                return []

            # ✅ リスト→辞書変換
            tasks = [self._convert_row_to_dict(row, self.TASK_SCHEMA) for row in tasks_list]

            # parent_goal_idでフィルタ
            goal_tasks = [task for task in tasks if task.get("parent_goal_id") == goal_id]

            return goal_tasks

        except Exception as e:
            logger.error(f"❌ タスク読み込みエラー: {e}")
            return []

    async def evaluate_goal(self, goal_id: str) -> Dict[str, Any]:
        """
        ゴール進捗評価（修正版）

        Args:
            goal_id: ゴールID

        Returns:
            評価結果
        """
        try:
            logger.info(f"�� ゴール評価開始: {goal_id}")

            # ゴール読み込み
            goal = await self._load_goal(goal_id)

            if not goal:
                logger.warning(f"⚠️ ゴールが見つかりません: {goal_id}")
                return {
                    "goal_id": goal_id,
                    "progress_percentage": 0,
                    "completed_tasks": 0,
                    "total_tasks": 0,
                }

            # タスク読み込み
            tasks = await self._load_tasks_for_goal(goal_id)

            total_tasks = len(tasks)
            completed_tasks = sum(
                1 for task in tasks if task.get("status", "").lower() == "completed"
            )

            progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            logger.info(f"✅ ゴール評価完了")
            logger.info(f"   進捗: {progress:.1f}%")
            logger.info(f"   完了: {completed_tasks}/{total_tasks}件")

            return {
                "goal_id": goal_id,
                "progress_percentage": progress,
                "completed_tasks": completed_tasks,
                "total_tasks": total_tasks,
                "goal_description": goal.get("description", ""),
            }

        except Exception as e:
            logger.error(f"❌ ゴール評価エラー: {e}")
            import traceback

            traceback.print_exc()

            return {
                "goal_id": goal_id,
                "progress_percentage": 0,
                "completed_tasks": 0,
                "total_tasks": 0,
                "error": str(e),
            }


# テスト
async def test_goal_evaluator():
    print("🧪 GoalEvaluator修正版テスト\n")

    evaluator = GoalEvaluatorFixed(None)

    # テスト1: ゴール読み込み
    print("テスト1: ゴール読み込み")
    goal = await evaluator._load_goal("1")
    if goal:
        print(f"✅ 成功: {goal.get('goal_id')} - {goal.get('description', '')[:50]}...")
    else:
        print("❌ ゴールなし")

    # テスト2: ゴール評価
    print("\nテスト2: ゴール評価")
    result = await evaluator.evaluate_goal("1")
    print(f"進捗: {result['progress_percentage']:.1f}%")
    print(f"完了: {result['completed_tasks']}/{result['total_tasks']}件")


if __name__ == "__main__":
    asyncio.run(test_goal_evaluator())
