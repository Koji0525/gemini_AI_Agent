"""
統合オーケストレーター v41: 初期化エラー修正版 + 実動作確認
各コンポーネントの正しい初期化パラメータを使用
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import logging

project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.sheets_manager import GoogleSheetsManager
from tools.safe_sheets_wrapper import SafeSheetsWrapper
from core_agents.pm_agent import PMAgent
from task_executor.task_executor_main import TaskExecutor
from core_agents.review_agent import ReviewAgent
from core_agents.quality_feedback_loop import QualityFeedbackLoop
from agents.goal_evaluator.goal_evaluator import GoalEvaluator
from agents.self_healing.utils.error_classifier import ErrorClassifier
from agents.self_healing.logging.decision_support_system import DecisionSupportSystem
from agents.self_healing.retry_manager import RetryManager
from agents.self_healing.rollback_agent import RollbackAgent
from agents.self_healing.self_learning_pipeline import SelfLearningPipeline
from agents.self_healing.logging.knowledge_base_manager import KnowledgeBaseManager
from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
from agents.observability.observability_manager import ObservabilityManager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IntegratedOrchestratorV41:
    """統合オーケストレーター v41 - 修正版"""

    def __init__(self):
        logger.info("=" * 80)
        logger.info("🚀 統合オーケストレーター v41 初期化開始（修正版）")
        logger.info("=" * 80)

        try:
            # 基盤
            logger.info("1️⃣ 基盤コンポーネント初期化中...")
            self.sheets = GoogleSheetsManager()
            self.safe_sheets = SafeSheetsWrapper(self.sheets)
            logger.info("   ✅ GoogleSheetsManager")
            logger.info("   ✅ SafeSheetsWrapper")

            # Loop 1: タスク処理
            logger.info("2️⃣ Loop 1: タスク処理コンポーネント初期化中...")

            self.pm_agent = PMAgent(sheets_manager=self.sheets)
            logger.info("   ✅ PMAgent")

            self.task_executor = TaskExecutor(sheets_manager=self.sheets)
            logger.info("   ✅ TaskExecutor")

            # ReviewAgent - sheets_wrapper を渡す
            self.review_agent = ReviewAgent(sheets_wrapper=self.safe_sheets)
            logger.info("   ✅ ReviewAgent")

            # QualityFeedbackLoop - sheets_wrapper を渡す
            self.quality_loop = QualityFeedbackLoop(sheets_wrapper=self.safe_sheets)
            logger.info("   ✅ QualityFeedbackLoop")

            # GoalEvaluator - sheets_manager を渡す
            self.goal_evaluator = GoalEvaluator(sheets_manager=self.sheets)
            logger.info("   ✅ GoalEvaluator")

            # Loop 2: 自己修復
            logger.info("3️⃣ Loop 2: 自己修復コンポーネント初期化中...")
            self.error_classifier = ErrorClassifier()
            self.dss = DecisionSupportSystem()
            self.retry_manager = RetryManager()
            self.rollback_agent = RollbackAgent()
            logger.info("   ✅ ErrorClassifier, DSS, RetryManager, RollbackAgent")

            # Loop 3: 学習
            logger.info("4️⃣ Loop 3: 学習コンポーネント初期化中...")
            self.learning_pipeline = SelfLearningPipeline()
            self.kb_manager = KnowledgeBaseManager()
            self.knowledge_manager = KnowledgeManager()
            logger.info("   ✅ SelfLearningPipeline, KBManager, KnowledgeManager")

            # オブザーバビリティ
            logger.info("5️⃣ オブザーバビリティコンポーネント初期化中...")
            self.observability = ObservabilityManager()
            logger.info("   ✅ ObservabilityManager")

            self.cycle_count = 0
            self.error_count = 0
            self.task_success_count = 0
            self.task_failure_count = 0
            self.last_learning_time = datetime.now()

            logger.info("=" * 80)
            logger.info("✅ 統合オーケストレーター v41 初期化完了")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"❌ 初期化エラー: {e}")
            import traceback

            traceback.print_exc()
            raise

    async def test_full_integration_flow(self):
        """
        完全統合フローのテスト
        1. ゴール読み込み
        2. タスク分解・書き込み
        3. タスク実行
        4. 品質評価
        5. ナレッジ蓄積
        """
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("🧪 完全統合フローテスト開始")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        try:
            # STEP 1: ゴール読み込み
            logger.info("1️⃣ project_goal シートからゴール読み込み")
            goals = self.safe_sheets.safe_read("project_goal!A2:C100", default=[])

            if goals:
                logger.info(f"   ✅ ゴール取得成功: {len(goals)}件")
                goal = goals[0]
                logger.info(f"   ゴール: {goal[2] if len(goal) > 2 else 'N/A'}...（最初の50文字）")

                # STEP 2: タスク分解・書き込み
                logger.info("2️⃣ PMAgent: タスク分解・pm_tasks シートへ書き込み")
                await self.pm_agent.run_pm_cycle()

                # 書き込み確認
                tasks = self.safe_sheets.safe_read("pm_tasks!A2:K10", default=[])
                logger.info(f"   ✅ pm_tasks シート確認: {len(tasks)}行")

            else:
                logger.warning("   ⚠️ ゴールが見つかりません")
                logger.info("   テスト用ゴールを作成します...")
                test_goal = [
                    ["GOAL_TEST_001", "active", "統合テスト用ゴール: システムの完全統合動作確認"]
                ]
                self.safe_sheets.safe_append("project_goal", test_goal)
                logger.info("   ✅ テスト用ゴール作成完了")

            # STEP 3: pending タスク実行
            logger.info("3️⃣ TaskExecutor: pending タスク実行")
            pending_tasks = self.task_executor.get_pending_tasks()
            logger.info(f"   📋 pending タスク数: {len(pending_tasks)}")

            if pending_tasks:
                task = pending_tasks[0]
                logger.info(f"   実行タスク: {task.get('description', 'N/A')[:50]}...")

                # タスク実行
                result = await self.task_executor.execute_task(task)

                if result["success"]:
                    logger.info("   ✅ タスク実行成功")

                    # STEP 4: 品質評価
                    logger.info("4️⃣ ReviewAgent: 品質評価")
                    review = await self.review_agent.review_task(result)
                    logger.info(f"   📊 品質スコア: {review.get('total_score', 0):.1f}/10")

                    # STEP 5: task_execution_log への書き込み確認
                    logger.info("5️⃣ task_execution_log シート確認")
                    logs = self.safe_sheets.safe_read("task_execution_log!A1:H10", default=[])
                    logger.info(f"   ✅ 実行ログ: {len(logs)}行")

                    # STEP 6: ナレッジ蓄積
                    logger.info("6️⃣ ナレッジベース: 実行結果を蓄積")
                    knowledge_entry = {
                        "title": f"タスク実行: {task.get('task_id')}",
                        "content": f"実行結果: {result.get('result', {})}",
                        "category": "task_execution",
                        "tags": "integration_test,execution",
                    }
                    self.knowledge_manager.add_knowledge(**knowledge_entry)
                    logger.info("   ✅ ナレッジ蓄積完了")

                    # STEP 7: ゴール進捗評価
                    logger.info("7️⃣ GoalEvaluator: ゴール進捗評価")
                    goal_id = task.get("parent_goal_id", "GOAL_001")
                    progress = await self.goal_evaluator.evaluate_goal(goal_id)
                    logger.info(f"   📈 ゴール進捗: {progress.get('progress_percentage', 0):.1f}%")

                else:
                    logger.error(f"   ❌ タスク実行失敗: {result.get('error')}")
            else:
                logger.info("   ⚠️ pending タスクがありません")

            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            logger.info("✅ 完全統合フローテスト完了")
            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        except Exception as e:
            logger.error(f"❌ 統合フローテストエラー: {e}")
            import traceback

            traceback.print_exc()

    async def execute_loop1_task_processing(self) -> Dict[str, Any]:
        """Loop 1: タスク処理"""
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("🔄 Loop 1: タスク処理開始")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        results = {
            "success": False,
            "tasks_executed": 0,
            "tasks_reviewed": 0,
            "goal_progress": 0,
            "errors": [],
        }

        try:
            # ゴール読み込み・タスク分解
            await self.pm_agent.run_pm_cycle()

            # pending タスク実行
            pending_tasks = self.task_executor.get_pending_tasks()
            logger.info(f"   📋 pending タスク数: {len(pending_tasks)}")

            for task in pending_tasks[:3]:  # 最大3件
                try:
                    # タスク実行
                    task_result = await self.task_executor.execute_task(task)

                    if task_result["success"]:
                        self.task_success_count += 1

                        # 品質評価
                        review_result = await self.review_agent.review_task(task_result)
                        logger.info(
                            f"   📊 品質スコア: {review_result.get('total_score', 0):.1f}/10"
                        )

                        # 品質フィードバック
                        if review_result.get("total_score", 10) < 7:
                            await self.quality_loop.process_task_result(task, task_result)

                        results["tasks_reviewed"] += 1
                    else:
                        self.task_failure_count += 1

                    results["tasks_executed"] += 1

                except Exception as e:
                    logger.error(f"   ❌ タスク実行エラー: {e}")
                    self.error_count += 1

            # ゴール進捗評価
            goals = self.safe_sheets.safe_read("project_goal!A2:C100", default=[])
            if goals and len(goals[0]) > 0:
                goal_id = goals[0][0]
                progress = await self.goal_evaluator.evaluate_goal(goal_id)
                results["goal_progress"] = progress.get("progress_percentage", 0)

            results["success"] = True
            logger.info("✅ Loop 1 完了")

        except Exception as e:
            logger.error(f"❌ Loop 1 エラー: {e}")
            results["errors"].append({"loop": "loop1", "error": str(e)})

        return results

    async def execute_loop3_learning(self) -> Dict[str, Any]:
        """Loop 3: 学習"""
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("🧠 Loop 3: 学習サイクル開始")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        results = {"success": False, "patterns_extracted": 0, "knowledge_updated": 0}

        try:
            logs = await self.learning_pipeline.collect_logs()
            patterns = await self.learning_pipeline.extract_patterns(logs)
            recipes = await self.learning_pipeline.generate_repair_recipes(patterns)

            for recipe in recipes:
                self.kb_manager.register_knowledge(recipe)
                results["knowledge_updated"] += 1

            self.last_learning_time = datetime.now()
            results["success"] = True
            logger.info("✅ Loop 3 完了")

        except Exception as e:
            logger.error(f"❌ Loop 3 エラー: {e}")

        return results

    async def run_continuous(self, max_hours: int = 24):
        """24時間連続稼働"""
        logger.info(f"🚀 {max_hours}時間連続稼働開始")

        start_time = datetime.now()

        while True:
            self.cycle_count += 1
            elapsed_hours = (datetime.now() - start_time).total_seconds() / 3600

            if elapsed_hours >= max_hours:
                logger.info(f"⏰ {max_hours}時間経過 - 稼働終了")
                break

            logger.info(f"サイクル {self.cycle_count} 開始（経過: {elapsed_hours:.2f}時間）")

            # Loop 1: タスク処理
            await self.execute_loop1_task_processing()

            # Loop 3: 学習
            hours_since_learning = (datetime.now() - self.last_learning_time).total_seconds() / 3600
            if hours_since_learning >= 6 or self.error_count >= 50:
                await self.execute_loop3_learning()
                self.error_count = 0

            # 統計
            logger.info(
                f"📊 サイクル統計: 成功={self.task_success_count}, 失敗={self.task_failure_count}"
            )

            # 3分待機
            await asyncio.sleep(180)

        total_elapsed = (datetime.now() - start_time).total_seconds() / 3600
        logger.info(f"🎊 連続稼働完了: {total_elapsed:.2f}時間, {self.cycle_count}サイクル")


async def main():
    """メイン関数"""
    try:
        orchestrator = IntegratedOrchestratorV41()

        # 完全統合フローテスト
        logger.info("\n🧪 完全統合フローテストを実行します\n")
        await orchestrator.test_full_integration_flow()

        # 24時間稼働テスト開始
        logger.info("\n🚀 24時間稼働テストを開始します\n")
        await orchestrator.run_continuous(max_hours=24)

    except Exception as e:
        logger.error(f"❌ 致命的エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
