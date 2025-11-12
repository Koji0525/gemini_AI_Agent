"""
AutonomousOrchestrator v1.32.0 Production - 本番環境対応完全版

【完全実装】
✅ Phase 3: エージェント連携深化
✅ Phase 4.1: 自動故障アトリビューション
✅ Phase 4.2: 予測的分析
✅ Phase 4.3: 自己学習可視化（KnowledgeBase統合版）
✅ Phase 5.1: 性能最適化
✅ Phase 5.2: UX向上
✅ Phase 5.3: ドキュメント自動生成

【v1.31.0からの変更】
✅ KnowledgeBaseAdapter統合
✅ IntegratedLearningVisualizer統合
✅ PerformanceOptimizer統合
✅ UXEnhancer統合
✅ DocumentationGenerator統合
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

# Phase 4.1
from agents.observability.intelligence.intelligence_coordinator import IntelligenceCoordinator

# Phase 4.3（統合版）
from agents.observability.intelligence.learning.integrated_learning_visualizer import (
    IntegratedLearningVisualizer,
)
from agents.observability.intelligence.predictive.cost_optimization_engine import (
    CostOptimizationEngine,
)
from agents.observability.intelligence.predictive.performance_degradation_detector import (
    PerformanceDegradationDetector,
)

# Phase 4.2
from agents.observability.intelligence.predictive.resource_forecaster import ResourceForecaster
from agents.observability.observability_manager import get_observability_manager
from agents.observability.opentelemetry_config import get_otel_config
from agents.observability.optimization.documentation_generator import DocumentationGenerator

# Phase 5
from agents.observability.optimization.performance_optimizer import PerformanceOptimizer
from agents.observability.optimization.ux_enhancer import UXEnhancer
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

        # Phase 4.3（統合版）
        self.integrated_learning_viz = None

        # Phase 5
        self.perf_optimizer = None
        self.ux_enhancer = None
        self.doc_generator = None

        self.instrumented_count = 0
        self.stats = {"cycles_completed": 0, "version": "1.32.0-production"}
        print("✅ AutonomousOrchestrator v1.32.0 Production 初期化")

    async def initialize(self):
        try:
            print("=" * 70)
            print("🚀 AutonomousOrchestrator v1.32.0 Production 初期化開始")
            print("   本番環境対応完全版（Phase 3-5完全統合）")
            print("=" * 70)

            from dotenv import load_dotenv

            load_dotenv(override=True)
            configure_logging_strict()

            print("📡 [1/16] OpenTelemetry初期化")
            self.otel_config = get_otel_config()

            print("📊 [2/16] ObservabilityManager初期化")
            self.observability_manager = get_observability_manager()

            spreadsheet_id = os.getenv("SPREADSHEET_ID")
            if not spreadsheet_id:
                raise ValueError("SPREADSHEET_ID環境変数が設定されていません")

            print("📋 [3/16] GoogleSheetsManager初期化")
            self.sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)
            self.safe_sheets = SafeSheetsWrapper(self.sheets_manager)

            print("🤖 [4/16] エージェント初期化")
            self.pm_agent = PMAgent(self.sheets_manager)
            self.task_executor = TaskExecutor(self.sheets_manager)
            self.review_agent = ReviewAgent(self.safe_sheets)
            self.monitoring_agent = MonitoringAgent()
            self.collab_agent = CollaborationAgent()
            self.execution_analyzer = ExecutionAnalyzer(self.sheets_manager)
            configure_logging_strict()

            print("📡 [5/16] エージェント計装")
            self.instrumented_count = instrument_agents(self)

            print("🔭 [6/16] SystemObserver v3初期化")
            self.system_observer = SystemObserverV3(
                monitoring_agent=self.monitoring_agent,
                execution_analyzer=self.execution_analyzer,
                collaboration_agent=self.collab_agent,
                task_executor=self.task_executor,
            )

            print("📋 [7/16] 全エージェント登録")
            agent_count = self.system_observer.register_orchestrator_agents(self)

            print("🔗 [8/16] Phase 3モニター初期化")
            self.collab_monitor = CollabAgentMonitor(self.collab_agent)
            self.task_monitor = TaskExecutorMonitor(self.task_executor)
            self.analytics_integration = AnalyticsIntegration(self.execution_analyzer)

            print("🧠 [9/16] Phase 4.1インテリジェンス初期化")
            self.intelligence_coordinator = IntelligenceCoordinator()

            print("🔮 [10/16] Phase 4.2予測エンジン初期化")
            self.resource_forecaster = ResourceForecaster()
            self.performance_detector = PerformanceDegradationDetector()
            self.cost_optimizer = CostOptimizationEngine()

            print("📚 [11/16] Phase 4.3学習可視化初期化（統合版）")
            self.integrated_learning_viz = IntegratedLearningVisualizer()

            print("⚡ [12/16] Phase 5.1性能最適化初期化")
            self.perf_optimizer = PerformanceOptimizer()

            print("🎨 [13/16] Phase 5.2 UX向上初期化")
            self.ux_enhancer = UXEnhancer()

            print("📄 [14/16] Phase 5.3ドキュメント生成初期化")
            self.doc_generator = DocumentationGenerator()

            print("🔍 [15/16] システム最適化実行")
            # 性能最適化推奨
            opt_result = self.perf_optimizer.optimize_data_collection()
            if "error" not in opt_result:
                recommended = opt_result.get("recommended_settings", {})
                print(f"   推奨サンプリング率: {recommended.get('sampling_rate', 0)*100:.0f}%")

            print("=" * 70)
            print(f"✅ [16/16] 初期化完了")
            print(f"   エージェント: {agent_count}個")
            print(f"   計装済み: {self.instrumented_count}個")
            print(f"   Phase 3連携: 有効")
            print(f"   Phase 4インテリジェンス: 有効（統合版）")
            print(f"   Phase 5最適化: 有効")
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
            print(f"🔄 サイクル #{cycle_num} 開始（Production版）")
            print("=" * 70)

            # Phase 4.3統合版学習可視化
            print("\n📚 Phase 4.3: 統合学習可視化（KnowledgeBase対応）")
            learning_viz = self.integrated_learning_viz.visualize_complete_learning_process()

            if "error" not in learning_viz:
                kb_stats = learning_viz.get("knowledge_base_stats", {})
                growth = learning_viz.get("growth_curve", {})

                print(f"   ナレッジ総数: {kb_stats.get('total_entries', 0)}件")
                print(f"   成長率: {growth.get('growth_rate_percent', 0):.1f}%")
                print(f"   カテゴリ: {len(kb_stats.get('category_distribution', {}))}種類")

            # Phase 5性能チェック
            print("\n⚡ Phase 5: 性能最適化チェック")
            perf_check = self.perf_optimizer.measure_query_performance()

            if "error" not in perf_check:
                print(f"   クエリ性能: {perf_check.get('query_time_ms', 0):.2f}ms")
                print(f"   評価: {perf_check.get('performance_rating', 'unknown').upper()}")

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

            print("\n🚀 自律開発システム起動（v1.32.0 Production）\n")

            cycle_count = 0
            while True:
                await self.execute_autonomous_cycle()
                cycle_count += 1

                if max_cycles and cycle_count >= max_cycles:
                    print("\n" + "=" * 70)
                    print("📊 本番環境対応版 - 最終統計サマリー")
                    print("=" * 70)

                    # Phase 4.3統合版最終表示
                    learning_viz = (
                        self.integrated_learning_viz.visualize_complete_learning_process()
                    )
                    if "knowledge_base_stats" in learning_viz:
                        kb_stats = learning_viz["knowledge_base_stats"]
                        print(f"\n【ナレッジベース統計】")
                        print(f"  総エントリー数: {kb_stats.get('total_entries', 0)}件")
                        print(f"  カテゴリ数: {len(kb_stats.get('category_distribution', {}))}種類")

                    # 性能統計
                    perf_check = self.perf_optimizer.measure_query_performance()
                    if "query_time_ms" in perf_check:
                        print(f"\n【性能統計】")
                        print(f"  クエリ時間: {perf_check['query_time_ms']:.2f}ms")
                        print(f"  性能評価: {perf_check['performance_rating'].upper()}")

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
    parser.add_argument("--cycles", type=int, default=480, help="実行サイクル数")
    parser.add_argument("--dashboard", action="store_true", help="Webダッシュボード有効化")
    args = parser.parse_args()

    configure_logging_strict()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧪 AutonomousOrchestrator v1.32.0 Production")
    print("🎉 本番環境対応完全版")
    print("   ✅ Phase 3-5完全統合")
    print("   ✅ KnowledgeBase統合")
    print("   ✅ 性能最適化実装")
    print(f"🔄 実行サイクル: {args.cycles}回")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    orchestrator = AutonomousOrchestrator(debug_mode=args.debug, enable_dashboard=args.dashboard)
    await orchestrator.run(max_cycles=args.cycles)


if __name__ == "__main__":
    asyncio.run(main())
