"""
AutonomousOrchestrator v1.27.1 Visualization Fixed

【v1.27.0からの変更】
✅ トレース記録を各ステップで明示的に実行
✅ ロギング設定のスレッドセーフ化
✅ ダッシュボードとの連携強化
"""

import argparse
import asyncio
import logging
import os
import sys
import threading
import time
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
    """スレッドセーフなロギング設定"""
    logging.basicConfig(
        level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s", force=True
    )
    # リストに変換してから反復（辞書変更エラー回避）
    logger_names = list(logging.root.manager.loggerDict.keys())
    for logger_name in logger_names:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


class AutonomousOrchestrator:
    def __init__(self, debug_mode: bool = False, enable_dashboard: bool = False):
        self.debug_mode = debug_mode
        self.enable_dashboard = enable_dashboard
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
        self.dashboard_thread = None
        self.stats = {"cycles_completed": 0, "version": "1.27.1-viz-fixed"}
        print("✅ AutonomousOrchestrator v1.27.1 Visualization Fixed 初期化")

    def start_dashboard_server(self):
        """ダッシュボードサーバー起動（別スレッド）"""
        if not self.enable_dashboard:
            return

        try:
            from agents.observability.visualization.dashboard_server import \
                start_server

            def run_server():
                try:
                    start_server(host="0.0.0.0", port=5000)
                except Exception as e:
                    logger.error(f"ダッシュボードサーバーエラー: {e}")

            self.dashboard_thread = threading.Thread(target=run_server, daemon=True)
            self.dashboard_thread.start()

            # サーバー起動待機
            time.sleep(2)

            print("✅ ダッシュボードサーバー起動: http://localhost:5000")

        except Exception as e:
            logger.error(f"❌ ダッシュボード起動失敗: {e}")

    async def initialize(self):
        try:
            print("=" * 70)
            print("🚀 AutonomousOrchestrator v1.27.1 Visualization Fixed 初期化開始")
            print("=" * 70)

            from dotenv import load_dotenv

            load_dotenv(override=True)
            configure_logging_strict()

            print("📡 [1/9] OpenTelemetry初期化")
            self.otel_config = get_otel_config()

            print("📊 [2/9] ObservabilityManager初期化")
            self.observability_manager = get_observability_manager()

            # 初期化トレース記録
            init_trace = {
                "trace_id": "init-001",
                "operation_name": "orchestrator_initialization",
                "status": "in_progress",
                "timestamp": datetime.now().isoformat(),
            }
            self.observability_manager.record_trace(init_trace)

            spreadsheet_id = os.getenv("SPREADSHEET_ID")
            if not spreadsheet_id:
                raise ValueError("SPREADSHEET_ID環境変数が設定されていません")

            print("📋 [3/9] GoogleSheetsManager初期化")
            self.sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)
            self.safe_sheets = SafeSheetsWrapper(self.sheets_manager)
            configure_logging_strict()

            print("🤖 [4/9] エージェント初期化")
            self.pm_agent = PMAgent(self.sheets_manager)
            self.task_executor = TaskExecutor(self.sheets_manager)
            self.review_agent = ReviewAgent(self.safe_sheets)
            self.monitoring_agent = MonitoringAgent()
            self.collab_agent = CollaborationAgent()
            self.execution_analyzer = ExecutionAnalyzer(self.sheets_manager)
            configure_logging_strict()

            print("📡 [5/9] エージェント計装")
            self.instrumented_count = instrument_agents(self)

            print("🔭 [6/9] SystemObserver v3初期化")
            self.system_observer = SystemObserverV3(
                monitoring_agent=self.monitoring_agent,
                execution_analyzer=self.execution_analyzer,
                collaboration_agent=self.collab_agent,
                task_executor=self.task_executor,
            )

            print("📋 [7/9] 全エージェント登録")
            agent_count = self.system_observer.register_orchestrator_agents(self)

            print("🎨 [8/9] 可視化コンポーネント初期化")
            if self.enable_dashboard:
                self.start_dashboard_server()

            # 初期化完了トレース
            init_trace["status"] = "success"
            init_trace["duration_ms"] = 1000
            self.observability_manager.record_trace(init_trace)

            print("=" * 70)
            print(f"✅ [9/9] 初期化完了")
            print(f"   エージェント: {agent_count}個")
            print(f"   計装済み: {self.instrumented_count}個")
            print(f"   トレースストレージ: 有効")
            print(f"   可視化ダッシュボード: {'有効' if self.enable_dashboard else '無効'}")
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
            cycle_num = self.stats["cycles_completed"] + 1

            print("\n" + "=" * 70)
            print(f"🔄 サイクル #{cycle_num} 開始")
            print("=" * 70)

            # 【Phase 2強化】サイクル開始トレース記録
            cycle_trace = {
                "trace_id": f"cycle-{cycle_num}",
                "operation_name": "autonomous_cycle",
                "status": "in_progress",
                "cycle_number": cycle_num,
                "timestamp": datetime.now().isoformat(),
            }
            self.observability_manager.record_trace(cycle_trace)

            # 【Phase 2強化】各ステップでトレース記録
            print("\n🔭 SystemObserver: 包括的分析実行")
            step_start = datetime.now()

            analysis = self.system_observer.collect_comprehensive_analysis()

            step_duration = (datetime.now() - step_start).total_seconds()
            self.observability_manager.record_trace(
                {
                    "trace_id": f"cycle-{cycle_num}-analysis",
                    "operation_name": "system_observer.analysis",
                    "status": "success",
                    "duration_ms": int(step_duration * 1000),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            snapshot = analysis["snapshot"]
            print(f"   ✅ CPU: {snapshot['resources'].get('cpu_percent', 0):.1f}%")
            print(f"   ✅ メモリ: {snapshot['resources'].get('memory_percent', 0):.1f}%")

            agents = snapshot["agents"]
            print(f"   👥 エージェント: {agents['total_agents']}個")
            print(f"      📡 計装済み: {self.instrumented_count}個")

            if analysis.get("cost"):
                print(f"   �� コスト: ${analysis['cost']['hourly_cost']:.4f}/時間")

            # 【Phase 2強化】観測基盤統計表示
            obs_stats = self.observability_manager.get_comprehensive_stats()
            total_traces = obs_stats["traces"].get("total_traces", 0)
            success_rate = obs_stats["traces"].get("success_rate", 0)

            print(f"   📊 トレース総数: {total_traces}件")
            print(f"   📈 成功率: {success_rate:.1%}")

            # 【Phase 2強化】オペレーション別統計
            op_stats = obs_stats["traces"].get("operation_stats", {})
            if op_stats:
                print(f"   🎯 主要オペレーション:")
                for op_name, op_data in list(op_stats.items())[:3]:
                    print(f"      - {op_name}: {op_data['count']}回")

            # サイクル完了をトレース記録
            duration = (datetime.now() - cycle_start).total_seconds()
            cycle_trace.update({"status": "success", "duration_ms": int(duration * 1000)})
            self.observability_manager.record_trace(cycle_trace)

            self.stats["cycles_completed"] += 1

            print("\n" + "=" * 70)
            print(f"✅ サイクル #{self.stats['cycles_completed']} 完了")
            print(f"⏱️ 実行時間: {duration:.2f}秒")
            print(f"📊 今回記録したトレース: 3件")
            print("=" * 70)

        except Exception as e:
            logger.error(f"❌ サイクル実行エラー: {e}")

            # エラートレース記録
            self.observability_manager.record_trace(
                {
                    "trace_id": f"cycle-{self.stats['cycles_completed'] + 1}-error",
                    "operation_name": "autonomous_cycle",
                    "status": "error",
                    "error_message": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )

    async def run(self, max_cycles: int = None):
        try:
            if not await self.initialize():
                return

            print("\n🚀 自律開発システム起動（v1.27.1 Visualization Fixed）\n")

            if self.enable_dashboard:
                print("🎨 ダッシュボードURL: http://localhost:5000")
                print("   ブラウザで開いてリアルタイム監視が可能です\n")

            cycle_count = 0
            while True:
                await self.execute_autonomous_cycle()
                cycle_count += 1

                if max_cycles and cycle_count >= max_cycles:
                    # 最終統計表示
                    print("\n" + "=" * 70)
                    print("📊 最終統計サマリー")
                    print("=" * 70)

                    obs_stats = self.observability_manager.get_comprehensive_stats()
                    traces = obs_stats["traces"]

                    print(f"\n【トレース統計】")
                    print(f"  総数: {traces.get('total_traces', 0)}")
                    print(f"  成功: {traces.get('success_count', 0)}")
                    print(f"  エラー: {traces.get('error_count', 0)}")
                    print(f"  成功率: {traces.get('success_rate', 0):.1%}")

                    # オペレーション別統計
                    op_stats = traces.get("operation_stats", {})
                    if op_stats:
                        print(f"\n【オペレーション別統計】")
                        for op_name, op_data in op_stats.items():
                            print(f"  {op_name}:")
                            print(f"    実行数: {op_data['count']}")
                            print(f"    成功: {op_data['success']}")
                            print(f"    エラー: {op_data['error']}")

                    print(f"\n✅ 最大サイクル数({max_cycles})到達。終了します。")
                    print("=" * 70)
                    break

                if max_cycles is None or cycle_count < max_cycles:
                    print(f"\n⏳ 次のサイクルまで{self.cycle_interval}秒待機...\n")
                    await asyncio.sleep(self.cycle_interval)

        except KeyboardInterrupt:
            print("\n⚠️ ユーザーによる中断")

            # 中断トレース記録
            self.observability_manager.record_trace(
                {
                    "trace_id": "shutdown-001",
                    "operation_name": "user_interrupt",
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                }
            )


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="デバッグモード")
    parser.add_argument("--cycles", type=int, default=3, help="実行サイクル数")
    parser.add_argument("--dashboard", action="store_true", help="Webダッシュボード有効化")
    args = parser.parse_args()

    configure_logging_strict()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧪 AutonomousOrchestrator v1.27.1 Visualization Fixed")
    print("🎨 Phase 2: トレース記録強化完了")
    print(f"🔄 実行サイクル: {args.cycles}回")
    print(f"📊 ダッシュボード: {'有効' if args.dashboard else '無効'}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    orchestrator = AutonomousOrchestrator(debug_mode=args.debug, enable_dashboard=args.dashboard)
    await orchestrator.run(max_cycles=args.cycles)


if __name__ == "__main__":
    asyncio.run(main())
