#!/usr/bin/env python3
"""
RateLimiter: Google Sheets APIレート制限対策

1分間に60リクエストの制限を回避するための
スマートレート制限機能。
"""
import time
from datetime import datetime, timedelta
from collections import deque


class RateLimiter:
    """シンプルなレート制限機能"""
    
    def __init__(self, max_requests: int = 50, time_window: int = 60):
        """
        初期化
        
        Args:
            max_requests: 時間枠内の最大リクエスト数（デフォルト: 50/分）
            time_window: 時間枠（秒）（デフォルト: 60秒）
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
    
    def wait_if_needed(self):
        """必要に応じて待機"""
        now = datetime.now()
        
        # 古いリクエストを削除
        cutoff = now - timedelta(seconds=self.time_window)
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()
        
        # リクエスト数が上限に達している場合は待機
        if len(self.requests) >= self.max_requests:
            oldest = self.requests[0]
            wait_time = (oldest + timedelta(seconds=self.time_window) - now).total_seconds()
            
            if wait_time > 0:
                print(f"⏳ レート制限: {wait_time:.1f}秒待機中...")
                time.sleep(wait_time + 0.1)  # 少し余裕を持たせる
        
        # リクエストを記録
        self.requests.append(now)


# グローバルインスタンス
_global_rate_limiter = RateLimiter(max_requests=50, time_window=60)


def apply_rate_limit():
    """レート制限を適用（デコレータとしても使用可能）"""
    _global_rate_limiter.wait_if_needed()
