"""
Metrics Collector - システムメトリクス収集
Phase 4: システムリソース監視
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import psutil

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("observer_enhanced.metrics_collector")


class MetricsCollector:
    """システムメトリクス収集クラス"""

    def __init__(self, metrics_file: str = "logs/system_metrics.json"):
        """初期化"""
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

        self.metrics_history: List[Dict] = []
        self._load_metrics()

        self.logger = logger
        self.logger.info(f"Initialized MetricsCollector with file: {metrics_file}")

    def _load_metrics(self):
        """保存されたメトリクスを読み込み"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, "r") as f:
                    self.metrics_history = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load metrics: {e}")
                self.metrics_history = []

    def _save_metrics(self):
        """メトリクスを保存"""
        try:
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]

            with open(self.metrics_file, "w") as f:
                json.dump(self.metrics_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def collect(self) -> Dict:
        """現在のシステムメトリクスを収集"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()

            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_total_mb = memory.total / (1024 * 1024)

            disk = psutil.disk_usage("/")
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024 * 1024 * 1024)
            disk_total_gb = disk.total / (1024 * 1024 * 1024)

            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu": {"percent": round(cpu_percent, 1), "count": cpu_count},
                "memory": {
                    "percent": round(memory_percent, 1),
                    "used_mb": round(memory_used_mb, 1),
                    "total_mb": round(memory_total_mb, 1),
                },
                "disk": {
                    "percent": round(disk_percent, 1),
                    "used_gb": round(disk_used_gb, 1),
                    "total_gb": round(disk_total_gb, 1),
                },
                "cpu_percent": round(cpu_percent, 1),
                "memory_percent": round(memory_percent, 1),
                "disk_percent": round(disk_percent, 1),
            }

            self.metrics_history.append(metrics)
            self._save_metrics()

            self.logger.info(f"Metrics collected: CPU={cpu_percent}%, Memory={memory_percent}%")

            return metrics

        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {e}")
            return {"timestamp": datetime.now().isoformat(), "error": str(e)}

    def get_latest(self) -> Optional[Dict]:
        """最新のメトリクスを取得"""
        return self.metrics_history[-1] if self.metrics_history else None

    def get_history(self, count: int = 100) -> List[Dict]:
        """メトリクス履歴を取得"""
        return self.metrics_history[-count:] if self.metrics_history else []

    def get_average(self, minutes: int = 10) -> Dict:
        """直近N分間の平均値を計算"""
        if not self.metrics_history:
            return {}

        recent_metrics = self.metrics_history[-minutes:]

        if not recent_metrics:
            return {}

        try:
            cpu_values = [m.get("cpu_percent", 0) for m in recent_metrics]
            avg_cpu = sum(cpu_values) / len(cpu_values)

            memory_values = [m.get("memory_percent", 0) for m in recent_metrics]
            avg_memory = sum(memory_values) / len(memory_values)

            return {
                "period_minutes": minutes,
                "sample_count": len(recent_metrics),
                "cpu_percent_avg": round(avg_cpu, 1),
                "memory_percent_avg": round(avg_memory, 1),
            }
        except Exception as e:
            self.logger.error(f"Failed to calculate average: {e}")
            return {}
