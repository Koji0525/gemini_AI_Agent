"""
MonitoringAgent - リアルタイムシステム監視
"""

import os
import json
import psutil
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import deque
import threading


class MonitoringAgent:
    """リアルタイム監視エージェント"""

    def __init__(self, project_root: str = "mvp_v4"):
        self.project_root = Path(project_root)
        self.knowledge_dir = self.project_root / "knowledge" / "learned"
        self.logs_dir = self.project_root / "logs" / "monitoring"

        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self.metrics_history = deque(maxlen=100)
        self.alerts = []

        self.thresholds = {"cpu_percent": 80.0, "memory_percent": 85.0, "disk_percent": 90.0}

        self.is_monitoring = False
        self.monitor_thread = None

    def collect_metrics(self) -> Dict[str, Any]:
        """システムメトリクスを収集"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": {"percent": psutil.cpu_percent(interval=1), "count": psutil.cpu_count()},
            "memory": {
                "percent": psutil.virtual_memory().percent,
                "available_mb": psutil.virtual_memory().available / (1024 * 1024),
                "total_mb": psutil.virtual_memory().total / (1024 * 1024),
            },
            "disk": {
                "percent": psutil.disk_usage("/").percent,
                "free_gb": psutil.disk_usage("/").free / (1024**3),
            },
        }

    def detect_anomalies(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """異常を検知"""
        anomalies = []

        if metrics["cpu"]["percent"] > self.thresholds["cpu_percent"]:
            anomalies.append(
                {
                    "type": "cpu_high",
                    "severity": "warning",
                    "message": f"CPU使用率が高い: {metrics['cpu']['percent']:.1f}%",
                }
            )

        if metrics["memory"]["percent"] > self.thresholds["memory_percent"]:
            anomalies.append(
                {
                    "type": "memory_high",
                    "severity": "warning",
                    "message": f"メモリ使用率が高い: {metrics['memory']['percent']:.1f}%",
                }
            )

        if metrics["disk"]["percent"] > self.thresholds["disk_percent"]:
            anomalies.append(
                {
                    "type": "disk_high",
                    "severity": "critical",
                    "message": f"ディスク使用率が高い: {metrics['disk']['percent']:.1f}%",
                }
            )

        return anomalies

    def monitor_loop(self, interval: int, duration: int):
        """監視ループ"""
        start_time = time.time()
        print(f"🔍 監視開始: {duration}秒間、{interval}秒間隔")

        while self.is_monitoring and (time.time() - start_time) < duration:
            metrics = self.collect_metrics()
            self.metrics_history.append(metrics)

            anomalies = self.detect_anomalies(metrics)
            for anomaly in anomalies:
                print(f"⚠️ {anomaly['message']}")
                self.alerts.append(anomaly)

            if len(self.metrics_history) % 5 == 0:
                print(
                    f"📊 CPU: {metrics['cpu']['percent']:.1f}% | "
                    f"MEM: {metrics['memory']['percent']:.1f}% | "
                    f"Disk: {metrics['disk']['percent']:.1f}%"
                )

            time.sleep(interval)

    def start_monitoring(self, interval: int = 2, duration: int = 10):
        """監視を開始"""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self.monitor_loop, args=(interval, duration), daemon=True
        )
        self.monitor_thread.start()
        self.monitor_thread.join()
        self.is_monitoring = False

        # レポート生成
        report = self.generate_report()

        # ナレッジ保存
        knowledge_file = self.knowledge_dir / "auto_registered_knowledge.json"
        knowledge_data = []
        if knowledge_file.exists():
            knowledge_data = json.loads(knowledge_file.read_text())

        knowledge_data.append(
            {
                "timestamp": datetime.now().isoformat(),
                "agent": "MonitoringAgent",
                "category": "監視/パフォーマンス",
                "details": report,
                "success": True,
            }
        )

        knowledge_file.write_text(json.dumps(knowledge_data, ensure_ascii=False, indent=2))

        return report

    def generate_report(self) -> Dict[str, Any]:
        """監視レポートを生成"""
        if not self.metrics_history:
            return {"error": "監視データがありません"}

        cpu_values = [m["cpu"]["percent"] for m in self.metrics_history]
        memory_values = [m["memory"]["percent"] for m in self.metrics_history]

        return {
            "timestamp": datetime.now().isoformat(),
            "samples": len(self.metrics_history),
            "cpu": {
                "avg": sum(cpu_values) / len(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values),
            },
            "memory": {
                "avg": sum(memory_values) / len(memory_values),
                "max": max(memory_values),
                "min": min(memory_values),
            },
            "alerts_total": len(self.alerts),
        }
