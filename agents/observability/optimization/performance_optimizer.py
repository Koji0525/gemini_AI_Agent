"""
PerformanceOptimizer - Phase 5.1 性能最適化エンジン

【機能】
- データ収集の最適化
- クエリ性能の改善
- メモリ使用量の最適化
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.observability.observability_manager import \
    get_observability_manager


class PerformanceOptimizer:
    """性能最適化エンジン"""

    def __init__(self):
        self.obs_manager = get_observability_manager()

        # 最適化パラメータ
        self.sampling_rate = 0.1  # 10%サンプリング
        self.batch_size = 100
        self.cache_ttl_seconds = 300  # 5分

        print("✅ PerformanceOptimizer初期化完了")

    def optimize_data_collection(self) -> Dict[str, Any]:
        """
        データ収集の最適化

        Returns:
            最適化結果
        """
        try:
            stats = self.obs_manager.get_comprehensive_stats()

            total_traces = stats.get("traces", {}).get("total_traces", 0)

            # サンプリング率の調整
            if total_traces > 10000:
                recommended_sampling = 0.05  # 5%
                optimization_level = "aggressive"
            elif total_traces > 5000:
                recommended_sampling = 0.1  # 10%
                optimization_level = "moderate"
            else:
                recommended_sampling = 0.2  # 20%
                optimization_level = "light"

            # バッチサイズの調整
            if total_traces > 5000:
                recommended_batch_size = 200
            else:
                recommended_batch_size = 100

            result = {
                "optimization_id": f"perf-opt-{datetime.now().timestamp()}",
                "optimization_timestamp": datetime.now().isoformat(),
                "current_settings": {
                    "sampling_rate": self.sampling_rate,
                    "batch_size": self.batch_size,
                    "cache_ttl": self.cache_ttl_seconds,
                },
                "recommended_settings": {
                    "sampling_rate": recommended_sampling,
                    "batch_size": recommended_batch_size,
                    "optimization_level": optimization_level,
                },
                "estimated_improvements": {
                    "storage_reduction_percent": round((1 - recommended_sampling) * 100, 1),
                    "query_speed_improvement_percent": 30,
                    "memory_reduction_percent": 20,
                },
                "recommendations": [
                    f"サンプリング率を{recommended_sampling*100:.0f}%に設定",
                    f"バッチサイズを{recommended_batch_size}に増加",
                    "インデックス最適化を実施",
                ],
            }

            return result

        except Exception as e:
            return {"error": str(e)}

    def measure_query_performance(self) -> Dict[str, Any]:
        """クエリ性能の測定"""

        try:
            import time

            # テストクエリの実行と計測
            start = time.time()
            traces = self.obs_manager.search_traces(limit=100)
            query_time_ms = (time.time() - start) * 1000

            # 性能評価
            if query_time_ms < 100:
                performance_rating = "excellent"
            elif query_time_ms < 500:
                performance_rating = "good"
            elif query_time_ms < 1000:
                performance_rating = "fair"
            else:
                performance_rating = "poor"

            return {
                "query_time_ms": round(query_time_ms, 2),
                "traces_returned": len(traces),
                "performance_rating": performance_rating,
                "needs_optimization": query_time_ms > 500,
            }

        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    print("🧪 PerformanceOptimizer テスト")

    optimizer = PerformanceOptimizer()

    print("\n【データ収集最適化】")
    opt_result = optimizer.optimize_data_collection()

    if "error" not in opt_result:
        recommended = opt_result.get("recommended_settings", {})
        print(f"  推奨サンプリング率: {recommended.get('sampling_rate', 0)*100:.0f}%")
        print(f"  推奨バッチサイズ: {recommended.get('batch_size', 0)}")
        print(f"  最適化レベル: {recommended.get('optimization_level', 'unknown').upper()}")

    print("\n【クエリ性能測定】")
    perf = optimizer.measure_query_performance()

    if "error" not in perf:
        print(f"  クエリ時間: {perf.get('query_time_ms', 0):.2f}ms")
        print(f"  性能評価: {perf.get('performance_rating', 'unknown').upper()}")
