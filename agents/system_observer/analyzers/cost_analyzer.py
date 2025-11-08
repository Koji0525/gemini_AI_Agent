"""
CostAnalyzer - コスト分析エージェント

【Phase 4.2: コスト分析機能】
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class CostAnalyzer:
    """コスト分析エージェント"""

    COST_PER_CPU_HOUR = 0.05
    COST_PER_GB_MEMORY_HOUR = 0.01
    COST_PER_1000_OPENAI_TOKENS = 0.002

    def __init__(self):
        self.cost_history = []
        logger.info("✅ CostAnalyzer初期化完了")

    def estimate_hourly_cost(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """時間あたりのコスト見積もり"""
        try:
            cpu_percent = resource_data.get("cpu_percent", 0)
            memory_percent = resource_data.get("memory_percent", 0)

            cpu_cores_used = (cpu_percent / 100) * 2
            cpu_cost = cpu_cores_used * self.COST_PER_CPU_HOUR

            memory_gb_used = (memory_percent / 100) * 8
            memory_cost = memory_gb_used * self.COST_PER_GB_MEMORY_HOUR

            api_tokens = 5000
            api_cost = (api_tokens / 1000) * self.COST_PER_1000_OPENAI_TOKENS

            total_cost = cpu_cost + memory_cost + api_cost

            return {
                "hourly_cost": total_cost,
                "daily_cost": total_cost * 24,
                "monthly_cost": total_cost * 24 * 30,
                "breakdown": {
                    "compute": {"cpu_cost": cpu_cost, "memory_cost": memory_cost},
                    "api": {"openai_cost": api_cost, "estimated_tokens": api_tokens},
                },
            }

        except Exception as e:
            logger.error(f"❌ コスト見積もりエラー: {e}")
            return {"status": "error", "error": str(e)}

    def analyze_cost_efficiency(
        self, cost_data: Dict[str, Any], performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """コスト効率を分析"""
        try:
            hourly_cost = cost_data.get("hourly_cost", 0)
            total_executions = performance_data.get("total_executions", 1)

            cost_per_task = hourly_cost / total_executions if total_executions > 0 else 0

            return {
                "cost_per_task": cost_per_task,
                "efficiency_rating": "excellent" if cost_per_task < 0.1 else "good",
            }

        except Exception as e:
            logger.error(f"❌ コスト効率分析エラー: {e}")
            return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    print("🧪 CostAnalyzer テスト")

    analyzer = CostAnalyzer()
    resource_data = {"cpu_percent": 50.0, "memory_percent": 60.0}

    cost = analyzer.estimate_hourly_cost(resource_data)
    print(f"\n💰 コスト見積もり:")
    print(f"  時間あたり: ${cost['hourly_cost']:.4f}")
    print(f"  日あたり:   ${cost['daily_cost']:.2f}")
    print(f"  月あたり:   ${cost['monthly_cost']:.2f}")
    print("\n✅ テスト完了")
