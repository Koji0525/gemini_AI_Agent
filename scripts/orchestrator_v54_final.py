"""
オーケストレーター v54 - 最終完全版
要件定義書v4.0完全実装・全エラー修正版
"""

import asyncio
import logging
import os
import sys

project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core_agents.integrated_controller_fixed import IntegratedControllerFixed

# ログ設定
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[logging.FileHandler("logs/orchestrator_v54.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class OrchestratorV54:
    """最終完全版オーケストレーター"""

    def __init__(self):
        logger.info("=" * 80)
        logger.info("🚀 オーケストレーター v54 - 要件定義書v4.0完全実装")
        logger.info("=" * 80)

        self.controller = IntegratedControllerFixed()

        self.stats = {
            "cycle": 0,
            "goals_processed": 0,
            "tasks_created": 0,
            "tasks_executed": 0,
            "tasks_completed": 0,
            "knowledge_accumulated": 0,
            "avg_quality": 0.0,
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
                else:
                    logger.info(f"ℹ️ タスク既存: {len(existing)}件")

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

            quality_scores = []

            for task in pending[:2]:
                result = await self.controller.execute_task_with_output(task)

                if result.get("success"):
                    self.stats["tasks_executed"] += 1
                    self.stats["tasks_completed"] += 1

                    # 4. レビュー
                    review = await self.controller.review_task(task, result)
                    quality_score = review.get("total_score", 0)
                    quality_scores.append(quality_score)

                    logger.info(f"   📊 品質: {quality_score:.1f}/10")

                    self.stats["knowledge_accumulated"] += 1

            if quality_scores:
                self.stats["avg_quality"] = sum(quality_scores) / len(quality_scores)

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
        logger.info("�� 統計情報")
        logger.info("=" * 80)
        logger.info(f"サイクル数: {self.stats['cycle']}")
        logger.info(f"処理ゴール: {self.stats['goals_processed']}")
        logger.info(f"作成タスク: {self.stats['tasks_created']}")
        logger.info(f"実行タスク: {self.stats['tasks_executed']}")
        logger.info(f"完了タスク: {self.stats['tasks_completed']}")
        logger.info(f"蓄積ナレッジ: {self.stats['knowledge_accumulated']}")
        logger.info(f"平均品質: {self.stats['avg_quality']:.1f}/10")
        logger.info("=" * 80 + "\n")

    async def run(self, max_cycles: int = 100):
        """メイン実行"""
        logger.info("🚀 要件定義書v4.0 完全実装システム起動\n")

        try:
            for _ in range(max_cycles):
                await self.run_cycle()

                logger.info("⏳ 3分待機...")
                await asyncio.sleep(180)

            logger.info("\n🎊 全サイクル完了\n")
            self.display_stats()

        except KeyboardInterrupt:
            logger.info("\n⚠️ ユーザーによる中断")
            self.display_stats()
        except Exception as e:
            logger.error(f"\n❌ 致命的エラー: {e}")
            import traceback

            traceback.print_exc()


async def main():
    orch = OrchestratorV54()
    await orch.run(max_cycles=100)


if __name__ == "__main__":
    asyncio.run(main())
