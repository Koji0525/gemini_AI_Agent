"""
Slack通知機能
実行結果をSlackに自動通知
"""

import requests
import json
import os
from typing import Dict
from datetime import datetime


class SlackNotifier:
    """Slack通知"""

    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")

        if not self.webhook_url:
            print("⚠️ SLACK_WEBHOOK_URLが設定されていません")

    def send_success_notification(self, result: Dict):
        """成功通知を送信"""

        if not self.webhook_url:
            print("⚠️ Slack通知スキップ（Webhook未設定）")
            return

        results_data = result["results"]

        message = {
            "blocks": [
                {"type": "header", "text": {"type": "plain_text", "text": "✅ WordPress自動投稿完了"}},
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*ステータス:*\n{result['status'].upper()}"},
                        {"type": "mrkdwn", "text": f"*実行時間:*\n{result['execution_time']}"},
                        {"type": "mrkdwn", "text": f"*成功:*\n{results_data['successful_posts']}社"},
                        {"type": "mrkdwn", "text": f"*品質スコア:*\n{results_data['quality_score']:.1f}/10"},
                    ],
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*投稿ID:*\n" + ", ".join([f"#{pid}" for pid in results_data["post_ids"][:3]]),
                    },
                },
            ]
        }

        try:
            response = requests.post(self.webhook_url, json=message)
            if response.status_code == 200:
                print("✅ Slack通知送信成功")
            else:
                print(f"⚠️ Slack通知送信失敗: {response.status_code}")
        except Exception as e:
            print(f"❌ Slack通知エラー: {e}")

    def send_error_notification(self, error_message: str):
        """エラー通知を送信"""

        if not self.webhook_url:
            return

        message = {
            "blocks": [
                {"type": "header", "text": {"type": "plain_text", "text": "⚠️ WordPress自動投稿エラー"}},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"```{error_message}```"}},
            ]
        }

        try:
            requests.post(self.webhook_url, json=message)
            print("✅ エラー通知送信")
        except Exception as e:
            print(f"❌ エラー通知失敗: {e}")
