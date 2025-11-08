"""
SystemObserver Complete - Phase 4統合完全版
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging

from agents.system_observer.analyzers.cost_analyzer import CostAnalyzer
from agents.system_observer.analyzers.performance_analyzer import \
    PerformanceAnalyzer
from agents.system_observer.analyzers.predictor import SystemPredictor
from agents.system_observer.system_observer_v2 import SystemObserverV2

logger = logging.getLogger(__name__)


class SystemObserverComplete(SystemObserverV2):
    """SystemObserver完全版 - Phase 4統合"""

    def __init__(
        self,
        monitoring_agent=None,
        execution_analyzer=None,
        collaboration_agent=None,
        task_executor=None,
    ):
        super().__init__(monitoring_agent, execution_analyzer, collaboration_agent, task_executor)

        self.performance_analyzer = PerformanceAnalyzer()
        self.cost_analyzer = CostAnalyzer()
        self.predictor = SystemPredictor()

        logger.info("✅ SystemObserver Complete Phase 4統合版 初期化完了")

    def collect_comprehensive_analysis(self) -> dict:
        """包括的な分析を実行"""
        snapshot = self.collect_system_snapshot()

        analysis = {
            "snapshot": snapshot,
            "trends": None,
            "cost": None,
            "predictions": None,
            "bottlenecks": [],
        }

        # トレンド分析
        if len(self.snapshot_history) >= 2:
            analysis["trends"] = self.performance_analyzer.analyze_trends(self.snapshot_history)

        # コスト分析
        if snapshot.get("resources"):
            analysis["cost"] = self.cost_analyzer.estimate_hourly_cost(snapshot["resources"])

        # 予測
        if len(self.snapshot_history) >= 3:
            analysis["predictions"] = self.predictor.predict_resource_usage(self.snapshot_history)

        # ボトルネック特定
        if snapshot.get("performance"):
            analysis["bottlenecks"] = self.performance_analyzer.identify_bottlenecks(
                snapshot["performance"]
            )

        return analysis


if __name__ == "__main__":
    from agents.advanced_analytics.execution_analyzer import ExecutionAnalyzer

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧪 SystemObserver Complete Phase 4統合版 テスト")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    analyzer = ExecutionAnalyzer()
    observer = SystemObserverComplete(execution_analyzer=analyzer)

    # 履歴を蓄積
    print("\n📊 スナップショット収集中...")
    for i in range(5):
        snapshot = observer.collect_system_snapshot()
        print(f"  スナップショット {i+1}/5 収集完了")

    # 包括的分析
    print("\n🔍 包括的分析実行中...")
    comprehensive = observer.collect_comprehensive_analysis()

    # 結果表示
    snapshot = comprehensive["snapshot"]
    print(f"\n✅ 基本メトリクス:")
    print(f"  CPU: {snapshot['resources'].get('cpu_percent', 0):.1f}%")
    print(f"  メモリ: {snapshot['resources'].get('memory_percent', 0):.1f}%")
    print(f"  ヘルス: {snapshot['health']}")

    if comprehensive.get("trends"):
        print(f"\n📈 トレンド:")
        trends = comprehensive["trends"]
        print(f"  CPU: {trends['cpu_trend']['trend']}")

    if comprehensive.get("cost"):
        print(f"\n💰 コスト:")
        cost = comprehensive["cost"]
        print(f"  時間あたり: ${cost['hourly_cost']:.4f}")
        print(f"  日あたり: ${cost['daily_cost']:.2f}")

    if comprehensive.get("predictions"):
        print(f"\n🔮 予測（4時間後）:")
        pred = comprehensive["predictions"]
        print(f"  CPU: {pred['predictions']['cpu']['predicted']:.1f}%")

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎉 Phase 4完全統合 テスト完了")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
