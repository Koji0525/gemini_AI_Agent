"""
Performance Monitor - システムパフォーマンス監視
Phase 4: Layer 0 (Monitoring)
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("observer_enhanced.performance_monitor")


class PerformanceMonitor:
    """パフォーマンスモニタークラス"""

    THRESHOLDS = {
        "cpu_high": 80.0,
        "cpu_critical": 95.0,
        "memory_high": 80.0,
        "memory_critical": 95.0,
        "disk_high": 80.0,
        "disk_critical": 90.0,
    }

    def __init__(self, alert_file: str = "logs/performance_alerts.json"):
        """初期化"""
        self.alert_file = Path(alert_file)
        self.alert_file.parent.mkdir(parents=True, exist_ok=True)

        self.alerts: List[Dict] = []
        self._load_alerts()

        self.logger = logger
        self.logger.info("Initialized PerformanceMonitor")

    def _load_alerts(self):
        """保存されたアラートを読み込み"""
        if self.alert_file.exists():
            try:
                with open(self.alert_file, "r") as f:
                    self.alerts = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load alerts: {e}")
                self.alerts = []

    def _save_alerts(self):
        """アラートを保存"""
        try:
            with open(self.alert_file, "w") as f:
                json.dump(self.alerts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save alerts: {e}")

    def analyze_metrics(self, metrics: Dict) -> Dict:
        """メトリクスを分析してアラートを生成"""
        alerts = []

        if "cpu_percent" in metrics:
            cpu = metrics["cpu_percent"]
            if cpu >= self.THRESHOLDS["cpu_critical"]:
                alerts.append(
                    {
                        "type": "cpu",
                        "level": "critical",
                        "value": cpu,
                        "threshold": self.THRESHOLDS["cpu_critical"],
                        "message": f"CPU使用率が危険域: {cpu}%",
                    }
                )
            elif cpu >= self.THRESHOLDS["cpu_high"]:
                alerts.append(
                    {
                        "type": "cpu",
                        "level": "warning",
                        "value": cpu,
                        "threshold": self.THRESHOLDS["cpu_high"],
                        "message": f"CPU使用率が高い: {cpu}%",
                    }
                )

        if "memory_percent" in metrics:
            memory = metrics["memory_percent"]
            if memory >= self.THRESHOLDS["memory_critical"]:
                alerts.append(
                    {
                        "type": "memory",
                        "level": "critical",
                        "value": memory,
                        "threshold": self.THRESHOLDS["memory_critical"],
                        "message": f"メモリ使用率が危険域: {memory}%",
                    }
                )
            elif memory >= self.THRESHOLDS["memory_high"]:
                alerts.append(
                    {
                        "type": "memory",
                        "level": "warning",
                        "value": memory,
                        "threshold": self.THRESHOLDS["memory_high"],
                        "message": f"メモリ使用率が高い: {memory}%",
                    }
                )

        if alerts:
            timestamp = datetime.now().isoformat()
            for alert in alerts:
                alert["timestamp"] = timestamp
                self.alerts.append(alert)
                self.logger.warning(alert["message"])
            self._save_alerts()

        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "alerts": alerts,
            "alert_count": len(alerts),
        }

    def get_status(self) -> str:
        """現在のステータスを取得"""
        if not self.alerts:
            return "normal"

        recent_alerts = self.alerts[-10:]
        for alert in recent_alerts:
            if alert.get("level") == "critical":
                return "critical"
        for alert in recent_alerts:
            if alert.get("level") == "warning":
                return "warning"
        return "normal"

    def get_recent_alerts(self, count: int = 10) -> List[Dict]:
        """最近のアラートを取得"""
        return self.alerts[-count:] if self.alerts else []

    def get_alert_summary(self) -> Dict:
        """アラートのサマリーを取得"""
        if not self.alerts:
            return {"total": 0, "critical": 0, "warning": 0, "by_type": {}}

        critical_count = sum(1 for a in self.alerts if a.get("level") == "critical")
        warning_count = sum(1 for a in self.alerts if a.get("level") == "warning")

        by_type = {}
        for alert in self.alerts:
            alert_type = alert.get("type", "unknown")
            if alert_type not in by_type:
                by_type[alert_type] = {"critical": 0, "warning": 0}

            level = alert.get("level", "unknown")
            if level in by_type[alert_type]:
                by_type[alert_type][level] += 1

        return {
            "total": len(self.alerts),
            "critical": critical_count,
            "warning": warning_count,
            "by_type": by_type,
            "status": self.get_status(),
        }

    def get_performance_trends(self) -> Dict:
        """パフォーマンス傾向を分析"""
        if len(self.alerts) < 2:
            return {"trend": "stable", "message": "データ不足"}

        recent = self.alerts[-10:]
        previous = self.alerts[-20:-10] if len(self.alerts) >= 20 else []

        recent_critical = sum(1 for a in recent if a.get("level") == "critical")
        previous_critical = sum(1 for a in previous if a.get("level") == "critical")

        if recent_critical > previous_critical:
            return {"trend": "deteriorating", "message": "パフォーマンスが悪化傾向"}
        elif recent_critical < previous_critical:
            return {"trend": "improving", "message": "パフォーマンスが改善傾向"}
        else:
            return {"trend": "stable", "message": "パフォーマンスは安定"}
