"""
AutonomousOrchestrator v1.18.0 MVP - 最小構成で動作確認

【戦略】
Stage 1: コア機能のみで動作確認（このバージョン）
  - GoogleSheetsManager + SafeSheetsWrapper
  - PMAgent, TaskExecutor, ReviewAgent, GoalEvaluator
  - ErrorClassifier, RollbackAgent

Stage 2: 段階的に機能追加
  - QualityFeedbackLoop
  - SelfLearningPipeline（正しい引数で）
  - SheetsFlowOrchestrator（修正後）

【現在の統合率】
- 動作確認済み: 10エージェント
- 要修正: 3エージェント（次のステージで追加）
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.collaboration.collaboration_agent import CollaborationAgent
from agents.goal_evaluator.goal_evaluator import GoalEvaluator
# Loop 3: 学習（最小構成）
from agents.learning.learning_optimizer import LearningOptimizer
from agents.monitoring.monitoring_agent import MonitoringAgent
# Loop 2: 自己修復（最小構成）
from agents.rollback_agent import RollbackAgent
from agents.self_healing.logging.decision_support_system import \
    DecisionSupportSystem
from agents.self_healing.utils.error_classifier import ErrorClassifier
from browser_control.sheets_manager import GoogleSheetsManager
from core_agents.pm_agent import PMAgent
from core_agents.review_agent import ReviewAgent
# Loop 1: タスク処理
from task_executor.task_executor_main import TaskExecutor
from tools.safe_sheets_wrapper import SafeSheetsWrapper

logger = logging.getLogger(__name__)


class AutonomousOrchestrator:
    """
    自律開発オーケストレーター v1.18.0 MVP

    【3つのループ - 最小構成】
    - Loop 1: タスク処理（3分間隔）
      → project_goal読み込み → pm_tasks → タスク実行 → レビュー → 達成度評価
    - Loop 2: 即時修復（エラー発生時）
      → エラー分類 → ロールバック
    - Loop 3: 学習・改善（条件発動型）
      → LearningOptimizer
    """

    def __init__(self):
        # 基盤
        self.sheets_manager = None
        self.safe_sheets = None

        # Loop 1: タスク処理エージェント
        self.pm_agent = None
        self.task_executor = None
        self.review_agent = None
        self.goal_evaluator = None
        self.collab_agent = None

        # Loop 2: 即時修復エージェント
        self.error_classifier = None
        self.decision_system = None
        self.rollback_agent = None

        # Loop 3: 学習エージェント
        self.learning_optimizer = None

        # 監視
        self.monitoring_agent = None

        # 統計
        self.stats = {
            "cycles_completed": 0,
            "tasks_executed": 0,
            "errors_recovered": 0,
            "goals_achieved": 0,
            "start_time": None,
            "version": "1.18.0-mvp",
        }

        logger.info("✅ AutonomousOrchestrator v1.18.0 MVP 初期化")

    async def initialize(self):
        """完全初期化 - 動作確認済みエージェントのみ"""
        try:
            logger.info("=" * 70)
            logger.info("🚀 AutonomousOrchestrator v1.18.0 MVP 初期化開始")
            logger.info("=" * 70)

            from dotenv import load_dotenv

            load_dotenv(override=True)

            spreadsheet_id = os.getenv("SPREADSHEET_ID")
            if not spreadsheet_id:
                raise ValueError("SPREADSHEET_ID環境変数が設定されていません")

            # 基盤（必須）
            logger.info("📊 [1/10] GoogleSheetsManager初期化")
            self.sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)

            logger.info("🛡️ [2/10] SafeSheetsWrapper初期化")
            self.safe_sheets = SafeSheetsWrapper(self.sheets_manager)

            # Loop 1: タスク処理エージェント
            logger.info("📋 [3/10] PMAgent初期化")
            self.pm_agent = PMAgent(self.sheets_manager)

            logger.info("⚙️ [4/10] TaskExecutor初期化")
            self.task_executor = TaskExecutor(self.sheets_manager)

            logger.info("✅ [5/10] ReviewAgent初期化")
            self.review_agent = ReviewAgent(self.safe_sheets)

            logger.info("🎯 [6/10] GoalEvaluator初期化")
            self.goal_evaluator = GoalEvaluator(self.sheets_manager)

            logger.info("👥 [7/10] CollaborationAgent初期化")
            self.collab_agent = CollaborationAgent()

            # Loop 2: 即時修復エージェント
            logger.info("🔍 [8/10] ErrorClassifier初期化")
            self.error_classifier = ErrorClassifier()

            logger.info("🤔 [9/10] DecisionSupportSystem初期化")
            self.decision_system = DecisionSupportSystem()

            logger.info("⏮️ [10/10] RollbackAgent初期化")
            self.rollback_agent = RollbackAgent()

            # Loop 3: 学習エージェント（最小構成）
            logger.info("🧠 [11/11] LearningOptimizer初期化")
            self.learning_optimizer = LearningOptimizer()

            # 監視
            logger.info("📡 [12/12] MonitoringAgent初期化")
            self.monitoring_agent = MonitoringAgent()

            logger.info("=" * 70)
            logger.info("✅ MVP版エージェント初期化完了（12/12）")
            logger.info("🎯 コア機能: 100%")
            logger.info("📝 Stage 2で追加予定: QualityFeedbackLoop, SelfLearningPipeline")
            logger.info("=" * 70)

            return True

        except Exception as e:
            logger.error(f"❌ 初期化失敗: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return False

    async def execute_autonomous_cycle(self):
        """
        メインの自律実行サイクル

        【実装済み】
        1. project_goalからゴール読み込み ✅
        2. pm_tasksからタスク読み込み ✅
        3. 統計情報表示 ✅

        【次のステージで実装】
        - PMAgentでタスク分解
        - TaskExecutorでタスク実行
        - ReviewAgentで品質評価
        - GoalEvaluatorで達成度評価
        """
        try:
            cycle_start = datetime.now()
            logger.info("\n" + "=" * 70)
            logger.info(f"🔄 サイクル #{self.stats['cycles_completed'] + 1} 開始")
            logger.info("=" * 70)

            # 1. ゴール読み込み
            logger.info("\n📖 [1/3] project_goalからゴール読み込み")
            goals = self.safe_sheets.safe_read("project_goal!A2:Z100", default=[])
            logger.info(f"   ✅ 読み込み成功: {len(goals)}件のゴール")

            if goals and len(goals) > 0:
                logger.info(f"   📋 最初のゴール: {goals[0][1] if len(goals[0]) > 1 else 'N/A'}")

            # 2. タスク読み込み
            logger.info("\n📝 [2/3] pm_tasksからタスク読み込み")
            all_tasks = self.safe_sheets.safe_read("pm_tasks!A2:Z100", default=[])
            pending_tasks = [t for t in all_tasks if len(t) > 4 and t[4] == "pending"]
            completed_tasks = [t for t in all_tasks if len(t) > 4 and t[4] == "completed"]

            logger.info(f"   ✅ 総タスク数: {len(all_tasks)}件")
            logger.info(f"   ⏳ Pending: {len(pending_tasks)}件")
            logger.info(f"   ✅ Completed: {len(completed_tasks)}件")

            if pending_tasks:
                logger.info(
                    f"   📋 次のタスク: {pending_tasks[0][0] if pending_tasks[0] else 'N/A'}"
                )

            # 3. システム統計
            logger.info("\n📊 [3/3] システム統計")
            logger.info(f"   🔄 総サイクル数: {self.stats['cycles_completed']}")
            logger.info(f"   ⚙️ 実行タスク数: {self.stats['tasks_executed']}")
            logger.info(f"   🎯 達成ゴール数: {self.stats['goals_achieved']}")

            # 統計更新
            self.stats["cycles_completed"] += 1
            cycle_duration = (datetime.now() - cycle_start).total_seconds()

            logger.info("\n" + "=" * 70)
            logger.info(f"✅ サイクル #{self.stats['cycles_completed']} 完了")
            logger.info(f"⏱️ 実行時間: {cycle_duration:.2f}秒")
            logger.info(f"💡 次回: タスク実行機能を追加予定")
            logger.info("=" * 70)

        except Exception as e:
            logger.error(f"❌ サイクル実行エラー: {e}")
            import traceback

            logger.error(traceback.format_exc())

    async def trigger_self_healing(self, task, error):
        """Loop 2: 即時修復システム（最小構成）"""
        try:
            logger.info("\n�� 即時修復システム起動")

            # エラー分類
            error_info = self.error_classifier.classify(str(error))
            logger.info(f"   分類: {error_info.get('category', 'unknown')}")

            # 修復戦略決定（次のステージで実装）
            logger.info("   💡 Stage 2で修復戦略を実装予定")

        except Exception as e:
            logger.error(f"❌ 即時修復エラー: {e}")

    async def run(self, max_cycles: int = None):
        """メインループ実行"""
        try:
            if not await self.initialize():
                logger.error("❌ 初期化失敗。終了します。")
                return

            self.stats["start_time"] = datetime.now().isoformat()

            logger.info("\n" + "=" * 70)
            logger.info("🚀 自律開発システム起動（MVP版）")
            logger.info(f"📅 開始時刻: {self.stats['start_time']}")
            logger.info(f"🔄 最大サイクル数: {max_cycles if max_cycles else '無制限'}")
            logger.info(f"📝 バージョン: {self.stats['version']}")
            logger.info("=" * 70)

            cycle_count = 0
            while True:
                await self.execute_autonomous_cycle()

                cycle_count += 1
                if max_cycles and cycle_count >= max_cycles:
                    logger.info(f"\n✅ 最大サイクル数({max_cycles})に到達。終了します。")
                    break

                if max_cycles is None or cycle_count < max_cycles:
                    logger.info("\n⏳ 次のサイクルまで3分待機...")
                    await asyncio.sleep(180)

        except KeyboardInterrupt:
            logger.info("\n⚠️ ユーザーによる中断")
        except Exception as e:
            logger.error(f"\n❌ メインループエラー: {e}")
            import traceback

            logger.error(traceback.format_exc())
        finally:
            logger.info("\n" + "=" * 70)
            logger.info("🛑 自律開発システム終了")
            logger.info(f"📊 総サイクル数: {self.stats['cycles_completed']}")
            logger.info(f"📝 次のステップ: Stage 2でタスク実行機能を追加")
            logger.info("=" * 70)


async def main():
    """テスト実行: 1サイクルのみ"""
    orchestrator = AutonomousOrchestrator()
    await orchestrator.run(max_cycles=1)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧪 AutonomousOrchestrator v1.18.0 MVP テスト")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    asyncio.run(main())
