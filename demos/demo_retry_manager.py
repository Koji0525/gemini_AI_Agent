"""
RetryManagerのデモンストレーション

相対インポートを使わない形式
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from agents.self_healing.retry_manager import RetryManager


# ================================================
# デモ用タスク関数
# ================================================


async def demo_task_success():
    """成功するデモタスク"""
    await asyncio.sleep(0.1)
    return "Success!"


async def demo_task_fail_then_succeed(attempt_state: dict):
    """最初は失敗、後で成功するタスク"""
    attempt_state["count"] = attempt_state.get("count", 0) + 1

    if attempt_state["count"] < 2:
        raise ConnectionError("Network is temporarily unavailable")

    return "Success after retry!"


async def demo_task_timeout():
    """タイムアウトするタスク"""
    raise TimeoutError("Operation timed out")


async def demo_task_rate_limit():
    """レート制限エラーを起こすタスク"""
    raise Exception("429 Too Many Requests")


async def demo_retry_manager():
    """RetryManagerのデモンストレーション"""
    print("\n" + "=" * 70)
    print("RetryManager デモンストレーション")
    print("=" * 70)

    manager = RetryManager()

    # デモ1: 成功するタスク
    print("\n【デモ1】正常に成功するタスク")
    result1 = await manager.execute_with_retry(task_func=demo_task_success, task_name="demo_success_task")

    # デモ2: リトライ後に成功
    print("\n【デモ2】リトライ後に成功するタスク")
    attempt_state = {}
    result2 = await manager.execute_with_retry(
        task_func=demo_task_fail_then_succeed, task_name="demo_retry_success_task", attempt_state=attempt_state
    )

    # デモ3: タイムアウト
    print("\n【デモ3】タイムアウトエラー")
    result3 = await manager.execute_with_retry(
        task_func=demo_task_timeout, task_name="demo_timeout_task", max_attempts=2
    )

    # デモ4: レート制限
    print("\n【デモ4】レート制限エラー")
    result4 = await manager.execute_with_retry(
        task_func=demo_task_rate_limit, task_name="demo_rate_limit_task", max_attempts=2
    )

    # 統計表示
    print("\n" + "=" * 70)
    print("📊 RetryManager統計")
    print("=" * 70)
    stats = manager.get_statistics()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demo_retry_manager())
