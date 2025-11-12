"""
統合オーケストレーター v52 - エラーハンドリング強化版
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.goal_evaluator.goal_evaluator_v2 import GoalEvaluatorV2
from agents.observability.observability_manager import ObservabilityManager
from agents.self_healing.logging.knowledge_base_manager import \
    KnowledgeBaseManager
from agents.self_healing.retry_manager import RetryManager
from agents.self_healing.rollback_agent import RollbackAgent
from agents.self_healing.self_learning_pipeline import SelfLearningPipeline
from agents.self_healing.utils.error_classifier import ErrorClassifier
from core_agents.pm_agent_v3_fixed import PMAgentV3Fixed
from core_agents.quality_feedback_loop import QualityFeedbackLoop
from core_agents.review_agent import ReviewAgent
from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
from task_executor.task_executor_main import TaskExecutor
from tools.safe_sheets_wrapper import SafeSheetsWrapper
from tools.sheets_manager import GoogleSheetsManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


class OrchestratorV52:
    """統合オーケストレーター v52"""

    def __init__(self):
        logger.info("=" * 80)
        logger.info("🚀 オーケストレーター v52 初期化")
        logger.info("=" * 80)

        try:
            self.sheets = GoogleSheetsManager()
            self.safe_sheets = SafeSheetsWrapper(self.sheets)

            self.pm_agent = PMAgentV3Fixed(self.sheets)
            self.task_executor = TaskExecutor(sheets_manager=self.sheets)
            self.review_agent = ReviewAgent(sheets_wrapper=self.safe_sheets)
            self.quality_loop = QualityFeedbackLoop(sheets_manager=self.sheets)
            self.goal_evaluator = GoalEvaluatorV2(self.sheets)

            self.error_classifier = ErrorClassifier()
            self.retry_manager = RetryManager()
            self.rollback_agent = RollbackAgent()

            self.kb_manager = KnowledgeBaseManager(sheets_manager=self.sheets)
            self.learning_pipeline = SelfLearningPipeline(
                sheets_manager=self.sheets, kb_manager=self.kb_manager
            )
            self.knowledge_manager = KnowledgeManager()
            self.observability = ObservabilityManager()

            self.stats = {
                "cycle": 0,
                "loop1": 0,
                "loop2": 0,
                "loop3": 0,
                "task_success": 0,
                "task_failure": 0,
                "error_count": 0,
            }
            self.last_learning = datetime.now()

            logger.info("=" * 80)
            logger.info("✅ 初期化完了")
            logger.info("=" * 80 + "\n")

        except Exception as e:
            logger.error(f"❌ 初期化エラー: {e}")
            raise

    async def execute_loop1(self):
        """🔄 Loop 1: タスク分解・実行"""
        self.stats["loop1"] += 1

        logger.info("\n" + "━" * 80)
        logger.info(f"🔄 Loop 1 (#{self.stats['loop1']})")
        logger.info("━" * 80)

        try:
            # PMAgent実行
            await self.pm_agent.run_pm_cycle()

            # タスク実行
            pending = self.task_executor.get_pending_tasks()
            logger.info(f"\n📋 pending タスク: {len(pending)}件")

            for i, task in enumerate(pending[:3], 1):
                try:
                    task_id = task.get("task_id", "UNKNOWN")
                    logger.info(f"\n▶ タスク {i}/{min(3, len(pending))}: {task_id}")

                    result = await self.task_executor.execute_task(task)

                    if result.get("success"):
                        self.stats["task_success"] += 1

                        try:
                            review = await self.review_agent.review_task(result)
                            score = review.get("total_score", 0)
                            logger.info(f"✅ 成功（品質: {score:.1f}/10）")

                            if score < 7:
                                await self.quality_loop.process_task_result(task, result)
                        except Exception as review_error:
                            logger.warning(f"⚠️ レビューエラー: {review_error}")
                    else:
                        self.stats["task_failure"] += 1
                        logger.error(f"❌ 失敗: {result.get('error', 'Unknown')}")
                        await self.execute_loop2(Exception(result.get("error", "Unknown")))

                except Exception as e:
                    self.stats["error_count"] += 1
                    logger.error(f"❌ タスク実行エラー: {e}")
                    await self.execute_loop2(e)

            # ゴール進捗
            try:
                goals = self.safe_sheets.safe_read("project_goal!A2:Z100", default=[])
                if goals:
                    goal_id = goals[0][0]
                    progress = await self.goal_evaluator.evaluate_goal(goal_id)
                    logger.info(f"\n📈 ゴール進捗: {progress.get('progress_percentage', 0):.1f}%")
            except Exception as e:
                logger.warning(f"⚠️ ゴール評価エラー: {e}")

            logger.info("\n" + "━" * 80)
            logger.info("✅ Loop 1 完了")
            logger.info("━" * 80)

        except Exception as e:
            logger.error(f"❌ Loop 1 エラー: {e}")
            await self.execute_loop2(e)

    async def execute_loop2(self, error: Exception):
        """🔧 Loop 2: 自己修復"""
        self.stats["loop2"] += 1
        self.stats["error_count"] += 1

        logger.info(f"\n🔧 Loop 2 (#{self.stats['loop2']})")
        logger.info(f"   エラー: {str(error)[:100]}")

        try:
            category = self.error_classifier.classify(error)
            logger.info(f"   カテゴリ: {category}")

            self.observability.record_trace(
                {
                    "event": "error",
                    "category": category,
                    "message": str(error)[:200],
                    "timestamp": datetime.now().isoformat(),
                }
            )

            logger.info("   ✅ Loop 2 完了")
        except Exception as e:
            logger.error(f"   ❌ Loop 2 エラー: {e}")

    async def execute_loop3(self):
        """🧠 Loop 3: 学習"""
        self.stats["loop3"] += 1

        logger.info(f"\n🧠 Loop 3 (#{self.stats['loop3']})")

        try:
            logs = await self.learning_pipeline.collect_logs()
            logger.info(f"   ログ収集: {len(logs) if logs else 0}件")

            if logs and len(logs) > 0:
                patterns = await self.learning_pipeline.extract_patterns(logs)
                recipes = await self.learning_pipeline.generate_repair_recipes(patterns)

                for recipe in recipes:
                    self.kb_manager.register_knowledge(recipe)

                logger.info(f"   パターン登録: {len(recipes)}件")

            self.last_learning = datetime.now()
            logger.info("   ✅ Loop 3 完了")

        except Exception as e:
            logger.error(f"   ❌ Loop 3 エラー: {e}")

    def display_status(self):
        """📊 システム状態表示"""
        total = self.stats["task_success"] + self.stats["task_failure"]
        rate = (self.stats["task_success"] / total * 100) if total > 0 else 0

        logger.info("\n" + "=" * 80)
        logger.info("📊 システム状態")
        logger.info("=" * 80)
        logger.info(
            f"Loop1={self.stats['loop1']}, Loop2={self.stats['loop2']}, Loop3={self.stats['loop3']}"
        )
        logger.info(
            f"タスク: 成功={self.stats['task_success']}, 失敗={self.stats['task_failure']}, 成功率={rate:.1f}%"
        )
        logger.info(f"エラー: {self.stats['error_count']}件")
        logger.info("=" * 80 + "\n")

    async def run(self, max_hours: float = 24):
        """メイン実行ループ"""
        logger.info("🚀 3ループ連続稼働開始\n")

        start = datetime.now()

        try:
            while True:
                self.stats["cycle"] += 1
                elapsed = (datetime.now() - start).total_seconds() / 3600

                if elapsed >= max_hours:
                    logger.info(f"⏰ {max_hours}時間経過 - 終了")
                    break

                logger.info(f"\n{'='*80}")
                logger.info(f"サイクル {self.stats['cycle']} ({elapsed:.2f}h)")
                logger.info("=" * 80)

                # Loop 1
                await self.execute_loop1()

                # Loop 3（6時間ごとまたはエラー50件）
                hours_since = (datetime.now() - self.last_learning).total_seconds() / 3600
                if hours_since >= 6 or self.stats["error_count"] >= 50:
                    await self.execute_loop3()
                    self.stats["error_count"] = 0

                # ステータス表示
                self.display_status()

                # 待機
                logger.info("⏳ 3分待機...")
                await asyncio.sleep(180)

            logger.info("\n🎊 稼働完了\n")
            self.display_status()

        except KeyboardInterrupt:
            logger.info("\n⚠️ ユーザーによる中断")
            self.display_status()
        except Exception as e:
            logger.error(f"\n❌ 致命的エラー: {e}")
            import traceback

            traceback.print_exc()


async def main():
    try:
        orch = OrchestratorV52()
        await orch.run(max_hours=24)
    except Exception as e:
        logger.error(f"❌ 起動エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
