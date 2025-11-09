"""
LearningEffectivenessAnalyzer - 学習効果定量化分析

【機能】
- 学習前後の性能比較
- 学習ROIの計算
- 学習効果の可視化
- 学習投資対効果の評価
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


class LearningEffectivenessAnalyzer:
    """学習効果定量化分析"""

    def __init__(self):
        self.obs_manager = get_observability_manager()
        print("✅ LearningEffectivenessAnalyzer初期化完了")

    def analyze_learning_effectiveness(self) -> Dict[str, Any]:
        """
        学習効果の定量化分析

        Returns:
            学習効果の統計と評価
        """
        try:
            # 全トレースを取得
            all_traces = self.obs_manager.search_traces(limit=1000)

            if len(all_traces) < 30:
                return {
                    "status": "insufficient_data",
                    "message": "学習効果分析に必要なデータが不足しています",
                }

            # 学習前後の比較
            before_after_comparison = self._compare_before_after(all_traces)

            # ROI計算
            roi_calculation = self._calculate_learning_roi(all_traces)

            # 効果の可視化データ
            visualization_data = self._generate_visualization_data(all_traces)

            # 総合評価
            overall_assessment = self._assess_learning_effectiveness(
                before_after_comparison, roi_calculation
            )

            result = {
                "analysis_id": f"learning-eff-{datetime.now().timestamp()}",
                "analysis_timestamp": datetime.now().isoformat(),
                "before_after_comparison": before_after_comparison,
                "roi_calculation": roi_calculation,
                "visualization_data": visualization_data,
                "overall_assessment": overall_assessment,
                "recommendations": self._generate_effectiveness_recommendations(
                    before_after_comparison, roi_calculation
                ),
            }

            # トレース記録
            self.obs_manager.record_trace(
                {
                    "trace_id": result["analysis_id"],
                    "operation_name": "learning.effectiveness_analysis",
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return result

        except Exception as e:
            return {"error": str(e)}

    def _compare_before_after(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """学習前後の性能比較"""

        # 前半30%を学習前、後半30%を学習後として比較
        total = len(traces)
        before_end = int(total * 0.3)
        after_start = int(total * 0.7)

        before_traces = traces[:before_end]
        after_traces = traces[after_start:]

        # 成功率比較
        before_success = len([t for t in before_traces if t.get("status") == "success"])
        before_total = len(before_traces)
        before_success_rate = (before_success / before_total * 100) if before_total > 0 else 0

        after_success = len([t for t in after_traces if t.get("status") == "success"])
        after_total = len(after_traces)
        after_success_rate = (after_success / after_total * 100) if after_total > 0 else 0

        success_rate_improvement = after_success_rate - before_success_rate

        # 応答時間比較
        before_durations = [t.get("duration_ms", 0) for t in before_traces if "duration_ms" in t]
        after_durations = [t.get("duration_ms", 0) for t in after_traces if "duration_ms" in t]

        if before_durations and after_durations:
            before_avg_duration = statistics.mean(before_durations)
            after_avg_duration = statistics.mean(after_durations)
            duration_improvement = (
                ((before_avg_duration - after_avg_duration) / before_avg_duration * 100)
                if before_avg_duration > 0
                else 0
            )
        else:
            before_avg_duration = 0
            after_avg_duration = 0
            duration_improvement = 0

        # エラー率比較
        before_errors = before_total - before_success
        after_errors = after_total - after_success
        before_error_rate = (before_errors / before_total * 100) if before_total > 0 else 0
        after_error_rate = (after_errors / after_total * 100) if after_total > 0 else 0
        error_rate_reduction = before_error_rate - after_error_rate

        return {
            "before_period": {
                "success_rate": round(before_success_rate, 2),
                "avg_duration_ms": round(before_avg_duration, 2),
                "error_rate": round(before_error_rate, 2),
                "sample_size": before_total,
            },
            "after_period": {
                "success_rate": round(after_success_rate, 2),
                "avg_duration_ms": round(after_avg_duration, 2),
                "error_rate": round(after_error_rate, 2),
                "sample_size": after_total,
            },
            "improvements": {
                "success_rate_improvement": round(success_rate_improvement, 2),
                "duration_improvement_percent": round(duration_improvement, 2),
                "error_rate_reduction": round(error_rate_reduction, 2),
            },
        }

    def _calculate_learning_roi(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """学習ROIの計算"""

        # 学習コスト（仮の値、実際は学習関連トレースのコストを集計）
        learning_traces = [
            t
            for t in traces
            if "learn" in t.get("operation_name", "").lower()
            or "knowledge" in t.get("operation_name", "").lower()
        ]

        learning_cost = len(learning_traces) * 0.01  # 仮の単価

        # 削減されたエラーコスト
        total = len(traces)
        before_end = int(total * 0.3)
        after_start = int(total * 0.7)

        before_errors = len([t for t in traces[:before_end] if t.get("status") == "error"])
        after_errors = len([t for t in traces[after_start:] if t.get("status") == "error"])

        before_error_rate = before_errors / before_end if before_end > 0 else 0
        after_error_rate = after_errors / (total - after_start) if (total - after_start) > 0 else 0

        # 推定されるエラー削減数
        if after_error_rate < before_error_rate:
            error_reduction_count = int((before_error_rate - after_error_rate) * total)
        else:
            error_reduction_count = 0

        # エラー1件あたりのコスト（仮の値）
        error_cost_per_incident = 1.0  # $1

        total_cost_saved = error_reduction_count * error_cost_per_incident

        # ROI計算
        roi = ((total_cost_saved - learning_cost) / learning_cost * 100) if learning_cost > 0 else 0

        # 回収期間
        if total_cost_saved > 0:
            payback_period_days = (learning_cost / total_cost_saved) * 30  # 月次換算
        else:
            payback_period_days = float("inf")

        return {
            "learning_investment": round(learning_cost, 2),
            "cost_saved": round(total_cost_saved, 2),
            "roi_percent": round(roi, 2),
            "payback_period_days": (
                round(payback_period_days, 1) if payback_period_days != float("inf") else None
            ),
            "error_reduction_count": error_reduction_count,
            "roi_assessment": (
                "excellent" if roi > 200 else "good" if roi > 100 else "fair" if roi > 0 else "poor"
            ),
        }

    def _generate_visualization_data(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """効果可視化データの生成"""

        # 時系列での成功率推移
        timeline = []
        window_size = 50  # 50件ごとに計算

        for i in range(0, len(traces), window_size):
            window = traces[i : i + window_size]
            if len(window) < 10:
                continue

            success_count = len([t for t in window if t.get("status") == "success"])
            success_rate = success_count / len(window) * 100

            timeline.append(
                {
                    "index": i // window_size + 1,
                    "success_rate": round(success_rate, 2),
                    "sample_size": len(window),
                }
            )

        return {"success_rate_timeline": timeline, "data_points": len(timeline)}

    def _assess_learning_effectiveness(
        self, before_after: Dict[str, Any], roi: Dict[str, Any]
    ) -> str:
        """総合的な学習効果評価"""

        success_improvement = before_after.get("improvements", {}).get(
            "success_rate_improvement", 0
        )
        roi_percent = roi.get("roi_percent", 0)

        if success_improvement > 10 and roi_percent > 200:
            return "highly_effective"
        elif success_improvement > 5 and roi_percent > 100:
            return "effective"
        elif success_improvement > 0 and roi_percent > 0:
            return "moderately_effective"
        else:
            return "ineffective"

    def _generate_effectiveness_recommendations(
        self, before_after: Dict[str, Any], roi: Dict[str, Any]
    ) -> List[str]:
        """効果改善推奨事項の生成"""

        recommendations = []

        success_improvement = before_after.get("improvements", {}).get(
            "success_rate_improvement", 0
        )
        roi_percent = roi.get("roi_percent", 0)

        if success_improvement < 0:
            recommendations.append("学習効果がマイナスです。学習内容の見直しが必要です")
        elif success_improvement < 5:
            recommendations.append("学習効果が小さいです。より効果的な学習手法を検討してください")

        if roi_percent < 0:
            recommendations.append(
                "ROIがマイナスです。学習コストの削減または学習効果の向上が必要です"
            )
        elif roi_percent < 100:
            recommendations.append("ROIが低いです。学習効率の改善を検討してください")

        if not recommendations:
            recommendations.append("学習効果は良好です。現在の学習戦略を継続してください")

        return recommendations


if __name__ == "__main__":
    print("🧪 LearningEffectivenessAnalyzer テスト")

    analyzer = LearningEffectivenessAnalyzer()

    # テスト: 学習効果分析
    print("\n【学習効果分析】")
    result = analyzer.analyze_learning_effectiveness()

    if result.get("status") == "insufficient_data":
        print(f"⚠️ {result.get('message')}")
    elif "error" in result:
        print(f"❌ エラー: {result.get('error')}")
    else:
        print(f"\n【学習前後比較】")
        comparison = result.get("before_after_comparison", {})
        before = comparison.get("before_period", {})
        after = comparison.get("after_period", {})
        improvements = comparison.get("improvements", {})

        print(f"  学習前成功率: {before.get('success_rate', 0):.2f}%")
        print(f"  学習後成功率: {after.get('success_rate', 0):.2f}%")
        print(f"  改善: {improvements.get('success_rate_improvement', 0):+.2f}%")

        print(f"\n【ROI分析】")
        roi = result.get("roi_calculation", {})
        print(f"  学習投資: ${roi.get('learning_investment', 0):.2f}")
        print(f"  コスト削減: ${roi.get('cost_saved', 0):.2f}")
        print(f"  ROI: {roi.get('roi_percent', 0):.1f}%")
        print(f"  評価: {roi.get('roi_assessment', 'unknown').upper()}")

        print(f"\n【総合評価】: {result.get('overall_assessment', 'unknown').upper()}")

        print(f"\n【推奨事項】")
        for rec in result.get("recommendations", []):
            print(f"  - {rec}")
