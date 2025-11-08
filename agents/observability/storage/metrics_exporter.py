"""
MetricsExporter - Prometheusスタイルメトリクスエクスポート

【Phase 1.2: Prometheus連携】
メトリクスデータの収集・エクスポート
"""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)


class MetricsExporter:
    """メトリクスエクスポーター"""

    def __init__(self):
        # メトリクスデータ
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)

        print("✅ MetricsExporter初期化完了")

    def increment_counter(self, name: str, value: int = 1, labels: Dict[str, str] = None):
        """カウンターをインクリメント"""
        key = self._make_key(name, labels)
        self.counters[key] += value

    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """ゲージ値を設定"""
        key = self._make_key(name, labels)
        self.gauges[key] = value

    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """ヒストグラムに値を記録"""
        key = self._make_key(name, labels)
        self.histograms[key].append(value)

        # 最大1000サンプルまで保持
        if len(self.histograms[key]) > 1000:
            self.histograms[key].pop(0)

    def _make_key(self, name: str, labels: Dict[str, str] = None) -> str:
        """メトリクスキーを生成"""
        if not labels:
            return name

        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def export_prometheus_format(self) -> str:
        """Prometheus形式でメトリクスをエクスポート"""
        lines = []

        # カウンター
        for key, value in self.counters.items():
            lines.append(f"{key} {value}")

        # ゲージ
        for key, value in self.gauges.items():
            lines.append(f"{key} {value}")

        # ヒストグラム（簡易版：平均値）
        for key, values in self.histograms.items():
            if values:
                avg = sum(values) / len(values)
                lines.append(f"{key}_avg {avg:.2f}")
                lines.append(f"{key}_count {len(values)}")

        return "\n".join(lines)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """メトリクスサマリーを取得"""
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {
                k: {
                    "count": len(v),
                    "avg": sum(v) / len(v) if v else 0,
                    "min": min(v) if v else 0,
                    "max": max(v) if v else 0,
                }
                for k, v in self.histograms.items()
            },
            "timestamp": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    print("🧪 MetricsExporter テスト")

    exporter = MetricsExporter()

    # テストメトリクス
    exporter.increment_counter("task_executed_total", labels={"agent": "PMAgent"})
    exporter.increment_counter("task_executed_total", labels={"agent": "PMAgent"})
    exporter.set_gauge("cpu_usage_percent", 45.5)
    exporter.observe_histogram("task_duration_seconds", 2.5, labels={"agent": "TaskExecutor"})
    exporter.observe_histogram("task_duration_seconds", 3.1, labels={"agent": "TaskExecutor"})

    # Prometheus形式
    print("\n📊 Prometheus形式:")
    print(exporter.export_prometheus_format())

    # サマリー
    print("\n📊 サマリー:")
    summary = exporter.get_metrics_summary()
    print(f"カウンター数: {len(summary['counters'])}")
    print(f"ゲージ数: {len(summary['gauges'])}")
