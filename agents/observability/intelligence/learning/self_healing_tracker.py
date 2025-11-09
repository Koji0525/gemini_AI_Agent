"""
SelfHealingTracker - 自己修復アクション追跡システム

【機能】
- 自己修復アクションの記録と追跡
- 修復成功率の計算
- 修復時間の分析
- 修復パターンの学習
"""

import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.observability.observability_manager import \
    get_observability_manager


class SelfHealingTracker:
    """自己修復アクション追跡システム"""

    def __init__(self):
        self.obs_manager = get_observability_manager()

        # 修復アクションタイプ定義
        self.healing_action_types = {
            "auto_retry": "自動リトライ",
            "resource_scaling": "リソーススケーリング",
            "cache_clear": "キャッシュクリア",
            "config_adjustment": "設定調整",
            "dependency_restart": "依存サービス再起動",
        }

        print("✅ SelfHealingTracker初期化完了")

    def track_healing_actions(self) -> Dict[str, Any]:
        """
        自己修復アクションの追跡

        Returns:
            修復アクションの統計と効果分析
        """
        try:
            # トレースから修復関連のオペレーションを抽出
            all_traces = self.obs_manager.search_traces(limit=1000)

            # 修復関連トレースのフィルタリング
            healing_traces = [
                t
                for t in all_traces
                if "heal" in t.get("operation_name", "").lower()
                or "retry" in t.get("operation_name", "").lower()
                or "recover" in t.get("operation_name", "").lower()
            ]

            if len(healing_traces) < 3:
                return {
                    "status": "insufficient_data",
                    "message": "修復データが不足しています（最低3件必要）",
                    "current_count": len(healing_traces),
                }

            # 修復成功率の計算
            success_rate_analysis = self._calculate_success_rate(healing_traces)

            # 修復時間の分析
            time_analysis = self._analyze_healing_time(healing_traces)

            # 修復パターンの学習
            pattern_learning = self._learn_healing_patterns(healing_traces)

            # 効果測定
            effectiveness = self._measure_healing_effectiveness(all_traces, healing_traces)

            result = {
                "tracking_id": f"healing-track-{datetime.now().timestamp()}",
                "tracking_timestamp": datetime.now().isoformat(),
                "success_rate_analysis": success_rate_analysis,
                "time_analysis": time_analysis,
                "pattern_learning": pattern_learning,
                "effectiveness": effectiveness,
                "total_healing_actions": len(healing_traces),
                "recommendations": self._generate_healing_recommendations(
                    success_rate_analysis, pattern_learning
                ),
            }

            # トレース記録
            self.obs_manager.record_trace(
                {
                    "trace_id": result["tracking_id"],
                    "operation_name": "learning.self_healing_tracking",
                    "status": "success",
                    "healing_actions": len(healing_traces),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return result

        except Exception as e:
            return {"error": str(e)}

    def _calculate_success_rate(self, healing_traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """修復成功率の計算"""

        total_attempts = len(healing_traces)
        successful = len([t for t in healing_traces if t.get("status") == "success"])
        failed = total_attempts - successful

        success_rate = (successful / total_attempts * 100) if total_attempts > 0 else 0

        # アクションタイプ別成功率
        type_success_rates = defaultdict(lambda: {"total": 0, "success": 0})

        for trace in healing_traces:
            action_type = self._classify_healing_action(trace)
            type_success_rates[action_type]["total"] += 1
            if trace.get("status") == "success":
                type_success_rates[action_type]["success"] += 1

        type_rates = {
            action_type: {
                "success_rate": (
                    round((data["success"] / data["total"] * 100), 2) if data["total"] > 0 else 0
                ),
                "total_attempts": data["total"],
                "successful_attempts": data["success"],
            }
            for action_type, data in type_success_rates.items()
        }

        return {
            "overall_success_rate": round(success_rate, 2),
            "total_attempts": total_attempts,
            "successful_attempts": successful,
            "failed_attempts": failed,
            "success_by_type": type_rates,
        }

    def _analyze_healing_time(self, healing_traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """修復時間の分析"""

        healing_times = []

        for trace in healing_traces:
            duration = trace.get("duration_ms", 0)
            if duration > 0:
                healing_times.append(duration)

        if not healing_times:
            return {"avg_healing_time_ms": 0, "min_healing_time_ms": 0, "max_healing_time_ms": 0}

        import statistics

        avg_time = statistics.mean(healing_times)
        min_time = min(healing_times)
        max_time = max(healing_times)
        median_time = statistics.median(healing_times)

        # 修復時間の分類
        fast_healings = len([t for t in healing_times if t < 1000])  # <1秒
        medium_healings = len([t for t in healing_times if 1000 <= t < 5000])  # 1-5秒
        slow_healings = len([t for t in healing_times if t >= 5000])  # >=5秒

        return {
            "avg_healing_time_ms": round(avg_time, 2),
            "median_healing_time_ms": round(median_time, 2),
            "min_healing_time_ms": min_time,
            "max_healing_time_ms": max_time,
            "fast_healings": fast_healings,
            "medium_healings": medium_healings,
            "slow_healings": slow_healings,
            "speed_distribution": {
                "fast_pct": round((fast_healings / len(healing_times) * 100), 2),
                "medium_pct": round((medium_healings / len(healing_times) * 100), 2),
                "slow_pct": round((slow_healings / len(healing_times) * 100), 2),
            },
        }

    def _learn_healing_patterns(self, healing_traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """修復パターンの学習"""

        # 最も成功したパターンの特定
        successful_patterns = defaultdict(int)
        failed_patterns = defaultdict(int)

        for trace in healing_traces:
            action_type = self._classify_healing_action(trace)

            if trace.get("status") == "success":
                successful_patterns[action_type] += 1
            else:
                failed_patterns[action_type] += 1

        # 最も効果的なパターン
        if successful_patterns:
            most_effective = max(successful_patterns.items(), key=lambda x: x[1])
        else:
            most_effective = ("unknown", 0)

        # 最も失敗しやすいパターン
        if failed_patterns:
            most_problematic = max(failed_patterns.items(), key=lambda x: x[1])
        else:
            most_problematic = ("unknown", 0)

        # 学習された推奨パターン
        recommended_patterns = [
            {
                "pattern": pattern,
                "success_count": count,
                "description": self.healing_action_types.get(pattern, "その他"),
            }
            for pattern, count in sorted(
                successful_patterns.items(), key=lambda x: x[1], reverse=True
            )[:3]
        ]

        return {
            "most_effective_pattern": most_effective[0],
            "most_effective_count": most_effective[1],
            "most_problematic_pattern": most_problematic[0],
            "most_problematic_count": most_problematic[1],
            "recommended_patterns": recommended_patterns,
            "total_patterns_learned": len(
                set(list(successful_patterns.keys()) + list(failed_patterns.keys()))
            ),
        }

    def _measure_healing_effectiveness(
        self, all_traces: List[Dict[str, Any]], healing_traces: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """修復効果の測定"""

        # エラートレース数
        error_traces = [t for t in all_traces if t.get("status") == "error"]

        # 修復されたエラーの推定（修復アクション後にエラーが減った場合）
        # 簡易実装: 修復成功数をカウント
        successful_healings = len([t for t in healing_traces if t.get("status") == "success"])

        total_errors = len(error_traces)

        # 修復率
        if total_errors > 0:
            healing_rate = successful_healings / total_errors * 100
        else:
            healing_rate = 100 if successful_healings > 0 else 0

        # システム安定性への寄与
        if healing_rate > 80:
            stability_impact = "high"
        elif healing_rate > 50:
            stability_impact = "medium"
        else:
            stability_impact = "low"

        return {
            "total_errors_detected": total_errors,
            "successful_healings": successful_healings,
            "healing_coverage_rate": round(healing_rate, 2),
            "stability_impact": stability_impact,
            "unhealed_errors": max(0, total_errors - successful_healings),
        }

    def _classify_healing_action(self, trace: Dict[str, Any]) -> str:
        """修復アクションの分類"""

        operation = trace.get("operation_name", "").lower()

        if "retry" in operation:
            return "auto_retry"
        elif "scale" in operation or "resource" in operation:
            return "resource_scaling"
        elif "cache" in operation:
            return "cache_clear"
        elif "config" in operation:
            return "config_adjustment"
        elif "restart" in operation:
            return "dependency_restart"
        else:
            return "other"

    def _generate_healing_recommendations(
        self, success_rate_analysis: Dict[str, Any], pattern_learning: Dict[str, Any]
    ) -> List[str]:
        """修復推奨事項の生成"""

        recommendations = []

        overall_rate = success_rate_analysis.get("overall_success_rate", 0)

        if overall_rate < 70:
            recommendations.append("修復成功率が低いため、修復ロジックの見直しを推奨します")

        most_effective = pattern_learning.get("most_effective_pattern")
        if most_effective and most_effective != "unknown":
            recommendations.append(
                f"{self.healing_action_types.get(most_effective, most_effective)}パターンが最も効果的です。優先的に使用してください"
            )

        most_problematic = pattern_learning.get("most_problematic_pattern")
        if most_problematic and most_problematic != "unknown":
            recommendations.append(
                f"{self.healing_action_types.get(most_problematic, most_problematic)}パターンの失敗率が高いため、改善が必要です"
            )

        if not recommendations:
            recommendations.append("自己修復システムは良好に機能しています")

        return recommendations


if __name__ == "__main__":
    print("🧪 SelfHealingTracker テスト")

    tracker = SelfHealingTracker()

    # テスト: 修復アクション追跡
    print("\n【自己修復アクション追跡】")
    result = tracker.track_healing_actions()

    if result.get("status") == "insufficient_data":
        print(f"⚠️ {result.get('message')}")
        print(f"   現在のデータ数: {result.get('current_count', 0)}件")
    elif "error" in result:
        print(f"❌ エラー: {result.get('error')}")
    else:
        print(f"\n【成功率分析】")
        success = result.get("success_rate_analysis", {})
        print(f"  総合成功率: {success.get('overall_success_rate', 0):.1f}%")
        print(f"  総試行回数: {success.get('total_attempts', 0)}回")
        print(f"  成功回数: {success.get('successful_attempts', 0)}回")

        print(f"\n【修復時間分析】")
        time_analysis = result.get("time_analysis", {})
        print(f"  平均修復時間: {time_analysis.get('avg_healing_time_ms', 0):.2f}ms")
        print(f"  高速修復: {time_analysis.get('fast_healings', 0)}回")
        print(f"  低速修復: {time_analysis.get('slow_healings', 0)}回")

        print(f"\n【パターン学習】")
        pattern = result.get("pattern_learning", {})
        print(f"  最も効果的: {pattern.get('most_effective_pattern', 'unknown')}")
        print(f"  学習パターン数: {pattern.get('total_patterns_learned', 0)}種類")

        print(f"\n【効果測定】")
        effectiveness = result.get("effectiveness", {})
        print(f"  修復カバー率: {effectiveness.get('healing_coverage_rate', 0):.1f}%")
        print(f"  安定性への影響: {effectiveness.get('stability_impact', 'unknown').upper()}")

        print(f"\n【推奨事項】")
        for rec in result.get("recommendations", []):
            print(f"  - {rec}")
