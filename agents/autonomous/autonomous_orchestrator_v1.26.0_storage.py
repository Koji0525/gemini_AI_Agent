"""
AutonomousOrchestrator v1.26.0 Storage - Phase 1.2統合版

【v1.25.0からの変更】
✅ Phase 1.2: 分散トレーシングストレージ統合
✅ トレースデータの永続化
✅ Prometheusメトリクスエクスポート
✅ 包括的観測基盤の確立
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
from agents.observability.instrumented_agents import instrument_agents
from agents.observability.observability_manager import \
    get_observability_manager
from agents.observability.opentelemetry_config import get_otel_config
from agents.system_observer.system_observer_v3 import SystemObserverV3
from browser_control.sheets_manager import GoogleSheetsManager
from core_agents.pm_agent import PMAgent
from core_agents.review_agent import ReviewAgent
from task_executor.task_executor_main import TaskExecutor
from tools.safe_sheets_wrapper import SafeSheetsWrapper

logger = logging.getLogger(__name__)


def configure_logging_strict():
    logging.basicConfig(
        level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s", force=True
    )
    for logger_name in logging.root.manager.loggerDict:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


class AutonomousOrchestrator:
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.cycle_interval = int(os.getenv("CYCLE_INTERVAL", "10" if debug_mode else "180"))
        self.sheets_manager = None
        self.safe_sheets = None
        self.pm_agent = None
        self.task_executor = None
        self.review_agent = None
        self.monitoring_agent = None
        self.collab_agent = None
        self.execution_analyzer = None
        self.system_observer = None
        self.otel_config = None
        self.observability_manager = None
        self.instrumented_count = 0
        self.stats = {"cycles_completed": 0, "version": "1.26.0-storage"}
        print("✅ AutonomousOrchestrator v1.26.0 Storage 初期化")

    async def initialize(self):
        try:
            print("=" * 70)
            print("🚀 AutonomousOrchestrator v1.26.0 Storage 初期化開始")
            print("=" * 70)

            from dotenv import load_dotenv

            load_dotenv(override=True)
            configure_logging_strict()

            print("📡 [1/8] OpenTelemetry初期化")
            self.otel_config = get_otel_config()

            print("📊 [2/8] ObservabilityManager初期化")
            self.observability_manager = get_observability_manager()

            spreadsheet_id = os.getenv("SPREADSHEET_ID")
            if not spreadsheet_id:
                raise ValueError("SPREADSHEET_ID環境変数が設定されていません")

            print("📋 [3/8] GoogleSheetsManager初期化")
            self.sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)
            self.safe_sheets = SafeSheetsWrapper(self.sheets_manager)
            configure_logging_strict()

            print("🤖 [4/8] エージェント初期化")
            self.pm_agent = PMAgent(self.sheets_manager)
            self.task_executor = TaskExecutor(self.sheets_manager)
            self.review_agent = ReviewAgent(self.safe_sheets)
            self.monitoring_agent = MonitoringAgent()
            self.collab_agent = CollaborationAgent()
            self.execution_analyzer = ExecutionAnalyzer(self.sheets_manager)
            configure_logging_strict()

            print("📡 [5/8] エージェント計装")
            self.instrumented_count = instrument_agents(self)

            print("🔭 [6/8] SystemObserver v3初期化")
            self.system_observer = SystemObserverV3(
                monitoring_agent=self.monitoring_agent,
                execution_analyzer=self.execution_analyzer,
                collaboration_agent=self.collab_agent,
                task_executor=self.task_executor,
            )

            print("📋 [7/8] 全エージェント登録")
            agent_count = self.system_observer.register_orchestrator_agents(self)

            print("=" * 70)
            print(f"✅ [8/8] 初期化完了")
            print(f"   エージェント: {agent_count}個")
            print(f"   計装済み: {self.instrumented_count}個")
            print(f"   トレースストレージ: 有効")
            print(f"   メトリクスエクスポート: 有効")
            print("=" * 70)
            configure_logging_strict()
            return True

        except Exception as e:
            logger.error(f"❌ 初期化失敗: {e}")
            import traceback

            traceback.print_exc()
            return False

    async def execute_autonomous_cycle(self):
        try:
            cycle_start = datetime.now()
            print("\n" + "=" * 70)
            print(f"🔄 サイクル #{self.stats['cycles_completed'] + 1} 開始")
            print("=" * 70)

            # トレース記録開始
            cycle_trace = {
                "trace_id": f"cycle-{self.stats['cycles_completed'] + 1}",
                "operation_name": "autonomous_cycle",
                "status": "in_progress",
                "cycle_number": self.stats["cycles_completed"] + 1,
            }

            print("\n🔭 SystemObserver: 包括的分析実行")
            analysis = self.system_observer.collect_comprehensive_analysis()

            snapshot = analysis["snapshot"]
            print(f"   ✅ CPU: {snapshot['resources'].get('cpu_percent', 0):.1f}%")
            print(f"   ✅ メモリ: {snapshot['resources'].get('memory_percent', 0):.1f}%")

            agents = snapshot["agents"]
            print(f"   👥 エージェント: {agents['total_agents']}個")
            print(f"      📡 計装済み: {self.instrumented_count}個")

            if analysis.get("cost"):
                print(f"   💰 コスト: ${analysis['cost']['hourly_cost']:.4f}/時間")

            # 観測基盤統計
            obs_stats = self.observability_manager.get_comprehensive_stats()
            print(f"   📊 トレース総数: {obs_stats['traces'].get('total_traces', 0)}件")

            # サイクル完了をトレース記録
            duration = (datetime.now() - cycle_start).total_seconds()
            cycle_trace.update({"status": "success", "duration_ms": int(duration * 1000)})
            self.observability_manager.record_trace(cycle_trace)

            self.stats["cycles_completed"] += 1

            print("\n" + "=" * 70)
            print(f"✅ サイクル #{self.stats['cycles_completed']} 完了")
            print(f"⏱️ 実行時間: {duration:.2f}秒")
            print("=" * 70)

        except Exception as e:
            logger.error(f"❌ サイクル実行エラー: {e}")

    async def run(self, max_cycles: int = None):
        try:
            if not await self.initialize():
                return

            print("\n🚀 自律開発システム起動（v1.26.0 Storage）\n")

            cycle_count = 0
            while True:
                await self.execute_autonomous_cycle()
                cycle_count += 1

                if max_cycles and cycle_count >= max_cycles:
                    # 最終統計表示
                    print("\n" + "=" * 70)
                    print("📊 最終統計")
                    print("=" * 70)

                    obs_stats = self.observability_manager.get_comprehensive_stats()
                    print(f"総トレース数: {obs_stats['traces'].get('total_traces', 0)}")
                    print(f"成功率: {obs_stats['traces'].get('success_rate', 0):.1%}")

                    print(f"\n✅ 最大サイクル数({max_cycles})到達。終了します。")
                    break

                if max_cycles is None or cycle_count < max_cycles:
                    print(f"\n⏳ 次のサイクルまで{self.cycle_interval}秒待機...\n")
                    await asyncio.sleep(self.cycle_interval)

        except KeyboardInterrupt:
            print("\n⚠️ ユーザーによる中断")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--cycles", type=int, default=2)
    args = parser.parse_args()

    configure_logging_strict()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧪 AutonomousOrchestrator v1.26.0 Storage")
    print("📊 Phase 1.2: 分散トレーシングストレージ統合完了")
    print(f"🔄 実行サイクル: {args.cycles}回")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    orchestrator = AutonomousOrchestrator(debug_mode=args.debug)
    await orchestrator.run(max_cycles=args.cycles)


if __name__ == "__main__":
    asyncio.run(main())
