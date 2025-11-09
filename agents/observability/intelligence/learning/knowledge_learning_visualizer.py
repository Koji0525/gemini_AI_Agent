"""
KnowledgeLearningVisualizer - ナレッジベース学習プロセス可視化

【機能】
- ナレッジベース更新履歴の追跡
- 学習内容のカテゴリ分類
- 知識の成長曲線可視化
- 再利用率の分析
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


class KnowledgeLearningVisualizer:
    """ナレッジベース学習プロセス可視化"""

    def __init__(self):
        self.obs_manager = get_observability_manager()

        # 学習カテゴリ定義
        self.learning_categories = {
            "error_resolution": "エラー解決ナレッジ",
            "optimization": "最適化ナレッジ",
            "best_practice": "ベストプラクティス",
            "configuration": "設定ナレッジ",
            "workflow": "ワークフローナレッジ",
        }

        print("✅ KnowledgeLearningVisualizer初期化完了")

    def visualize_learning_process(self) -> Dict[str, Any]:
        """
        学習プロセスの可視化

        Returns:
            学習プロセスの統計と可視化データ
        """
        try:
            # トレースからナレッジ関連のオペレーションを抽出
            all_traces = self.obs_manager.search_traces(limit=1000)

            # ナレッジ関連トレースのフィルタリング
            knowledge_traces = [
                t for t in all_traces if "knowledge" in t.get("operation_name", "").lower()
            ]

            if len(knowledge_traces) < 5:
                return {
                    "status": "insufficient_data",
                    "message": "学習データが不足しています（最低5件必要）",
                    "current_count": len(knowledge_traces),
                }

            # 学習履歴の分析
            learning_history = self._analyze_learning_history(knowledge_traces)

            # 知識成長曲線の生成
            growth_curve = self._generate_growth_curve(knowledge_traces)

            # カテゴリ別分布
            category_distribution = self._analyze_category_distribution(knowledge_traces)

            # 再利用率分析
            reuse_analysis = self._analyze_knowledge_reuse(all_traces, knowledge_traces)

            result = {
                "visualization_id": f"kb-viz-{datetime.now().timestamp()}",
                "visualization_timestamp": datetime.now().isoformat(),
                "learning_history": learning_history,
                "growth_curve": growth_curve,
                "category_distribution": category_distribution,
                "reuse_analysis": reuse_analysis,
                "summary": self._generate_learning_summary(
                    learning_history, growth_curve, reuse_analysis
                ),
                "total_knowledge_entries": len(knowledge_traces),
            }

            # トレース記録
            self.obs_manager.record_trace(
                {
                    "trace_id": result["visualization_id"],
                    "operation_name": "learning.knowledge_visualization",
                    "status": "success",
                    "knowledge_entries": len(knowledge_traces),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return result

        except Exception as e:
            return {"error": str(e)}

    def _analyze_learning_history(self, knowledge_traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """学習履歴の分析"""

        if not knowledge_traces:
            return {}

        # 時系列でソート
        sorted_traces = sorted(knowledge_traces, key=lambda x: x.get("timestamp", ""), reverse=True)

        # 最新10件の学習内容
        recent_learnings = []
        for trace in sorted_traces[:10]:
            learning_entry = {
                "timestamp": trace.get("timestamp"),
                "operation": trace.get("operation_name", "unknown"),
                "category": self._classify_learning_category(trace),
                "description": trace.get("description", "学習内容の記録"),
            }
            recent_learnings.append(learning_entry)

        # 学習頻度分析（日別）
        learning_by_date = defaultdict(int)
        for trace in knowledge_traces:
            timestamp = trace.get("timestamp", datetime.now().isoformat())
            date = timestamp.split("T")[0]
            learning_by_date[date] += 1

        # 平均学習頻度
        if learning_by_date:
            avg_learnings_per_day = sum(learning_by_date.values()) / len(learning_by_date)
        else:
            avg_learnings_per_day = 0

        return {
            "recent_learnings": recent_learnings,
            "learning_by_date": dict(learning_by_date),
            "avg_learnings_per_day": round(avg_learnings_per_day, 2),
            "total_learning_days": len(learning_by_date),
        }

    def _generate_growth_curve(self, knowledge_traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """知識成長曲線の生成"""

        # 累積学習数の計算
        sorted_traces = sorted(knowledge_traces, key=lambda x: x.get("timestamp", ""))

        growth_points = []
        cumulative_count = 0

        for idx, trace in enumerate(sorted_traces):
            cumulative_count += 1

            # 10件ごとにプロット点を作成
            if idx % 10 == 0 or idx == len(sorted_traces) - 1:
                growth_points.append(
                    {
                        "index": idx + 1,
                        "timestamp": trace.get("timestamp"),
                        "cumulative_knowledge": cumulative_count,
                    }
                )

        # 成長率の計算
        if len(growth_points) >= 2:
            first = growth_points[0]["cumulative_knowledge"]
            last = growth_points[-1]["cumulative_knowledge"]
            growth_rate = ((last - first) / first * 100) if first > 0 else 0
        else:
            growth_rate = 0

        return {
            "growth_points": growth_points,
            "growth_rate_percent": round(growth_rate, 2),
            "current_knowledge_count": cumulative_count,
            "growth_trend": "increasing" if growth_rate > 10 else "stable",
        }

    def _analyze_category_distribution(
        self, knowledge_traces: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """カテゴリ別分布の分析"""

        category_counts = defaultdict(int)

        for trace in knowledge_traces:
            category = self._classify_learning_category(trace)
            category_counts[category] += 1

        total = len(knowledge_traces)

        distribution = {
            category: {
                "count": count,
                "percentage": round((count / total * 100), 2) if total > 0 else 0,
                "description": self.learning_categories.get(category, "その他"),
            }
            for category, count in category_counts.items()
        }

        # 最多カテゴリ
        if category_counts:
            most_common_category = max(category_counts.items(), key=lambda x: x[1])
        else:
            most_common_category = ("unknown", 0)

        return {
            "distribution": distribution,
            "most_common_category": most_common_category[0],
            "most_common_count": most_common_category[1],
            "total_categories": len(category_counts),
        }

    def _analyze_knowledge_reuse(
        self, all_traces: List[Dict[str, Any]], knowledge_traces: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """ナレッジ再利用率の分析"""

        # ナレッジ参照トレースの検出（仮の実装）
        reuse_traces = [
            t
            for t in all_traces
            if "retrieve" in t.get("operation_name", "").lower()
            or "search" in t.get("operation_name", "").lower()
        ]

        total_knowledge = len(knowledge_traces)
        total_reuses = len(reuse_traces)

        # 再利用率
        if total_knowledge > 0:
            reuse_rate = (total_reuses / total_knowledge) * 100
        else:
            reuse_rate = 0

        # 最近の再利用トレンド（直近100件）
        recent_reuses = reuse_traces[-100:] if len(reuse_traces) > 100 else reuse_traces

        # 日別再利用
        reuse_by_date = defaultdict(int)
        for trace in recent_reuses:
            timestamp = trace.get("timestamp", datetime.now().isoformat())
            date = timestamp.split("T")[0]
            reuse_by_date[date] += 1

        return {
            "total_knowledge_entries": total_knowledge,
            "total_reuse_instances": total_reuses,
            "reuse_rate_percent": round(reuse_rate, 2),
            "reuse_by_date": dict(reuse_by_date),
            "average_reuses_per_day": (
                round(sum(reuse_by_date.values()) / len(reuse_by_date), 2) if reuse_by_date else 0
            ),
            "effectiveness": "high" if reuse_rate > 50 else "medium" if reuse_rate > 20 else "low",
        }

    def _classify_learning_category(self, trace: Dict[str, Any]) -> str:
        """学習内容のカテゴリ分類"""

        operation = trace.get("operation_name", "").lower()

        if "error" in operation or "failure" in operation:
            return "error_resolution"
        elif "optim" in operation or "improve" in operation:
            return "optimization"
        elif "best" in operation or "practice" in operation:
            return "best_practice"
        elif "config" in operation or "setting" in operation:
            return "configuration"
        elif "workflow" in operation or "process" in operation:
            return "workflow"
        else:
            return "other"

    def _generate_learning_summary(
        self,
        learning_history: Dict[str, Any],
        growth_curve: Dict[str, Any],
        reuse_analysis: Dict[str, Any],
    ) -> str:
        """学習サマリーの生成"""

        avg_learnings = learning_history.get("avg_learnings_per_day", 0)
        growth_rate = growth_curve.get("growth_rate_percent", 0)
        reuse_rate = reuse_analysis.get("reuse_rate_percent", 0)
        effectiveness = reuse_analysis.get("effectiveness", "low")

        summary = (
            f"平均学習頻度: {avg_learnings:.1f}件/日。"
            f"知識成長率: {growth_rate:.1f}%。"
            f"再利用率: {reuse_rate:.1f}%（{effectiveness}）。"
        )

        if reuse_rate > 50:
            summary += " 学習した知識が効果的に活用されています。"
        elif reuse_rate > 20:
            summary += " 知識の活用は中程度です。"
        else:
            summary += " 知識の活用を促進する施策が必要です。"

        return summary


if __name__ == "__main__":
    print("🧪 KnowledgeLearningVisualizer テスト")

    visualizer = KnowledgeLearningVisualizer()

    # テスト: 学習プロセス可視化
    print("\n【学習プロセス可視化】")
    result = visualizer.visualize_learning_process()

    if result.get("status") == "insufficient_data":
        print(f"⚠️ {result.get('message')}")
        print(f"   現在のデータ数: {result.get('current_count', 0)}件")
    elif "error" in result:
        print(f"❌ エラー: {result.get('error')}")
    else:
        print(f"\n【学習履歴】")
        history = result.get("learning_history", {})
        print(f"  平均学習頻度: {history.get('avg_learnings_per_day', 0):.2f}件/日")
        print(f"  学習日数: {history.get('total_learning_days', 0)}日")

        print(f"\n【成長曲線】")
        growth = result.get("growth_curve", {})
        print(f"  現在の知識数: {growth.get('current_knowledge_count', 0)}件")
        print(f"  成長率: {growth.get('growth_rate_percent', 0):.1f}%")
        print(f"  トレンド: {growth.get('growth_trend', 'unknown')}")

        print(f"\n【カテゴリ分布】")
        category = result.get("category_distribution", {})
        print(f"  最多カテゴリ: {category.get('most_common_category', 'unknown')}")
        print(f"  カテゴリ数: {category.get('total_categories', 0)}種類")

        print(f"\n【再利用分析】")
        reuse = result.get("reuse_analysis", {})
        print(f"  再利用率: {reuse.get('reuse_rate_percent', 0):.1f}%")
        print(f"  効果性: {reuse.get('effectiveness', 'unknown').upper()}")

        print(f"\n【サマリー】")
        print(f"  {result.get('summary', '不明')}")
