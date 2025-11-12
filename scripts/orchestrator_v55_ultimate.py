"""
オーケストレーター v55 - 完全統合最終版
要件定義書v4.0完全実装 + オブザーバビリティ + 人間との対話
"""

import asyncio
import logging
import os
import sys

project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.human_interface.interactive_agent import InteractiveAgent
from agents.observability.dashboard import ObservabilityDashboard
from core_agents.integrated_controller_fixed import IntegratedControllerFixed

os.makedirs("logs", exist_ok=True)
os.makedirs("agent_outputs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[logging.FileHandler("logs/orchestrator_v55.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class OrchestratorV55:
    """完全統合オーケストレーター v55"""

    def __init__(self):
        logger.info("=" * 80)
        logger.info("🚀 オーケストレーター v55 - 要件定義書v4.0完全統合")
        logger.info("=" * 80)

        self.controller = IntegratedControllerFixed()
        self.dashboard = ObservabilityDashboard()
        self.human_agent = InteractiveAgent()

        self.stats = {
            "cycle": 0,
            "goals_processed": 0,
            "tasks_created": 0,
            "tasks_executed": 0,
            "tasks_completed": 0,
            "knowledge_accumulated": 0,
            "questions_asked": 0,
            "quality_scores": [],
        }

        logger.info("✅ 初期化完了\n")

    async def run_cycle(self):
        """1サイクル実行"""
        self.stats["cycle"] += 1

        logger.info("\n" + "=" * 80)
        logger.info(f"🔄 サイクル {self.stats['cycle']}")
        logger.info("=" * 80)

        try:
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # 1. ゴール読み込み
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            logger.info("\n📋 STEP 1: ゴール読み込み")
            goals = self.controller.read_sheet_as_dicts(
                "project_goal",
                filter_func=lambda g: g.get("status", "").lower() in ["active", "pending"],
            )

            if not goals:
                logger.warning("⚠️ active/pending ゴールなし")
                await self.human_agent.ask_human(
                    "処理可能なゴールがありません。新しいゴールを追加しますか？",
                    context={"available_goals": 0},
                )
                self.stats["questions_asked"] += 1
                return

            goal = goals[0]
            logger.info(f"✅ ゴール: {goal.get('goal_id')}")
            logger.info(f"   内容: {goal.get('goal_description', '')[:80]}...")
            self.stats["goals_processed"] += 1

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # 2. タスク分解と保存
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            logger.info("\n📋 STEP 2: タスク分解")
            tasks = await self.controller.decompose_goal_to_tasks(goal)

            if tasks:
                existing = self.controller.read_sheet_as_dicts(
                    "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal.get("goal_id")
                )

                if not existing:
                    success = await self.controller.save_tasks(tasks)
                    if success:
                        self.stats["tasks_created"] += len(tasks)
                        logger.info(f"✅ 新規タスク作成: {len(tasks)}件")
                        logger.info("   pm_tasksシートに保存完了")
                else:
                    logger.info(f"ℹ️ タスク既存: {len(existing)}件")

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # 3. タスク実行
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            logger.info("\n📋 STEP 3: タスク実行")
            pending = self.controller.read_sheet_as_dicts(
                "pm_tasks",
                filter_func=lambda t: (
                    t.get("parent_goal_id") == goal.get("goal_id")
                    and t.get("status", "").lower() == "pending"
                ),
            )

            logger.info(f"   pending タスク: {len(pending)}件")

            if len(pending) == 0:
                logger.info("   ℹ️ 実行可能なタスクなし")

                # 進捗が100%未満なら質問
                all_tasks = self.controller.read_sheet_as_dicts(
                    "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal.get("goal_id")
                )
                completed = sum(1 for t in all_tasks if t.get("status", "").lower() == "completed")
                progress = (completed / len(all_tasks) * 100) if all_tasks else 0

                if progress < 100:
                    await self.human_agent.ask_human(
                        f"ゴール{goal.get('goal_id')}の進捗が{progress:.1f}%です。追加タスクが必要ですか？",
                        context={
                            "goal_id": goal.get("goal_id"),
                            "progress": f"{progress:.1f}%",
                            "completed": completed,
                            "total": len(all_tasks),
                        },
                    )
                    self.stats["questions_asked"] += 1
            else:
                for i, task in enumerate(pending[:2], 1):
                    logger.info(f"\n   ▶ タスク {i}/{min(2, len(pending))}: {task.get('task_id')}")

                    # タスク実行
                    result = await self.controller.execute_task_with_output(task)

                    if result.get("success"):
                        self.stats["tasks_executed"] += 1
                        self.stats["tasks_completed"] += 1

                        logger.info(f"   ✅ 実行完了")
                        logger.info(f"   📂 出力: {result.get('output_file')}")
                        logger.info(f"   📊 ログ: task_execution_logに記録")

                        # レビュー
                        review = await self.controller.review_task(task, result)
                        quality_score = review.get("total_score", 0)
                        self.stats["quality_scores"].append(quality_score)

                        logger.info(f"   ⭐ 品質: {quality_score:.1f}/10")

                        # 低品質の場合は質問
                        if quality_score < 7.0:
                            await self.human_agent.ask_human(
                                f"タスク{task.get('task_id')}の品質が{quality_score:.1f}/10です。再実行しますか？",
                                context={
                                    "task_id": task.get("task_id"),
                                    "quality_score": quality_score,
                                },
                            )
                            self.stats["questions_asked"] += 1

                        self.stats["knowledge_accumulated"] += 1

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # 4. 進捗チェックと追加タスク
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            logger.info("\n📋 STEP 4: 進捗チェック")
            new_tasks = await self.controller.check_progress_and_generate_tasks(goal)

            if new_tasks:
                self.stats["tasks_created"] += len(new_tasks)
                logger.info(f"   ✅ 追加タスク生成: {len(new_tasks)}件")

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # 5. ダッシュボード表示
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            logger.info("\n📋 STEP 5: ダッシュボード表示")
            self.dashboard.display_goal_progress(goal.get("goal_id"))
            self.dashboard.display_recent_outputs()

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # 6. 統計表示
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            self.display_stats()

        except Exception as e:
            logger.error(f"❌ サイクルエラー: {e}")
            import traceback

            traceback.print_exc()

    def display_stats(self):
        """統計表示"""
        avg_quality = (
            sum(self.stats["quality_scores"]) / len(self.stats["quality_scores"])
            if self.stats["quality_scores"]
            else 0
        )

        logger.info("\n" + "=" * 80)
        logger.info("📊 累積統計")
        logger.info("=" * 80)
        logger.info(f"サイクル数: {self.stats['cycle']}")
        logger.info(f"処理ゴール: {self.stats['goals_processed']}")
        logger.info(f"作成タスク: {self.stats['tasks_created']}")
        logger.info(f"実行タスク: {self.stats['tasks_executed']}")
        logger.info(f"完了タスク: {self.stats['tasks_completed']}")
        logger.info(f"蓄積ナレッジ: {self.stats['knowledge_accumulated']}")
        logger.info(f"平均品質: {avg_quality:.1f}/10")
        logger.info(f"質問回数: {self.stats['questions_asked']}")
        logger.info("=" * 80 + "\n")

    async def run(self, max_cycles: int = 100):
        """メイン実行"""
        logger.info("🚀 要件定義書v4.0 完全統合システム起動\n")
        logger.info("📋 実装機能:")
        logger.info("  ✅ ゴール読み込み → タスク分解 → pm_tasks保存")
        logger.info("  ✅ タスク実行 → agent_outputs保存")
        logger.info("  ✅ task_execution_logシート記録")
        logger.info("  ✅ ナレッジ自動蓄積・参照")
        logger.info("  ✅ レビュー・品質評価")
        logger.info("  ✅ 進捗チェック・追加タスク生成")
        logger.info("  ✅ オブザーバビリティダッシュボード")
        logger.info("  ✅ 人間との対話機能")
        logger.info("")

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


async def main():
    orch = OrchestratorV55()
    await orch.run(max_cycles=100)


if __name__ == "__main__":
    asyncio.run(main())
