"""
PMAgent v3 修正版 - 完全エラーハンドリング
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# パス設定
project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.base_data_accessor import BaseDataAccessor

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class PMAgentV3Fixed(BaseDataAccessor):
    """PMAgent v3 修正版"""

    def __init__(self, sheets_manager=None):
        try:
            super().__init__(sheets_manager)
            logger.info("✅ PMAgentV3Fixed 初期化完了")
        except Exception as e:
            logger.error(f"❌ PMAgentV3Fixed 初期化エラー: {e}")
            raise

    async def load_project_goal(self) -> Optional[Dict]:
        """active/pending ゴール読み込み"""
        try:
            logger.info("📋 ゴール読み込み中...")

            active_goals = self.read_sheet_as_dicts(
                "project_goal",
                filter_func=lambda g: g.get("status", "").strip().lower() in ["active", "pending"],
            )

            if not active_goals:
                logger.warning("⚠️ active/pending ゴールなし")
                return None

            goal = active_goals[0]
            logger.info(f"✅ ゴール選択: {goal.get('goal_id')}")
            return goal

        except Exception as e:
            logger.error(f"❌ ゴール読み込みエラー: {e}")
            return None

    async def break_down_goal_to_tasks(self, goal: Dict) -> List[Dict]:
        """ゴールをタスクに分解"""
        try:
            goal_id = goal.get("goal_id")
            goal_desc = goal.get("goal_description", "")

            logger.info(f"🔨 タスク分解: {goal_id}")

            # 既存タスクチェック
            existing_tasks = self.read_sheet_as_dicts(
                "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal_id
            )

            if existing_tasks:
                logger.info(f"   既存タスク: {len(existing_tasks)}件")
                return existing_tasks

            # タスク生成
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            tasks = [
                {
                    "task_id": f"{goal_id}_TASK_001",
                    "parent_goal_id": goal_id,
                    "description": f"【調査】{goal_desc[:80]}",
                    "required_role": "developer",
                    "status": "pending",
                    "priority": "high",
                    "estimated_time": "2h",
                    "dependencies": "",
                    "created_at": timestamp,
                    "batch_id": f"BATCH_{goal_id}",
                    "detail_file_path": "",
                    "blank": "",
                    "execution_type": "sequential",
                },
                {
                    "task_id": f"{goal_id}_TASK_002",
                    "parent_goal_id": goal_id,
                    "description": f"【設計】{goal_desc[:80]}",
                    "required_role": "developer",
                    "status": "pending",
                    "priority": "high",
                    "estimated_time": "3h",
                    "dependencies": f"{goal_id}_TASK_001",
                    "created_at": timestamp,
                    "batch_id": f"BATCH_{goal_id}",
                    "detail_file_path": "",
                    "blank": "",
                    "execution_type": "sequential",
                },
                {
                    "task_id": f"{goal_id}_TASK_003",
                    "parent_goal_id": goal_id,
                    "description": f"【実装】{goal_desc[:80]}",
                    "required_role": "developer",
                    "status": "pending",
                    "priority": "high",
                    "estimated_time": "5h",
                    "dependencies": f"{goal_id}_TASK_002",
                    "created_at": timestamp,
                    "batch_id": f"BATCH_{goal_id}",
                    "detail_file_path": "",
                    "blank": "",
                    "execution_type": "sequential",
                },
            ]

            logger.info(f"   ✅ タスク生成: {len(tasks)}件")
            return tasks

        except Exception as e:
            logger.error(f"❌ タスク分解エラー: {e}")
            import traceback

            traceback.print_exc()
            return []

    async def save_tasks_to_sheet(self, tasks: List[Dict]) -> bool:
        """タスクをpm_tasksに保存"""
        try:
            if not tasks:
                return False

            logger.info(f"💾 タスク保存: {len(tasks)}件")

            # 列構造取得
            column_map = self._get_column_map("pm_tasks")
            if not column_map:
                logger.error("❌ 列構造取得失敗")
                return False

            # 辞書→リスト変換
            rows = []
            for task in tasks:
                row = [""] * len(column_map)
                for col_name, col_idx in column_map.items():
                    if col_name in task:
                        row[col_idx] = str(task[col_name])
                rows.append(row)

            # 保存
            success = self.safe_sheets.safe_append("pm_tasks", rows)

            if success:
                logger.info("   ✅ 保存成功")
            else:
                logger.error("   ❌ 保存失敗")

            return success

        except Exception as e:
            logger.error(f"❌ タスク保存エラー: {e}")
            import traceback

            traceback.print_exc()
            return False

    async def run_pm_cycle(self):
        """PMサイクル実行"""
        try:
            logger.info("\n" + "=" * 60)
            logger.info("🔄 PMサイクル開始")
            logger.info("=" * 60)

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

            # 既存チェック
            existing = self.read_sheet_as_dicts(
                "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal.get("goal_id")
            )

            if existing:
                logger.info(f"ℹ️ タスク既存: {len(existing)}件")
            else:
                # 保存
                await self.save_tasks_to_sheet(tasks)

            logger.info("=" * 60)
            logger.info("✅ PMサイクル完了")
            logger.info(f"   ゴール: {goal.get('goal_id')}")
            logger.info(f"   タスク: {len(tasks)}件")
            logger.info("=" * 60 + "\n")

        except Exception as e:
            logger.error(f"❌ PMサイクルエラー: {e}")
            import traceback

            traceback.print_exc()


async def test():
    print("🧪 PMAgent v3 テスト\n")

    try:
        pm = PMAgentV3Fixed()
        await pm.run_pm_cycle()
        print("\n✅ テスト成功")
    except Exception as e:
        print(f"\n❌ テスト失敗: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test())
