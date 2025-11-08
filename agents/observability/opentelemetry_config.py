"""
OpenTelemetry Configuration - テレメトリー基盤

【Phase 1.1: OpenTelemetry導入】
既存エージェントを非侵襲的に計装し、トレースとメトリクスを収集
"""

import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenTelemetryConfig:
    """OpenTelemetry設定と初期化"""

    def __init__(self, service_name: str = "autonomous-ai-system"):
        self.service_name = service_name
        self.tracer_provider = None
        self.meter_provider = None
        self.tracer = None
        self.meter = None
        self.otel_available = self._check_otel_availability()

        if self.otel_available:
            self._initialize_otel()
        else:
            print("⚠️ OpenTelemetry未インストール（基本機能で動作）")

    def _check_otel_availability(self) -> bool:
        """OpenTelemetryの利用可能性をチェック"""
        try:
            return True
        except ImportError:
            return False

    def _initialize_otel(self):
        """OpenTelemetryを初期化"""
        try:
            from opentelemetry import metrics, trace
            from opentelemetry.sdk.metrics import MeterProvider
            from opentelemetry.sdk.metrics.export import (
                ConsoleMetricExporter, PeriodicExportingMetricReader)
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                                        ConsoleSpanExporter)

            resource = Resource.create(
                {
                    "service.name": self.service_name,
                    "service.version": "1.25.0",
                    "deployment.environment": os.getenv("ENVIRONMENT", "development"),
                }
            )

            self.tracer_provider = TracerProvider(resource=resource)
            console_exporter = ConsoleSpanExporter()
            span_processor = BatchSpanProcessor(console_exporter)
            self.tracer_provider.add_span_processor(span_processor)

            trace.set_tracer_provider(self.tracer_provider)
            self.tracer = trace.get_tracer(__name__)

            metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
            self.meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
            metrics.set_meter_provider(self.meter_provider)
            self.meter = metrics.get_meter(__name__)

            print("✅ OpenTelemetry初期化完了")

        except Exception as e:
            print(f"❌ OpenTelemetry初期化エラー: {e}")
            self.otel_available = False

    def get_tracer(self, name: str):
        """トレーサーを取得"""
        if self.otel_available and self.tracer:
            from opentelemetry import trace

            return trace.get_tracer(name)
        return None

    def get_meter(self, name: str):
        """メーターを取得"""
        if self.otel_available and self.meter:
            from opentelemetry import metrics

            return metrics.get_meter(name)
        return None


class TracingDecorator:
    """エージェント計装用デコレーター"""

    def __init__(self, otel_config: OpenTelemetryConfig):
        self.otel_config = otel_config
        self.tracer = otel_config.get_tracer("agent-tracing")

    def trace_method(self, operation_name: str = None):
        """メソッドをトレース"""

        def decorator(func):
            def wrapper(*args, **kwargs):
                if self.tracer:
                    op_name = operation_name or func.__name__
                    with self.tracer.start_as_current_span(op_name) as span:
                        span.set_attribute("function.name", func.__name__)
                        span.set_attribute("timestamp", datetime.now().isoformat())

                        try:
                            result = func(*args, **kwargs)
                            span.set_attribute("status", "success")
                            return result
                        except Exception as e:
                            span.set_attribute("status", "error")
                            span.set_attribute("error.message", str(e))
                            span.record_exception(e)
                            raise
                else:
                    return func(*args, **kwargs)

            return wrapper

        return decorator


_otel_config = None


def get_otel_config() -> OpenTelemetryConfig:
    """OpenTelemetry設定を取得"""
    global _otel_config
    if _otel_config is None:
        _otel_config = OpenTelemetryConfig()
    return _otel_config


if __name__ == "__main__":
    print("🧪 OpenTelemetry設定テスト")
    config = OpenTelemetryConfig()

    if config.otel_available:
        print("✅ OpenTelemetry利用可能")
        decorator = TracingDecorator(config)

        @decorator.trace_method("test_operation")
        def test_function():
            print("テスト関数実行")
            return "success"

        result = test_function()
        print(f"結果: {result}")
    else:
        print("⚠️ OpenTelemetry未インストール")
