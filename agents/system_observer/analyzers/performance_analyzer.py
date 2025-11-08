"""
PerformanceAnalyzer - パフォーマンス分析エージェント

【Phase 4.1: パフォーマンス分析ダッシュボード】
既存エージェントのデータを観測し、分析結果を提供
※既存エージェントは一切変更しない（オブザーバーパターン）
"""

import logging
import statistics
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """パフォーマンス分析エージェント"""

    def __init__(self):
        self.analysis_history = []
        logger.info("✅ PerformanceAnalyzer初期化完了")

    def analyze_trends(self, snapshots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """スナップショット履歴からトレンド分析"""
        if len(snapshots) < 2:
            return {"status": "insufficient_data"}

        try:
            # CPU使用率のトレンド
            cpu_values = [
                s.get("resources", {}).get("cpu_percent", 0)
                for s in snapshots
                if isinstance(s.get("resources", {}).get("cpu_percent"), (int, float))
            ]

            # メモリ使用率のトレンド
            memory_values = [
                s.get("resources", {}).get("memory_percent", 0)
                for s in snapshots
                if isinstance(s.get("resources", {}).get("memory_percent"), (int, float))
            ]

            # 成功率のトレンド
            success_rates = [
                s.get("performance", {}).get("overall_success_rate", 0)
                for s in snapshots
                if isinstance(s.get("performance", {}).get("overall_success_rate"), (int, float))
            ]

            def calculate_trend(values: List[float]) -> str:
                """トレンドを計算"""
                if len(values) < 2:
                    return "stable"

                recent = statistics.mean(values[-3:]) if len(values) >= 3 else values[-1]
                past = statistics.mean(values[:3]) if len(values) >= 3 else values[0]

                change_rate = (recent - past) / past if past != 0 else 0

                if abs(change_rate) < 0.05:
                    return "stable"
                elif change_rate > 0:
                    return "increasing"
                else:
                    return "decreasing"

            return {
                "cpu_trend": {
                    "current": cpu_values[-1] if cpu_values else 0,
                    "average": statistics.mean(cpu_values) if cpu_values else 0,
                    "trend": calculate_trend(cpu_values),
                },
                "memory_trend": {
                    "current": memory_values[-1] if memory_values else 0,
                    "average": statistics.mean(memory_values) if memory_values else 0,
                    "trend": calculate_trend(memory_values),
                },
                "success_rate_trend": {
                    "current": success_rates[-1] if success_rates else 0,
                    "average": statistics.mean(success_rates) if success_rates else 0,
                    "trend": (
                        "improving"
                        if calculate_trend(success_rates) == "increasing"
                        else (
                            "degrading"
                            if calculate_trend(success_rates) == "decreasing"
                            else "stable"
                        )
                    ),
                },
            }

        except Exception as e:
            logger.error(f"❌ トレンド分析エラー: {e}")
            return {"status": "error", "error": str(e)}

    def identify_bottlenecks(self, performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """ボトルネックを特定"""
        bottlenecks = []

        try:
            # エージェント別の成功率をチェック
            by_agent = performance_data.get("by_agent", {})
            for agent_id, stats in by_agent.items():
                success_rate = stats.get("success_rate", 1.0)
                if success_rate < 0.8:
                    bottlenecks.append(
                        {
                            "type": "agent_performance",
                            "agent_id": agent_id,
                            "success_rate": success_rate,
                            "severity": "high" if success_rate < 0.6 else "medium",
                            "recommendation": f"{agent_id}の成功率が低い。エラーログを確認してください。",
                        }
                    )

            # 応答時間をチェック
            avg_response_time = performance_data.get("average_response_time", 0)
            if avg_response_time > 5.0:
                bottlenecks.append(
                    {
                        "type": "response_time",
                        "value": avg_response_time,
                        "severity": "high" if avg_response_time > 10.0 else "medium",
                        "recommendation": "応答時間が長い。処理の最適化を検討してください。",
                    }
                )

            return bottlenecks

        except Exception as e:
            logger.error(f"❌ ボトルネック特定エラー: {e}")
            return []


if __name__ == "__main__":
    print("🧪 PerformanceAnalyzer テスト")

    analyzer = PerformanceAnalyzer()

    snapshots = [
        {
            "resources": {"cpu_percent": 45.0, "memory_percent": 60.0},
            "performance": {"overall_success_rate": 0.95},
        },
        {
            "resources": {"cpu_percent": 50.0, "memory_percent": 62.0},
            "performance": {"overall_success_rate": 0.93},
        },
        {
            "resources": {"cpu_percent": 48.0, "memory_percent": 61.0},
            "performance": {"overall_success_rate": 0.94},
        },
    ]

    trends = analyzer.analyze_trends(snapshots)
    print(f"\n📈 トレンド分析:")
    print(
        f"  CPU: {trends['cpu_trend']['current']:.1f}% (トレンド: {trends['cpu_trend']['trend']})"
    )
    print(
        f"  成功率: {trends['success_rate_trend']['current']:.1%} (トレンド: {trends['success_rate_trend']['trend']})"
    )
    print("\n✅ テスト完了")
