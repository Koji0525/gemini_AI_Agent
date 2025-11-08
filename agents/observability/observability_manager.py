"""
ObservabilityManager - 統合観測基盤マネージャー

【Phase 1.2完成版】
トレースとメトリクスを統合管理
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from datetime import datetime
from typing import Any, Dict, List

from agents.observability.opentelemetry_config import get_otel_config
from agents.observability.storage.metrics_exporter import MetricsExporter
from agents.observability.storage.trace_storage import TraceStorage


class ObservabilityManager:
    """統合観測基盤マネージャー"""

    def __init__(self):
        # OpenTelemetry設定
        self.otel_config = get_otel_config()

        # ストレージ
        self.trace_storage = TraceStorage()
        self.metrics_exporter = MetricsExporter()

        print("✅ ObservabilityManager初期化完了")

    def record_trace(self, trace_data: Dict[str, Any]):
        """トレースを記録"""
        # トレースストレージに保存
        self.trace_storage.store_trace(trace_data)

        # メトリクスも更新
        if trace_data.get("status") == "success":
            self.metrics_exporter.increment_counter(
                "trace_success_total",
                labels={"operation": trace_data.get("operation_name", "unknown")},
            )
        elif trace_data.get("status") == "error":
            self.metrics_exporter.increment_counter(
                "trace_error_total",
                labels={"operation": trace_data.get("operation_name", "unknown")},
            )

        # 実行時間を記録
        if "duration_ms" in trace_data:
            self.metrics_exporter.observe_histogram(
                "trace_duration_seconds",
                trace_data["duration_ms"] / 1000.0,
                labels={"operation": trace_data.get("operation_name", "unknown")},
            )

    def search_traces(self, **kwargs) -> List[Dict[str, Any]]:
        """トレースを検索"""
        return self.trace_storage.search_traces(**kwargs)

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """包括的な統計を取得"""
        trace_stats = self.trace_storage.get_trace_stats()
        metrics_summary = self.metrics_exporter.get_metrics_summary()

        return {
            "traces": trace_stats,
            "metrics": metrics_summary,
            "opentelemetry": {
                "available": self.otel_config.otel_available,
                "service_name": self.otel_config.service_name,
            },
            "timestamp": datetime.now().isoformat(),
        }

    def export_metrics_prometheus(self) -> str:
        """Prometheus形式でメトリクスをエクスポート"""
        return self.metrics_exporter.export_prometheus_format()


# グローバルインスタンス
_observability_manager = None


def get_observability_manager() -> ObservabilityManager:
    """ObservabilityManagerを取得"""
    global _observability_manager
    if _observability_manager is None:
        _observability_manager = ObservabilityManager()
    return _observability_manager


if __name__ == "__main__":
    print("🧪 ObservabilityManager テスト")

    manager = ObservabilityManager()

    # トレース記録
    test_trace = {
        "trace_id": "test-456",
        "operation_name": "TaskExecutor.execute_task",
        "status": "success",
        "duration_ms": 250,
    }

    manager.record_trace(test_trace)

    # 統計取得
    stats = manager.get_comprehensive_stats()
    print(f"\n📊 包括的統計:")
    print(f"  総トレース数: {stats['traces']['total_traces']}")
    print(f"  OpenTelemetry: {stats['opentelemetry']['available']}")

    # Prometheus形式エクスポート
    print(f"\n📊 Prometheusメトリクス:")
    print(manager.export_metrics_prometheus())
