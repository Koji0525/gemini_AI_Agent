"""
通知マネージャー

アラートをSlack/メール/ログで通知
"""

import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """通知チャネル"""

    SLACK = "slack"
    EMAIL = "email"
    LOG = "log"
    WEBHOOK = "webhook"


class NotificationPriority(Enum):
    """通知優先度"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationManager:
    """通知マネージャー"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初期化

        Args:
            config_path: 設定ファイルパス
        """
        self.config_path = config_path or "config/notification_config.json"
        self.config = self._load_config()
        self.notification_log = Path("logs/notifications.json")
        self.notification_log.parent.mkdir(exist_ok=True)

        # 通知履歴
        self.history = self._load_history()

        logger.info(f"Initialized NotificationManager")

    def _load_config(self) -> Dict[str, Any]:
        """設定読み込み"""
        default_config = {
            "channels": {
                "slack": {"enabled": False, "webhook_url": "", "default_channel": "#alerts"},
                "email": {
                    "enabled": False,
                    "smtp_server": "",
                    "smtp_port": 587,
                    "from_address": "",
                    "to_addresses": [],
                },
                "log": {"enabled": True, "level": "INFO"},
            },
            "rules": {
                "critical": ["slack", "email", "log"],
                "high": ["slack", "log"],
                "medium": ["log"],
                "low": ["log"],
            },
            "rate_limit": {"enabled": True, "max_per_hour": 10, "max_per_day": 50},
        }

        config_path = Path(self.config_path)
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)
                logger.info(f"Loaded config from {config_path}")
                return config
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using default")

        # デフォルト設定を保存
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def _load_history(self) -> List[Dict[str, Any]]:
        """通知履歴読み込み"""
        if self.notification_log.exists():
            try:
                with open(self.notification_log) as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_history(self):
        """通知履歴保存"""
        try:
            with open(self.notification_log, "w") as f:
                json.dump(self.history[-1000:], f, indent=2)  # 最新1000件
        except Exception as e:
            logger.error(f"Failed to save notification history: {e}")

    def _check_rate_limit(self) -> bool:
        """
        レート制限チェック

        Returns:
            通知可能ならTrue
        """
        if not self.config.get("rate_limit", {}).get("enabled", True):
            return True

        now = datetime.now()
        hour_ago = now.timestamp() - 3600
        day_ago = now.timestamp() - 86400

        # 過去1時間・24時間の通知数をカウント
        recent_hour = sum(
            1 for n in self.history if datetime.fromisoformat(n["timestamp"]).timestamp() > hour_ago
        )
        recent_day = sum(
            1 for n in self.history if datetime.fromisoformat(n["timestamp"]).timestamp() > day_ago
        )

        max_hour = self.config["rate_limit"].get("max_per_hour", 10)
        max_day = self.config["rate_limit"].get("max_per_day", 50)

        if recent_hour >= max_hour:
            logger.warning(f"Rate limit exceeded: {recent_hour}/{max_hour} per hour")
            return False

        if recent_day >= max_day:
            logger.warning(f"Rate limit exceeded: {recent_day}/{max_day} per day")
            return False

        return True

    def send_notification(
        self,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        通知送信

        Args:
            title: タイトル
            message: メッセージ
            priority: 優先度
            metadata: 追加メタデータ

        Returns:
            送信成功ならTrue
        """
        try:
            # レート制限チェック
            if not self._check_rate_limit():
                logger.warning("Notification skipped due to rate limit")
                return False

            # 送信チャネル決定
            channels = self.config["rules"].get(priority.value, ["log"])

            notification = {
                "timestamp": datetime.now().isoformat(),
                "title": title,
                "message": message,
                "priority": priority.value,
                "channels": channels,
                "metadata": metadata or {},
                "status": "sent",
            }

            # チャネルごとに送信
            success = True
            for channel in channels:
                try:
                    if channel == "slack":
                        self._send_slack(notification)
                    elif channel == "email":
                        self._send_email(notification)
                    elif channel == "log":
                        self._send_log(notification)
                    elif channel == "webhook":
                        self._send_webhook(notification)
                except Exception as e:
                    logger.error(f"Failed to send to {channel}: {e}")
                    success = False

            # 履歴に記録
            self.history.append(notification)
            self._save_history()

            logger.info(
                f"Notification sent: {title} " f"(priority={priority.value}, channels={channels})"
            )

            return success

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    def _send_slack(self, notification: Dict[str, Any]):
        """Slack通知"""
        slack_config = self.config["channels"]["slack"]
        if not slack_config.get("enabled", False):
            logger.debug("Slack disabled, skipping")
            return

        # TODO: 実際のSlack APIコール実装
        logger.info(f"[SLACK] {notification['title']}: {notification['message']}")

    def _send_email(self, notification: Dict[str, Any]):
        """メール通知"""
        email_config = self.config["channels"]["email"]
        if not email_config.get("enabled", False):
            logger.debug("Email disabled, skipping")
            return

        # TODO: 実際のメール送信実装
        logger.info(f"[EMAIL] {notification['title']}: {notification['message']}")

    def _send_log(self, notification: Dict[str, Any]):
        """ログ通知"""
        priority = notification["priority"]
        title = notification["title"]
        message = notification["message"]

        log_msg = f"[{priority.upper()}] {title}: {message}"

        if priority == "critical":
            logger.critical(log_msg)
        elif priority == "high":
            logger.error(log_msg)
        elif priority == "medium":
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

    def _send_webhook(self, notification: Dict[str, Any]):
        """Webhook通知"""
        # TODO: 実装
        logger.info(f"[WEBHOOK] {notification['title']}: {notification['message']}")

    def get_history(
        self, limit: int = 50, priority: Optional[NotificationPriority] = None
    ) -> List[Dict[str, Any]]:
        """
        通知履歴取得

        Args:
            limit: 取得数
            priority: 優先度フィルタ

        Returns:
            通知履歴
        """
        history = self.history

        if priority:
            history = [n for n in history if n["priority"] == priority.value]

        return history[-limit:]

    def send_alert_notification(self, alert: Dict[str, Any]) -> bool:
        """
        アラート通知

        Args:
            alert: アラート情報

        Returns:
            送信成功ならTrue
        """
        # アラートの重要度を通知優先度にマッピング
        severity_map = {
            "critical": NotificationPriority.CRITICAL,
            "high": NotificationPriority.HIGH,
            "medium": NotificationPriority.MEDIUM,
            "low": NotificationPriority.LOW,
        }

        priority = severity_map.get(alert.get("severity", "medium"), NotificationPriority.MEDIUM)

        title = f"🚨 {alert.get('title', 'System Alert')}"
        message = alert.get("message", "")

        return self.send_notification(
            title=title,
            message=message,
            priority=priority,
            metadata={"alert_id": alert.get("id"), "source": "alert_manager"},
        )


# テストコード
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    manager = NotificationManager()

    print("【NotificationManager テスト】")
    print()

    # 1. 低優先度通知
    print("1. 低優先度通知...")
    success = manager.send_notification(
        title="システム起動",
        message="Enhanced Observer Systemが起動しました",
        priority=NotificationPriority.LOW,
    )
    print(f"   {'✅' if success else '❌'} 送信完了")

    # 2. 高優先度通知
    print("\n2. 高優先度通知...")
    success = manager.send_notification(
        title="ヘルススコア低下",
        message="システムヘルススコアが30点を下回りました",
        priority=NotificationPriority.HIGH,
        metadata={"current_score": 28.5},
    )
    print(f"   {'✅' if success else '❌'} 送信完了")

    # 3. 通知履歴
    print("\n3. 通知履歴...")
    history = manager.get_history(limit=10)
    print(f"   総数: {len(history)}件")
    for n in history[-3:]:
        print(f"   - [{n['priority']}] {n['title']}")

    print("\n✅ NotificationManager テスト完了")
