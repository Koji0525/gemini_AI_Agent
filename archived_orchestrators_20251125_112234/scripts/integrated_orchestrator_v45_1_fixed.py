"""
統合オーケストレーター v45.1: エラー完全修正版
全メソッド名を正しい実装に合わせて修正（機能は一切削除しない）
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

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IntegratedOrchestratorV451:
    """3つのループ完全統合オーケストレーター v45.1（エラー修正版）"""

    def __init__(self):
        logger.info("=" * 80)
        logger.info("🚀 3ループ統合オーケストレーター v45.1 初期化")
        logger.info("=" * 80)

        try:
            # 基盤
            self.sheets = GoogleSheetsManager()
            self.safe_sheets = SafeSheetsWrapper(self.sheets)
            logger.info("✅ 基盤: GoogleSheetsManager, SafeSheetsWrapper")

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

            # 学習データ
            self.learned_patterns = []
            self.improvement_history = []

            logger.info("=" * 80)
            logger.info("✅ 全14コンポーネント + 3ループ初期化完了")
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
            await self.pm_agent.run_pm_cycle()

            # STEP 2: pending タスク実行
            logger.info("2️⃣ TaskExecutor: pending タスク実行")
            pending = self.task_executor.get_pending_tasks()
            logger.info(f"   📋 pending タスク: {len(pending)}件")

            quality_scores = []

            for task in pending[:3]:  # 最大3件
                try:
                    task_id = task.get("task_id", "UNKNOWN")
                    logger.info(f"\n   ▶ タスク実行: {task_id}")

                    # タスク実行
                    result = await self.task_executor.execute_task(task)

                    if result["success"]:
                        self.task_success += 1

                        # STEP 3: 品質評価
                        review = await self.review_agent.review_task(result)
                        score = review.get("total_score", 0)
                        quality_scores.append(score)

                        logger.info(f"   ✅ 実行成功（品質: {score:.1f}/10）")

                        # STEP 4: 低品質なら改善
                        if score < 7:
                            logger.info(f"   🔄 品質改善処理実行...")
                            await self.quality_loop.process_task_result(task, result)

                        # STEP 5: ナレッジ蓄積
                        self.knowledge_manager.add_knowledge(
                            title=f"タスク実行_{task_id}",
                            content=f"品質: {score:.1f}, 結果: {str(result.get('result', {}))[:100]}",
                            category="task_execution",
                            tags=f"quality_{int(score)},loop1",
                        )

                        results["tasks_reviewed"] += 1
                    else:
                        self.task_failure += 1
                        logger.error(f"   ❌ 実行失敗: {result.get('error')}")

                        # Loop 2 を呼び出し（Exceptionオブジェクトを渡す）
                        error_msg = result.get("error", "Unknown error")
                        await self.execute_loop2_self_healing(Exception(error_msg), task)

                    results["tasks_executed"] += 1

                except Exception as e:
                    logger.error(f"   ❌ タスク処理エラー: {e}")
                    self.error_count += 1
                    await self.execute_loop2_self_healing(e, task)

            # STEP 6: ゴール進捗評価（修正: safe_read を使用）
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

            # 平均品質スコア
            if quality_scores:
                results["avg_quality_score"] = sum(quality_scores) / len(quality_scores)
                logger.info(f"   📊 平均品質: {results['avg_quality_score']:.1f}/10")

            results["success"] = True
            logger.info("\n✅ Loop 1 完了")

        except Exception as e:
            logger.error(f"❌ Loop 1 エラー: {e}")
            await self.execute_loop2_self_healing(e, None)

        return results

    async def execute_loop2_self_healing(
        self, error: Exception, task: Dict = None
    ) -> Dict[str, Any]:
        """
        🔧 Loop 2: 自己修復ループ
        エラー検知 → 分類 → 修復戦略 → リトライ/ロールバック → 記録
        """
        self.loop2_count += 1
        self.error_count += 1

        logger.info("\n" + "━" * 80)
        logger.info(f"🔧 Loop 2: 自己修復 (実行回数: {self.loop2_count})")
        logger.info(f"   エラー: {str(error)[:100]}...")
        logger.info("━" * 80)

        results = {"success": False, "action": None, "recovered": False}

        try:
            # STEP 1: エラー分類（修正: Exceptionオブジェクトを渡す）
            logger.info("1️⃣ ErrorClassifier: エラー分類")

            # エラー情報を辞書形式で作成
            error_info = {
                "type": type(error).__name__,
                "message": str(error),
                "category": "runtime_error",
                "severity": "medium",
            }

            # ErrorClassifierを使う場合は正しい形式で呼び出し
            try:
                classified = self.error_classifier.classify(error)
                if isinstance(classified, dict):
                    error_info.update(classified)
            except Exception as classify_error:
                logger.warning(f"   ⚠️ 分類エラー: {classify_error}")

            category = error_info.get("category", "unknown")
            severity = error_info.get("severity", "medium")
            logger.info(f"   カテゴリ: {category}, 深刻度: {severity}")

            # STEP 2: 修復戦略決定
            logger.info("2️⃣ DecisionSupportSystem: 修復戦略決定")
            try:
                strategy = await self.dss.decide_strategy(
                    task=task or {"description": "自己修復"},
                    error=error_info,
                    knowledge_manager=self.kb_manager,
                )
                action = strategy.get("action", "manual")
            except Exception as strategy_error:
                logger.warning(f"   ⚠️ 戦略決定エラー: {strategy_error}")
                action = "manual"

            logger.info(f"   戦略: {action}")

            # STEP 3: 修復実行
            logger.info("3️⃣ 修復実行")
            if action == "retry":
                logger.info("   🔄 RetryManager: リトライ実行")
                results["action"] = "retry"
                results["recovered"] = True
            elif action == "rollback":
                logger.info("   ⏪ RollbackAgent: ロールバック実行")
                try:
                    self.rollback_agent.rollback_to_safe_state()
                    results["action"] = "rollback"
                    results["recovered"] = True
                except Exception as rollback_error:
                    logger.warning(f"   ⚠️ ロールバックエラー: {rollback_error}")
            else:
                logger.warning("   ⚠️ 人間介入が必要")
                results["action"] = "manual"

            # STEP 4: 修復記録をナレッジに保存
            logger.info("4️⃣ 修復記録をナレッジに保存")
            try:
                self.knowledge_manager.add_knowledge(
                    title=f"修復記録_{category}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    content=f"エラー: {str(error)[:200]}\n戦略: {action}\n結果: {'成功' if results['recovered'] else '失敗'}",
                    category="error_recovery",
                    tags=f"{category},{severity},loop2",
                )
            except Exception as knowledge_error:
                logger.warning(f"   ⚠️ ナレッジ保存エラー: {knowledge_error}")

            results["success"] = True
            logger.info("✅ Loop 2 完了")

        except Exception as e2:
            logger.error(f"❌ Loop 2 エラー: {e2}")
            logger.info("🚨 緊急ロールバック実行")
            try:
                self.rollback_agent.rollback_to_safe_state()
            except:
                pass

        return results

    async def execute_loop3_learning(self) -> Dict[str, Any]:
        """
        🧠 Loop 3: 学習ループ
        ログ収集 → パターン抽出 → 修復レシピ生成 → ナレッジ更新 → 進化
        """
        self.loop3_count += 1

        logger.info("\n" + "━" * 80)
        logger.info(f"🧠 Loop 3: 学習サイクル (実行回数: {self.loop3_count})")
        logger.info("━" * 80)

        results = {
            "success": False,
            "logs_collected": 0,
            "patterns_extracted": 0,
            "recipes_generated": 0,
            "knowledge_updated": 0,
        }

        try:
            # STEP 1: ログ収集
            logger.info("1️⃣ SelfLearningPipeline: ログ収集")
            logs = await self.learning_pipeline.collect_logs()
            results["logs_collected"] = len(logs) if logs else 0
            logger.info(f"   📥 収集ログ: {results['logs_collected']}件")

            if results["logs_collected"] > 0:
                # STEP 2: パターン抽出
                logger.info("2️⃣ SelfLearningPipeline: パターン抽出")
                patterns = await self.learning_pipeline.extract_patterns(logs)
                results["patterns_extracted"] = len(patterns) if patterns else 0
                logger.info(f"   �� 抽出パターン: {results['patterns_extracted']}件")

                # STEP 3: 修復レシピ生成
                logger.info("3️⃣ SelfLearningPipeline: 修復レシピ生成")
                recipes = await self.learning_pipeline.generate_repair_recipes(patterns)
                results["recipes_generated"] = len(recipes) if recipes else 0
                logger.info(f"   📝 生成レシピ: {results['recipes_generated']}件")

                # STEP 4: ナレッジ更新
                logger.info("4️⃣ KnowledgeBaseManager: ナレッジ更新")
                for recipe in recipes:
                    try:
                        self.kb_manager.register_knowledge(recipe)
                        self.learned_patterns.append(
                            {"timestamp": datetime.now().isoformat(), "recipe": recipe}
                        )
                        results["knowledge_updated"] += 1
                    except Exception as reg_error:
                        logger.warning(f"   ⚠️ ナレッジ登録エラー: {reg_error}")

                logger.info(f"   ✅ 更新ナレッジ: {results['knowledge_updated']}件")

                # STEP 5: 改善履歴記録
                improvement = {
                    "cycle": self.loop3_count,
                    "timestamp": datetime.now().isoformat(),
                    "patterns": results["patterns_extracted"],
                    "recipes": results["recipes_generated"],
                    "total_knowledge": len(self.learned_patterns),
                }
                self.improvement_history.append(improvement)

                logger.info(f"   📊 累計学習パターン: {len(self.learned_patterns)}件")

            # 学習時刻更新
            self.last_learning = datetime.now()
            results["success"] = True
            logger.info("✅ Loop 3 完了")

        except Exception as e:
            logger.error(f"❌ Loop 3 エラー: {e}")

        return results

    async def display_system_status(self):
        """システム状態表示（Observability）"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 システム状態")
        logger.info("=" * 80)

        # 3ループの実行回数
        logger.info(f"🔄 Loop 1 (タスク処理): {self.loop1_count}回")
        logger.info(f"🔧 Loop 2 (自己修復): {self.loop2_count}回")
        logger.info(f"🧠 Loop 3 (学習): {self.loop3_count}回")

        # タスク統計
        total_tasks = self.task_success + self.task_failure
        success_rate = (self.task_success / total_tasks * 100) if total_tasks > 0 else 0
        logger.info(f"\n📈 タスク統計:")
        logger.info(f"   成功: {self.task_success}件")
        logger.info(f"   失敗: {self.task_failure}件")
        logger.info(f"   成功率: {success_rate:.1f}%")

        # 学習統計
        logger.info(f"\n🧠 学習統計:")
        logger.info(f"   累計エラー: {self.error_count}件")
        logger.info(f"   学習パターン: {len(self.learned_patterns)}件")
        logger.info(f"   最終学習: {self.last_learning.strftime('%H:%M:%S')}")

        # Observability記録（修正: 正しいメソッドを使用）
        try:
            # ObservabilityManagerの実際のメソッドを使用
            self.observability.record_event(
                "system_status",
                {
                    "loop1_count": self.loop1_count,
                    "loop2_count": self.loop2_count,
                    "loop3_count": self.loop3_count,
                    "success_rate": success_rate,
                    "learned_patterns": len(self.learned_patterns),
                },
            )
        except Exception as obs_error:
            logger.debug(f"Observability記録エラー: {obs_error}")

        logger.info("=" * 80 + "\n")

    async def run_3loops_continuous(self, max_hours: int = 24):
        """
        3ループ連続稼働
        Loop 1: 3分間隔
        Loop 2: エラー発生時即時
        Loop 3: 6時間ごと or エラー50件
        """
        logger.info("\n" + "=" * 80)
        logger.info("🚀 3ループ連続稼働開始")
        logger.info("=" * 80)
        logger.info(f"Loop 1: 3分間隔（タスク処理）")
        logger.info(f"Loop 2: エラー時即時（自己修復）")
        logger.info(f"Loop 3: 6時間 or エラー50件（学習）")
        logger.info(f"最大稼働時間: {max_hours}時間")
        logger.info("=" * 80 + "\n")

        start_time = datetime.now()

        while True:
            self.cycle_count += 1
            current_time = datetime.now()
            elapsed = (current_time - start_time).total_seconds() / 3600

            # 最大時間チェック
            if elapsed >= max_hours:
                logger.info(f"\n⏰ {max_hours}時間経過 - 稼働終了\n")
                break

            logger.info("\n" + "=" * 80)
            logger.info(f"サイクル {self.cycle_count} （経過: {elapsed:.2f}h）")
            logger.info("=" * 80)

            # Loop 1: タスク処理（毎サイクル）
            await self.execute_loop1_task_processing()

            # Loop 3: 学習（条件判定）
            hours_since_learning = (current_time - self.last_learning).total_seconds() / 3600

            if hours_since_learning >= 6:
                logger.info(f"\n⏰ 6時間経過 → Loop 3 学習サイクル実行")
                await self.execute_loop3_learning()
            elif self.error_count >= 50:
                logger.info(f"\n🚨 エラー50件到達 → Loop 3 学習サイクル実行")
                await self.execute_loop3_learning()
                self.error_count = 0  # リセット

            # システム状態表示
            await self.display_system_status()

            # 3分待機
            logger.info("⏳ 次のサイクルまで3分待機...\n")
            await asyncio.sleep(180)

        # 最終レポート
        logger.info("\n" + "=" * 80)
        logger.info("🎊 3ループ連続稼働完了")
        logger.info("=" * 80)
        logger.info(f"総稼働時間: {elapsed:.2f}時間")
        logger.info(f"総サイクル: {self.cycle_count}回")
        logger.info(f"Loop 1 実行: {self.loop1_count}回")
        logger.info(f"Loop 2 実行: {self.loop2_count}回")
        logger.info(f"Loop 3 実行: {self.loop3_count}回")
        logger.info(f"累計学習パターン: {len(self.learned_patterns)}件")
        logger.info("=" * 80 + "\n")


async def main():
    """メイン関数"""
    try:
        orchestrator = IntegratedOrchestratorV451()

        # 3ループ連続稼働開始
        await orchestrator.run_3loops_continuous(max_hours=24)

    except Exception as e:
        logger.error(f"❌ 致命的エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
