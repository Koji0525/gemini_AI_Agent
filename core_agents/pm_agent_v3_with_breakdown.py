"""
PMAgent v3 - タスク分解機能付き
ゴールからタスクを自動生成
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.base_data_accessor import BaseDataAccessor

logger = logging.getLogger(__name__)


class PMAgentV3(BaseDataAccessor):
    """PMAgent v3 - タスク分解機能付き"""

    def __init__(self, sheets_manager=None):
        super().__init__(sheets_manager)
        logger.info("✅ PMAgentV3 初期化完了")

    async def load_project_goal(self) -> Optional[Dict]:
        """active/pending ゴール読み込み"""
        try:
            logger.info("📋 project_goal読み込み中...")

            # active/pending ゴールを取得
            active_goals = self.read_sheet_as_dicts(
                "project_goal",
                filter_func=lambda g: g.get("status", "").strip().lower() in ["active", "pending"],
            )

            logger.info(f"🎯 active/pending ゴール: {len(active_goals)}件")

            if not active_goals:
                logger.warning("⚠️ 処理可能な目標がありません")
                return None

            selected_goal = active_goals[0]
            logger.info(f"✅ ゴール選択: {selected_goal.get('goal_id')}")

            return selected_goal

        except Exception as e:
            logger.error(f"❌ 目標読み込みエラー: {e}")
            return None

    async def break_down_goal_to_tasks(self, goal: Dict) -> List[Dict]:
        """
        ゴールをタスクに分解

        Args:
            goal: ゴール情報

        Returns:
            タスクのリスト
        """
        try:
            goal_id = goal.get("goal_id")
            goal_desc = goal.get("goal_description", "")

            logger.info(f"🔨 ゴール分解開始: {goal_id}")
            logger.info(f"   内容: {goal_desc[:100]}...")

            # 既存タスクをチェック
            existing_tasks = self.read_sheet_as_dicts(
                "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal_id
            )

            if existing_tasks:
                logger.info(f"   既存タスク: {len(existing_tasks)}件")
                return existing_tasks

            # タスク分解（シンプルな3フェーズ分解）
            logger.info("   タスク生成中...")

            tasks = [
                {
                    "task_id": f"{goal_id}_TASK_001",
                    "parent_goal_id": goal_id,
                    "description": f"【調査】{goal_desc[:80]}...",
                    "required_role": "developer",
                    "status": "pending",
                    "priority": "high",
                    "estimated_time": "2h",
                    "dependencies": "",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "batch_id": f"BATCH_{goal_id}",
                    "detail_file_path": "",
                    "execution_type": "sequential",
                },
                {
                    "task_id": f"{goal_id}_TASK_002",
                    "parent_goal_id": goal_id,
                    "description": f"【設計】{goal_desc[:80]}...",
                    "required_role": "developer",
                    "status": "pending",
                    "priority": "high",
                    "estimated_time": "3h",
                    "dependencies": f"{goal_id}_TASK_001",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "batch_id": f"BATCH_{goal_id}",
                    "detail_file_path": "",
                    "execution_type": "sequential",
                },
                {
                    "task_id": f"{goal_id}_TASK_003",
                    "parent_goal_id": goal_id,
                    "description": f"【実装】{goal_desc[:80]}...",
                    "required_role": "developer",
                    "status": "pending",
                    "priority": "high",
                    "estimated_time": "5h",
                    "dependencies": f"{goal_id}_TASK_002",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "batch_id": f"BATCH_{goal_id}",
                    "detail_file_path": "",
                    "execution_type": "sequential",
                },
            ]

            logger.info(f"   ✅ タスク生成完了: {len(tasks)}件")

            return tasks

        except Exception as e:
            logger.error(f"❌ タスク分解エラー: {e}")
            import traceback

            traceback.print_exc()
            return []

    async def save_tasks_to_sheet(self, tasks: List[Dict]) -> bool:
        """
        タスクをpm_tasksシートに保存

        Args:
            tasks: タスクのリスト

        Returns:
            成功した場合True
        """
        try:
            if not tasks:
                return False

            logger.info(f"💾 タスク保存中: {len(tasks)}件")

            # 列構造を取得
            column_map = self._get_column_map("pm_tasks")

            # 辞書→リスト変換
            rows = []
            for task in tasks:
                row = [""] * len(column_map)
                for col_name, col_idx in column_map.items():
                    if col_name in task:
                        row[col_idx] = task[col_name]
                rows.append(row)

            # シートに追加
            success = self.safe_sheets.safe_append("pm_tasks", rows)

            if success:
                logger.info("   ✅ タスク保存成功")
            else:
                logger.error("   ❌ タスク保存失敗")

            return success

        except Exception as e:
            logger.error(f"❌ タスク保存エラー: {e}")
            import traceback

            traceback.print_exc()
            return False

    async def run_pm_cycle(self):
        """PMサイクル実行（タスク分解含む）"""
        try:
            logger.info("🔄 PMサイクル開始")

            # ゴール読み込み
            goal = await self.load_project_goal()

            if not goal:
                logger.warning("⚠️ 処理可能なゴールなし")
                return

            # タスク分解
            tasks = await self.break_down_goal_to_tasks(goal)

            if not tasks:
                logger.warning("⚠️ タスク生成失敗")
                return

            # 新規タスクのみ保存
            existing_tasks = self.read_sheet_as_dicts(
                "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal.get("goal_id")
            )

            if not existing_tasks:
                # タスク保存
                await self.save_tasks_to_sheet(tasks)
            else:
                logger.info(f"   ℹ️ タスクは既に存在（{len(existing_tasks)}件）")

            logger.info("✅ PMサイクル完了")
            logger.info(f"   処理ゴール: {goal.get('goal_id')}")
            logger.info(f"   タスク数: {len(tasks)}件")

        except Exception as e:
            logger.error(f"❌ PMサイクルエラー: {e}")


# テスト
async def test_pm_agent_v3():
    print("🧪 PMAgent v3 テスト\n")

    pm = PMAgentV3()

    # テスト: PMサイクル実行
    print("テスト: PMサイクル実行（タスク分解含む）")
    await pm.run_pm_cycle()


if __name__ == "__main__":
    asyncio.run(test_pm_agent_v3())
