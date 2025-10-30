#!/usr/bin/env python3
"""
レート制限対策モジュール

Google Sheets APIの制限を自動で回避する汎用モジュール
"""

import time
from typing import Callable, Any, List
from functools import wraps

class RateLimiter:
    """レート制限対策クラス"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.request_count = 0
        self.last_request_time = 0
    
    def wait_if_needed(self):
        """必要に応じて待機"""
        current_time = time.time()
        
        # 1秒以内に複数リクエストがある場合は待機
        if current_time - self.last_request_time < 1.0:
            time.sleep(1.0)
        
        self.last_request_time = time.time()
        self.request_count += 1
        
        # 10リクエストごとに長めの待機
        if self.request_count % 10 == 0:
            time.sleep(2.0)
    
    def with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """リトライ付きで関数実行"""
        
        for attempt in range(self.max_retries):
            try:
                self.wait_if_needed()
                return func(*args, **kwargs)
            
            except Exception as e:
                error_str = str(e)
                
                # レート制限エラー（429）
                if '429' in error_str or 'quota' in error_str.lower():
                    if attempt < self.max_retries - 1:
                        # Exponential Backoff
                        delay = self.base_delay * (2 ** attempt)
                        print(f"   ⚠️  レート制限検知 - {delay}秒待機...")
                        time.sleep(delay)
                        continue
                
                # その他のエラー
                raise e
        
        raise Exception(f"リトライ上限({self.max_retries}回)に達しました")

def batch_write(data: List[List], sheet, batch_size: int = 50, rate_limiter: RateLimiter = None):
    """
    バッチ書き込み（レート制限対策）
    
    Args:
        data: 書き込むデータ（2次元配列）
        sheet: gspreadのworksheetオブジェクト
        batch_size: バッチサイズ
        rate_limiter: RateLimiterインスタンス
    """
    
    if rate_limiter is None:
        rate_limiter = RateLimiter()
    
    total = len(data)
    
    for i in range(0, total, batch_size):
        batch = data[i:i+batch_size]
        
        # リトライ付きで書き込み
        rate_limiter.with_retry(sheet.append_rows, batch)
        
        progress = min(i + batch_size, total)
        print(f"      進捗: {progress}/{total}件")
