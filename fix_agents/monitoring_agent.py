# monitoring_agent.py
"""
モニタリングエージェント
システム監視とヘルスチェック
"""

import asyncio
import logging
import psutil
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """ヘルスステータス"""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class MonitoringAgent:
    """
    モニタリングエージェント

    機能:
    - システムリソース監視
    - エラー発生率の追跡
    - パフォーマンスメトリクス収集
    - ヘルスチェック
    - アラート発行
    """

    def __init__(
        self,
        check_interval: int = 60,  # 秒
        cpu_threshold: float = 80.0,  # %
        memory_threshold: float = 85.0,  # %
        disk_threshold: float = 90.0,  # %
        error_rate_threshold: float = 0.3,  # 30%
    ):
        """
        初期化

        Args:
            check_interval: チェック間隔（秒）
            cpu_threshold: CPU使用率閾値
            memory_threshold: メモリ使用率閾値
            disk_threshold: ディスク使用率閾値
            error_rate_threshold: エラー率閾値
        """
        self.check_interval = check_interval
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
        self.error_rate_threshold = error_rate_threshold

        # モニタリングデータ
        self.metrics_history = []
        self.alerts = []

        # システム情報
        self.start_time = datetime.now()
        self.is_monitoring = False
        self.monitoring_task = None

        # 統計情報
        self.stats = {
            "total_checks": 0,
            "health_checks": 0,
            "warnings_issued": 0,
            "critical_alerts": 0,
            "avg_cpu_usage": 0.0,
            "avg_memory_usage": 0.0,
            "avg_response_time": 0.0,
        }

        logger.info("✅ MonitoringAgent 初期化完了")

    async def start_monitoring(self):
        """モニタリング開始"""
        if self.is_monitoring:
            logger.warning("⚠️ モニタリングは既に実行中です")
            return

        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

        logger.info(f"🔍 モニタリング開始 (間隔={self.check_interval}秒)")

    async def stop_monitoring(self):
        """モニタリング停止"""
        self.is_monitoring = False

        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("⏹️ モニタリング停止")

    async def _monitoring_loop(self):
        """モニタリングループ"""
        try:
            while self.is_monitoring:
                # ヘルスチェック実行
                await self.perform_health_check()

                # 次のチェックまで待機
                await asyncio.sleep(self.check_interval)

        except asyncio.CancelledError:
            logger.info("モニタリングループがキャンセルされました")
        except Exception as e:
            logger.error(f"❌ モニタリングループエラー: {e}", exc_info=True)

    async def perform_health_check(self) -> Dict[str, Any]:
        """ヘルスチェックを実行"""
        try:
            check_time = datetime.now()
            self.stats["health_checks"] += 1
            self.stats["total_checks"] += 1

            # メトリクス収集
            metrics = {
                "timestamp": check_time.isoformat(),
                "system": await self._collect_system_metrics(),
                "process": await self._collect_process_metrics(),
                "application": await self._collect_application_metrics(),
            }

            # ヘルスステータス判定
            health_status = self._determine_health_status(metrics)
            metrics["health_status"] = health_status.value

            # 履歴に追加
            self.metrics_history.append(metrics)

            # 古い履歴を削除（直近100件のみ保持）
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]

            # アラートチェック
            await self._check_and_issue_alerts(metrics, health_status)

            # 統計更新
            self._update_statistics(metrics)

            logger.debug(
                f"✅ ヘルスチェック完了: {health_status.value} "
                f"(CPU={metrics['system']['cpu_percent']:.1f}%, "
                f"Memory={metrics['system']['memory_percent']:.1f}%)"
            )

            return {"success": True, "health_status": health_status.value, "metrics": metrics}

        except Exception as e:
            logger.error(f"❌ ヘルスチェックエラー: {e}")
            return {"success": False, "error": str(e)}

    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """システムメトリクスを収集"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # メモリ使用率
            memory = psutil.virtual_memory()

            # ディスク使用率
            disk = psutil.disk_usage("/")

            # ネットワーク統計
            net_io = psutil.net_io_counters()

            return {
                "cpu_percent": cpu_percent,
                "cpu_count": cpu_count,
                "memory_percent": memory.percent,
                "memory_used_gb": memory.used / (1024**3),
                "memory_total_gb": memory.total / (1024**3),
                "disk_percent": disk.percent,
                "disk_used_gb": disk.used / (1024**3),
                "disk_total_gb": disk.total / (1024**3),
                "network_bytes_sent": net_io.bytes_sent,
                "network_bytes_recv": net_io.bytes_recv,
            }

        except Exception as e:
            logger.error(f"❌ システムメトリクス収集エラー: {e}")
            return {}

    async def _collect_process_metrics(self) -> Dict[str, Any]:
        """プロセスメトリクスを収集"""
        try:
            process = psutil.Process(os.getpid())

            # プロセス情報
            with process.oneshot():
                cpu_percent = process.cpu_percent()
                memory_info = process.memory_info()
                num_threads = process.num_threads()
                open_files = len(process.open_files())

            return {
                "pid": process.pid,
                "cpu_percent": cpu_percent,
                "memory_mb": memory_info.rss / (1024**2),
                "num_threads": num_threads,
                "open_files": open_files,
                "status": process.status(),
            }

        except Exception as e:
            logger.error(f"❌ プロセスメトリクス収集エラー: {e}")
            return {}

    async def _collect_application_metrics(self) -> Dict[str, Any]:
        """アプリケーションメトリクスを収集"""
        try:
            # 稼働時間
            uptime = (datetime.now() - self.start_time).total_seconds()

            return {
                "uptime_seconds": uptime,
                "uptime_hours": uptime / 3600,
                "total_health_checks": self.stats["health_checks"],
                "warnings_issued": self.stats["warnings_issued"],
                "critical_alerts": self.stats["critical_alerts"],
            }

        except Exception as e:
            logger.error(f"❌ アプリケーションメトリクス収集エラー: {e}")
            return {}

    def _determine_health_status(self, metrics: Dict[str, Any]) -> HealthStatus:
        """ヘルスステータスを判定"""
        try:
            system = metrics.get("system", {})

            # Critical条件チェック
            if (
                system.get("cpu_percent", 0) > 95
                or system.get("memory_percent", 0) > 95
                or system.get("disk_percent", 0) > 95
            ):
                return HealthStatus.CRITICAL

            # Warning条件チェック
            if (
                system.get("cpu_percent", 0) > self.cpu_threshold
                or system.get("memory_percent", 0) > self.memory_threshold
                or system.get("disk_percent", 0) > self.disk_threshold
            ):
                return HealthStatus.WARNING

            # Healthy
            return HealthStatus.HEALTHY

        except Exception as e:
            logger.error(f"❌ ヘルスステータス判定エラー: {e}")
            return HealthStatus.UNKNOWN

    async def _check_and_issue_alerts(self, metrics: Dict[str, Any], health_status: HealthStatus):
        """アラートをチェックして発行"""
        try:
            system = metrics.get("system", {})
            timestamp = metrics.get("timestamp")

            alerts = []

            # CPU警告
            if system.get("cpu_percent", 0) > self.cpu_threshold:
                alerts.append(
                    {
                        "level": "warning" if health_status == HealthStatus.WARNING else "critical",
                        "type": "cpu_usage",
                        "message": f"CPU使用率が高い: {system['cpu_percent']:.1f}%",
                        "value": system["cpu_percent"],
                        "threshold": self.cpu_threshold,
                        "timestamp": timestamp,
                    }
                )

            # メモリ警告
            if system.get("memory_percent", 0) > self.memory_threshold:
                alerts.append(
                    {
                        "level": "warning" if health_status == HealthStatus.WARNING else "critical",
                        "type": "memory_usage",
                        "message": f"メモリ使用率が高い: {system['memory_percent']:.1f}%",
                        "value": system["memory_percent"],
                        "threshold": self.memory_threshold,
                        "timestamp": timestamp,
                    }
                )

            # ディスク警告
            if system.get("disk_percent", 0) > self.disk_threshold:
                alerts.append(
                    {
                        "level": "warning" if health_status == HealthStatus.WARNING else "critical",
                        "type": "disk_usage",
                        "message": f"ディスク使用率が高い: {system['disk_percent']:.1f}%",
                        "value": system["disk_percent"],
                        "threshold": self.disk_threshold,
                        "timestamp": timestamp,
                    }
                )

            # アラートを記録
            for alert in alerts:
                self.alerts.append(alert)

                if alert["level"] == "critical":
                    self.stats["critical_alerts"] += 1
                    logger.critical(f"🚨 CRITICAL: {alert['message']}")
                else:
                    self.stats["warnings_issued"] += 1
                    logger.warning(f"⚠️ WARNING: {alert['message']}")

            # 古いアラートを削除（直近50件のみ保持）
            if len(self.alerts) > 50:
                self.alerts = self.alerts[-50:]

        except Exception as e:
            logger.error(f"❌ アラートチェックエラー: {e}")

    def _update_statistics(self, metrics: Dict[str, Any]):
        """統計情報を更新"""
        try:
            system = metrics.get("system", {})

            # 移動平均を計算
            n = self.stats["health_checks"]

            self.stats["avg_cpu_usage"] = (self.stats["avg_cpu_usage"] * (n - 1) + system.get("cpu_percent", 0)) / n

            self.stats["avg_memory_usage"] = (
                self.stats["avg_memory_usage"] * (n - 1) + system.get("memory_percent", 0)
            ) / n

        except Exception as e:
            logger.error(f"❌ 統計更新エラー: {e}")

    def get_current_status(self) -> Dict[str, Any]:
        """現在のステータスを取得"""
        if not self.metrics_history:
            return {"status": "no_data", "message": "モニタリングデータがありません"}

        latest_metrics = self.metrics_history[-1]

        return {
            "status": latest_metrics.get("health_status", "unknown"),
            "timestamp": latest_metrics.get("timestamp"),
            "system": latest_metrics.get("system", {}),
            "process": latest_metrics.get("process", {}),
            "application": latest_metrics.get("application", {}),
            "recent_alerts": self.alerts[-5:] if self.alerts else [],
        }

    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        uptime = (datetime.now() - self.start_time).total_seconds()

        return {
            **self.stats,
            "uptime_seconds": uptime,
            "uptime_hours": uptime / 3600,
            "is_monitoring": self.is_monitoring,
            "metrics_count": len(self.metrics_history),
            "alerts_count": len(self.alerts),
        }

    def print_status(self):
        """ステータスを表示"""
        status = self.get_current_status()
        stats = self.get_stats()

        print("\n" + "=" * 80)
        print("🔍 システムモニタリング ステータス")
        print("=" * 80)
        print(f"ヘルスステータス: {status.get('status', 'unknown').upper()}")
        print(f"稼働時間: {stats['uptime_hours']:.1f}時間")
        print(f"\n【システムリソース】")
        system = status.get("system", {})
        print(f"  CPU使用率: {system.get('cpu_percent', 0):.1f}%")
        print(f"  メモリ使用率: {system.get('memory_percent', 0):.1f}%")
        print(f"  ディスク使用率: {system.get('disk_percent', 0):.1f}%")
        print(f"\n【統計】")
        print(f"  ヘルスチェック: {stats['health_checks']}回")
        print(f"  警告発行: {stats['warnings_issued']}回")
        print(f"  重要アラート: {stats['critical_alerts']}回")
        print(f"  平均CPU: {stats['avg_cpu_usage']:.1f}%")
        print(f"  平均メモリ: {stats['avg_memory_usage']:.1f}%")

        if status.get("recent_alerts"):
            print(f"\n【最近のアラート】")
            for alert in status["recent_alerts"]:
                print(f"  - [{alert['level'].upper()}] {alert['message']}")

        print("=" * 80 + "\n")
