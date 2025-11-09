"""
ImprovementCycleMonitor - 改善サイクル進捗監視

【機能】
- PDCAサイクルの追跡
- 改善効果の測定
- 継続的改善の進捗可視化
- 改善速度の分析
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


class ImprovementCycleMonitor:
    """改善サイクル進捗監視"""

    def __init__(self):
        self.obs_manager = get_observability_manager()

        # PDCAフェーズ定義
        self.pdca_phases = {"plan": "計画", "do": "実行", "check": "検証", "act": "改善"}

        print("✅ ImprovementCycleMonitor初期化完了")

    def monitor_improvement_cycles(self) -> Dict[str, Any]:
        """
        改善サイクルの監視

        Returns:
            改善サイクルの進捗と効果
        """
        try:
            # 全トレースを取得
            all_traces = self.obs_manager.search_traces(limit=1000)

            if len(all_traces) < 20:
                return {
                    "status": "insufficient_data",
                    "message": "改善サイクル分析に必要なデータが不足しています",
                }

            # サイクル進捗の分析
            cycle_progress = self._analyze_cycle_progress(all_traces)

            # 改善効果の測定
            improvement_effects = self._measure_improvement_effects(all_traces)

            # 改善速度の分析
            improvement_velocity = self._analyze_improvement_velocity(all_traces)

            # サイクル完了率
            completion_rate = self._calculate_completion_rate(all_traces)

            result = {
                "monitor_id": f"improve-cycle-{datetime.now().timestamp()}",
                "monitor_timestamp": datetime.now().isoformat(),
                "cycle_progress": cycle_progress,
                "improvement_effects": improvement_effects,
                "improvement_velocity": improvement_velocity,
                "completion_rate": completion_rate,
                "overall_health": self._assess_overall_health(improvement_effects, completion_rate),
                "action_items": self._generate_action_items(cycle_progress, improvement_effects),
            }

            # トレース記録
            self.obs_manager.record_trace(
                {
                    "trace_id": result["monitor_id"],
                    "operation_name": "learning.improvement_cycle_monitoring",
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return result

        except Exception as e:
            return {"error": str(e)}

    def _analyze_cycle_progress(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """サイクル進捗の分析"""

        # 成功/失敗の時系列推移
        timeline = defaultdict(lambda: {"success": 0, "error": 0})

        for trace in traces:
            timestamp = trace.get("timestamp", datetime.now().isoformat())
            date = timestamp.split("T")[0]

            if trace.get("status") == "success":
                timeline[date]["success"] += 1
            else:
                timeline[date]["error"] += 1

        # 最近7日間の成功率推移
        recent_dates = sorted(timeline.keys())[-7:]
        success_rate_trend = []

        for date in recent_dates:
            total = timeline[date]["success"] + timeline[date]["error"]
            success_rate = (timeline[date]["success"] / total * 100) if total > 0 else 0

            success_rate_trend.append(
                {"date": date, "success_rate": round(success_rate, 2), "total_operations": total}
            )

        # トレンド判定
        if len(success_rate_trend) >= 2:
            first_rate = success_rate_trend[0]["success_rate"]
            last_rate = success_rate_trend[-1]["success_rate"]

            if last_rate > first_rate + 5:
                trend = "improving"
            elif last_rate < first_rate - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "unknown"

        return {
            "success_rate_trend": success_rate_trend,
            "overall_trend": trend,
            "days_monitored": len(recent_dates),
        }

    def _measure_improvement_effects(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """改善効果の測定"""

        # 前半と後半で比較
        mid_point = len(traces) // 2
        first_half = traces[:mid_point]
        second_half = traces[mid_point:]

        # 前半の統計
        first_half_success = len([t for t in first_half if t.get("status") == "success"])
        first_half_total = len(first_half)
        first_half_rate = (
            (first_half_success / first_half_total * 100) if first_half_total > 0 else 0
        )

        # 後半の統計
        second_half_success = len([t for t in second_half if t.get("status") == "success"])
        second_half_total = len(second_half)
        second_half_rate = (
            (second_half_success / second_half_total * 100) if second_half_total > 0 else 0
        )

        # 改善率
        improvement = second_half_rate - first_half_rate

        # 平均応答時間の改善（もしduration_msがある場合）
        first_durations = [t.get("duration_ms", 0) for t in first_half if "duration_ms" in t]
        second_durations = [t.get("duration_ms", 0) for t in second_half if "duration_ms" in t]

        if first_durations and second_durations:
            import statistics

            first_avg_duration = statistics.mean(first_durations)
            second_avg_duration = statistics.mean(second_durations)
            duration_improvement = (
                ((first_avg_duration - second_avg_duration) / first_avg_duration * 100)
                if first_avg_duration > 0
                else 0
            )
        else:
            first_avg_duration = 0
            second_avg_duration = 0
            duration_improvement = 0

        return {
            "first_half_success_rate": round(first_half_rate, 2),
            "second_half_success_rate": round(second_half_rate, 2),
            "success_rate_improvement": round(improvement, 2),
            "first_half_avg_duration_ms": round(first_avg_duration, 2),
            "second_half_avg_duration_ms": round(second_avg_duration, 2),
            "duration_improvement_percent": round(duration_improvement, 2),
            "improvement_direction": (
                "positive" if improvement > 0 else "negative" if improvement < 0 else "neutral"
            ),
        }

    def _analyze_improvement_velocity(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """改善速度の分析"""

        # 週ごとの改善率を計算
        weekly_improvements = []

        # トレースを7日ごとに分割
        traces_by_date = defaultdict(list)
        for trace in traces:
            timestamp = trace.get("timestamp", datetime.now().isoformat())
            date = timestamp.split("T")[0]
            traces_by_date[date].append(trace)

        sorted_dates = sorted(traces_by_date.keys())

        # 週単位でグループ化
        week_groups = []
        current_week = []

        for date in sorted_dates:
            current_week.extend(traces_by_date[date])

            if len(current_week) >= 50:  # 週ごとに約50件のトレース
                week_groups.append(current_week)
                current_week = []

        if current_week:
            week_groups.append(current_week)

        # 週ごとの成功率
        for week_idx, week_traces in enumerate(week_groups):
            success_count = len([t for t in week_traces if t.get("status") == "success"])
            total_count = len(week_traces)
            success_rate = (success_count / total_count * 100) if total_count > 0 else 0

            weekly_improvements.append(
                {
                    "week": week_idx + 1,
                    "success_rate": round(success_rate, 2),
                    "trace_count": total_count,
                }
            )

        # 改善速度（週あたりの成功率増加）
        if len(weekly_improvements) >= 2:
            first_week_rate = weekly_improvements[0]["success_rate"]
            last_week_rate = weekly_improvements[-1]["success_rate"]
            weeks_count = len(weekly_improvements)

            velocity = (last_week_rate - first_week_rate) / weeks_count if weeks_count > 0 else 0
        else:
            velocity = 0

        return {
            "weekly_improvements": weekly_improvements,
            "improvement_velocity_per_week": round(velocity, 2),
            "weeks_analyzed": len(weekly_improvements),
            "velocity_assessment": (
                "fast" if velocity > 5 else "moderate" if velocity > 1 else "slow"
            ),
        }

    def _calculate_completion_rate(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """サイクル完了率の計算"""

        # 改善関連トレースの抽出
        improvement_traces = [
            t
            for t in traces
            if any(
                keyword in t.get("operation_name", "").lower()
                for keyword in ["improve", "optimize", "enhance", "fix"]
            )
        ]

        total_improvement_attempts = len(improvement_traces)
        completed_improvements = len(
            [t for t in improvement_traces if t.get("status") == "success"]
        )

        completion_rate = (
            (completed_improvements / total_improvement_attempts * 100)
            if total_improvement_attempts > 0
            else 0
        )

        return {
            "total_improvement_attempts": total_improvement_attempts,
            "completed_improvements": completed_improvements,
            "completion_rate_percent": round(completion_rate, 2),
            "pending_improvements": total_improvement_attempts - completed_improvements,
        }

    def _assess_overall_health(
        self, improvement_effects: Dict[str, Any], completion_rate: Dict[str, Any]
    ) -> str:
        """総合的な健全性評価"""

        success_improvement = improvement_effects.get("success_rate_improvement", 0)
        completion = completion_rate.get("completion_rate_percent", 0)

        if success_improvement > 10 and completion > 80:
            return "excellent"
        elif success_improvement > 5 and completion > 60:
            return "good"
        elif success_improvement > 0 and completion > 40:
            return "fair"
        else:
            return "needs_attention"

    def _generate_action_items(
        self, cycle_progress: Dict[str, Any], improvement_effects: Dict[str, Any]
    ) -> List[str]:
        """アクションアイテムの生成"""

        action_items = []

        trend = cycle_progress.get("overall_trend")
        improvement = improvement_effects.get("success_rate_improvement", 0)

        if trend == "declining":
            action_items.append("成功率が低下傾向にあります。根本原因の調査を実施してください")

        if improvement < 0:
            action_items.append("改善効果がマイナスです。改善戦略の見直しが必要です")
        elif improvement < 5:
            action_items.append("改善効果が小さいです。より積極的な改善施策を検討してください")

        if not action_items:
            action_items.append("改善サイクルは良好に機能しています。現在の戦略を継続してください")

        return action_items


if __name__ == "__main__":
    print("🧪 ImprovementCycleMonitor テスト")

    monitor = ImprovementCycleMonitor()

    # テスト: 改善サイクル監視
    print("\n【改善サイクル監視】")
    result = monitor.monitor_improvement_cycles()

    if result.get("status") == "insufficient_data":
        print(f"⚠️ {result.get('message')}")
    elif "error" in result:
        print(f"❌ エラー: {result.get('error')}")
    else:
        print(f"\n【サイクル進捗】")
        progress = result.get("cycle_progress", {})
        print(f"  全体トレンド: {progress.get('overall_trend', 'unknown').upper()}")
        print(f"  監視日数: {progress.get('days_monitored', 0)}日")

        print(f"\n【改善効果】")
        effects = result.get("improvement_effects", {})
        print(f"  成功率改善: {effects.get('success_rate_improvement', 0):+.2f}%")
        print(f"  応答時間改善: {effects.get('duration_improvement_percent', 0):+.2f}%")
        print(f"  改善方向: {effects.get('improvement_direction', 'unknown').upper()}")

        print(f"\n【改善速度】")
        velocity = result.get("improvement_velocity", {})
        print(f"  週あたり改善速度: {velocity.get('improvement_velocity_per_week', 0):+.2f}%")
        print(f"  速度評価: {velocity.get('velocity_assessment', 'unknown').upper()}")

        print(f"\n【完了率】")
        completion = result.get("completion_rate", {})
        print(f"  完了率: {completion.get('completion_rate_percent', 0):.1f}%")
        print(f"  完了数: {completion.get('completed_improvements', 0)}件")

        print(f"\n【総合健全性】: {result.get('overall_health', 'unknown').upper()}")

        print(f"\n【アクションアイテム】")
        for item in result.get("action_items", []):
            print(f"  - {item}")
