"""
PMAgent - Project Management Agent（sheets_schema対応版）
運用ルール: SafeSheetsWrapper必須、sheets_schema参照
"""

import sys
import os
import logging
from typing import Dict, Any, Optional, List
import asyncio

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from tools.sheets_manager import GoogleSheetsManager
from tools.safe_sheets_wrapper import SafeSheetsWrapper
from configuration.sheets_schema import (
    PROJECT_GOAL_SCHEMA,
    PM_TASKS_SCHEMA,
    get_schema,
    row_to_dict,
    dict_to_row,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PMAgent:
    """
    Project Management Agent（sheets_schema統合版）

    【主な機能】
    1. project_goalから目標を読み込み
    2. 目標をタスクに分解
    3. pm_tasksに書き込み
    """

    def __init__(self, sheets_manager: GoogleSheetsManager):
        """
        Args:
            sheets_manager: GoogleSheetsManager（外部から注入）
        """
        self.sheets = SafeSheetsWrapper(sheets_manager)
        self.current_goal = None
        logger.info("✅ PMAgent を初期化しました（sheets_schema対応）")

    async def load_project_goal(self) -> Optional[Dict]:
        """
        project_goalから最新のアクティブな目標を読み込み

        Returns:
            目標情報（辞書形式）
        """
        try:
            # schemas定義を参照
            schema = get_schema("project_goal")
            expected_headers = schema["headers"]

            logger.info(f"📋 project_goalを読み込み中（期待ヘッダー: {expected_headers}）")

            # SafeSheetsWrapperで安全に読み取り
            all_goals = self.sheets.safe_read("project_goal", default=[])

            if not all_goals:
                logger.warning("⚠️ project_goalにデータがありません")
                return None

            # activeまたはpendingステータスの目標を検索
            active_goals = [
                goal
                for goal in all_goals
                if goal.get("status", "").lower() in ["active", "pending"]
            ]

            if not active_goals:
                logger.warning("⚠️ アクティブな目標が見つかりません")
                return None

            # 最新の目標を取得
            latest_goal = active_goals[0]

            logger.info(f"✅ 目標を読み込みました: {latest_goal.get('goal_id', 'unknown')}")
            logger.info(f"   説明: {latest_goal.get('goal_description', '')[:50]}...")

            self.current_goal = latest_goal
            return latest_goal

        except Exception as e:
            logger.error(f"❌ 目標読み込みエラー: {e}")
            import traceback

            traceback.print_exc()
            return None

    async def break_down_goal_to_tasks(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        目標をタスクに分解

        Args:
            goal: 目標情報

        Returns:
            タスクのリスト
        """
        goal_id = goal.get("goal_id", "unknown")
        goal_desc = goal.get("goal_description", "")

        logger.info(f"🔧 目標をタスクに分解中: {goal_id}")

        # TODO: 実際のタスク分解ロジック（LLM使用）
        # 現在は仮の実装

        tasks = [
            {
                "task_id": f"{goal_id}_TASK_001",
                "parent_goal_id": goal_id,
                "description": f"{goal_desc} - サブタスク1",
                "required_role": "developer",
                "status": "pending",
                "priority": "high",
                "estimated_time": "2h",
                "dependencies": "",
                "created_at": "",
                "batch_id": "",
                "detail_file_path": "",
                "blank": "",
                "execution_type": "manual",
            },
            {
                "task_id": f"{goal_id}_TASK_002",
                "parent_goal_id": goal_id,
                "description": f"{goal_desc} - サブタスク2",
                "required_role": "developer",
                "status": "pending",
                "priority": "medium",
                "estimated_time": "1h",
                "dependencies": f"{goal_id}_TASK_001",
                "created_at": "",
                "batch_id": "",
                "detail_file_path": "",
                "blank": "",
                "execution_type": "manual",
            },
        ]

        logger.info(f"✅ {len(tasks)}個のタスクを生成しました")
        return tasks

    async def write_tasks_to_sheet(self, tasks: List[Dict[str, Any]]):
        """
        タスクをpm_tasksに書き込み

        Args:
            tasks: タスクのリスト
        """
        try:
            logger.info(f"📝 {len(tasks)}個のタスクをpm_tasksに書き込み中...")

            # schemas定義に従って行データに変換
            task_rows = [dict_to_row("pm_tasks", task) for task in tasks]

            # SafeSheetsWrapperで安全に追記
            for i, task_row in enumerate(task_rows, 1):
                success = self.sheets.safe_append("pm_tasks", [task_row])

                if success:
                    logger.info(f"  ✅ タスク {i}/{len(task_rows)} 書き込み完了")
                else:
                    logger.warning(f"  ⚠️ タスク {i}/{len(task_rows)} 書き込み失敗")

            logger.info("✅ すべてのタスク書き込み完了")

        except Exception as e:
            logger.error(f"❌ タスク書き込みエラー: {e}")
            import traceback

            traceback.print_exc()

    async def run_pm_cycle(self):
        """
        PMサイクルを1回実行

        1. 目標読み込み
        2. タスク分解
        3. タスク書き込み
        """
        logger.info("🔄 PMサイクル開始")

        # 目標読み込み
        goal = await self.load_project_goal()

        if not goal:
            logger.warning("ℹ️ 処理可能な目標がありません")
            return

        # タスク分解
        tasks = await self.break_down_goal_to_tasks(goal)

        if not tasks:
            logger.warning("⚠️ タスクが生成されませんでした")
            return

        # タスク書き込み
        await self.write_tasks_to_sheet(tasks)

        logger.info("✅ PMサイクル完了")


async def test_pm_agent():
    """テスト実行"""
    print("\n" + "=" * 60)
    print("🧪 PMAgent テスト（sheets_schema対応版）")
    print("=" * 60)

    try:
        sheets = GoogleSheetsManager()
        pm_agent = PMAgent(sheets)

        # PMサイクルを1回実行
        await pm_agent.run_pm_cycle()

        print("\n" + "=" * 60)
        print("✅ テスト完了")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ テスト中にエラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_pm_agent())
