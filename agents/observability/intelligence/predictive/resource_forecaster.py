"""
ResourceForecaster - リソース使用率時系列予測エンジン

【機能】
- CPU/メモリ使用率の予測（6時間先まで）
- トレンド分析（上昇/下降/安定）
- 閾値超過の事前警告
- 予測信頼度の計算
"""

import statistics
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.observability.observability_manager import \
    get_observability_manager


class ResourceForecaster:
    """リソース使用率予測エンジン"""

    def __init__(self):
        self.obs_manager = get_observability_manager()

        # 予測パラメータ
        self.forecast_horizon_hours = 6
        self.warning_threshold_cpu = 85.0
        self.warning_threshold_memory = 90.0
        self.critical_threshold_cpu = 95.0
        self.critical_threshold_memory = 95.0

        print("✅ ResourceForecaster初期化完了")

    def forecast_resource_usage(self) -> Dict[str, Any]:
        """
        リソース使用率の予測

        Returns:
            予測結果と警告
        """
        try:
            # メトリクス取得
            metrics = self.obs_manager.get_comprehensive_stats()
            resource_data = metrics.get("metrics", {}).get("resource_metrics", [])

            if not resource_data:
                return {
                    "status": "no_data",
                    "message": "予測に必要なメトリクスデータが不足しています",
                }

            # CPU予測
            cpu_forecast = self._forecast_metric(resource_data, "cpu_percent")

            # メモリ予測
            memory_forecast = self._forecast_metric(resource_data, "memory_percent")

            # 警告生成
            warnings = self._generate_warnings(cpu_forecast, memory_forecast)

            forecast_result = {
                "forecast_id": f"forecast-{datetime.now().timestamp()}",
                "forecast_timestamp": datetime.now().isoformat(),
                "forecast_horizon_hours": self.forecast_horizon_hours,
                "cpu_forecast": cpu_forecast,
                "memory_forecast": memory_forecast,
                "warnings": warnings,
                "overall_risk_level": self._calculate_risk_level(warnings),
                "recommendation": self._generate_recommendation(
                    cpu_forecast, memory_forecast, warnings
                ),
            }

            # トレース記録
            self.obs_manager.record_trace(
                {
                    "trace_id": forecast_result["forecast_id"],
                    "operation_name": "predictive.resource_forecast",
                    "status": "success",
                    "forecast_horizon": self.forecast_horizon_hours,
                    "warnings_count": len(warnings),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return forecast_result

        except Exception as e:
            return {"error": str(e)}

    def _forecast_metric(
        self, resource_data: List[Dict[str, Any]], metric_name: str
    ) -> Dict[str, Any]:
        """
        個別メトリクスの予測

        Args:
            resource_data: リソースメトリクスデータ
            metric_name: 予測対象メトリクス名

        Returns:
            予測結果
        """
        # データ抽出
        values = []
        timestamps = []

        for entry in resource_data[-100:]:  # 最新100件
            if metric_name in entry:
                values.append(entry[metric_name])
                timestamps.append(entry.get("timestamp", datetime.now().isoformat()))

        if len(values) < 3:
            return {
                "current_value": values[-1] if values else 0,
                "predicted_value": values[-1] if values else 0,
                "trend": "insufficient_data",
                "confidence": 0.0,
            }

        # 現在値
        current_value = values[-1]

        # 簡易線形予測（移動平均ベース）
        recent_avg = statistics.mean(values[-10:]) if len(values) >= 10 else statistics.mean(values)
        older_avg = statistics.mean(values[-30:-10]) if len(values) >= 30 else recent_avg

        # トレンド計算
        trend_delta = recent_avg - older_avg

        # 6時間後の予測値（線形外挿）
        # 単純化: 1サンプル=1分と仮定（実際はタイムスタンプから計算）
        predicted_value = current_value + (trend_delta * 360)  # 6時間=360分

        # 予測値のクリッピング（0-100%）
        predicted_value = max(0, min(100, predicted_value))

        # トレンド判定
        if abs(trend_delta) < 0.5:
            trend = "stable"
        elif trend_delta > 0:
            trend = "increasing"
        else:
            trend = "decreasing"

        # 信頼度計算（データ量と分散ベース）
        variance = statistics.variance(values) if len(values) > 1 else 0
        data_quality = min(1.0, len(values) / 100)
        variance_penalty = max(0, 1.0 - (variance / 100))
        confidence = data_quality * variance_penalty

        return {
            "current_value": round(current_value, 2),
            "predicted_value": round(predicted_value, 2),
            "predicted_at": (
                datetime.now() + timedelta(hours=self.forecast_horizon_hours)
            ).isoformat(),
            "trend": trend,
            "trend_delta_per_hour": round(trend_delta * 60, 2),
            "confidence": round(confidence, 2),
            "data_points_used": len(values),
        }

    def _generate_warnings(
        self, cpu_forecast: Dict[str, Any], memory_forecast: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """警告の生成"""

        warnings = []

        # CPU警告
        cpu_predicted = cpu_forecast.get("predicted_value", 0)
        if cpu_predicted >= self.critical_threshold_cpu:
            warnings.append(
                {
                    "type": "cpu",
                    "severity": "critical",
                    "message": f"CPU使用率が危険水準に達する予測（{cpu_predicted:.1f}%）",
                    "predicted_time": cpu_forecast.get("predicted_at"),
                    "recommended_action": "即座にスケールアウトまたはタスク優先度の見直しを実施",
                }
            )
        elif cpu_predicted >= self.warning_threshold_cpu:
            warnings.append(
                {
                    "type": "cpu",
                    "severity": "warning",
                    "message": f"CPU使用率が高水準になる予測（{cpu_predicted:.1f}%）",
                    "predicted_time": cpu_forecast.get("predicted_at"),
                    "recommended_action": "リソース使用状況の監視を強化",
                }
            )

        # メモリ警告
        memory_predicted = memory_forecast.get("predicted_value", 0)
        if memory_predicted >= self.critical_threshold_memory:
            warnings.append(
                {
                    "type": "memory",
                    "severity": "critical",
                    "message": f"メモリ使用率が危険水準に達する予測（{memory_predicted:.1f}%）",
                    "predicted_time": memory_forecast.get("predicted_at"),
                    "recommended_action": "メモリリークの調査またはメモリ増設を検討",
                }
            )
        elif memory_predicted >= self.warning_threshold_memory:
            warnings.append(
                {
                    "type": "memory",
                    "severity": "warning",
                    "message": f"メモリ使用率が高水準になる予測（{memory_predicted:.1f}%）",
                    "predicted_time": memory_forecast.get("predicted_at"),
                    "recommended_action": "不要なプロセスの停止を検討",
                }
            )

        return warnings

    def _calculate_risk_level(self, warnings: List[Dict[str, Any]]) -> str:
        """総合リスクレベルの計算"""

        if not warnings:
            return "low"

        severities = [w.get("severity") for w in warnings]

        if "critical" in severities:
            return "critical"
        elif "warning" in severities:
            return "medium"
        else:
            return "low"

    def _generate_recommendation(
        self,
        cpu_forecast: Dict[str, Any],
        memory_forecast: Dict[str, Any],
        warnings: List[Dict[str, Any]],
    ) -> str:
        """推奨事項の生成"""

        if not warnings:
            return "システムリソースは安定しています。継続的な監視を推奨します。"

        critical_warnings = [w for w in warnings if w.get("severity") == "critical"]

        if critical_warnings:
            actions = [w.get("recommended_action") for w in critical_warnings]
            return f"緊急対応が必要: {'; '.join(actions)}"
        else:
            return "警告レベルの予測があります。予防的な対策を検討してください。"


if __name__ == "__main__":
    print("🧪 ResourceForecaster テスト")

    forecaster = ResourceForecaster()

    # テスト: リソース予測
    print("\n【リソース使用率予測】")
    forecast = forecaster.forecast_resource_usage()

    if forecast.get("status") == "no_data":
        print(f"⚠️ {forecast.get('message')}")
    elif "error" in forecast:
        print(f"❌ エラー: {forecast.get('error')}")
    else:
        print(f"\n【CPU予測】")
        cpu = forecast["cpu_forecast"]
        print(f"  現在値: {cpu.get('current_value', 0):.1f}%")
        print(f"  予測値: {cpu.get('predicted_value', 0):.1f}%（6時間後）")
        print(f"  トレンド: {cpu.get('trend')}")
        print(f"  信頼度: {cpu.get('confidence', 0):.1%}")

        print(f"\n【メモリ予測】")
        memory = forecast["memory_forecast"]
        print(f"  現在値: {memory.get('current_value', 0):.1f}%")
        print(f"  予測値: {memory.get('predicted_value', 0):.1f}%（6時間後）")
        print(f"  トレンド: {memory.get('trend')}")
        print(f"  信頼度: {memory.get('confidence', 0):.1%}")

        print(f"\n【警告】")
        warnings = forecast.get("warnings", [])
        if warnings:
            for w in warnings:
                print(f"  [{w.get('severity').upper()}] {w.get('message')}")
        else:
            print("  警告なし")

        print(f"\n【総合リスク】: {forecast.get('overall_risk_level').upper()}")
        print(f"【推奨】: {forecast.get('recommendation')}")
