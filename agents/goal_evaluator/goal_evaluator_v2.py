"""
GoalEvaluator v2 - TaskExecutorパターン完全適用版
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


class GoalEvaluatorV2:
    """GoalEvaluator v2 - TaskExecutorパターン完全適用"""

    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = GoogleSheetsManager()
        self.safe_sheets = SafeSheetsWrapper(self.sheets)

        # ✅ ヘッダー行から列構造を検出
        self.goal_column_map = {}
        self.task_column_map = {}
        self._initialize_column_maps()

        logger.info("✅ GoalEvaluatorV2 初期化完了")

    def _initialize_column_maps(self):
        """列構造の初期化"""
        try:
            # project_goal のヘッダー
            goal_headers = self.safe_sheets.safe_read("project_goal!A1:Z1", default=[])
            if goal_headers:
                self.goal_column_map = {header: idx for idx, header in enumerate(goal_headers[0])}
                logger.info(f"✅ project_goal列構造: {list(self.goal_column_map.keys())}")

            # pm_tasks のヘッダー
            task_headers = self.safe_sheets.safe_read("pm_tasks!A1:Z1", default=[])
            if task_headers:
                self.task_column_map = {header: idx for idx, header in enumerate(task_headers[0])}
                logger.info(f"✅ pm_tasks列構造: {list(self.task_column_map.keys())}")

        except Exception as e:
            logger.error(f"❌ 列構造初期化エラー: {e}")

    def _convert_row_to_dict(self, row: List[Any], column_map: Dict[str, int]) -> Dict[str, Any]:
        """行データを辞書に変換"""
        result = {}
        for col_name, col_idx in column_map.items():
            if col_idx < len(row):
                result[col_name] = row[col_idx]
            else:
                result[col_name] = ""
        return result

    async def _load_goal(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """ゴール読み込み（v2）"""
        try:
            goals_list = self.safe_sheets.safe_read("project_goal!A2:Z100", default=[])

            if not goals_list:
                return None

            # リスト→辞書変換
            goals = [self._convert_row_to_dict(row, self.goal_column_map) for row in goals_list]

            # goal_idで検索
            for goal in goals:
                if str(goal.get("goal_id")) == str(goal_id):
                    return goal

            return None

        except Exception as e:
            logger.error(f"❌ ゴール読み込みエラー: {e}")
            return None

    async def _load_tasks_for_goal(self, goal_id: str) -> List[Dict[str, Any]]:
        """ゴールに紐づくタスク読み込み（v2）"""
        try:
            tasks_list = self.safe_sheets.safe_read("pm_tasks!A2:Z100", default=[])

            if not tasks_list:
                return []

            # リスト→辞書変換
            tasks = [self._convert_row_to_dict(row, self.task_column_map) for row in tasks_list]

            # parent_goal_idでフィルタ
            goal_tasks = [task for task in tasks if str(task.get("parent_goal_id")) == str(goal_id)]

            return goal_tasks

        except Exception as e:
            logger.error(f"❌ タスク読み込みエラー: {e}")
            return []

    async def evaluate_goal(self, goal_id: str) -> Dict[str, Any]:
        """ゴール進捗評価（v2）"""
        try:
            logger.info(f"📊 ゴール評価開始: {goal_id}")

            goal = await self._load_goal(goal_id)

            if not goal:
                logger.warning(f"⚠️ ゴールが見つかりません: {goal_id}")
                return {
                    "goal_id": goal_id,
                    "progress_percentage": 0,
                    "completed_tasks": 0,
                    "total_tasks": 0,
                }

            tasks = await self._load_tasks_for_goal(goal_id)

            total_tasks = len(tasks)
            completed_tasks = sum(
                1 for task in tasks if task.get("status", "").strip().lower() == "completed"
            )

            progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            logger.info(f"✅ ゴール評価完了")
            logger.info(f"   進捗: {progress:.1f}%")
            logger.info(f"   完了: {completed_tasks}/{total_tasks}件")

            desc = goal.get("goal_description", goal.get("description", ""))

            return {
                "goal_id": goal_id,
                "progress_percentage": progress,
                "completed_tasks": completed_tasks,
                "total_tasks": total_tasks,
                "goal_description": desc,
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
async def test_goal_evaluator_v2():
    print("🧪 GoalEvaluator v2 テスト\n")

    evaluator = GoalEvaluatorV2(None)

    # テスト: ゴール評価
    print("テスト: ゴール評価（goal_id=6）")
    result = await evaluator.evaluate_goal("6")
    print(f"進捗: {result['progress_percentage']:.1f}%")
    print(f"完了: {result['completed_tasks']}/{result['total_tasks']}件")


if __name__ == "__main__":
    asyncio.run(test_goal_evaluator_v2())
