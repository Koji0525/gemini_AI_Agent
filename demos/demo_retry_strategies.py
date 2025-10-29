"""
RetryStrategiesのデモンストレーション
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from agents.self_healing.retry_strategies import (
    ExponentialBackoffStrategy,
    TimeoutStrategy,
    RateLimitStrategy,
    SelectorStrategy,
    AuthStrategy,
    StrategyFactory,
)


async def demo_strategies():
    """各戦略のデモンストレーション"""
    print("\n" + "=" * 70)
    print("RetryStrategies デモンストレーション")
    print("=" * 70)

    # 1. ExponentialBackoff
    print("\n【1】ExponentialBackoffStrategy")
    print("-" * 70)
    exp_strategy = ExponentialBackoffStrategy(base_delay=1.0, max_delay=10.0)
    for attempt in range(1, 6):
        wait = exp_strategy.calculate_wait_time(attempt, {})
        print(f"  試行{attempt}: {wait:.2f}秒待機")

    # 2. Timeout
    print("\n【2】TimeoutStrategy")
    print("-" * 70)
    timeout_strategy = TimeoutStrategy()
    for attempt in range(1, 4):
        wait = timeout_strategy.calculate_wait_time(attempt, {})
        new_timeout = timeout_strategy.get_increased_timeout(30.0)
        print(f"  試行{attempt}: {wait:.2f}秒待機 | 新タイムアウト: {new_timeout:.1f}秒")

    # 3. RateLimit
    print("\n【3】RateLimitStrategy")
    print("-" * 70)
    rate_strategy = RateLimitStrategy()
    for attempt in range(1, 4):
        wait = rate_strategy.calculate_wait_time(attempt, {})
        print(f"  試行{attempt}: {wait:.1f}秒待機（レート制限解除待ち）")

    # 4. Selector
    print("\n【4】SelectorStrategy")
    print("-" * 70)
    selector_strategy = SelectorStrategy(
        fallback_selectors=[
            'div[contenteditable="true"]',
            "div.input-area",
            "#chat-input",
            '[data-testid="message-input"]',
        ]
    )
    for attempt in range(1, 5):
        selector = selector_strategy.get_next_selector(attempt)
        wait = selector_strategy.calculate_wait_time(attempt, {})
        print(f"  試行{attempt}: セレクタ '{selector}' | {wait:.1f}秒待機")

    # 5. Auth
    print("\n【5】AuthStrategy")
    print("-" * 70)
    auth_strategy = AuthStrategy()
    wait = auth_strategy.calculate_wait_time(1, {})
    print(f"  待機時間: {wait:.1f}秒")
    refreshed = await auth_strategy.refresh_credentials({})
    print(f"  リフレッシュ結果: {'✅ 成功' if refreshed else '❌ 失敗'}")

    # 6. StrategyFactory
    print("\n【6】StrategyFactory")
    print("-" * 70)
    print("利用可能な戦略:")
    for strategy_name in StrategyFactory.list_strategies():
        strategy = StrategyFactory.create(strategy_name)
        print(f"  - {strategy_name}: {strategy.name}")

    # 7. 統計情報
    print("\n【7】統計情報")
    print("-" * 70)
    exp_strategy.on_retry(1, Exception())
    exp_strategy.on_retry(2, Exception())
    exp_strategy.on_success(3)

    stats = exp_strategy.get_statistics()
    print(f"戦略名: {stats['name']}")
    print(f"総試行回数: {stats['total_attempts']}")
    print(f"成功回数: {stats['successes']}")
    print(f"失敗回数: {stats['failures']}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(demo_strategies())
