"""非同期テストヘルパー - 修正版"""

import asyncio
from typing import Any, Awaitable, Callable
from unittest.mock import AsyncMock, patch


class AsyncTestHelper:
    """非同期テスト用のヘルパークラス"""

    @staticmethod
    async def run_async_test(async_func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """非同期関数をテスト環境で実行"""
        return await async_func(*args, **kwargs)

    @staticmethod
    def create_async_mock(return_value: Any = None) -> AsyncMock:
        """非同期モックオブジェクトを作成"""
        mock = AsyncMock()
        if return_value is not None:
            mock.return_value = return_value
        return mock

    @staticmethod
    def patch_async_method(target: str, return_value: Any = None):
        """非同期メソッドをモックでパッチ"""
        return patch(target, new_callable=AsyncMock, return_value=return_value)


async def example_async_function(value: str) -> dict:
    """テスト用のサンプル非同期関数"""
    await asyncio.sleep(0.01)
    return {"result": value}


if __name__ == "__main__":
    print("✅ AsyncTestHelper モジュール")
