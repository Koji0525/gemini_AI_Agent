# notification_agent.py
"""
通知エージェント
Slack/メール/その他の通知管理
"""

import asyncio
import logging
import json
import smtplib
from typing import Dict, Any, List, Optional
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from enum import Enum

import aiohttp

logger = logging.getLogger(__name__)


class NotificationLevel(Enum):
    """通知レベル"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SUCCESS = "success"


class NotificationChannel(Enum):
    """通知チャネル"""
    SLACK = "slack"
    EMAIL = "email"
    DISCORD = "discord"
    WEBHOOK = "webhook"


class NotificationAgent:
    """
    通知エージェント
    
    機能:
    - Slack通知
    - メール通知
    - Discord通知
    - Webhook通知
    - 通知のフィルタリング
    - 通知テンプレート管理
    """
    
    def __init__(
        self,
        slack_webhook_url: Optional[str] = None,
        email_config: Optional[Dict[str, str]] = None,
        discord_webhook_url: Optional[str] = None,
        min_notification_level: NotificationLevel = NotificationLevel.WARNING
    ):
        """
        初期化
        
        Args:
            slack_webhook_url: Slack Webhook URL
            email_config: メール設定（smtp_server, smtp_port, username, password, recipients）
            discord_webhook_url: Discord Webhook URL
            min_notification_level: 最小通知レベル
        """
        self.slack_webhook_url = slack_webhook_url
        self.email_config = email_config or {}
        self.discord_webhook_url = discord_webhook_url
        self.min_notification_level = min_notification_level
        
        # 通知履歴
        self.notification_history = []
        
        # 統計情報
        self.stats = {
            "total_notifications": 0,
            "slack_notifications": 0,
            "email_notifications": 0,
            "discord_notifications": 0,
            "failed_notifications": 0
        }
        
        # 通知テンプレート
        self._init_templates()
        
        logger.info("✅ NotificationAgent 初期化完了")
    
    def _init_templates(self):
        """通知テンプレートを初期化"""
        self.templates = {
            "fix_success": {
                "title": "✅ 自動修正成功",
                "color": "#36a64f",
                "emoji": "✅"
            },
            "fix_failure": {
                "title": "❌ 自動修正失敗",
                "color": "#ff0000",
                "emoji": "❌"
            },
            "error_detected": {
                "title": "🔍 エラー検出",
                "color": "#ff9900",
                "emoji": "🔍"
            },
            "system_warning": {
                "title": "⚠️ システム警告",
                "color": "#ffcc00",
                "emoji": "⚠️"
            },
            "system_critical": {
                "title": "🚨 システム重大",
                "color": "#cc0000",
                "emoji": "🚨"
            },
            "pr_created": {
                "title": "🌿 PR作成完了",
                "color": "#0366d6",
                "emoji": "🌿"
            }
        }
    
    async def send_notification(
        self,
        message: str,
        level: NotificationLevel = NotificationLevel.INFO,
        channels: Optional[List[NotificationChannel]] = None,
        template_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        通知を送信
        
        Args:
            message: 通知メッセージ
            level: 通知レベル
            channels: 通知チャネル（省略時は全チャネル）
            template_name: テンプレート名
            metadata: 追加メタデータ
            
        Returns:
            Dict: 送信結果
        """
        try:
            # レベルフィルタリング
            if not self._should_notify(level):
                logger.debug(f"通知スキップ: レベル={level.value}")
                return {"success": True, "skipped": True}
            
            self.stats["total_notifications"] += 1
            
            # チャネルの決定
            if channels is None:
                channels = self._get_available_channels()
            
            # 通知内容を構築
            notification = self._build_notification(
                message=message,
                level=level,
                template_name=template_name,
                metadata=metadata
            )
            
            # 各チャネルに送信
            results = {}
            
            for channel in channels:
                try:
                    if channel == NotificationChannel.SLACK:
                        result = await self._send_slack_notification(notification)
                        results["slack"] = result
                        
                    elif channel == NotificationChannel.EMAIL:
                        result = await self._send_email_notification(notification)
                        results["email"] = result
                        
                    elif channel == NotificationChannel.DISCORD:
                        result = await self._send_discord_notification(notification)
                        results["discord"] = result
                        
                except Exception as e:
                    logger.error(f"❌ {channel.value}通知エラー: {e}")
                    results[channel.value] = {"success": False, "error": str(e)}
                    self.stats["failed_notifications"] += 1
            
            # 履歴に追加
            self.notification_history.append({
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "level": level.value,
                "channels": [c.value for c in channels],
                "results": results
            })
            
            # 古い履歴を削除（直近100件のみ）
            if len(self.notification_history) > 100:
                self.notification_history = self.notification_history[-100:]
            
            logger.info(f"📤 通知送信完了: {message[:50]}...")
            
            return {
                "success": True,
                "channels": results
            }
            
        except Exception as e:
            logger.error(f"❌ 通知送信エラー: {e}", exc_info=True)
            self.stats["failed_notifications"] += 1
            return {
                "success": False,
                "error": str(e)
            }
    
    async def notify_fix_success(
        self,
        task_id: str,
        modified_files: List[str],
        execution_time: float,
        confidence: float
    ):
        """修正成功の通知"""
        message = (
            f"タスク {task_id} の自動修正が成功しました\n"
            f"修正ファイル: {', '.join(modified_files)}\n"
            f"実行時間: {execution_time:.2f}秒\n"
            f"信頼度: {confidence:.1%}"
        )
        
        await self.send_notification(
            message=message,
            level=NotificationLevel.SUCCESS,
            template_name="fix_success",
            metadata={
                "task_id": task_id,
                "modified_files": modified_files,
                "execution_time": execution_time,
                "confidence": confidence
            }
        )
    
    async def notify_fix_failure(
        self,
        task_id: str,
        error_message: str
    ):
        """修正失敗の通知"""
        message = (
            f"タスク {task_id} の自動修正が失敗しました\n"
            f"エラー: {error_message}\n"
            f"手動介入が必要です"
        )
        
        await self.send_notification(
            message=message,
            level=NotificationLevel.ERROR,
            template_name="fix_failure",
            metadata={
                "task_id": task_id,
                "error_message": error_message
            }
        )
    
    async def notify_system_warning(
        self,
        warning_type: str,
        details: str
    ):
        """システム警告の通知"""
        message = f"システム警告: {warning_type}\n詳細: {details}"
        
        await self.send_notification(
            message=message,
            level=NotificationLevel.WARNING,
            template_name="system_warning",
            metadata={
                "warning_type": warning_type,
                "details": details
            }
        )
    
    async def notify_pr_created(
        self,
        task_id: str,
        pr_url: str,
        branch_name: str
    ):
        """PR作成の通知"""
        message = (
            f"タスク {task_id} の修正PRが作成されました\n"
            f"ブランチ: {branch_name}\n"
            f"PR URL: {pr_url}"
        )
        
        await self.send_notification(
            message=message,
            level=NotificationLevel.INFO,
            template_name="pr_created",
            metadata={
                "task_id": task_id,
                "pr_url": pr_url,
                "branch_name": branch_name
            }
        )
    
    # ========================================
    # 内部メソッド
    # ========================================
    
    def _should_notify(self, level: NotificationLevel) -> bool:
        """通知すべきかチェック"""
        level_priority = {
            NotificationLevel.INFO: 0,
            NotificationLevel.SUCCESS: 1,
            NotificationLevel.WARNING: 2,
            NotificationLevel.ERROR: 3,
            NotificationLevel.CRITICAL: 4
        }
        
        return level_priority.get(level, 0) >= level_priority.get(self.min_notification_level, 0)
    
    def _get_available_channels(self) -> List[NotificationChannel]:
        """利用可能なチャネルを取得"""
        channels = []
        
        if self.slack_webhook_url:
            channels.append(NotificationChannel.SLACK)
        
        if self.email_config.get("smtp_server"):
            channels.append(NotificationChannel.EMAIL)
        
        if self.discord_webhook_url:
            channels.append(NotificationChannel.DISCORD)
        
        return channels
    
    def _build_notification(
        self,
        message: str,
        level: NotificationLevel,
        template_name: Optional[str],
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """通知内容を構築"""
        template = self.templates.get(template_name, {}) if template_name else {}
        
        return {
            "message": message,
            "level": level.value,
            "title": template.get("title", f"{level.value.upper()} Notification"),
            "color": template.get("color", "#cccccc"),
            "emoji": template.get("emoji", "📢"),
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
    
    async def _send_slack_notification(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Slack通知を送信"""
        if not self.slack_webhook_url:
            return {"success": False, "error": "Slack webhook URL not configured"}
        
        try:
            # Slackペイロード構築
            payload = {
                "text": f"{notification['emoji']} {notification['title']}",
                "attachments": [{
                    "color": notification['color'],
                    "text": notification['message'],
                    "footer": "Hybrid Fix System",
                    "ts": int(datetime.now().timestamp())
                }]
            }
            
            # メタデータを追加
            if notification.get('metadata'):
                fields = []
                for key, value in notification['metadata'].items():
                    fields.append({
                        "title": key,
                        "value": str(value),
                        "short": True
                    })
                payload["attachments"][0]["fields"] = fields
            
            # Webhook送信
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.slack_webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        self.stats["slack_notifications"] += 1
                        return {"success": True}
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
            
        except Exception as e:
            logger.error(f"❌ Slack通知エラー: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_email_notification(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """メール通知を送信"""
        if not self.email_config.get("smtp_server"):
            return {"success": False, "error": "Email not configured"}
        
        try:
            # メール作成
            msg = MIMEMultipart()
            msg['From'] = self.email_config.get("username", "noreply@example.com")
            msg['To'] = self.email_config.get("recipients", "admin@example.com")
            msg['Subject'] = f"{notification['emoji']} {notification['title']}"
            
            # 本文
            body = f"""
{notification['title']}

{notification['message']}

---
Timestamp: {notification['timestamp']}
System: Hybrid Fix System
"""
            
            if notification.get('metadata'):
                body += "\nDetails:\n"
                for key, value in notification['metadata'].items():
                    body += f"  {key}: {value}\n"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # SMTP送信
            await asyncio.to_thread(self._send_smtp_email, msg)
            
            self.stats["email_notifications"] += 1
            return {"success": True}
            
        except Exception as e:
            logger.error(f"❌ メール通知エラー: {e}")
            return {"success": False, "error": str(e)}
    
    def _send_smtp_email(self, msg: MIMEMultipart):
        """SMTP経由でメール送信（同期）"""
        server = smtplib.SMTP(
            self.email_config["smtp_server"],
            int(self.email_config.get("smtp_port", 587))
        )
        server.starttls()
        server.login(
            self.email_config["username"],
            self.email_config["password"]
        )
        server.send_message(msg)
        server.quit()
    
    async def _send_discord_notification(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Discord通知を送信"""
        if not self.discord_webhook_url:
            return {"success": False, "error": "Discord webhook URL not configured"}
        
        try:
            # Discordペイロード構築
            payload = {
                "content": f"{notification['emoji']} **{notification['title']}**",
                "embeds": [{
                    "description": notification['message'],
                    "color": int(notification['color'].replace('#', ''), 16),
                    "timestamp": notification['timestamp'],
                    "footer": {
                        "text": "Hybrid Fix System"
                    }
                }]
            }
            
            # メタデータを追加
            if notification.get('metadata'):
                fields = []
                for key, value in notification['metadata'].items():
                    fields.append({
                        "name": key,
                        "value": str(value),
                        "inline": True
                    })
                payload["embeds"][0]["fields"] = fields
            
            # Webhook送信
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.discord_webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status in [200, 204]:
                        self.stats["discord_notifications"] += 1
                        return {"success": True}
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
            
        except Exception as e:
            logger.error(f"❌ Discord通知エラー: {e}")
            return {"success": False, "error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        success_rate = 0.0
        if self.stats["total_notifications"] > 0:
            success_rate = (
                (self.stats["total_notifications"] - self.stats["failed_notifications"]) /
                self.stats["total_notifications"]
            )
        
        return {
            **self.stats,
            "success_rate": success_rate,
            "recent_notifications": self.notification_history[-10:]
        }
    
    def print_stats(self):
        """統計情報を表示"""
        stats = self.get_stats()
        
        print("\n" + "=" * 80)
        print("📤 通知エージェント 統計情報")
        print("=" * 80)
        print(f"総通知数: {stats['total_notifications']}")
        print(f"成功率: {stats['success_rate']:.1%}")
        print(f"\nチャネル別:")
        print(f"  Slack: {stats['slack_notifications']}回")
        print(f"  メール: {stats['email_notifications']}回")
        print(f"  Discord: {stats['discord_notifications']}回")
        print(f"\n失敗: {stats['failed_notifications']}回")
        print("=" * 80 + "\n")