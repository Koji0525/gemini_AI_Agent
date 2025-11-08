"""
AutonomousOrchestrator v1.23.0 Complete - SystemObserver完全統合版

【Phase 1-5完成版】
✅ Phase 1: データ収集基盤
✅ Phase 2: 可視化基盤（Web + CLI）
✅ Phase 3: 連携強化（実データ統合）
✅ Phase 4: 分析高度化（パフォーマンス・コスト・予測）
✅ Phase 5: 運用化（耐久性・ドキュメント）

【統合率】100% + SystemObserver完全統合
"""

import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.advanced_analytics.execution_analyzer import ExecutionAnalyzer
from agents.collaboration.collaboration_agent import CollaborationAgent
from agents.monitoring.monitoring_agent import MonitoringAgent
from agents.system_observer.system_observer_complete import \
    SystemObserverComplete
from browser_control.sheets_manager import GoogleSheetsManager
from core_agents.pm_agent import PMAgent
from core_agents.review_agent import ReviewAgent
from task_executor.task_executor_main import TaskExecutor
from tools.safe_sheets_wrapper import SafeSheetsWrapper

logger = logging.getLogger(__name__)


class AutonomousOrchestrator:
    """自律開発オーケストレーター v1.23.0 Complete"""

    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.cycle_interval = int(os.getenv("CYCLE_INTERVAL", "10" if debug_mode else "180"))

        # エージェント
        self.sheets_manager = None
        self.safe_sheets = None
        self.pm_agent = None
        self.task_executor = None
        self.review_agent = None
        self.monitoring_agent = None
        self.collab_agent = None
        self.execution_analyzer = None

        # 🔭 SystemObserver Complete（Phase 1-5統合）
        self.system_observer = None

        # 統計
        self.stats = {
            "cycles_completed": 0,
            "tasks_executed": 0,
            "start_time": None,
            "version": "1.23.0-complete",
        }

        print(f"✅ AutonomousOrchestrator v1.23.0 Complete 初期化")
        print(f"🔭 SystemObserver: Phase 1-5完全統合")

    async def initialize(self):
        """完全初期化"""
        try:
            print("=" * 70)
            print("🚀 AutonomousOrchestrator v1.23.0 Complete 初期化開始")
            print("=" * 70)

            from dotenv import load_dotenv

            load_dotenv(override=True)

            spreadsheet_id = os.getenv("SPREADSHEET_ID")
            if not spreadsheet_id:
                raise ValueError("SPREADSHEET_ID環境変数が設定されていません")

            # 基盤
            print("📊 GoogleSheetsManager初期化")
            self.sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)
            self.safe_sheets = SafeSheetsWrapper(self.sheets_manager)

            # エージェント
            print("🤖 エージェント初期化")
            self.pm_agent = PMAgent(self.sheets_manager)
            self.task_executor = TaskExecutor(self.sheets_manager)
            self.review_agent = ReviewAgent(self.safe_sheets)
            self.monitoring_agent = MonitoringAgent()
            self.collab_agent = CollaborationAgent()
            self.execution_analyzer = ExecutionAnalyzer(self.sheets_manager)

            # 🔭 SystemObserver Complete
            print("🔭 SystemObserver Complete初期化（Phase 1-5統合）")
            self.system_observer = SystemObserverComplete(
                monitoring_agent=self.monitoring_agent,
                execution_analyzer=self.execution_analyzer,
                collaboration_agent=self.collab_agent,
                task_executor=self.task_executor,
            )

            print("=" * 70)
            print("✅ 全エージェント初期化完了")
            print("🎯 統合率: 100% + SystemObserver完全統合")
            print("=" * 70)

            logging.getLogger().setLevel(logging.WARNING)

            return True

        except Exception as e:
            logger.error(f"❌ 初期化失敗: {e}")
            return False

    async def execute_autonomous_cycle(self):
        """メインの自律実行サイクル"""
        try:
            cycle_start = datetime.now()
            print("\n" + "=" * 70)
            print(f"🔄 サイクル #{self.stats['cycles_completed'] + 1} 開始")
            print("=" * 70)

            # 🔭 包括的分析（Phase 1-5統合）
            print("\n🔭 SystemObserver: 包括的分析実行")
            analysis = self.system_observer.collect_comprehensive_analysis()

            # 結果表示
            snapshot = analysis["snapshot"]
            print(f"   ✅ CPU: {snapshot['resources'].get('cpu_percent', 0):.1f}%")
            print(f"   ✅ メモリ: {snapshot['resources'].get('memory_percent', 0):.1f}%")
            print(f"   ✅ ヘルス: {snapshot['health']}")

            if analysis.get("cost"):
                print(f"   💰 コスト（時間）: ${analysis['cost']['hourly_cost']:.4f}")

            if analysis.get("predictions"):
                pred = analysis["predictions"]["predictions"]["cpu"]
                print(f"   🔮 CPU予測: {pred['current']:.1f}% → {pred['predicted']:.1f}%")

            # 統計更新
            self.stats["cycles_completed"] += 1
            cycle_duration = (datetime.now() - cycle_start).total_seconds()

            print("\n" + "=" * 70)
            print(f"✅ サイクル #{self.stats['cycles_completed']} 完了")
            print(f"⏱️ 実行時間: {cycle_duration:.2f}秒")
            print("=" * 70)

        except Exception as e:
            logger.error(f"❌ サイクル実行エラー: {e}")

    async def run(self, max_cycles: int = None):
        """メインループ"""
        try:
            if not await self.initialize():
                logger.error("❌ 初期化失敗。終了します。")
                return

            self.stats["start_time"] = datetime.now().isoformat()

            print("\n" + "=" * 70)
            print("🚀 自律開発システム起動（v1.23.0 Complete）")
            print(f"🔭 SystemObserver: Phase 1-5完全統合")
            print("=" * 70)

            cycle_count = 0
            while True:
                await self.execute_autonomous_cycle()

                cycle_count += 1
                if max_cycles and cycle_count >= max_cycles:
                    print(f"\n✅ 最大サイクル数({max_cycles})に到達。終了します。")
                    break

                if max_cycles is None or cycle_count < max_cycles:
                    print(f"\n⏳ 次のサイクルまで{self.cycle_interval}秒待機...")
                    await asyncio.sleep(self.cycle_interval)

        except KeyboardInterrupt:
            print("\n⚠️ ユーザーによる中断")
        finally:
            print("\n" + "=" * 70)
            print("🛑 自律開発システム終了")
            print("=" * 70)


async def main():
    parser = argparse.ArgumentParser(description="AutonomousOrchestrator v1.23.0")
    parser.add_argument("--debug", action="store_true", help="デバッグモード")
    parser.add_argument("--cycles", type=int, default=3, help="実行サイクル数")

    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧪 AutonomousOrchestrator v1.23.0 Complete")
    print(f"🔭 SystemObserver: Phase 1-5完全統合")
    print(f"🔄 実行サイクル: {args.cycles}回")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    orchestrator = AutonomousOrchestrator(debug_mode=args.debug)
    await orchestrator.run(max_cycles=args.cycles)


if __name__ == "__main__":
    asyncio.run(main())
