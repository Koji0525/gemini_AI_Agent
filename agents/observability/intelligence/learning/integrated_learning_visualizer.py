"""
IntegratedLearningVisualizer - KnowledgeBase統合版学習可視化（KnowledgeManagerV2対応）

【機能】
KnowledgeManagerV2（SQLite + FAISS）のデータを活用した学習プロセス可視化
"""

import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.observability.intelligence.learning.knowledge_base_adapter import \
    KnowledgeBaseAdapter
from agents.observability.observability_manager import \
    get_observability_manager


class IntegratedLearningVisualizer:
    """統合版学習可視化（KnowledgeManagerV2対応）"""

    def __init__(self):
        self.kb_adapter = KnowledgeBaseAdapter()
        self.obs_manager = get_observability_manager()
        print("✅ IntegratedLearningVisualizer初期化完了（KnowledgeManagerV2対応）")

    def visualize_complete_learning_process(self) -> Dict[str, Any]:
        """
        完全な学習プロセスの可視化

        Returns:
            統合された学習統計
        """
        try:
            # KnowledgeBaseからデータ取得
            kb_stats = self.kb_adapter.get_knowledge_statistics()
            kb_entries = self.kb_adapter.load_knowledge_entries()

            # ObservabilityManagerからトレース取得
            obs_traces = self.obs_manager.search_traces(limit=500)

            # 統合統計の生成
            total_knowledge = kb_stats.get("total_entries", 0)
            total_traces = len(obs_traces)

            # カテゴリ別分布
            category_dist = kb_stats.get("categories", {})

            # 最近の学習活動
            recent_learning = self._analyze_recent_learning(kb_entries, obs_traces)

            # 成長曲線
            growth_curve = self._generate_integrated_growth_curve(kb_entries)

            # 再利用率（トレース数 vs ナレッジ数で推定）
            reuse_estimate = self._estimate_knowledge_reuse(total_traces, total_knowledge)

            # 品質指標
            quality_metrics = self._calculate_quality_metrics(kb_stats, kb_entries)

            result = {
                "visualization_id": f"integrated-learn-{datetime.now().timestamp()}",
                "visualization_timestamp": datetime.now().isoformat(),
                "system_version": "KnowledgeManagerV2",
                "knowledge_base_stats": {
                    "total_entries": total_knowledge,
                    "category_distribution": category_dist,
                    "oldest_entry": kb_stats.get("oldest_timestamp"),
                    "newest_entry": kb_stats.get("newest_timestamp"),
                    "db_stats": kb_stats.get("db_stats", {}),
                },
                "observability_stats": {
                    "total_traces": total_traces,
                    "recent_operations": len([t for t in obs_traces if "timestamp" in t]),
                },
                "recent_learning": recent_learning,
                "growth_curve": growth_curve,
                "reuse_estimate": reuse_estimate,
                "quality_metrics": quality_metrics,
                "summary": self._generate_integrated_summary(
                    total_knowledge, category_dist, growth_curve, reuse_estimate, quality_metrics
                ),
            }

            return result

        except Exception as e:
            import traceback

            traceback.print_exc()
            return {"error": str(e)}

    def _analyze_recent_learning(
        self, kb_entries: List[Dict[str, Any]], obs_traces: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """最近の学習活動分析"""

        # 最新10件のナレッジ
        sorted_kb = sorted(kb_entries, key=lambda x: x.get("timestamp", ""), reverse=True)

        recent_kb = [
            {
                "title": entry.get("title", "unknown"),
                "category": entry.get("category", "other"),
                "timestamp": entry.get("timestamp"),
                "confidence": entry.get("confidence", 0),
            }
            for entry in sorted_kb[:10]
        ]

        # 日別学習頻度
        learning_by_date = defaultdict(int)
        for entry in kb_entries:
            timestamp = entry.get("timestamp", datetime.now().isoformat())
            date = timestamp.split("T")[0]
            learning_by_date[date] += 1

        return {
            "recent_entries": recent_kb,
            "learning_by_date": dict(learning_by_date),
            "avg_learnings_per_day": (
                round(sum(learning_by_date.values()) / len(learning_by_date), 2)
                if learning_by_date
                else 0
            ),
            "total_learning_days": len(learning_by_date),
        }

    def _generate_integrated_growth_curve(self, kb_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """統合成長曲線の生成"""

        if not kb_entries:
            return {
                "growth_points": [],
                "growth_rate_percent": 0,
                "current_knowledge_count": 0,
                "growth_trend": "no_data",
            }

        # 時系列でソート
        sorted_entries = sorted(kb_entries, key=lambda x: x.get("timestamp", ""))

        # 成長点の計算
        growth_points = []
        step = max(1, len(sorted_entries) // 20)  # 最大20点

        for idx in range(0, len(sorted_entries), step):
            growth_points.append(
                {
                    "index": idx + 1,
                    "timestamp": sorted_entries[idx].get("timestamp"),
                    "cumulative_knowledge": idx + 1,
                }
            )

        # 最後の点を必ず追加
        if growth_points[-1]["index"] != len(sorted_entries):
            growth_points.append(
                {
                    "index": len(sorted_entries),
                    "timestamp": sorted_entries[-1].get("timestamp"),
                    "cumulative_knowledge": len(sorted_entries),
                }
            )

        # 成長率計算
        if len(growth_points) >= 2:
            first = growth_points[0]["cumulative_knowledge"]
            last = growth_points[-1]["cumulative_knowledge"]
            growth_rate = ((last - first) / first * 100) if first > 0 else 0
        else:
            growth_rate = 0

        return {
            "growth_points": growth_points,
            "growth_rate_percent": round(growth_rate, 2),
            "current_knowledge_count": len(sorted_entries),
            "growth_trend": "increasing" if growth_rate > 10 else "stable",
        }

    def _estimate_knowledge_reuse(self, total_traces: int, total_knowledge: int) -> Dict[str, Any]:
        """ナレッジ再利用率の推定"""

        # 簡易推定: トレース数がナレッジ数の何倍か
        if total_knowledge > 0:
            reuse_ratio = total_traces / total_knowledge
            reuse_rate = min(100, reuse_ratio * 10)  # 10倍で100%と仮定
        else:
            reuse_ratio = 0
            reuse_rate = 0

        effectiveness = "high" if reuse_rate > 50 else "medium" if reuse_rate > 20 else "low"

        return {
            "total_knowledge_entries": total_knowledge,
            "total_traces": total_traces,
            "reuse_ratio": round(reuse_ratio, 2),
            "estimated_reuse_rate_percent": round(reuse_rate, 2),
            "effectiveness": effectiveness,
        }

    def _calculate_quality_metrics(
        self, kb_stats: Dict[str, Any], kb_entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """品質指標の計算"""

        db_stats = kb_stats.get("db_stats", {})

        # 信頼度と成功率の分析
        if kb_entries:
            high_confidence = len([e for e in kb_entries if e.get("confidence", 0) > 0.8])
            len([e for e in kb_entries if e.get("success_rate", 0) > 0.8])

            confidence_distribution = {
                "high": high_confidence,
                "medium": len([e for e in kb_entries if 0.6 <= e.get("confidence", 0) <= 0.8]),
                "low": len([e for e in kb_entries if e.get("confidence", 0) < 0.6]),
            }
        else:
            high_confidence = 0
            confidence_distribution = {"high": 0, "medium": 0, "low": 0}

        total = len(kb_entries)

        return {
            "avg_confidence": db_stats.get("avg_confidence", 0),
            "avg_success_rate": db_stats.get("avg_success_rate", 0),
            "high_quality_ratio": round((high_confidence / total * 100), 2) if total > 0 else 0,
            "confidence_distribution": confidence_distribution,
            "overall_quality": (
                "excellent"
                if high_confidence > total * 0.7
                else "good" if high_confidence > total * 0.5 else "fair"
            ),
        }

    def _generate_integrated_summary(
        self,
        total_knowledge: int,
        category_dist: Dict[str, int],
        growth_curve: Dict[str, Any],
        reuse_estimate: Dict[str, Any],
        quality_metrics: Dict[str, Any],
    ) -> str:
        """統合サマリーの生成"""

        growth_rate = growth_curve.get("growth_rate_percent", 0)
        reuse_rate = reuse_estimate.get("estimated_reuse_rate_percent", 0)
        category_count = len(category_dist)
        avg_confidence = quality_metrics.get("avg_confidence", 0)

        summary = (
            f"合計{total_knowledge}件のナレッジが{category_count}カテゴリに登録されています。"
            f"知識成長率: {growth_rate:.1f}%。"
            f"推定再利用率: {reuse_rate:.1f}%。"
            f"平均信頼度: {avg_confidence:.2f}。"
        )

        if total_knowledge > 200:
            summary += " 豊富なナレッジが蓄積されています。"
        elif total_knowledge > 50:
            summary += " ナレッジベースは順調に成長しています。"
        else:
            summary += " ナレッジ蓄積を継続してください。"

        return summary


if __name__ == "__main__":
    print("🧪 IntegratedLearningVisualizer テスト（KnowledgeManagerV2対応）")

    visualizer = IntegratedLearningVisualizer()

    print("\n【統合学習プロセス可視化】")
    result = visualizer.visualize_complete_learning_process()

    if "error" in result:
        print(f"❌ エラー: {result.get('error')}")
    else:
        kb_stats = result.get("knowledge_base_stats", {})
        obs_stats = result.get("observability_stats", {})
        growth = result.get("growth_curve", {})
        reuse = result.get("reuse_estimate", {})
        quality = result.get("quality_metrics", {})

        print(f"\n【ナレッジベース統計】")
        print(f"  総エントリー数: {kb_stats.get('total_entries', 0)}件")
        print(f"  カテゴリ数: {len(kb_stats.get('category_distribution', {}))}種類")

        db_stats = kb_stats.get("db_stats", {})
        if db_stats:
            print(f"  DB総ナレッジ数: {db_stats.get('total_knowledge', 0)}件")
            print(f"  平均信頼度: {db_stats.get('avg_confidence', 0):.2f}")

        print(f"\n【成長曲線】")
        print(f"  現在の知識数: {growth.get('current_knowledge_count', 0)}件")
        print(f"  成長率: {growth.get('growth_rate_percent', 0):.1f}%")
        print(f"  トレンド: {growth.get('growth_trend', 'unknown').upper()}")

        print(f"\n【再利用推定】")
        print(f"  推定再利用率: {reuse.get('estimated_reuse_rate_percent', 0):.1f}%")
        print(f"  効果性: {reuse.get('effectiveness', 'unknown').upper()}")

        print(f"\n【品質指標】")
        print(f"  平均信頼度: {quality.get('avg_confidence', 0):.2f}")
        print(f"  平均成功率: {quality.get('avg_success_rate', 0):.2f}")
        print(f"  総合品質: {quality.get('overall_quality', 'unknown').upper()}")

        print(f"\n【サマリー】")
        print(f"  {result.get('summary', '不明')}")
