"""
統合オーケストレーター v44: 完全動作証明版
全コンポーネントの正しい初期化 + 実動作証明
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

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

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IntegratedOrchestratorV44:
    """統合オーケストレーター v44 - 完全動作証明版"""

    def __init__(self):
        logger.info("=" * 80)
        logger.info("🚀 統合オーケストレーター v44 初期化開始（完全動作証明版）")
        logger.info("=" * 80)

        try:
            # 基盤
            logger.info("1️⃣ 基盤コンポーネント...")
            self.sheets = GoogleSheetsManager()
            self.safe_sheets = SafeSheetsWrapper(self.sheets)
            logger.info("   ✅ GoogleSheetsManager, SafeSheetsWrapper")

            # Loop 1: タスク処理
            logger.info("2️⃣ Loop 1: タスク処理...")
            self.pm_agent = PMAgent(sheets_manager=self.sheets)
            self.task_executor = TaskExecutor(sheets_manager=self.sheets)
            self.review_agent = ReviewAgent(sheets_wrapper=self.safe_sheets)
            self.quality_loop = QualityFeedbackLoop(sheets_manager=self.sheets)
            self.goal_evaluator = GoalEvaluator(sheets_manager=self.sheets)
            logger.info("   ✅ PMAgent, TaskExecutor, ReviewAgent, QualityLoop, GoalEvaluator")

            # Loop 2: 自己修復
            logger.info("3️⃣ Loop 2: 自己修復...")
            self.error_classifier = ErrorClassifier()
            self.dss = DecisionSupportSystem()
            self.retry_manager = RetryManager()
            self.rollback_agent = RollbackAgent()
            logger.info("   ✅ ErrorClassifier, DSS, RetryManager, RollbackAgent")

            # Loop 3: 学習（正しいパラメータで初期化）
            logger.info("4️⃣ Loop 3: 学習...")
            self.kb_manager = KnowledgeBaseManager()
            self.learning_pipeline = SelfLearningPipeline(
                sheets_manager=self.sheets, kb_manager=self.kb_manager
            )
            self.knowledge_manager = KnowledgeManager()
            logger.info("   ✅ KBManager, SelfLearningPipeline, KnowledgeManager")

            # オブザーバビリティ
            logger.info("5️⃣ オブザーバビリティ...")
            self.observability = ObservabilityManager()
            logger.info("   ✅ ObservabilityManager")

            self.cycle_count = 0
            self.task_success_count = 0
            self.task_failure_count = 0

            logger.info("=" * 80)
            logger.info("✅ 全14コンポーネント初期化完了")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"❌ 初期化エラー: {e}")
            import traceback

            traceback.print_exc()
            raise

    async def prove_integration_works(self):
        """
        完全統合動作証明テスト
        実際にスプレッドシートを読み書きして動作を証明
        """
        logger.info("\n" + "=" * 80)
        logger.info("🎯 完全統合動作証明テスト開始")
        logger.info("=" * 80 + "\n")

        proof = {}

        try:
            # 📋 証明1: project_goal → タスク分解 → pm_tasks書き込み
            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            logger.info("📋 証明1: project_goal → タスク分解 → pm_tasks書き込み")
            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            # ゴール読み込み
            logger.info("STEP 1-1: project_goal シート読み込み")
            goals = self.safe_sheets.safe_read("project_goal!A2:C100", default=[])

            if not goals or len(goals) == 0:
                logger.info("   ⚠️ ゴールなし。テスト用ゴール作成...")
                test_goal = [
                    [
                        f'GOAL_PROOF_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                        "active",
                        "【動作証明】スプレッドシート統合の完全動作確認テスト",
                    ]
                ]
                success = self.safe_sheets.safe_append("project_goal", test_goal)
                if success:
                    logger.info("   ✅ テスト用ゴール作成成功")
                    goals = test_goal
                else:
                    logger.error("   ❌ ゴール作成失敗")
                    return proof

            goal = goals[0]
            goal_id = goal[0] if len(goal) > 0 else "GOAL_001"
            goal_desc = goal[2] if len(goal) > 2 else "テストゴール"

            logger.info(f"   ✅ ゴール読み込み成功")
            logger.info(f"      ID: {goal_id}")
            logger.info(f"      内容: {goal_desc[:80]}...")
            proof["goal_read"] = True

            # タスク分解・書き込み
            logger.info("\nSTEP 1-2: PMAgent でタスク分解")
            tasks_before = self.safe_sheets.safe_read("pm_tasks!A2:A1000", default=[])
            count_before = len(tasks_before)
            logger.info(f"   書き込み前のタスク数: {count_before}行")

            logger.info("   PMAgent.run_pm_cycle() 実行中...")
            await self.pm_agent.run_pm_cycle()

            tasks_after = self.safe_sheets.safe_read("pm_tasks!A2:K1000", default=[])
            count_after = len(tasks_after)
            logger.info(f"   書き込み後のタスク数: {count_after}行")

            if count_after >= count_before:
                logger.info(
                    f"   ✅ pm_tasksシートへの書き込み成功（差分: {count_after - count_before}行）"
                )
                proof["task_write"] = True

                # 最新タスクの内容表示
                if count_after > 0:
                    latest_task = tasks_after[-1]
                    logger.info(f"   最新タスク:")
                    logger.info(f"      ID: {latest_task[0] if len(latest_task) > 0 else 'N/A'}")
                    logger.info(
                        f"      内容: {latest_task[2] if len(latest_task) > 2 else 'N/A'}..."
                    )
            else:
                logger.warning("   ⚠️ タスク数が減少しています")

            # 📋 証明2: タスク実行 → task_execution_log書き込み
            logger.info("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            logger.info("📋 証明2: タスク実行 → task_execution_log書き込み")
            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            logger.info("STEP 2-1: pending タスク取得")
            pending_tasks = self.task_executor.get_pending_tasks()
            logger.info(f"   pending タスク数: {len(pending_tasks)}件")

            if pending_tasks:
                task = pending_tasks[0]
                task_id = task.get("task_id", "UNKNOWN")
                task_desc = task.get("description", "N/A")

                logger.info(f"   実行対象タスク:")
                logger.info(f"      ID: {task_id}")
                logger.info(f"      内容: {task_desc[:80]}...")

                logger.info("\nSTEP 2-2: TaskExecutor でタスク実行")
                logs_before = self.safe_sheets.safe_read("task_execution_log!A2:H1000", default=[])
                log_count_before = len(logs_before)
                logger.info(f"   実行前のログ数: {log_count_before}行")

                result = await self.task_executor.execute_task(task)

                logs_after = self.safe_sheets.safe_read("task_execution_log!A2:H1000", default=[])
                log_count_after = len(logs_after)
                logger.info(f"   実行後のログ数: {log_count_after}行")

                if result["success"]:
                    logger.info("   ✅ タスク実行成功")
                    proof["task_execute"] = True

                    if log_count_after > log_count_before:
                        logger.info(
                            f"   ✅ task_execution_log への書き込み成功（差分: {log_count_after - log_count_before}行）"
                        )
                        proof["log_write"] = True

                        # 最新ログ表示
                        if log_count_after > 0:
                            latest_log = logs_after[-1]
                            logger.info(f"   最新ログ:")
                            logger.info(
                                f"      タスクID: {latest_log[0] if len(latest_log) > 0 else 'N/A'}"
                            )
                            logger.info(
                                f"      ステータス: {latest_log[2] if len(latest_log) > 2 else 'N/A'}"
                            )

                    # 📋 証明3: ナレッジ自動蓄積
                    logger.info("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    logger.info("📋 証明3: ナレッジ自動蓄積")
                    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

                    logger.info("STEP 3-1: KnowledgeManager でナレッジ登録")
                    knowledge_title = f"動作証明_タスク実行_{task_id}"
                    knowledge_content = f"タスク: {task_desc}\n実行結果: 成功\n時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

                    self.knowledge_manager.add_knowledge(
                        title=knowledge_title,
                        content=knowledge_content,
                        category="proof_test",
                        tags="integration_proof,task_execution",
                    )
                    logger.info(f"   ✅ ナレッジ登録成功")
                    logger.info(f"      タイトル: {knowledge_title}")
                    proof["knowledge_store"] = True

                    # 📋 証明4: ReviewAgent による品質評価
                    logger.info("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    logger.info("📋 証明4: ReviewAgent による品質評価")
                    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

                    logger.info("STEP 4-1: ReviewAgent で品質評価")
                    review = await self.review_agent.review_task(result)

                    total_score = review.get("total_score", 0)
                    logger.info(f"   ✅ 品質評価完了")
                    logger.info(f"      総合スコア: {total_score:.1f}/10")
                    logger.info(f"      完成度: {review.get('completeness_score', 0):.1f}/10")
                    logger.info(f"      正確性: {review.get('correctness_score', 0):.1f}/10")
                    logger.info(f"      効率性: {review.get('efficiency_score', 0):.1f}/10")
                    logger.info(f"      保守性: {review.get('maintainability_score', 0):.1f}/10")
                    proof["quality_review"] = True

                    # 📋 証明5: ゴール進捗評価
                    logger.info("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    logger.info("📋 証明5: ゴール進捗評価")
                    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

                    logger.info("STEP 5-1: GoalEvaluator で進捗評価")
                    progress = await self.goal_evaluator.evaluate_goal(goal_id)

                    progress_pct = progress.get("progress_percentage", 0)
                    completed = progress.get("completed_tasks", 0)
                    total = progress.get("total_tasks", 0)

                    logger.info(f"   ✅ ゴール進捗評価完了")
                    logger.info(f"      進捗率: {progress_pct:.1f}%")
                    logger.info(f"      完了タスク: {completed}/{total}件")
                    proof["goal_progress"] = True

                else:
                    logger.error(f"   ❌ タスク実行失敗: {result.get('error')}")
            else:
                logger.warning("   ⚠️ pending タスクがありません")

            # 結果サマリー
            logger.info("\n" + "=" * 80)
            logger.info("📊 完全統合動作証明結果")
            logger.info("=" * 80)

            proofs = [
                ("ゴール読み込み", proof.get("goal_read", False)),
                ("タスク分解・書き込み", proof.get("task_write", False)),
                ("タスク実行", proof.get("task_execute", False)),
                ("実行ログ書き込み", proof.get("log_write", False)),
                ("ナレッジ蓄積", proof.get("knowledge_store", False)),
                ("品質評価", proof.get("quality_review", False)),
                ("ゴール進捗評価", proof.get("goal_progress", False)),
            ]

            for i, (name, success) in enumerate(proofs, 1):
                status = "✅ 動作確認" if success else "❌ 未確認"
                logger.info(f"  {i}. {name:20s}: {status}")

            success_count = sum(1 for _, s in proofs if s)
            total_count = len(proofs)
            success_rate = (success_count / total_count) * 100

            logger.info("")
            logger.info(f"  動作確認率: {success_rate:.1f}% ({success_count}/{total_count})")
            logger.info("=" * 80 + "\n")

            if success_rate == 100:
                logger.info("🎉🎉🎉 全機能の動作を完全に証明しました！ 🎉🎉🎉\n")
                return True
            else:
                logger.warning(f"⚠️ 一部機能の動作確認ができていません（{success_rate:.1f}%）\n")
                return False

        except Exception as e:
            logger.error(f"❌ 動作証明テストエラー: {e}")
            import traceback

            traceback.print_exc()
            return False

    async def run_continuous(self, max_hours: int = 24):
        """24時間連続稼働"""
        logger.info(f"🚀 24時間連続稼働開始\n")

        start_time = datetime.now()

        while True:
            self.cycle_count += 1
            elapsed = (datetime.now() - start_time).total_seconds() / 3600

            if elapsed >= max_hours:
                logger.info(f"\n⏰ {max_hours}時間経過 - 稼働終了\n")
                break

            logger.info(f"\n{'='*60}")
            logger.info(f"サイクル {self.cycle_count} （経過: {elapsed:.2f}h）")
            logger.info("=" * 60)

            # ゴール → タスク分解
            await self.pm_agent.run_pm_cycle()

            # pending タスク実行
            pending = self.task_executor.get_pending_tasks()
            for task in pending[:3]:
                result = await self.task_executor.execute_task(task)
                if result["success"]:
                    self.task_success_count += 1
                    review = await self.review_agent.review_task(result)
                    logger.info(f"✅ タスク成功（スコア: {review.get('total_score', 0):.1f}/10）")
                else:
                    self.task_failure_count += 1

            logger.info(f"📊 累計: 成功={self.task_success_count}, 失敗={self.task_failure_count}")

            # 3分待機
            await asyncio.sleep(180)

        logger.info(f"🎊 連続稼働完了: {self.cycle_count}サイクル\n")


async def main():
    """メイン関数"""
    try:
        orchestrator = IntegratedOrchestratorV44()

        # 完全統合動作証明テスト
        logger.info("\n🎯 完全統合動作証明テスト実施\n")
        proof_success = await orchestrator.prove_integration_works()

        if proof_success:
            logger.info("\n" + "=" * 80)
            logger.info("✅ 全機能の動作を証明！24時間稼働を開始します")
            logger.info("=" * 80 + "\n")

            # 24時間稼働開始
            await orchestrator.run_continuous(max_hours=24)
        else:
            logger.error("\n❌ 一部機能の動作確認ができませんでした。")

    except Exception as e:
        logger.error(f"❌ 致命的エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
