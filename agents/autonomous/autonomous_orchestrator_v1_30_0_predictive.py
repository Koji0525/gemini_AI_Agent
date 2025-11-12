"""
AutonomousOrchestrator v1.30.0 Predictive - Phase 4.2統合版

【v1.29.0からの変更】
✅ Phase 4.2: 予測的分析機能完全統合
✅ ResourceForecaster統合（リソース予測）
✅ PerformanceDegradationDetector統合（性能劣化検知）
✅ CostOptimizationEngine統合（コスト最適化）
✅ 予測ダッシュボード機能追加
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
from agents.observability.integration.analytics_integration import AnalyticsIntegration
from agents.observability.integration.collab_agent_monitor import CollabAgentMonitor
from agents.observability.integration.task_executor_monitor import TaskExecutorMonitor
from agents.observability.intelligence.intelligence_coordinator import IntelligenceCoordinator
from agents.observability.intelligence.predictive.cost_optimization_engine import (
    CostOptimizationEngine,
)
from agents.observability.intelligence.predictive.performance_degradation_detector import (
    PerformanceDegradationDetector,
)
from agents.observability.intelligence.predictive.resource_forecaster import ResourceForecaster
from agents.observability.observability_manager import get_observability_manager
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

        # Phase 3
        self.collab_monitor = None
        self.task_monitor = None
        self.analytics_integration = None

        # Phase 4.1
        self.intelligence_coordinator = None

        # Phase 4.2 新規追加
        self.resource_forecaster = None
        self.performance_detector = None
        self.cost_optimizer = None

        self.instrumented_count = 0
        self.stats = {"cycles_completed": 0, "version": "1.30.0-predictive"}
        print("✅ AutonomousOrchestrator v1.30.0 Predictive 初期化")

    async def initialize(self):
        try:
            print("=" * 70)
            print("🚀 AutonomousOrchestrator v1.30.0 Predictive 初期化開始")
            print("=" * 70)

            from dotenv import load_dotenv

            load_dotenv(override=True)
            configure_logging_strict()

            print("📡 [1/14] OpenTelemetry初期化")
            self.otel_config = get_otel_config()

            print("📊 [2/14] ObservabilityManager初期化")
            self.observability_manager = get_observability_manager()

            spreadsheet_id = os.getenv("SPREADSHEET_ID")
            if not spreadsheet_id:
                raise ValueError("SPREADSHEET_ID環境変数が設定されていません")

            print("📋 [3/14] GoogleSheetsManager初期化")
            self.sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)
            self.safe_sheets = SafeSheetsWrapper(self.sheets_manager)

            print("🤖 [4/14] エージェント初期化")
            self.pm_agent = PMAgent(self.sheets_manager)
            self.task_executor = TaskExecutor(self.sheets_manager)
            self.review_agent = ReviewAgent(self.safe_sheets)
            self.monitoring_agent = MonitoringAgent()
            self.collab_agent = CollaborationAgent()
            self.execution_analyzer = ExecutionAnalyzer(self.sheets_manager)
            configure_logging_strict()

            print("📡 [5/14] エージェント計装")
            self.instrumented_count = instrument_agents(self)

            print("🔭 [6/14] SystemObserver v3初期化")
            self.system_observer = SystemObserverV3(
                monitoring_agent=self.monitoring_agent,
                execution_analyzer=self.execution_analyzer,
                collaboration_agent=self.collab_agent,
                task_executor=self.task_executor,
            )

            print("📋 [7/14] 全エージェント登録")
            agent_count = self.system_observer.register_orchestrator_agents(self)

            print("🔗 [8/14] Phase 3モニター初期化")
            self.collab_monitor = CollabAgentMonitor(self.collab_agent)
            self.task_monitor = TaskExecutorMonitor(self.task_executor)
            self.analytics_integration = AnalyticsIntegration(self.execution_analyzer)

            print("🧠 [9/14] Phase 4.1インテリジェンス初期化")
            self.intelligence_coordinator = IntelligenceCoordinator()

            print("🔮 [10/14] Phase 4.2予測エンジン初期化")
            self.resource_forecaster = ResourceForecaster()
            self.performance_detector = PerformanceDegradationDetector()
            self.cost_optimizer = CostOptimizationEngine()

            print("🎨 [11/14] 可視化コンポーネント初期化")
            # ダッシュボード初期化（省略可能）

            print("🔍 [12/14] エージェント依存関係マッピング")
            self.collab_monitor.map_agent_dependencies()

            print("⚖️ [13/14] 負荷分散分析")
            self.collab_monitor.analyze_load_distribution()

            print("=" * 70)
            print(f"✅ [14/14] 初期化完了")
            print(f"   エージェント: {agent_count}個")
            print(f"   計装済み: {self.instrumented_count}個")
            print(f"   Phase 3連携: 有効")
            print(f"   Phase 4.1インテリジェンス: 有効")
            print(f"   Phase 4.2予測分析: 有効")
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

            # Phase 3エージェント連携監視
            print("\n🔗 Phase 3: エージェント連携分析")
            registration_status = self.collab_monitor.monitor_agent_registration()
            print(f"   👥 登録エージェント: {registration_status.get('total_agents', 0)}個")

            task_details = self.task_monitor.measure_execution_details(f"task-cycle-{cycle_num}")
            print(f"   ⏱️ タスク実行時間: {task_details.get('total_duration_ms', 0)}ms")

            # Phase 4.1インテリジェンス分析
            print("\n🧠 Phase 4.1: インテリジェンス分析")
            dashboard = self.intelligence_coordinator.generate_intelligence_dashboard()
            print(f"   📊 総エラー数: {dashboard.get('system_health', {}).get('total_errors', 0)}")
            print(
                f"   📈 分類率: {dashboard.get('system_health', {}).get('classification_rate', 0):.1%}"
            )

            # Phase 4.2予測分析（新機能）
            print("\n🔮 Phase 4.2: 予測的分析")

            # リソース予測
            print("   [1/3] リソース使用率予測...")
            resource_forecast = self.resource_forecaster.forecast_resource_usage()

            if resource_forecast.get("status") != "no_data" and "error" not in resource_forecast:
                cpu_pred = resource_forecast.get("cpu_forecast", {}).get("predicted_value", 0)
                mem_pred = resource_forecast.get("memory_forecast", {}).get("predicted_value", 0)
                risk = resource_forecast.get("overall_risk_level", "low")

                print(f"      CPU予測: {cpu_pred:.1f}%（6時間後）")
                print(f"      メモリ予測: {mem_pred:.1f}%（6時間後）")
                print(f"      リスクレベル: {risk.upper()}")

                warnings = resource_forecast.get("warnings", [])
                if warnings:
                    print(f"      ⚠️ 警告: {len(warnings)}件")
            else:
                print(
                    f"      ⚠️ {resource_forecast.get('message', resource_forecast.get('error', '不明'))}"
                )

            # 性能劣化検知
            print("   [2/3] 性能劣化検知...")
            perf_detect = self.performance_detector.detect_performance_degradation()

            if perf_detect.get("status") != "insufficient_data" and "error" not in perf_detect:
                health = perf_detect.get("overall_health", "healthy")
                degradations = perf_detect.get("degradations_detected", [])

                print(f"      システム健全性: {health.upper()}")
                if degradations:
                    print(f"      ⚠️ 劣化検出: {len(degradations)}件")
                    for deg in degradations[:2]:
                        print(f"         - [{deg.get('severity').upper()}] {deg.get('message')}")
            else:
                print(f"      ⚠️ {perf_detect.get('message', perf_detect.get('error', '不明'))}")

            # コスト最適化
            print("   [3/3] コスト最適化分析...")
            cost_opt = self.cost_optimizer.analyze_cost_optimization()

            if cost_opt.get("status") != "insufficient_data" and "error" not in cost_opt:
                total_savings = cost_opt.get("total_potential_savings", 0)
                opportunities = cost_opt.get("optimization_opportunities", [])

                print(f"      潜在的節約額: ${total_savings:.2f}")
                print(f"      最適化機会: {len(opportunities)}件")

                top_actions = cost_opt.get("prioritized_actions", [])[:2]
                if top_actions:
                    print(f"      優先アクション:")
                    for action in top_actions:
                        print(
                            f"         {action.get('rank')}. {action.get('action')} (節約: {action.get('savings')})"
                        )
            else:
                print(f"      ⚠️ {cost_opt.get('message', cost_opt.get('error', '不明'))}")

            # SystemObserver包括的分析
            print("\n🔭 SystemObserver: 包括的分析実行")
            obs_analysis = self.system_observer.collect_comprehensive_analysis()
            snapshot = obs_analysis["snapshot"]
            print(f"   ✅ CPU: {snapshot['resources'].get('cpu_percent', 0):.1f}%")
            print(f"   ✅ メモリ: {snapshot['resources'].get('memory_percent', 0):.1f}%")

            obs_stats = self.observability_manager.get_comprehensive_stats()
            total_traces = obs_stats["traces"].get("total_traces", 0)
            success_rate = obs_stats["traces"].get("success_rate", 0)
            print(f"   📊 トレース総数: {total_traces}件")
            print(f"   📈 成功率: {success_rate:.1%}")

            self.stats["cycles_completed"] += 1
            duration = (datetime.now() - cycle_start).total_seconds()

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

            print("\n🚀 自律開発システム起動（v1.30.0 Predictive）\n")

            cycle_count = 0
            while True:
                await self.execute_autonomous_cycle()
                cycle_count += 1

                if max_cycles and cycle_count >= max_cycles:
                    print("\n" + "=" * 70)
                    print("📊 Phase 4.2最終統計サマリー")
                    print("=" * 70)

                    # 最終予測ダッシュボード
                    print(f"\n【リソース予測】")
                    resource_forecast = self.resource_forecaster.forecast_resource_usage()
                    if "cpu_forecast" in resource_forecast:
                        print(
                            f"  CPU: {resource_forecast['cpu_forecast']['current_value']:.1f}% → {resource_forecast['cpu_forecast']['predicted_value']:.1f}%"
                        )
                        print(
                            f"  メモリ: {resource_forecast['memory_forecast']['current_value']:.1f}% → {resource_forecast['memory_forecast']['predicted_value']:.1f}%"
                        )

                    print(f"\n【性能劣化】")
                    perf_detect = self.performance_detector.detect_performance_degradation()
                    if "overall_health" in perf_detect:
                        print(f"  健全性: {perf_detect['overall_health'].upper()}")
                        print(f"  劣化検出: {len(perf_detect.get('degradations_detected', []))}件")

                    print(f"\n【コスト最適化】")
                    cost_opt = self.cost_optimizer.analyze_cost_optimization()
                    if "total_potential_savings" in cost_opt:
                        print(f"  潜在的節約: ${cost_opt['total_potential_savings']:.2f}")
                        print(
                            f"  最適化機会: {len(cost_opt.get('optimization_opportunities', []))}件"
                        )

                    print(f"\n✅ 最大サイクル数({max_cycles})到達。終了します。")
                    print("=" * 70)
                    break

                if max_cycles is None or cycle_count < max_cycles:
                    print(f"\n⏳ 次のサイクルまで{self.cycle_interval}秒待機...\n")
                    await asyncio.sleep(self.cycle_interval)

        except KeyboardInterrupt:
            print("\n⚠️ ユーザーによる中断")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="デバッグモード")
    parser.add_argument("--cycles", type=int, default=3, help="実行サイクル数")
    parser.add_argument("--dashboard", action="store_true", help="Webダッシュボード有効化")
    args = parser.parse_args()

    configure_logging_strict()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧪 AutonomousOrchestrator v1.30.0 Predictive")
    print("🔮 Phase 4.2: 予測的分析完了")
    print(f"🔄 実行サイクル: {args.cycles}回")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    orchestrator = AutonomousOrchestrator(debug_mode=args.debug, enable_dashboard=args.dashboard)
    await orchestrator.run(max_cycles=args.cycles)


if __name__ == "__main__":
    asyncio.run(main())
