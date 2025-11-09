"""
PerformanceDegradationDetector - 性能劣化早期検知システム

【機能】
- 応答時間の異常検知（統計的手法）
- スループット低下の検出
- エラー率上昇の監視
- 性能ベースライン自動学習
"""

import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.observability.observability_manager import \
    get_observability_manager


class PerformanceDegradationDetector:
    """性能劣化早期検知システム"""

    def __init__(self):
        self.obs_manager = get_observability_manager()

        # 劣化検知パラメータ
        self.response_time_threshold_multiplier = 2.0  # ベースラインの2倍
        self.error_rate_threshold = 0.05  # 5%
        self.throughput_drop_threshold = 0.3  # 30%低下

        print("✅ PerformanceDegradationDetector初期化完了")

    def detect_performance_degradation(self) -> Dict[str, Any]:
        """
        性能劣化の検知

        Returns:
            劣化検知結果
        """
        try:
            # トレースデータ取得
            all_traces = self.obs_manager.search_traces(limit=500)

            if len(all_traces) < 10:
                return {
                    "status": "insufficient_data",
                    "message": "性能分析に必要なデータが不足しています",
                }

            # ベースライン計算（過去のデータ）
            baseline = self._calculate_baseline(all_traces[:400])

            # 最近のパフォーマンス計算
            recent_performance = self._calculate_recent_performance(all_traces[-100:])

            # 劣化検知
            degradations = self._detect_degradations(baseline, recent_performance)

            # アラート生成
            alerts = self._generate_performance_alerts(degradations)

            result = {
                "detection_id": f"perf-detect-{datetime.now().timestamp()}",
                "detection_timestamp": datetime.now().isoformat(),
                "baseline": baseline,
                "recent_performance": recent_performance,
                "degradations_detected": degradations,
                "performance_alerts": alerts,
                "overall_health": self._calculate_overall_health(degradations),
                "recommended_actions": self._generate_performance_recommendations(degradations),
            }

            # トレース記録
            self.obs_manager.record_trace(
                {
                    "trace_id": result["detection_id"],
                    "operation_name": "predictive.performance_degradation_detection",
                    "status": "success",
                    "degradations_count": len(degradations),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return result

        except Exception as e:
            return {"error": str(e)}

    def _calculate_baseline(self, historical_traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ベースライン性能の計算"""

        if not historical_traces:
            return {}

        # 応答時間の統計
        durations = [t.get("duration_ms", 0) for t in historical_traces if "duration_ms" in t]

        # エラー率
        total_traces = len(historical_traces)
        error_traces = len([t for t in historical_traces if t.get("status") == "error"])
        error_rate = error_traces / total_traces if total_traces > 0 else 0

        # スループット（トレース数/時間）
        if historical_traces:
            first_time = datetime.fromisoformat(
                historical_traces[0].get("timestamp", datetime.now().isoformat())
            )
            last_time = datetime.fromisoformat(
                historical_traces[-1].get("timestamp", datetime.now().isoformat())
            )
            time_span_hours = max((last_time - first_time).total_seconds() / 3600, 0.1)
            throughput = total_traces / time_span_hours
        else:
            throughput = 0

        baseline = {
            "avg_response_time_ms": round(statistics.mean(durations), 2) if durations else 0,
            "median_response_time_ms": round(statistics.median(durations), 2) if durations else 0,
            "p95_response_time_ms": round(self._percentile(durations, 95), 2) if durations else 0,
            "error_rate": round(error_rate, 4),
            "throughput_per_hour": round(throughput, 2),
            "sample_size": len(historical_traces),
        }

        return baseline

    def _calculate_recent_performance(self, recent_traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """最近の性能計算"""

        # ベースライン計算と同じロジック
        return self._calculate_baseline(recent_traces)

    def _detect_degradations(
        self, baseline: Dict[str, Any], recent: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """劣化の検出"""

        degradations = []

        if not baseline or not recent:
            return degradations

        # 応答時間劣化
        baseline_avg = baseline.get("avg_response_time_ms", 0)
        recent_avg = recent.get("avg_response_time_ms", 0)

        if baseline_avg > 0 and recent_avg > baseline_avg * self.response_time_threshold_multiplier:
            degradations.append(
                {
                    "type": "response_time",
                    "severity": "high",
                    "message": f"応答時間が{recent_avg / baseline_avg:.1f}倍に増加",
                    "baseline_value": f"{baseline_avg:.2f}ms",
                    "current_value": f"{recent_avg:.2f}ms",
                }
            )

        # エラー率上昇
        baseline_error = baseline.get("error_rate", 0)
        recent_error = recent.get("error_rate", 0)

        if recent_error > self.error_rate_threshold:
            degradations.append(
                {
                    "type": "error_rate",
                    "severity": "critical",
                    "message": f"エラー率が{recent_error:.1%}に上昇",
                    "baseline_value": f"{baseline_error:.1%}",
                    "current_value": f"{recent_error:.1%}",
                }
            )

        # スループット低下
        baseline_throughput = baseline.get("throughput_per_hour", 0)
        recent_throughput = recent.get("throughput_per_hour", 0)

        if baseline_throughput > 0:
            throughput_ratio = recent_throughput / baseline_throughput
            if throughput_ratio < (1 - self.throughput_drop_threshold):
                degradations.append(
                    {
                        "type": "throughput",
                        "severity": "medium",
                        "message": f"スループットが{(1 - throughput_ratio) * 100:.1f}%低下",
                        "baseline_value": f"{baseline_throughput:.2f}/h",
                        "current_value": f"{recent_throughput:.2f}/h",
                    }
                )

        return degradations

    def _generate_performance_alerts(
        self, degradations: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """性能アラートの生成"""

        alerts = []

        for deg in degradations:
            alert = {
                "alert_type": deg.get("type"),
                "severity": deg.get("severity"),
                "description": deg.get("message"),
                "detection_time": datetime.now().isoformat(),
            }

            # アラート別の推奨アクション
            if deg.get("type") == "response_time":
                alert["action"] = "タスク実行の最適化またはリソース追加を検討"
            elif deg.get("type") == "error_rate":
                alert["action"] = "エラーログの詳細調査を即座に実施"
            elif deg.get("type") == "throughput":
                alert["action"] = "ボトルネックの特定と並列処理の改善"

            alerts.append(alert)

        return alerts

    def _calculate_overall_health(self, degradations: List[Dict[str, str]]) -> str:
        """総合的な健全性評価"""

        if not degradations:
            return "healthy"

        severities = [d.get("severity") for d in degradations]

        if "critical" in severities:
            return "critical"
        elif "high" in severities:
            return "degraded"
        else:
            return "warning"

    def _generate_performance_recommendations(
        self, degradations: List[Dict[str, str]]
    ) -> List[str]:
        """性能改善推奨事項の生成"""

        if not degradations:
            return ["システムは正常に動作しています"]

        recommendations = []

        for deg in degradations:
            deg_type = deg.get("type")

            if deg_type == "response_time":
                recommendations.append("応答時間の詳細プロファイリングを実施")
                recommendations.append("データベースクエリの最適化を検討")
            elif deg_type == "error_rate":
                recommendations.append("エラーパターン分析を実施（Phase 4.1連携）")
                recommendations.append("根本原因の特定と修正を優先")
            elif deg_type == "throughput":
                recommendations.append("並列処理の導入または改善")
                recommendations.append("キャッシュ戦略の見直し")

        # 重複削除
        return list(set(recommendations))

    def _percentile(self, data: List[float], percentile: int) -> float:
        """パーセンタイル計算"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


if __name__ == "__main__":
    print("🧪 PerformanceDegradationDetector テスト")

    detector = PerformanceDegradationDetector()

    # テスト: 性能劣化検知
    print("\n【性能劣化検知】")
    result = detector.detect_performance_degradation()

    if result.get("status") == "insufficient_data":
        print(f"⚠️ {result.get('message')}")
    elif "error" in result:
        print(f"❌ エラー: {result.get('error')}")
    else:
        print(f"\n【ベースライン】")
        baseline = result.get("baseline", {})
        print(f"  平均応答時間: {baseline.get('avg_response_time_ms', 0):.2f}ms")
        print(f"  エラー率: {baseline.get('error_rate', 0):.1%}")
        print(f"  スループット: {baseline.get('throughput_per_hour', 0):.2f}/h")

        print(f"\n【最近の性能】")
        recent = result.get("recent_performance", {})
        print(f"  平均応答時間: {recent.get('avg_response_time_ms', 0):.2f}ms")
        print(f"  エラー率: {recent.get('error_rate', 0):.1%}")
        print(f"  スループット: {recent.get('throughput_per_hour', 0):.2f}/h")

        print(f"\n【劣化検知】")
        degradations = result.get("degradations_detected", [])
        if degradations:
            for deg in degradations:
                print(f"  [{deg.get('severity').upper()}] {deg.get('message')}")
        else:
            print("  劣化は検出されませんでした")

        print(f"\n【総合健全性】: {result.get('overall_health').upper()}")

        print(f"\n【推奨事項】")
        for rec in result.get("recommended_actions", []):
            print(f"  - {rec}")
