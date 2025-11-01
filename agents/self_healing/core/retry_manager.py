#!/usr/bin/env python3
"""
適応的リトライマネージャー - Phase 5
"""

import time
import logging
from typing import Callable, Any, Dict
from enum import Enum

class RetryStrategy(Enum):
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    FIXED_INTERVAL = "fixed_interval"
    RATE_LIMIT = "rate_limit"

class RetryManager:
    """適応的リトライマネージャー"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.logger = logging.getLogger(__name__)
    
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """リトライ付きで関数を実行"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                self.logger.info(f"🔄 試行 {attempt + 1}/{self.max_retries + 1}")
                return func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                self.logger.warning(f"❌ 試行 {attempt + 1} 失敗: {e}")
                
                if attempt < self.max_retries:
                    delay = self.calculate_delay(attempt, str(e))
                    self.logger.info(f"⏰ {delay}秒後に再試行...")
                    time.sleep(delay)
                else:
                    self.logger.error(f"💥 全 {self.max_retries + 1} 回の試行が失敗")
                    raise last_exception
        
        raise last_exception
    
    def calculate_delay(self, attempt: int, error_message: str) -> float:
        """試行回数とエラーに基づいて待機時間を計算"""
        # エラータイプに応じた戦略選択
        if "timeout" in error_message.lower():
            return self.base_delay * (2 ** attempt)  # 指数バックオフ
        elif "rate_limit" in error_message.lower():
            return 60.0  # レート制限時は60秒待機
        else:
            return self.base_delay * (attempt + 1)  # 線形増加
    
    def get_retry_delay(self, attempt: int) -> float:
        """リトライ待機時間を取得"""
        return self.calculate_delay(attempt, "")

if __name__ == "__main__":
    # テストコード
    def failing_function():
        raise Exception("テストエラー")
    
    manager = RetryManager(max_retries=2)
    try:
        manager.execute_with_retry(failing_function)
    except Exception as e:
        print(f"期待通りの失敗: {e}")
