#!/usr/bin/env python3
"""
Google Sheets API リトライヘルパー
503エラー等の一時的なエラーに対応
"""

import asyncio
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)


def retry_on_api_error(max_retries: int = 3, base_delay: float = 1.0):
    """
    APIエラー時の自動リトライデコレータ

    Args:
        max_retries: 最大リトライ回数
        base_delay: 基本待機時間（秒）

    【対応エラー】
    - 503 Service Unavailable
    - 429 Too Many Requests
    - 500 Internal Server Error
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)

                except Exception as e:
                    error_str = str(e)

                    # リトライ対象エラー判定
                    should_retry = any(code in error_str for code in ["503", "429", "500"])
                    is_last_attempt = attempt == max_retries - 1

                    if should_retry and not is_last_attempt:
                        # 指数バックオフ
                        delay = base_delay * (2**attempt)
                        logger.warning(
                            f"⚠️ APIエラー検出。{delay:.1f}秒後に再試行... "
                            f"({attempt + 1}/{max_retries})"
                        )
                        await asyncio.sleep(delay)
                    else:
                        # リトライ不可 or 最終試行
                        if should_retry:
                            logger.error(f"❌ {max_retries}回リトライしましたが失敗")
                        raise

            return None

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            """同期関数用ラッパー"""
            import time

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    error_str = str(e)
                    should_retry = any(code in error_str for code in ["503", "429", "500"])
                    is_last_attempt = attempt == max_retries - 1

                    if should_retry and not is_last_attempt:
                        delay = base_delay * (2**attempt)
                        logger.warning(
                            f"⚠️ APIエラー検出。{delay:.1f}秒後に再試行... "
                            f"({attempt + 1}/{max_retries})"
                        )
                        time.sleep(delay)
                    else:
                        if should_retry:
                            logger.error(f"❌ {max_retries}回リトライしましたが失敗")
                        raise

            return None

        # 関数がasync定義かどうかで分岐
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# 使用例
if __name__ == "__main__":
    print("📦 sheets_retry_helper.py")
    print("✅ リトライヘルパー定義完了")
    print("\n使用例:")
    print(
        """
    from tools.sheets_retry_helper import retry_on_api_error
    
    @retry_on_api_error(max_retries=3, base_delay=1.0)
    async def read_with_retry(self, range_name):
        return await self.sheets.read_range(range_name)
    """
    )
