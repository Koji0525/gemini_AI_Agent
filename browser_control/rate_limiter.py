"""
レート制限対策モジュール
"""

import asyncio
import time
from datetime import datetime, timedelta


class RateLimiter:
    """
    レート制限を管理するクラス
    """

    def __init__(
        self, max_requests_per_hour: int = 50, min_interval_seconds: int = 30  # 1時間あたり最大50回  # 最小30秒間隔
    ):
        self.max_requests_per_hour = max_requests_per_hour
        self.min_interval_seconds = min_interval_seconds
        self.request_history = []  # 実行履歴
        self.last_request_time = None

    async def wait_if_needed(self):
        """
        必要に応じて待機する
        """
        now = datetime.now()

        # 1. 最小間隔のチェック
        if self.last_request_time:
            elapsed = (now - self.last_request_time).total_seconds()

            if elapsed < self.min_interval_seconds:
                wait_time = self.min_interval_seconds - elapsed
                print(f"⏳ レート制限: {wait_time:.1f}秒待機中...")
                await asyncio.sleep(wait_time)

        # 2. 1時間あたりの実行回数チェック
        one_hour_ago = now - timedelta(hours=1)
        self.request_history = [t for t in self.request_history if t > one_hour_ago]

        if len(self.request_history) >= self.max_requests_per_hour:
            # 最も古いリクエストから1時間経つまで待機
            oldest_request = min(self.request_history)
            wait_until = oldest_request + timedelta(hours=1)
            wait_seconds = (wait_until - now).total_seconds()

            if wait_seconds > 0:
                print(f"⚠️  1時間の制限到達: {wait_seconds/60:.1f}分待機します...")
                await asyncio.sleep(wait_seconds)

        # 3. 記録
        self.last_request_time = now
        self.request_history.append(now)

    def get_stats(self):
        """
        統計情報を取得
        """
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        recent_requests = [t for t in self.request_history if t > one_hour_ago]

        return {
            "requests_last_hour": len(recent_requests),
            "max_per_hour": self.max_requests_per_hour,
            "remaining": self.max_requests_per_hour - len(recent_requests),
        }
