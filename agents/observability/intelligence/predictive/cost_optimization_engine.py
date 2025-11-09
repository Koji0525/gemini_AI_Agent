"""
CostOptimizationEngine - コスト最適化推奨システム

【機能】
- API使用コストの分析
- コスト削減機会の特定
- ROI計算
- 最適化アクションの優先順位付け
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


class CostOptimizationEngine:
    """コスト最適化推奨エンジン"""

    def __init__(self):
        self.obs_manager = get_observability_manager()

        # コストパラメータ（仮の値、環境変数から取得可能）
        self.cost_per_1k_input_tokens = 0.003  # $3 per 1M tokens
        self.cost_per_1k_output_tokens = 0.015  # $15 per 1M tokens
        self.target_monthly_budget = 100.0  # $100/month

        print("✅ CostOptimizationEngine初期化完了")

    def analyze_cost_optimization(self) -> Dict[str, Any]:
        """
        コスト最適化分析

        Returns:
            最適化推奨事項
        """
        try:
            # トレースデータ取得
            all_traces = self.obs_manager.search_traces(limit=1000)

            if len(all_traces) < 10:
                return {
                    "status": "insufficient_data",
                    "message": "コスト分析に必要なデータが不足しています",
                }

            # コスト分析
            cost_breakdown = self._calculate_cost_breakdown(all_traces)

            # 最適化機会の特定
            optimization_opportunities = self._identify_optimization_opportunities(
                all_traces, cost_breakdown
            )

            # ROI計算
            roi_analysis = self._calculate_roi(optimization_opportunities)

            result = {
                "analysis_id": f"cost-opt-{datetime.now().timestamp()}",
                "analysis_timestamp": datetime.now().isoformat(),
                "cost_breakdown": cost_breakdown,
                "optimization_opportunities": optimization_opportunities,
                "roi_analysis": roi_analysis,
                "total_potential_savings": sum(
                    opp.get("estimated_savings", 0) for opp in optimization_opportunities
                ),
                "prioritized_actions": self._prioritize_actions(optimization_opportunities),
                "budget_status": self._check_budget_status(cost_breakdown),
            }

            # トレース記録
            self.obs_manager.record_trace(
                {
                    "trace_id": result["analysis_id"],
                    "operation_name": "predictive.cost_optimization",
                    "status": "success",
                    "opportunities_found": len(optimization_opportunities),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return result

        except Exception as e:
            return {"error": str(e)}

    def _calculate_cost_breakdown(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """コスト内訳の計算"""

        # オペレーション別コスト
        operation_costs = defaultdict(float)
        total_input_tokens = 0
        total_output_tokens = 0

        for trace in traces:
            operation = trace.get("operation_name", "unknown")

            # トークン数（仮のデータ、実際はトレースに含まれる）
            input_tokens = trace.get("input_tokens", 100)  # デフォルト100
            output_tokens = trace.get("output_tokens", 50)  # デフォルト50

            cost = (input_tokens / 1000) * self.cost_per_1k_input_tokens + (
                output_tokens / 1000
            ) * self.cost_per_1k_output_tokens

            operation_costs[operation] += cost
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens

        total_cost = sum(operation_costs.values())

        # オペレーション別コスト率
        cost_distribution = {
            op: {
                "cost": round(cost, 4),
                "percentage": round((cost / total_cost * 100), 2) if total_cost > 0 else 0,
            }
            for op, cost in sorted(operation_costs.items(), key=lambda x: x[1], reverse=True)
        }

        breakdown = {
            "total_cost": round(total_cost, 4),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "operation_distribution": cost_distribution,
            "sample_size": len(traces),
        }

        return breakdown

    def _identify_optimization_opportunities(
        self, traces: List[Dict[str, Any]], cost_breakdown: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """最適化機会の特定"""

        opportunities = []

        operation_dist = cost_breakdown.get("operation_distribution", {})

        # 機会1: 高コストオペレーションの最適化
        for op_name, op_data in operation_dist.items():
            cost_pct = op_data.get("percentage", 0)

            if cost_pct > 20:  # 20%以上のコスト占有
                opportunities.append(
                    {
                        "opportunity_type": "high_cost_operation",
                        "operation_name": op_name,
                        "current_cost": op_data.get("cost", 0),
                        "cost_percentage": cost_pct,
                        "estimated_savings": op_data.get("cost", 0) * 0.3,  # 30%削減を仮定
                        "optimization_approach": "プロンプト最適化、キャッシュ導入",
                        "implementation_effort": "medium",
                        "priority": "high",
                    }
                )

        # 機会2: 重複呼び出しの削減
        operation_counts = defaultdict(int)
        for trace in traces:
            operation_counts[trace.get("operation_name", "unknown")] += 1

        for op_name, count in operation_counts.items():
            if count > 100:  # 頻繁に呼び出されるオペレーション
                op_cost = operation_dist.get(op_name, {}).get("cost", 0)
                opportunities.append(
                    {
                        "opportunity_type": "frequent_calls",
                        "operation_name": op_name,
                        "call_count": count,
                        "current_cost": op_cost,
                        "estimated_savings": op_cost * 0.2,  # 20%削減を仮定
                        "optimization_approach": "レスポンスキャッシュ、バッチ処理",
                        "implementation_effort": "low",
                        "priority": "medium",
                    }
                )

        # 機会3: 全体的なプロンプト最適化
        total_cost = cost_breakdown.get("total_cost", 0)
        if total_cost > 1.0:  # $1以上の場合
            opportunities.append(
                {
                    "opportunity_type": "prompt_optimization",
                    "operation_name": "全オペレーション",
                    "current_cost": total_cost,
                    "estimated_savings": total_cost * 0.15,  # 15%削減を仮定
                    "optimization_approach": "プロンプトの簡潔化、不要な出力削減",
                    "implementation_effort": "high",
                    "priority": "low",
                }
            )

        return opportunities

    def _calculate_roi(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ROI計算"""

        total_potential_savings = sum(opp.get("estimated_savings", 0) for opp in opportunities)

        # 実装コスト（仮の値）
        implementation_costs = {
            "low": 10.0,  # $10相当の工数
            "medium": 50.0,  # $50相当の工数
            "high": 100.0,  # $100相当の工数
        }

        total_implementation_cost = sum(
            implementation_costs.get(opp.get("implementation_effort", "medium"), 50)
            for opp in opportunities
        )

        # 月次節約額（仮に30日換算）
        monthly_savings = total_potential_savings * 30

        # ROI計算
        roi = (
            (monthly_savings - total_implementation_cost) / total_implementation_cost
            if total_implementation_cost > 0
            else 0
        )

        roi_analysis = {
            "total_potential_savings": round(total_potential_savings, 2),
            "monthly_savings_estimate": round(monthly_savings, 2),
            "total_implementation_cost": round(total_implementation_cost, 2),
            "roi": round(roi * 100, 2),  # パーセンテージ
            "payback_period_days": (
                round(total_implementation_cost / total_potential_savings, 1)
                if total_potential_savings > 0
                else 0
            ),
        }

        return roi_analysis

    def _prioritize_actions(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """アクションの優先順位付け"""

        # 優先度スコア計算
        priority_scores = {"high": 3, "medium": 2, "low": 1}

        effort_scores = {"low": 3, "medium": 2, "high": 1}

        # スコアリング
        scored_opportunities = []
        for opp in opportunities:
            priority_score = priority_scores.get(opp.get("priority", "low"), 1)
            effort_score = effort_scores.get(opp.get("implementation_effort", "medium"), 2)
            savings = opp.get("estimated_savings", 0)

            # 総合スコア = 優先度 + 労力の低さ + 節約額（正規化）
            total_score = priority_score + effort_score + (savings * 10)

            scored_opportunities.append({"opportunity": opp, "score": total_score})

        # スコア順にソート
        scored_opportunities.sort(key=lambda x: x["score"], reverse=True)

        # 上位5件を抽出
        prioritized = []
        for idx, item in enumerate(scored_opportunities[:5], 1):
            opp = item["opportunity"]
            prioritized.append(
                {
                    "rank": idx,
                    "operation": opp.get("operation_name", "unknown"),
                    "type": opp.get("opportunity_type", "unknown"),
                    "savings": f"${opp.get('estimated_savings', 0):.2f}",
                    "effort": opp.get("implementation_effort", "medium"),
                    "action": opp.get("optimization_approach", "不明"),
                }
            )

        return prioritized

    def _check_budget_status(self, cost_breakdown: Dict[str, Any]) -> Dict[str, Any]:
        """予算ステータスの確認"""

        total_cost = cost_breakdown.get("total_cost", 0)
        monthly_projected_cost = total_cost * 30  # 月次換算

        budget_utilization = (
            (monthly_projected_cost / self.target_monthly_budget * 100)
            if self.target_monthly_budget > 0
            else 0
        )

        if budget_utilization > 100:
            status = "over_budget"
            message = f"予算超過: 月次予測コスト${monthly_projected_cost:.2f}が目標${self.target_monthly_budget:.2f}を超過"
        elif budget_utilization > 80:
            status = "warning"
            message = f"予算警告: 月次予測コスト${monthly_projected_cost:.2f}が目標の80%を超過"
        else:
            status = "healthy"
            message = f"予算内: 月次予測コスト${monthly_projected_cost:.2f}"

        return {
            "status": status,
            "message": message,
            "budget_utilization_pct": round(budget_utilization, 2),
            "monthly_projected_cost": round(monthly_projected_cost, 2),
            "target_budget": self.target_monthly_budget,
        }


if __name__ == "__main__":
    print("🧪 CostOptimizationEngine テスト")

    engine = CostOptimizationEngine()

    # テスト: コスト最適化分析
    print("\n【コスト最適化分析】")
    result = engine.analyze_cost_optimization()

    if result.get("status") == "insufficient_data":
        print(f"⚠️ {result.get('message')}")
    elif "error" in result:
        print(f"❌ エラー: {result.get('error')}")
    else:
        print(f"\n【コスト内訳】")
        breakdown = result.get("cost_breakdown", {})
        print(f"  総コスト: ${breakdown.get('total_cost', 0):.4f}")
        print(f"  総入力トークン: {breakdown.get('total_input_tokens', 0):,}")
        print(f"  総出力トークン: {breakdown.get('total_output_tokens', 0):,}")

        print(f"\n【最適化機会】")
        opportunities = result.get("optimization_opportunities", [])
        print(f"  発見された機会: {len(opportunities)}件")
        print(f"  潜在的な節約額: ${result.get('total_potential_savings', 0):.2f}")

        print(f"\n【ROI分析】")
        roi = result.get("roi_analysis", {})
        print(f"  月次節約見込み: ${roi.get('monthly_savings_estimate', 0):.2f}")
        print(f"  実装コスト: ${roi.get('total_implementation_cost', 0):.2f}")
        print(f"  ROI: {roi.get('roi', 0):.1f}%")
        print(f"  回収期間: {roi.get('payback_period_days', 0):.1f}日")

        print(f"\n【優先アクション（上位3件）】")
        for action in result.get("prioritized_actions", [])[:3]:
            print(
                f"  {action.get('rank')}. [{action.get('effort').upper()}] {action.get('action')}"
            )
            print(f"     節約見込み: {action.get('savings')}")

        print(f"\n【予算ステータス】")
        budget = result.get("budget_status", {})
        print(f"  ステータス: {budget.get('status').upper()}")
        print(f"  {budget.get('message')}")
