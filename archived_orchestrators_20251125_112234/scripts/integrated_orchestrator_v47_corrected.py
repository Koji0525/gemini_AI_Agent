"""
統合オーケストレーター v47: 即時解決版
全メソッド名を正しく修正（append_rows, record_trace, add_knowledge）
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict

project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.goal_evaluator.goal_evaluator import GoalEvaluator
from agents.observability.observability_manager import ObservabilityManager
from agents.self_healing.logging.decision_support_system import \
    DecisionSupportSystem
from agents.self_healing.logging.knowledge_base_manager import \
    KnowledgeBaseManager
from agents.self_healing.retry_manager import RetryManager
from agents.self_healing.rollback_agent import RollbackAgent
from agents.self_healing.self_learning_pipeline import SelfLearningPipeline
from agents.self_healing.utils.error_classifier import ErrorClassifier
from core_agents.pm_agent import PMAgent
from core_agents.quality_feedback_loop import QualityFeedbackLoop
from core_agents.review_agent import ReviewAgent
from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
from task_executor.task_executor_main import TaskExecutor
from tools.safe_sheets_wrapper import SafeSheetsWrapper
from tools.sheets_manager import GoogleSheetsManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class IntegratedOrchestratorV47:
    """3ループ統合オーケストレーター v47（即時解決版）"""

    def __init__(self):
        logger.info("🚀 オーケストレーター v47 初期化")

        self.sheets = GoogleSheetsManager()
        self.safe_sheets = SafeSheetsWrapper(self.sheets)

        self.pm_agent = PMAgent(sheets_manager=self.sheets)
        self.task_executor = TaskExecutor(sheets_manager=self.sheets)
        self.review_agent = ReviewAgent(sheets_wrapper=self.safe_sheets)
        self.quality_loop = QualityFeedbackLoop(sheets_manager=self.sheets)
        self.goal_evaluator = GoalEvaluator(sheets_manager=self.sheets)

        self.error_classifier = ErrorClassifier()
        self.dss = DecisionSupportSystem()
        self.retry_manager = RetryManager()
        self.rollback_agent = RollbackAgent()

        self.kb_manager = KnowledgeBaseManager(sheets_manager=self.sheets)
        self.learning_pipeline = SelfLearningPipeline(
            sheets_manager=self.sheets, kb_manager=self.kb_manager
        )
        self.knowledge_manager = KnowledgeManager()

        self.observability = ObservabilityManager()

        self.cycle_count = 0
        self.loop1_count = 0
        self.loop2_count = 0
        self.loop3_count = 0
        self.task_success = 0
        self.task_failure = 0
        self.error_count = 0
        self.last_learning = datetime.now()
        self.learned_patterns = []

        logger.info("✅ 初期化完了\n")

    async def execute_loop1(self) -> Dict[str, Any]:
        """🔄 Loop 1: タスク処理"""
        self.loop1_count += 1
        logger.info(f"\n🔄 Loop 1 (#{self.loop1_count})")

        results = {"success": False, "tasks_executed": 0}

        try:
            # PMAgent実行
            await self.pm_agent.run_pm_cycle()

            # タスク実行
            pending = self.task_executor.get_pending_tasks()
            logger.info(f"📋 pending: {len(pending)}件")

            for task in pending[:3]:
                try:
                    task_id = task.get("task_id", "UNKNOWN")
                    logger.info(f"▶ {task_id}")

                    result = await self.task_executor.execute_task(task)

                    if result["success"]:
                        self.task_success += 1
                        review = await self.review_agent.review_task(result)
                        score = review.get("total_score", 0)

                        logger.info(f"✅ 成功（品質: {score:.1f}/10）")

                        if score < 7:
                            await self.quality_loop.process_task_result(task, result)

                        # ✅ 正しいメソッド名: add_knowledge
                        self.knowledge_manager.add_knowledge(
                            title=f"タスク_{task_id}",
                            content=f"品質: {score:.1f}",
                            category="task",
                            tags=f"q{int(score)}",
                        )

                        results["tasks_executed"] += 1
                    else:
                        self.task_failure += 1
                        await self.execute_loop2(Exception(result.get("error", "Unknown")), task)

                except Exception as e:
                    self.error_count += 1
                    await self.execute_loop2(e, task)

            # ゴール進捗
            goals = self.safe_sheets.safe_read("project_goal!A2:C100", default=[])
            if goals:
                try:
                    progress = await self.goal_evaluator.evaluate_goal(goals[0][0])
                    logger.info(f"📈 進捗: {progress.get('progress_percentage', 0):.1f}%")
                except:
                    pass

            results["success"] = True
            logger.info("✅ Loop 1 完了")

        except Exception as e:
            logger.error(f"❌ Loop 1 エラー: {e}")
            await self.execute_loop2(e, None)

        return results

    async def execute_loop2(self, error: Exception, task: Dict = None):
        """🔧 Loop 2: 自己修復"""
        self.loop2_count += 1
        self.error_count += 1

        logger.info(f"🔧 Loop 2 (#{self.loop2_count}): {str(error)[:60]}...")

        try:
            category = self.error_classifier.classify(error)
            logger.info(f"カテゴリ: {category}")

            # ✅ 正しいメソッド名: record_trace
            self.observability.record_trace(
                {
                    "event": "error",
                    "category": category,
                    "message": str(error)[:200],
                    "timestamp": datetime.now().isoformat(),
                }
            )

            logger.info("✅ Loop 2 完了")
        except Exception as e2:
            logger.error(f"❌ Loop 2 エラー: {e2}")

    async def execute_loop3(self):
        """🧠 Loop 3: 学習"""
        self.loop3_count += 1
        logger.info(f"🧠 Loop 3 (#{self.loop3_count})")

        try:
            logs = await self.learning_pipeline.collect_logs()
            logger.info(f"📥 ログ: {len(logs) if logs else 0}件")

            if logs and len(logs) > 0:
                patterns = await self.learning_pipeline.extract_patterns(logs)
                recipes = await self.learning_pipeline.generate_repair_recipes(patterns)

                for recipe in recipes:
                    self.kb_manager.register_knowledge(recipe)
                    self.learned_patterns.append(recipe)

                logger.info(f"📊 パターン: {len(self.learned_patterns)}件")

            self.last_learning = datetime.now()
            logger.info("✅ Loop 3 完了")
        except Exception as e:
            logger.error(f"❌ Loop 3 エラー: {e}")

    async def display_status(self):
        """📊 システム状態"""
        logger.info("\n" + "=" * 60)
        logger.info(f"Loop1={self.loop1_count}, Loop2={self.loop2_count}, Loop3={self.loop3_count}")
        total = self.task_success + self.task_failure
        rate = (self.task_success / total * 100) if total > 0 else 0
        logger.info(f"タスク: 成功={self.task_success}, 失敗={self.task_failure}, 率={rate:.1f}%")
        logger.info(f"学習パターン: {len(self.learned_patterns)}件")
        logger.info("=" * 60 + "\n")

    async def run_3loops(self, max_hours: int = 24):
        """3ループ連続稼働"""
        logger.info("🚀 3ループ連続稼働開始\n")

        start = datetime.now()

        while True:
            self.cycle_count += 1
            elapsed = (datetime.now() - start).total_seconds() / 3600

            if elapsed >= max_hours:
                break

            logger.info(f"\nサイクル {self.cycle_count} ({elapsed:.2f}h)")

            await self.execute_loop1()

            hours_since = (datetime.now() - self.last_learning).total_seconds() / 3600
            if hours_since >= 6 or self.error_count >= 50:
                await self.execute_loop3()
                self.error_count = 0

            await self.display_status()

            logger.info("⏳ 3分待機...")
            await asyncio.sleep(180)

        logger.info("🎊 完了\n")


async def main():
    try:
        orch = IntegratedOrchestratorV47()
        await orch.run_3loops(max_hours=24)
    except Exception as e:
        logger.error(f"❌ {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
