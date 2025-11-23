"""
システムメトリクス収集モジュール

CPU、メモリ、ディスク、ネットワークなどのシステムメトリクスを収集。
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any,  Dict, List

import psutil

logger = logging.getLogger(__name__)


class MetricsCollector:
    """システムメトリクス収集クラス"""

    def __init__(self, metrics_file: str = "logs/system_metrics.json"):
        """
        初期化

        Args:
            metrics_file: メトリクスを保存するファイルパス
        """
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

        # メトリクス履歴（最新1000件まで保持）
        self.metrics_history: List[Dict] = []
        self._load_history()

        logger.info(f"Initialized MetricsCollector with file: {metrics_file}")

    def _load_history(self):
        """保存されたメトリクス履歴を読み込み"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, "r") as f:
                    data = json.load(f)
                    self.metrics_history = data.get("metrics", [])[-1000:]  # 最新1000件
                logger.info(f"Loaded {len(self.metrics_history)} metrics from history")
            except Exception as e:
                logger.error(f"Failed to load metrics history: {e}")

    def _save_history(self):
        """メトリクス履歴を保存"""
        try:
            with open(self.metrics_file, "w") as f:
                json.dump(
                    {
                        "metrics": self.metrics_history[-1000:],  # 最新1000件
                        "last_updated": datetime.now().isoformat(),
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            logger.error(f"Failed to save metrics history: {e}")

    def collect_system_metrics(self) -> Dict[str, Any]:
        """
        システムメトリクスを収集
        
        Returns:
            Dict[str, Any]: CPU、メモリ、ディスク、ネットワークの情報
        """
        try:
            # CPU使用率（パーセント値）
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            
            # メモリ情報
            memory = psutil.virtual_memory()
            
            # ディスク情報
            disk = psutil.disk_usage('/')
            
            # ネットワーク情報
            network = psutil.net_io_counters()
            
            # 構造化されたメトリクス
            metrics = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cpu": {
                    "percent": float(cpu_percent),
                    "count": cpu_count
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": float(memory.percent),
                    "used": memory.used,
                    "free": memory.free
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": float(disk.percent)
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            }
            
            self.logger.info(f"Metrics collected: CPU={cpu_percent:.1f}%, Memory={memory.percent:.1f}%")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {e}")
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
                "cpu": {"percent": 0, "count": 0},
                "memory": {"percent": 0, "total": 0, "used": 0},
                "disk": {"percent": 0, "total": 0, "used": 0},
                "network": {"bytes_sent": 0, "bytes_recv": 0}
            }
    def _collect_cpu_metrics(self) -> Dict:
        """CPU関連メトリクス"""
        return {
            "usage_percent": psutil.cpu_percent(interval=0.1),
            "count": psutil.cpu_count(),
            "count_logical": psutil.cpu_count(logical=True),
            "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
        }

    def _collect_memory_metrics(self) -> Dict:
        """メモリ関連メトリクス"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent,
            "swap_total": swap.total,
            "swap_used": swap.used,
            "swap_percent": swap.percent,
        }

    def _collect_disk_metrics(self) -> Dict:
        """ディスク関連メトリクス"""
        disk = psutil.disk_usage("/")

        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
        }

    def _collect_network_metrics(self) -> Dict:
        """ネットワーク関連メトリクス"""
        net = psutil.net_io_counters()

        return {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
        }

    def _collect_process_metrics(self) -> Dict:
        """プロセス関連メトリクス（現在のPythonプロセス）"""
        try:
            process = psutil.Process()

            return {
                "cpu_percent": process.cpu_percent(interval=0.1),
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "num_threads": process.num_threads(),
                "num_fds": process.num_fds() if hasattr(process, "num_fds") else None,
            }
        except Exception as e:
            logger.error(f"Failed to collect process metrics: {e}")
            return {}

    def get_metrics_summary(self, minutes: int = 10) -> Dict:
        """
        直近N分のメトリクスサマリーを取得

        Args:
            minutes: 取得する分数

        Returns:
            サマリーデータ
        """
        cutoff_time = datetime.now().timestamp() - (minutes * 60)

        recent_metrics = [
            m
            for m in self.metrics_history
            if datetime.fromisoformat(m["timestamp"]).timestamp() > cutoff_time
        ]

        if not recent_metrics:
            return {"count": 0, "time_range_minutes": minutes}

        # 平均値を計算
        cpu_avg = sum(m["cpu"]["usage_percent"] for m in recent_metrics) / len(recent_metrics)
        memory_avg = sum(m["memory"]["percent"] for m in recent_metrics) / len(recent_metrics)

        return {
            "count": len(recent_metrics),
            "time_range_minutes": minutes,
            "cpu_usage_avg": round(cpu_avg, 2),
            "memory_usage_avg": round(memory_avg, 2),
            "latest": recent_metrics[-1] if recent_metrics else None,
        }

    def get_all_metrics(self, limit: int = 100) -> List[Dict]:
        """
        メトリクス履歴を取得

        Args:
            limit: 取得する最大件数

        Returns:
            メトリクスリスト
        """
        return self.metrics_history[-limit:]



    def collect_metrics(self) -> Dict[str, Any]:
        """
        メトリクス収集（エイリアス）
        
        collect_system_metrics() の別名
        """
        return self.collect_system_metrics()


def get_metrics_collector() -> MetricsCollector:
    """メトリクスコレクターのシングルトンインスタンスを取得"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

