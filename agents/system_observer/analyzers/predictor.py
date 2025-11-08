"""
SystemPredictor - システム予測エージェント

【Phase 4.3: 予測機能の実装】
"""

import logging
import statistics
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class SystemPredictor:
    """システム予測エージェント"""

    def __init__(self):
        logger.info("✅ SystemPredictor初期化完了")

    def predict_resource_usage(
        self, snapshots: List[Dict[str, Any]], hours_ahead: int = 4
    ) -> Dict[str, Any]:
        """リソース使用率を予測"""
        if len(snapshots) < 3:
            return {"status": "insufficient_data"}

        try:
            cpu_values = [
                s.get("resources", {}).get("cpu_percent", 0)
                for s in snapshots
                if isinstance(s.get("resources", {}).get("cpu_percent"), (int, float))
            ]

            memory_values = [
                s.get("resources", {}).get("memory_percent", 0)
                for s in snapshots
                if isinstance(s.get("resources", {}).get("memory_percent"), (int, float))
            ]

            def simple_forecast(values: List[float], steps: int = 1) -> tuple:
                if len(values) < 2:
                    return values[-1] if values else 0, 0.5

                recent_avg = statistics.mean(values[-3:]) if len(values) >= 3 else values[-1]
                past_avg = statistics.mean(values[:3]) if len(values) >= 3 else values[0]

                trend = (recent_avg - past_avg) / len(values)
                predicted = recent_avg + (trend * steps)
                confidence = min(len(values) / 10, 0.95)

                return predicted, confidence

            cpu_predicted, cpu_confidence = simple_forecast(cpu_values, hours_ahead)
            memory_predicted, memory_confidence = simple_forecast(memory_values, hours_ahead)

            warnings = []
            if cpu_predicted > 80:
                warnings.append(
                    {
                        "type": "cpu_overload",
                        "severity": "high" if cpu_predicted > 90 else "medium",
                        "message": f"CPUが{cpu_predicted:.1f}%に達する予測",
                    }
                )

            return {
                "time_horizon": f"next_{hours_ahead}_hours",
                "predictions": {
                    "cpu": {
                        "current": cpu_values[-1] if cpu_values else 0,
                        "predicted": cpu_predicted,
                        "confidence": cpu_confidence,
                    },
                    "memory": {
                        "current": memory_values[-1] if memory_values else 0,
                        "predicted": memory_predicted,
                        "confidence": memory_confidence,
                    },
                },
                "warnings": warnings,
            }

        except Exception as e:
            logger.error(f"❌ リソース予測エラー: {e}")
            return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    print("🧪 SystemPredictor テスト")

    predictor = SystemPredictor()
    snapshots = [
        {"resources": {"cpu_percent": 45.0, "memory_percent": 60.0}},
        {"resources": {"cpu_percent": 48.0, "memory_percent": 62.0}},
        {"resources": {"cpu_percent": 50.0, "memory_percent": 64.0}},
        {"resources": {"cpu_percent": 52.0, "memory_percent": 65.0}},
    ]

    prediction = predictor.predict_resource_usage(snapshots, hours_ahead=4)
    print(f"\n�� リソース予測（4時間後）:")
    print(
        f"  CPU: {prediction['predictions']['cpu']['current']:.1f}% → {prediction['predictions']['cpu']['predicted']:.1f}%"
    )
    print(
        f"  メモリ: {prediction['predictions']['memory']['current']:.1f}% → {prediction['predictions']['memory']['predicted']:.1f}%"
    )
    print("\n✅ テスト完了")
