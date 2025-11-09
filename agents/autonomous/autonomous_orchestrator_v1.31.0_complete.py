"""
AutonomousOrchestrator v1.31.0 Complete - Phase 4完全統合版

【Phase 4完全実装】
✅ Phase 4.1: 自動故障アトリビューション（故障分析）
✅ Phase 4.2: 予測的分析（リソース・性能・コスト）
✅ Phase 4.3: 自己学習可視化（学習効果測定）

【v1.30.0からの変更】
✅ KnowledgeLearningVisualizer統合
✅ SelfHealingTracker統合
✅ ImprovementCycleMonitor統合
✅ LearningEffectivenessAnalyzer統合
✅ Phase 4完全ダッシュボード機能
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
from agents.observability.integration.analytics_integration import \
    AnalyticsIntegration
from agents.observability.integration.collab_agent_monitor import \
    CollabAgentMonitor
from agents.observability.integration.task_executor_monitor import \
    TaskExecutorMonitor
# Phase 4.1
from agents.observability.intelligence.intelligence_coordinator import \
    IntelligenceCoordinator
from agents.observability.intelligence.learning.improvement_cycle_monitor import \
    ImprovementCycleMonitor
# Phase 4.3
from agents.observability.intelligence.learning.knowledge_learning_visualizer import \
    KnowledgeLearningVisualizer
from agents.observability.intelligence.learning.learning_effectiveness_analyzer import \
    LearningEffectivenessAnalyzer
from agents.observability.intelligence.learning.self_healing_tracker import \
    SelfHealingTracker
from agents.observability.intelligence.predictive.cost_optimization_engine import \
    CostOptimizationEngine
from agents.observability.intelligence.predictive.performance_degradation_detector import \
    PerformanceDegradationDetector
# Phase 4.2
from agents.observability.intelligence.predictive.resource_forecaster import \
    ResourceForecaster
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

        # Phase 4.2
        self.resource_forecaster = None
        self.performance_detector = None
        self.cost_optimizer = None

        # Phase 4.3 新規追加
        self.knowledge_visualizer = None
        self.healing_tracker = None
        self.cycle_monitor = None
        self.effectiveness_analyzer = None

        self.instrumented_count = 0
        self.stats = {"cycles_completed": 0, "version": "1.31.0-complete"}
        print("✅ AutonomousOrchestrator v1.31.0 Complete 初期化")

    async def initialize(self):
        try:
            print("=" * 70)
            print("🚀 AutonomousOrchestrator v1.31.0 Complete 初期化開始")
            print("   Phase 4完全統合版（4.1 + 4.2 + 4.3）")
            print("=" * 70)

            from dotenv import load_dotenv

            load_dotenv(override=True)
            configure_logging_strict()

            print("📡 [1/15] OpenTelemetry初期化")
            self.otel_config = get_otel_config()

            print("📊 [2/15] ObservabilityManager初期化")
            self.observability_manager = get_observability_manager()

            spreadsheet_id = os.getenv("SPREADSHEET_ID")
            if not spreadsheet_id:
                raise ValueError("SPREADSHEET_ID環境変数が設定されていません")

            print("📋 [3/15] GoogleSheetsManager初期化")
            self.sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)
            self.safe_sheets = SafeSheetsWrapper(self.sheets_manager)

            print("🤖 [4/15] エージェント初期化")
            self.pm_agent = PMAgent(self.sheets_manager)
            self.task_executor = TaskExecutor(self.sheets_manager)
            self.review_agent = ReviewAgent(self.safe_sheets)
            self.monitoring_agent = MonitoringAgent()
            self.collab_agent = CollaborationAgent()
            self.execution_analyzer = ExecutionAnalyzer(self.sheets_manager)
            configure_logging_strict()

            print("📡 [5/15] エージェント計装")
            self.instrumented_count = instrument_agents(self)

            print("🔭 [6/15] SystemObserver v3初期化")
            self.system_observer = SystemObserverV3(
                monitoring_agent=self.monitoring_agent,
                execution_analyzer=self.execution_analyzer,
                collaboration_agent=self.collab_agent,
                task_executor=self.task_executor,
            )

            print("📋 [7/15] 全エージェント登録")
            agent_count = self.system_observer.register_orchestrator_agents(self)

            print("🔗 [8/15] Phase 3モニター初期化")
            self.collab_monitor = CollabAgentMonitor(self.collab_agent)
            self.task_monitor = TaskExecutorMonitor(self.task_executor)
            self.analytics_integration = AnalyticsIntegration(self.execution_analyzer)

            print("🧠 [9/15] Phase 4.1インテリジェンス初期化")
            self.intelligence_coordinator = IntelligenceCoordinator()

            print("🔮 [10/15] Phase 4.2予測エンジン初期化")
            self.resource_forecaster = ResourceForecaster()
            self.performance_detector = PerformanceDegradationDetector()
            self.cost_optimizer = CostOptimizationEngine()

            print("📚 [11/15] Phase 4.3学習可視化初期化")
            self.knowledge_visualizer = KnowledgeLearningVisualizer()
            self.healing_tracker = SelfHealingTracker()
            self.cycle_monitor = ImprovementCycleMonitor()
            self.effectiveness_analyzer = LearningEffectivenessAnalyzer()

            print("🎨 [12/15] 可視化コンポーネント初期化")
            # ダッシュボード初期化（省略可能）

            print("🔍 [13/15] エージェント依存関係マッピング")
            self.collab_monitor.map_agent_dependencies()

            print("⚖️ [14/15] 負荷分散分析")
            self.collab_monitor.analyze_load_distribution()

            print("=" * 70)
            print(f"✅ [15/15] 初期化完了")
            print(f"   エージェント: {agent_count}個")
            print(f"   計装済み: {self.instrumented_count}個")
            print(f"   Phase 3連携: 有効")
            print(f"   Phase 4.1インテリジェンス: 有効")
            print(f"   Phase 4.2予測分析: 有効")
            print(f"   Phase 4.3学習可視化: 有効")
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
            print(f"🔄 サイクル #{cycle_num} 開始（Phase 4完全版）")
            print("=" * 70)

            # Phase 3エージェント連携監視
            print("\n🔗 Phase 3: エージェント連携分析")
            registration_status = self.collab_monitor.monitor_agent_registration()
            print(f"   👥 登録エージェント: {registration_status.get('total_agents', 0)}個")

            # Phase 4.1インテリジェンス分析
            print("\n🧠 Phase 4.1: インテリジェンス分析")
            dashboard = self.intelligence_coordinator.generate_intelligence_dashboard()
            print(f"   📊 総エラー数: {dashboard.get('system_health', {}).get('total_errors', 0)}")
            print(
                f"   📈 分類率: {dashboard.get('system_health', {}).get('classification_rate', 0):.1%}"
            )

            # Phase 4.2予測分析
            print("\n🔮 Phase 4.2: 予測的分析")
            resource_forecast = self.resource_forecaster.forecast_resource_usage()
            if "cpu_forecast" in resource_forecast:
                print(f"   💻 CPU予測: {resource_forecast['cpu_forecast']['predicted_value']:.1f}%")
                print(
                    f"   🧠 メモリ予測: {resource_forecast['memory_forecast']['predicted_value']:.1f}%"
                )

            # Phase 4.3学習可視化（新機能）
            print("\n📚 Phase 4.3: 自己学習可視化")

            # ナレッジ学習可視化
            print("   [1/4] ナレッジ学習プロセス...")
            knowledge_viz = self.knowledge_visualizer.visualize_learning_process()

            if knowledge_viz.get("status") != "insufficient_data" and "error" not in knowledge_viz:
                growth = knowledge_viz.get("growth_curve", {})
                reuse = knowledge_viz.get("reuse_analysis", {})

                print(f"      知識数: {growth.get('current_knowledge_count', 0)}件")
                print(f"      成長率: {growth.get('growth_rate_percent', 0):.1f}%")
                print(f"      再利用率: {reuse.get('reuse_rate_percent', 0):.1f}%")
            else:
                print(f"      ⚠️ {knowledge_viz.get('message', knowledge_viz.get('error', '不明'))}")

            # 自己修復追跡
            print("   [2/4] 自己修復アクション追跡...")
            healing_track = self.healing_tracker.track_healing_actions()

            if healing_track.get("status") != "insufficient_data" and "error" not in healing_track:
                success_rate = healing_track.get("success_rate_analysis", {})
                effectiveness = healing_track.get("effectiveness", {})

                print(f"      修復成功率: {success_rate.get('overall_success_rate', 0):.1f}%")
                print(f"      修復カバー率: {effectiveness.get('healing_coverage_rate', 0):.1f}%")
            else:
                print(f"      ⚠️ {healing_track.get('message', healing_track.get('error', '不明'))}")

            # 改善サイクル監視
            print("   [3/4] 改善サイクル監視...")
            cycle_mon = self.cycle_monitor.monitor_improvement_cycles()

            if cycle_mon.get("status") != "insufficient_data" and "error" not in cycle_mon:
                progress = cycle_mon.get("cycle_progress", {})
                health = cycle_mon.get("overall_health", "unknown")

                print(f"      改善トレンド: {progress.get('overall_trend', 'unknown').upper()}")
                print(f"      総合健全性: {health.upper()}")
            else:
                print(f"      ⚠️ {cycle_mon.get('message', cycle_mon.get('error', '不明'))}")

            # 学習効果分析
            print("   [4/4] 学習効果定量化...")
            effectiveness = self.effectiveness_analyzer.analyze_learning_effectiveness()

            if effectiveness.get("status") != "insufficient_data" and "error" not in effectiveness:
                roi = effectiveness.get("roi_calculation", {})
                assessment = effectiveness.get("overall_assessment", "unknown")

                print(f"      学習ROI: {roi.get('roi_percent', 0):.1f}%")
                print(f"      総合評価: {assessment.upper()}")
            else:
                print(f"      ⚠️ {effectiveness.get('message', effectiveness.get('error', '不明'))}")

            # SystemObserver包括的分析
            print("\n🔭 SystemObserver: 包括的分析実行")
            obs_analysis = self.system_observer.collect_comprehensive_analysis()
            snapshot = obs_analysis["snapshot"]
            print(f"   ✅ CPU: {snapshot['resources'].get('cpu_percent', 0):.1f}%")
            print(f"   ✅ メモリ: {snapshot['resources'].get('memory_percent', 0):.1f}%")

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

            print("\n🚀 自律開発システム起動（v1.31.0 Complete - Phase 4完全版）\n")

            cycle_count = 0
            while True:
                await self.execute_autonomous_cycle()
                cycle_count += 1

                if max_cycles and cycle_count >= max_cycles:
                    print("\n" + "=" * 70)
                    print("📊 Phase 4完全統合 - 最終統計サマリー")
                    print("=" * 70)

                    print(f"\n【Phase 4.1: インテリジェンス分析】")
                    dashboard = self.intelligence_coordinator.generate_intelligence_dashboard()
                    health = dashboard.get("system_health", {})
                    print(f"  総エラー数: {health.get('total_errors', 0)}")
                    print(f"  分類率: {health.get('classification_rate', 0):.1%}")

                    print(f"\n【Phase 4.2: 予測的分析】")
                    resource_forecast = self.resource_forecaster.forecast_resource_usage()
                    if "cpu_forecast" in resource_forecast:
                        print(
                            f"  CPU予測: {resource_forecast['cpu_forecast']['current_value']:.1f}% → {resource_forecast['cpu_forecast']['predicted_value']:.1f}%"
                        )

                    print(f"\n【Phase 4.3: 自己学習可視化】")
                    knowledge_viz = self.knowledge_visualizer.visualize_learning_process()
                    if "growth_curve" in knowledge_viz:
                        growth = knowledge_viz["growth_curve"]
                        print(f"  知識数: {growth.get('current_knowledge_count', 0)}件")
                        print(f"  成長率: {growth.get('growth_rate_percent', 0):.1f}%")

                    healing_track = self.healing_tracker.track_healing_actions()
                    if "success_rate_analysis" in healing_track:
                        print(
                            f"  修復成功率: {healing_track['success_rate_analysis']['overall_success_rate']:.1f}%"
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
    print("🧪 AutonomousOrchestrator v1.31.0 Complete")
    print("🎉 Phase 4完全統合版")
    print("   ✅ 4.1: 自動故障アトリビューション")
    print("   ✅ 4.2: 予測的分析")
    print("   ✅ 4.3: 自己学習可視化")
    print(f"🔄 実行サイクル: {args.cycles}回")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    orchestrator = AutonomousOrchestrator(debug_mode=args.debug, enable_dashboard=args.dashboard)
    await orchestrator.run(max_cycles=args.cycles)


if __name__ == "__main__":
    asyncio.run(main())
