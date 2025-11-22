"""
パフォーマンスモニタリングモジュール

システムメトリクスを分析し、パフォーマンス問題を検出。
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any,  Dict, List

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """パフォーマンスモニタークラス"""

    # しきい値設定
    THRESHOLDS = {
        "cpu_high": 80.0,  # CPU使用率高
        "cpu_critical": 95.0,  # CPU使用率危険
        "memory_high": 80.0,  # メモリ使用率高
        "memory_critical": 95.0,  # メモリ使用率危険
        "disk_high": 80.0,  # ディスク使用率高
        "disk_critical": 90.0,  # ディスク使用率危険
    }

    def __init__(self, alert_file: str = "logs/performance_alerts.json"):
        """
        初期化

        Args:
            alert_file: アラートを保存するファイルパス
        """
        self.alert_file = Path(alert_file)
        self.alert_file.parent.mkdir(parents=True, exist_ok=True)

        # アラート履歴
        self.alerts: List[Dict] = []
        self._load_alerts()

        logger.info("Initialized PerformanceMonitor")

    def _load_alerts(self):
        """保存されたアラートを読み込み"""
        if self.alert_file.exists():
            try:
                with open(self.alert_file, "r") as f:
                    data = json.load(f)
                    self.alerts = data.get("alerts", [])[-100:]  # 最新100件
                logger.info(f"Loaded {len(self.alerts)} performance alerts")
            except Exception as e:
                logger.error(f"Failed to load alerts: {e}")

    def _save_alerts(self):
        """アラートを保存"""
        try:
            with open(self.alert_file, "w") as f:
                json.dump(
                    {
                        "alerts": self.alerts[-100:],  # 最新100件
                        "last_updated": datetime.now().isoformat(),
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            logger.error(f"Failed to save alerts: {e}")

    def analyze_metrics(self, metrics: Dict) -> Dict:
        """
        メトリクスを分析してパフォーマンス評価

        Args:
            metrics: システムメトリクス

        Returns:
            分析結果
        """
        issues = []
        warnings = []
        status = "healthy"

        try:
            # CPU分析
            cpu_usage = metrics["cpu"]["usage_percent"]
            if cpu_usage >= self.THRESHOLDS["cpu_critical"]:
                issues.append(
                    {
                        "type": "cpu_critical",
                        "message": f"CPU使用率が危険レベル: {cpu_usage}%",
                        "severity": "critical",
                    }
                )
                status = "critical"
            elif cpu_usage >= self.THRESHOLDS["cpu_high"]:
                warnings.append(
                    {
                        "type": "cpu_high",
                        "message": f"CPU使用率が高い: {cpu_usage}%",
                        "severity": "warning",
                    }
                )
                if status == "healthy":
                    status = "warning"

            # メモリ分析
            memory_usage = metrics["memory"]["percent"]
            if memory_usage >= self.THRESHOLDS["memory_critical"]:
                issues.append(
                    {
                        "type": "memory_critical",
                        "message": f"メモリ使用率が危険レベル: {memory_usage}%",
                        "severity": "critical",
                    }
                )
                status = "critical"
            elif memory_usage >= self.THRESHOLDS["memory_high"]:
                warnings.append(
                    {
                        "type": "memory_high",
                        "message": f"メモリ使用率が高い: {memory_usage}%",
                        "severity": "warning",
                    }
                )
                if status == "healthy":
                    status = "warning"

            # ディスク分析
            disk_usage = metrics["disk"]["percent"]
            if disk_usage >= self.THRESHOLDS["disk_critical"]:
                issues.append(
                    {
                        "type": "disk_critical",
                        "message": f"ディスク使用率が危険レベル: {disk_usage}%",
                        "severity": "critical",
                    }
                )
                status = "critical"
            elif disk_usage >= self.THRESHOLDS["disk_high"]:
                warnings.append(
                    {
                        "type": "disk_high",
                        "message": f"ディスク使用率が高い: {disk_usage}%",
                        "severity": "warning",
                    }
                )
                if status == "healthy":
                    status = "warning"

            # アラートを記録
            if issues or warnings:
                alert = {
                    "timestamp": datetime.now().isoformat(),
                    "status": status,
                    "issues": issues,
                    "warnings": warnings,
                    "metrics_snapshot": {
                        "cpu": cpu_usage,
                        "memory": memory_usage,
                        "disk": disk_usage,
                    },
                }
                self.alerts.append(alert)
                self.alerts = self.alerts[-100:]  # 最新100件
                self._save_alerts()

            return {
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "issues": issues,
                "warnings": warnings,
                "healthy": len(issues) == 0 and len(warnings) == 0,
                "metrics": {
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage,
                    "disk_usage": disk_usage,
                },
            }

        except Exception as e:
            logger.error(f"Failed to analyze metrics: {e}")
            return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}

    def get_performance_trends(self, metrics_history: List[Dict], minutes: int = 60) -> Dict:
        """
        パフォーマンストレンドを分析

        Args:
            metrics_history: メトリクス履歴
            minutes: 分析期間（分）

        Returns:
            トレンド分析結果
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)

        # 期間内のメトリクスをフィルタ
        recent = [
            m for m in metrics_history if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]

        if not recent:
            return {"available": False, "message": "データ不足"}

        # トレンド計算
        cpu_values = [m["cpu"]["usage_percent"] for m in recent]
        memory_values = [m["memory"]["percent"] for m in recent]

        return {
            "available": True,
            "time_range_minutes": minutes,
            "data_points": len(recent),
            "cpu": {
                "current": cpu_values[-1],
                "average": sum(cpu_values) / len(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values),
                "trend": "increasing" if cpu_values[-1] > cpu_values[0] else "decreasing",
            },
            "memory": {
                "current": memory_values[-1],
                "average": sum(memory_values) / len(memory_values),
                "max": max(memory_values),
                "min": min(memory_values),
                "trend": "increasing" if memory_values[-1] > memory_values[0] else "decreasing",
            },
        }

    def get_recent_alerts(self, limit: int = 20) -> List[Dict]:
        """
        最近のアラートを取得

        Args:
            limit: 取得する最大件数

        Returns:
            アラートリスト
        """
        return self.alerts[-limit:]

    def get_alert_summary(self, hours: int = 24) -> Dict:
        """
        アラートサマリーを取得

        Args:
            hours: 集計期間（時間）

        Returns:
            サマリーデータ
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        recent_alerts = [
            a for a in self.alerts if datetime.fromisoformat(a["timestamp"]) > cutoff_time
        ]

        critical_count = sum(1 for a in recent_alerts if a["status"] == "critical")
        warning_count = sum(1 for a in recent_alerts if a["status"] == "warning")

        return {
            "total": len(recent_alerts),
            "critical": critical_count,
            "warning": warning_count,
            "time_range_hours": hours,
        }



    def get_status(self) -> Dict[str, Any]:
        """
        パフォーマンスステータス取得（エイリアス）
        
        Returns:
            パフォーマンスステータス
        """
        return self.get_performance_status()

# グローバルインスタンス
_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """パフォーマンスモニターのシングルトンインスタンスを取得"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor
