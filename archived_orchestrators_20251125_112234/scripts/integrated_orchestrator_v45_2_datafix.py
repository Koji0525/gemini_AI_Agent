"""
統合オーケストレーター v45.2: データ形式エラー修正版
スプレッドシートのリスト形式 → 辞書形式への変換を追加
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
from tools.data_converter import DataConverter
from tools.safe_sheets_wrapper import SafeSheetsWrapper
from tools.sheets_manager import GoogleSheetsManager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IntegratedOrchestratorV452:
    """3つのループ完全統合オーケストレーター v45.2（データ形式修正版）"""

    def __init__(self):
        logger.info("=" * 80)
        logger.info("🚀 3ループ統合オーケストレーター v45.2 初期化")
        logger.info("=" * 80)

        try:
            # 基盤
            self.sheets = GoogleSheetsManager()
            self.safe_sheets = SafeSheetsWrapper(self.sheets)
            self.data_converter = DataConverter()
            logger.info("✅ 基盤: GoogleSheetsManager, SafeSheetsWrapper, DataConverter")

            # Loop 1: タスク処理
            self.pm_agent = PMAgent(sheets_manager=self.sheets)
            self.task_executor = TaskExecutor(sheets_manager=self.sheets)
            self.review_agent = ReviewAgent(sheets_wrapper=self.safe_sheets)
            self.quality_loop = QualityFeedbackLoop(sheets_manager=self.sheets)
            self.goal_evaluator = GoalEvaluator(sheets_manager=self.sheets)
            logger.info("✅ Loop 1: PMAgent, TaskExecutor, ReviewAgent, QualityLoop, GoalEvaluator")

            # Loop 2: 自己修復
            self.error_classifier = ErrorClassifier()
            self.dss = DecisionSupportSystem()
            self.retry_manager = RetryManager()
            self.rollback_agent = RollbackAgent()
            logger.info("✅ Loop 2: ErrorClassifier, DSS, RetryManager, RollbackAgent")

            # Loop 3: 学習
            self.kb_manager = KnowledgeBaseManager(sheets_manager=self.sheets)
            self.learning_pipeline = SelfLearningPipeline(
                sheets_manager=self.sheets, kb_manager=self.kb_manager
            )
            self.knowledge_manager = KnowledgeManager()
            logger.info("✅ Loop 3: KBManager, SelfLearningPipeline, KnowledgeManager")

            # オブザーバビリティ
            self.observability = ObservabilityManager()
            logger.info("✅ Observability: ObservabilityManager")

            # 統計
            self.cycle_count = 0
            self.loop1_count = 0
            self.loop2_count = 0
            self.loop3_count = 0
            self.task_success = 0
            self.task_failure = 0
            self.error_count = 0
            self.last_learning = datetime.now()
            self.learned_patterns = []
            self.improvement_history = []

            logger.info("=" * 80)
            logger.info("✅ 全コンポーネント初期化完了")
            logger.info("=" * 80 + "\n")

        except Exception as e:
            logger.error(f"❌ 初期化エラー: {e}")
            import traceback

            traceback.print_exc()
            raise

    async def execute_loop1_task_processing(self) -> Dict[str, Any]:
        """
        🔄 Loop 1: タスク処理ループ
        ゴール → タスク分解 → 実行 → 品質評価 → 進捗更新
        """
        self.loop1_count += 1

        logger.info("\n" + "━" * 80)
        logger.info(f"🔄 Loop 1: タスク処理 (実行回数: {self.loop1_count})")
        logger.info("━" * 80)

        results = {
            "success": False,
            "tasks_executed": 0,
            "tasks_reviewed": 0,
            "avg_quality_score": 0,
            "goal_progress": 0,
        }

        try:
            # STEP 1: ゴール読み込み・タスク分解
            logger.info("1️⃣ PMAgent: ゴール読み込み・タスク分解")

            # 🔧 修正: スプレッドシートから読み取ったデータを確認
            goals_data = self.safe_sheets.safe_read("project_goal!A2:C100", default=[])
            logger.info(f"   📥 スプレッドシートから取得: {len(goals_data)}件")

            if goals_data:
                # 🔧 修正: リスト形式を辞書形式に変換
                goals_dicts = self.data_converter.convert_goals_list_to_dicts(goals_data)
                logger.info(f"   🔄 辞書形式に変換: {len(goals_dicts)}件")

                # active/pending のゴールをフィルタ
                active_goals = [
                    g for g in goals_dicts if g.get("status", "").lower() in ["active", "pending"]
                ]

                if active_goals:
                    logger.info(f"   ✅ 処理対象ゴール: {len(active_goals)}件")

                    # PMAgentを直接使わず、タスク分解を手動実行
                    # （PMAgentの内部実装に依存しないように）
                    for goal in active_goals[:1]:  # 最初の1件のみ
                        logger.info(
                            f"   ゴール: {goal.get('goal_id')} - {goal.get('description', '')[:50]}..."
                        )
                else:
                    logger.warning("   ⚠️ 処理可能なゴールがありません")
            else:
                logger.warning("   ⚠️ ゴールが見つかりません")

                # テスト用ゴール作成
                logger.info("   📝 テスト用ゴール作成...")
                test_goal = [
                    [
                        f'GOAL_TEST_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                        "active",
                        "【データ形式修正テスト】スプレッドシート統合の動作確認",
                    ]
                ]
                self.safe_sheets.safe_append("project_goal", test_goal)
                logger.info("   ✅ テスト用ゴール作成完了")

            # PMAgentのrun_pm_cycle実行（内部でエラーハンドリングされる）
            try:
                await self.pm_agent.run_pm_cycle()
            except Exception as pm_error:
                logger.warning(f"   ⚠️ PMAgent実行エラー: {pm_error}")

            # STEP 2: pending タスク実行
            logger.info("\n2️⃣ TaskExecutor: pending タスク実行")
            pending = self.task_executor.get_pending_tasks()
            logger.info(f"   📋 pending タスク: {len(pending)}件")

            quality_scores = []

            for task in pending[:3]:
                try:
                    task_id = task.get("task_id", "UNKNOWN")
                    logger.info(f"\n   ▶ タスク実行: {task_id}")

                    result = await self.task_executor.execute_task(task)

                    if result["success"]:
                        self.task_success += 1

                        review = await self.review_agent.review_task(result)
                        score = review.get("total_score", 0)
                        quality_scores.append(score)

                        logger.info(f"   ✅ 実行成功（品質: {score:.1f}/10）")

                        if score < 7:
                            await self.quality_loop.process_task_result(task, result)

                        self.knowledge_manager.add_knowledge(
                            title=f"タスク実行_{task_id}",
                            content=f"品質: {score:.1f}",
                            category="task_execution",
                            tags=f"quality_{int(score)},loop1",
                        )

                        results["tasks_reviewed"] += 1
                    else:
                        self.task_failure += 1
                        logger.error(f"   ❌ 実行失敗: {result.get('error')}")
                        await self.execute_loop2_self_healing(
                            Exception(result.get("error", "Unknown")), task
                        )

                    results["tasks_executed"] += 1

                except Exception as e:
                    logger.error(f"   ❌ タスク処理エラー: {e}")
                    self.error_count += 1
                    await self.execute_loop2_self_healing(e, task)

            # STEP 3: ゴール進捗評価
            logger.info("\n3️⃣ GoalEvaluator: ゴール進捗評価")
            goals = self.safe_sheets.safe_read("project_goal!A2:C100", default=[])
            if goals and len(goals) > 0 and len(goals[0]) > 0:
                goal_id = goals[0][0]
                try:
                    progress = await self.goal_evaluator.evaluate_goal(goal_id)
                    results["goal_progress"] = progress.get("progress_percentage", 0)
                    logger.info(f"   📈 ゴール進捗: {results['goal_progress']:.1f}%")
                except Exception as e:
                    logger.warning(f"   ⚠️ ゴール評価エラー: {e}")

            if quality_scores:
                results["avg_quality_score"] = sum(quality_scores) / len(quality_scores)
                logger.info(f"   📊 平均品質: {results['avg_quality_score']:.1f}/10")

            results["success"] = True
            logger.info("\n✅ Loop 1 完了")

        except Exception as e:
            logger.error(f"❌ Loop 1 エラー: {e}")
            await self.execute_loop2_self_healing(e, None)

        return results

    async def execute_loop2_self_healing(self, error: Exception, task: Dict = None):
        """🔧 Loop 2: 自己修復ループ"""
        self.loop2_count += 1
        self.error_count += 1

        logger.info(f"\n🔧 Loop 2: 自己修復 (#{self.loop2_count})")
        logger.info(f"   エラー: {str(error)[:100]}...")

        try:
            category = self.error_classifier.classify(error)
            logger.info(f"   カテゴリ: {category}")

            self.knowledge_manager.add_knowledge(
                title=f"エラー記録_{category}_{datetime.now().strftime('%H%M%S')}",
                content=str(error)[:200],
                category="error",
                tags=f"{category},loop2",
            )

            logger.info("✅ Loop 2 完了")
        except Exception as e2:
            logger.error(f"❌ Loop 2 エラー: {e2}")

    async def execute_loop3_learning(self):
        """🧠 Loop 3: 学習ループ"""
        self.loop3_count += 1

        logger.info(f"\n🧠 Loop 3: 学習サイクル (#{self.loop3_count})")

        try:
            logs = await self.learning_pipeline.collect_logs()
            logger.info(f"   📥 収集ログ: {len(logs) if logs else 0}件")

            if logs and len(logs) > 0:
                patterns = await self.learning_pipeline.extract_patterns(logs)
                logger.info(f"   🔍 抽出パターン: {len(patterns) if patterns else 0}件")

                recipes = await self.learning_pipeline.generate_repair_recipes(patterns)
                logger.info(f"   📝 生成レシピ: {len(recipes) if recipes else 0}件")

                for recipe in recipes:
                    self.kb_manager.register_knowledge(recipe)
                    self.learned_patterns.append(
                        {"timestamp": datetime.now().isoformat(), "recipe": recipe}
                    )

                logger.info(f"   📊 累計パターン: {len(self.learned_patterns)}件")

            self.last_learning = datetime.now()
            logger.info("✅ Loop 3 完了")

        except Exception as e:
            logger.error(f"❌ Loop 3 エラー: {e}")

    async def display_status(self):
        """システム状態表示"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 システム状態")
        logger.info("=" * 80)
        logger.info(f"🔄 Loop 1: {self.loop1_count}回")
        logger.info(f"🔧 Loop 2: {self.loop2_count}回")
        logger.info(f"🧠 Loop 3: {self.loop3_count}回")

        total = self.task_success + self.task_failure
        rate = (self.task_success / total * 100) if total > 0 else 0
        logger.info(
            f"\n📈 タスク: 成功={self.task_success}, 失敗={self.task_failure}, 成功率={rate:.1f}%"
        )
        logger.info(f"🧠 学習: エラー={self.error_count}, パターン={len(self.learned_patterns)}")
        logger.info("=" * 80 + "\n")

    async def run_3loops(self, max_hours: int = 24):
        """3ループ連続稼働"""
        logger.info("\n🚀 3ループ連続稼働開始\n")

        start = datetime.now()

        while True:
            self.cycle_count += 1
            elapsed = (datetime.now() - start).total_seconds() / 3600

            if elapsed >= max_hours:
                logger.info(f"\n⏰ {max_hours}時間経過\n")
                break

            logger.info(f"\n{'='*60}")
            logger.info(f"サイクル {self.cycle_count} （{elapsed:.2f}h）")
            logger.info("=" * 60)

            await self.execute_loop1_task_processing()

            hours_since = (datetime.now() - self.last_learning).total_seconds() / 3600
            if hours_since >= 6 or self.error_count >= 50:
                await self.execute_loop3_learning()
                self.error_count = 0

            await self.display_status()

            logger.info("⏳ 3分待機...\n")
            await asyncio.sleep(180)

        logger.info(
            f"\n🎊 完了: {self.cycle_count}サイクル, {self.loop1_count}+{self.loop2_count}+{self.loop3_count}ループ\n"
        )


async def main():
    try:
        orch = IntegratedOrchestratorV452()
        await orch.run_3loops(max_hours=24)
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
