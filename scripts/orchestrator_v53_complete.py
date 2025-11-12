"""
オーケストレーター v53 - 要件定義書v4.0完全実装
全機能統合・実動作版
"""

import asyncio
import logging
import os
import sys

project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.observability.observability_manager import ObservabilityManager
from core_agents.integrated_controller import IntegratedController

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[logging.FileHandler("logs/orchestrator_v53.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class OrchestratorV53:
    """要件定義書v4.0完全実装オーケストレーター"""

    def __init__(self):
        logger.info("=" * 80)
        logger.info("🚀 オーケストレーター v53 - 要件定義書v4.0完全実装")
        logger.info("=" * 80)

        self.controller = IntegratedController()
        self.observability = ObservabilityManager()

        self.stats = {
            "cycle": 0,
            "goals_processed": 0,
            "tasks_created": 0,
            "tasks_executed": 0,
            "tasks_completed": 0,
            "knowledge_accumulated": 0,
        }

        logger.info("✅ 初期化完了\n")

    async def run_cycle(self):
        """1サイクル実行"""
        self.stats["cycle"] += 1

        logger.info("\n" + "=" * 80)
        logger.info(f"サイクル {self.stats['cycle']}")
        logger.info("=" * 80)

        try:
            # 1. ゴール読み込み
            logger.info("\n📋 ステップ1: ゴール読み込み")
            goals = self.controller.read_sheet_as_dicts(
                "project_goal",
                filter_func=lambda g: g.get("status", "").lower() in ["active", "pending"],
            )

            if not goals:
                logger.warning("⚠️ active/pending ゴールなし")
                return

            goal = goals[0]
            logger.info(
                f"✅ ゴール: {goal.get('goal_id')} - {goal.get('goal_description', '')[:50]}..."
            )
            self.stats["goals_processed"] += 1

            # 2. タスク分解
            logger.info("\n📋 ステップ2: タスク分解")
            tasks = await self.controller.decompose_goal_to_tasks(goal)

            if tasks:
                existing = self.controller.read_sheet_as_dicts(
                    "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal.get("goal_id")
                )

                if not existing:
                    success = await self.controller.save_tasks(tasks)
                    if success:
                        self.stats["tasks_created"] += len(tasks)
                        logger.info(f"✅ タスク作成: {len(tasks)}件")

            # 3. タスク実行
            logger.info("\n📋 ステップ3: タスク実行")
            pending = self.controller.read_sheet_as_dicts(
                "pm_tasks",
                filter_func=lambda t: (
                    t.get("parent_goal_id") == goal.get("goal_id")
                    and t.get("status", "").lower() == "pending"
                ),
            )

            logger.info(f"   pending タスク: {len(pending)}件")

            for task in pending[:2]:  # 1サイクルで2件実行
                result = await self.controller.execute_task_with_output(task)

                if result.get("success"):
                    self.stats["tasks_executed"] += 1
                    self.stats["tasks_completed"] += 1

                    # 4. レビュー
                    review = await self.controller.review_task(task, result)
                    logger.info(f"   📊 品質: {review.get('total_score', 0):.1f}/10")

                    self.stats["knowledge_accumulated"] += 1

            # 5. 進捗チェックと追加タスク
            logger.info("\n📋 ステップ4: 進捗チェック")
            new_tasks = await self.controller.check_progress_and_generate_tasks(goal)

            if new_tasks:
                self.stats["tasks_created"] += len(new_tasks)

            # 6. 統計表示
            self.display_stats()

        except Exception as e:
            logger.error(f"❌ サイクルエラー: {e}")
            import traceback

            traceback.print_exc()

    def display_stats(self):
        """統計表示"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 統計情報")
        logger.info("=" * 80)
        logger.info(f"サイクル数: {self.stats['cycle']}")
        logger.info(f"処理ゴール: {self.stats['goals_processed']}")
        logger.info(f"作成タスク: {self.stats['tasks_created']}")
        logger.info(f"実行タスク: {self.stats['tasks_executed']}")
        logger.info(f"完了タスク: {self.stats['tasks_completed']}")
        logger.info(f"蓄積ナレッジ: {self.stats['knowledge_accumulated']}")
        logger.info("=" * 80 + "\n")

    async def run(self, max_cycles: int = 100):
        """メイン実行"""
        logger.info("🚀 要件定義書v4.0 完全実装システム起動\n")

        try:
            for _ in range(max_cycles):
                await self.run_cycle()

                # 3分待機
                logger.info("⏳ 3分待機...")
                await asyncio.sleep(180)

            logger.info("\n🎊 全サイクル完了\n")
            self.display_stats()

        except KeyboardInterrupt:
            logger.info("\n⚠️ ユーザーによる中断")
            self.display_stats()


async def main():
    # ログディレクトリ作成
    os.makedirs("logs", exist_ok=True)

    orch = OrchestratorV53()
    await orch.run(max_cycles=100)


if __name__ == "__main__":
    asyncio.run(main())
