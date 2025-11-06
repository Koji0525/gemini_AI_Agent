"""
MonitoringAgent - リアルタイムパフォーマンス監視

機能:
1. CPU/メモリ/ディスク使用率の監視
2. 異常検知とアラート
3. Slack通知（オプション）
4. パフォーマンスログの記録
"""

import psutil
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import asyncio


class MonitoringAgent:
    """リアルタイムパフォーマンス監視エージェント"""

    def __init__(
        self,
        knowledge_path: str = "mvp_v4/knowledge/learned",
        alert_thresholds: Optional[Dict[str, float]] = None,
    ):
        """
        初期化

        Args:
            knowledge_path: ナレッジ保存先パス
            alert_thresholds: アラート閾値
        """
        self.knowledge_path = knowledge_path
        self.alert_thresholds = alert_thresholds or {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
        }
        self.metrics_history = []
        self.alerts = []

    async def collect_metrics(self) -> Dict[str, Any]:
        """
        システムメトリクスを収集

        Returns:
            メトリクス情報
        """
        try:
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": psutil.cpu_percent(interval=1),
                    "count": psutil.cpu_count(),
                    "per_cpu": psutil.cpu_percent(interval=1, percpu=True),
                },
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent,
                    "used": psutil.virtual_memory().used,
                },
                "disk": {
                    "total": psutil.disk_usage("/").total,
                    "used": psutil.disk_usage("/").used,
                    "free": psutil.disk_usage("/").free,
                    "percent": psutil.disk_usage("/").percent,
                },
                "network": {
                    "bytes_sent": psutil.net_io_counters().bytes_sent,
                    "bytes_recv": psutil.net_io_counters().bytes_recv,
                    "packets_sent": psutil.net_io_counters().packets_sent,
                    "packets_recv": psutil.net_io_counters().packets_recv,
                },
            }

            # 履歴に追加（最大1000件）
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 1000:
                self.metrics_history.pop(0)

            return metrics

        except Exception as e:
            return {"timestamp": datetime.now().isoformat(), "error": str(e)}

    async def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        メトリクスをチェックしてアラートを生成

        Args:
            metrics: メトリクス情報

        Returns:
            アラートリスト
        """
        new_alerts = []

        # CPU使用率チェック
        if metrics["cpu"]["percent"] > self.alert_thresholds["cpu_percent"]:
            alert = {
                "type": "cpu_high",
                "severity": "warning",
                "message": f"CPU使用率が高い: {metrics['cpu']['percent']:.1f}%",
                "timestamp": datetime.now().isoformat(),
                "value": metrics["cpu"]["percent"],
                "threshold": self.alert_thresholds["cpu_percent"],
            }
            new_alerts.append(alert)

        # メモリ使用率チェック
        if metrics["memory"]["percent"] > self.alert_thresholds["memory_percent"]:
            alert = {
                "type": "memory_high",
                "severity": "warning",
                "message": f"メモリ使用率が高い: {metrics['memory']['percent']:.1f}%",
                "timestamp": datetime.now().isoformat(),
                "value": metrics["memory"]["percent"],
                "threshold": self.alert_thresholds["memory_percent"],
            }
            new_alerts.append(alert)

        # ディスク使用率チェック
        if metrics["disk"]["percent"] > self.alert_thresholds["disk_percent"]:
            alert = {
                "type": "disk_high",
                "severity": "critical",
                "message": f"ディスク使用率が高い: {metrics['disk']['percent']:.1f}%",
                "timestamp": datetime.now().isoformat(),
                "value": metrics["disk"]["percent"],
                "threshold": self.alert_thresholds["disk_percent"],
            }
            new_alerts.append(alert)

        # アラート履歴に追加
        self.alerts.extend(new_alerts)

        return new_alerts

    async def generate_report(self, duration_minutes: int = 60) -> Dict[str, Any]:
        """
        パフォーマンスレポートを生成

        Args:
            duration_minutes: レポート対象期間（分）

        Returns:
            レポート情報
        """
        if not self.metrics_history:
            return {"error": "メトリクス履歴がありません"}

        # 最新N件のメトリクスを取得
        recent_metrics = (
            self.metrics_history[-duration_minutes:]
            if len(self.metrics_history) >= duration_minutes
            else self.metrics_history
        )

        # 統計計算
        cpu_values = [m["cpu"]["percent"] for m in recent_metrics if "error" not in m]
        memory_values = [m["memory"]["percent"] for m in recent_metrics if "error" not in m]
        disk_values = [m["disk"]["percent"] for m in recent_metrics if "error" not in m]

        report = {
            "period": {
                "start": recent_metrics[0]["timestamp"],
                "end": recent_metrics[-1]["timestamp"],
                "duration_minutes": len(recent_metrics),
            },
            "cpu": {
                "avg": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                "max": max(cpu_values) if cpu_values else 0,
                "min": min(cpu_values) if cpu_values else 0,
            },
            "memory": {
                "avg": sum(memory_values) / len(memory_values) if memory_values else 0,
                "max": max(memory_values) if memory_values else 0,
                "min": min(memory_values) if memory_values else 0,
            },
            "disk": {
                "avg": sum(disk_values) / len(disk_values) if disk_values else 0,
                "max": max(disk_values) if disk_values else 0,
                "min": min(disk_values) if disk_values else 0,
            },
            "alerts": {
                "total": len(self.alerts),
                "critical": len([a for a in self.alerts if a["severity"] == "critical"]),
                "warning": len([a for a in self.alerts if a["severity"] == "warning"]),
            },
            "generated_at": datetime.now().isoformat(),
        }

        return report

    async def save_metrics_log(self, output_path: str = "logs/metrics.json") -> bool:
        """
        メトリクスログを保存

        Args:
            output_path: 出力先パス

        Returns:
            成功/失敗
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            log_data = {
                "metrics_history": self.metrics_history,
                "alerts": self.alerts,
                "saved_at": datetime.now().isoformat(),
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"❌ メトリクスログ保存失敗: {e}")
            return False

    async def save_knowledge(self, event: str, details: Dict[str, Any]) -> bool:
        """
        ナレッジベースに登録

        Args:
            event: イベント名
            details: 詳細情報

        Returns:
            成功/失敗
        """
        try:
            knowledge_file = f"{self.knowledge_path}/auto_registered_knowledge.json"

            # 既存データ読み込み
            if os.path.exists(knowledge_file):
                with open(knowledge_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {"knowledge_base": [], "total_entries": 0, "last_updated": None}

            # 新規エントリ追加
            entry = {
                "event": event,
                "details": details,
                "timestamp": datetime.now().isoformat(),
                "agent": "MonitoringAgent",
            }

            data["knowledge_base"].append(entry)
            data["total_entries"] = len(data["knowledge_base"])
            data["last_updated"] = datetime.now().isoformat()

            # 保存
            os.makedirs(os.path.dirname(knowledge_file), exist_ok=True)
            with open(knowledge_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"❌ ナレッジ登録失敗: {e}")
            return False

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスク実行（統一インターフェース）

        Args:
            task: タスク情報

        Returns:
            実行結果
        """
        task_type = task.get("type")

        if task_type == "collect":
            metrics = await self.collect_metrics()
            alerts = await self.check_alerts(metrics)

            if alerts:
                await self.save_knowledge(
                    "alerts_generated", {"alerts": alerts, "metrics": metrics}
                )

            return {"status": "success", "metrics": metrics, "alerts": alerts}

        elif task_type == "report":
            duration = task.get("duration_minutes", 60)
            report = await self.generate_report(duration)

            await self.save_knowledge("report_generated", report)

            return {"status": "success", "report": report}

        elif task_type == "save_log":
            output_path = task.get("output_path", "logs/metrics.json")
            success = await self.save_metrics_log(output_path)

            return {"status": "success" if success else "error", "output_path": output_path}

        else:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}

    def get_latest_metrics(self) -> Optional[Dict[str, Any]]:
        """最新のメトリクスを取得"""
        return self.metrics_history[-1] if self.metrics_history else None

    def get_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        アラートを取得

        Args:
            severity: フィルタ（warning/critical）

        Returns:
            アラートリスト
        """
        if severity:
            return [a for a in self.alerts if a["severity"] == severity]
        return self.alerts.copy()
