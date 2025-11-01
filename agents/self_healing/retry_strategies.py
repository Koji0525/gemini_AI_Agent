"""
Week 5: RetryStrategies - 各エラー種別専用のリトライ戦略

戦略パターンを使用した実装
"""

import asyncio
import random
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta


class RetryStrategy(ABC):
    """
    リトライ戦略の基底クラス

    全ての戦略はこのクラスを継承する
    """

    def __init__(self, name: str, max_attempts: int = 3):
        """
        Args:
            name: 戦略名
            max_attempts: 最大試行回数
        """
        self.name = name
        self.max_attempts = max_attempts
        self.attempt_count = 0
        self.success_count = 0
        self.failure_count = 0

    @abstractmethod
    def calculate_wait_time(self, attempt: int, context: Dict[str, Any]) -> float:
        """
        待機時間を計算

        Args:
            attempt: 現在の試行回数
            context: コンテキスト情報

        Returns:
            待機時間（秒）
        """
        pass

    @abstractmethod
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """
        リトライすべきか判定

        Args:
            attempt: 現在の試行回数
            error: 発生したエラー

        Returns:
            リトライすべきならTrue
        """
        pass

    def on_retry(self, attempt: int, error: Exception):
        """
        リトライ時のコールバック

        Args:
            attempt: 試行回数
            error: エラー
        """
        self.attempt_count += 1
        print(f"   [{self.name}] 試行 {attempt}/{self.max_attempts}")

    def on_success(self, attempt: int):
        """
        成功時のコールバック

        Args:
            attempt: 成功した試行回数
        """
        self.success_count += 1
        print(f"   [{self.name}] ✅ 成功 (試行{attempt}回目)")

    def on_failure(self, attempt: int, error: Exception):
        """
        失敗時のコールバック

        Args:
            attempt: 試行回数
            error: 最終エラー
        """
        self.failure_count += 1
        print(f"   [{self.name}] ❌ 最終失敗 (試行{attempt}回)")

    def get_statistics(self) -> Dict[str, Any]:
        """
        戦略の統計情報を取得

        Returns:
            統計データ
        """
        return {
            "name": self.name,
            "total_attempts": self.attempt_count,
            "successes": self.success_count,
            "failures": self.failure_count,
        }


class ExponentialBackoffStrategy(RetryStrategy):
    """
    指数バックオフ戦略

    待機時間を指数的に増加させる（ネットワークエラー用）
    wait_time = base_delay * (2 ^ attempt) + jitter
    """

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        max_attempts: int = 5,
    ):
        """
        Args:
            base_delay: 基本待機時間（秒）
            max_delay: 最大待機時間（秒）
            exponential_base: 指数の基数
            jitter: ジッター追加するか
            max_attempts: 最大試行回数
        """
        super().__init__("ExponentialBackoff", max_attempts)
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def calculate_wait_time(self, attempt: int, context: Dict[str, Any]) -> float:
        """
        指数バックオフで待機時間を計算

        Examples:
            attempt 1: 1秒 + jitter
            attempt 2: 2秒 + jitter
            attempt 3: 4秒 + jitter
            attempt 4: 8秒 + jitter
        """
        # 指数バックオフ
        wait_time = self.base_delay * (self.exponential_base ** (attempt - 1))

        # 最大値でクリップ
        wait_time = min(wait_time, self.max_delay)

        # ジッター追加（衝突回避）
        if self.jitter:
            jitter_amount = random.uniform(0, min(1.0, wait_time * 0.1))
            wait_time += jitter_amount

        return wait_time

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """ネットワークエラーはリトライ可能"""
        return attempt < self.max_attempts


class TimeoutStrategy(RetryStrategy):
    """
    タイムアウト戦略

    短い待機時間で素早くリトライ
    必要に応じてタイムアウト値を増加
    """

    def __init__(
        self,
        base_wait: float = 1.0,
        wait_increment: float = 0.5,
        timeout_multiplier: float = 1.5,
        max_attempts: int = 3,
    ):
        """
        Args:
            base_wait: 基本待機時間（秒）
            wait_increment: 待機時間の増分
            timeout_multiplier: タイムアウト値の倍率
            max_attempts: 最大試行回数
        """
        super().__init__("Timeout", max_attempts)
        self.base_wait = base_wait
        self.wait_increment = wait_increment
        self.timeout_multiplier = timeout_multiplier
        self.current_timeout = None

    def calculate_wait_time(self, attempt: int, context: Dict[str, Any]) -> float:
        """短い待機時間を返す"""
        return self.base_wait + (attempt * self.wait_increment)

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """タイムアウトは基本的にリトライ可能"""
        return attempt < self.max_attempts

    def get_increased_timeout(self, current_timeout: float) -> float:
        """
        タイムアウト値を増やす

        Args:
            current_timeout: 現在のタイムアウト値

        Returns:
            増加後のタイムアウト値
        """
        return current_timeout * self.timeout_multiplier


class RateLimitStrategy(RetryStrategy):
    """
    レート制限戦略

    APIのレート制限を考慮した待機
    """

    def __init__(self, base_wait: float = 60.0, wait_increment: float = 10.0, max_attempts: int = 3):
        """
        Args:
            base_wait: 基本待機時間（秒）- レート制限リセット時間
            wait_increment: 追加待機時間
            max_attempts: 最大試行回数
        """
        super().__init__("RateLimit", max_attempts)
        self.base_wait = base_wait
        self.wait_increment = wait_increment

    def calculate_wait_time(self, attempt: int, context: Dict[str, Any]) -> float:
        """
        レート制限を考慮した待機時間

        多くのAPIは1分でリセットされるため、
        base_wait + 段階的増加
        """
        return self.base_wait + (attempt * self.wait_increment)

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """レート制限は通常リトライ可能"""
        return attempt < self.max_attempts


class SelectorStrategy(RetryStrategy):
    """
    セレクタ戦略

    フォールバックセレクタを順番に試す
    """

    def __init__(self, fallback_selectors: Optional[List[str]] = None, base_wait: float = 0.5, max_attempts: int = 5):
        """
        Args:
            fallback_selectors: フォールバックセレクタリスト
            base_wait: 基本待機時間
            max_attempts: 最大試行回数
        """
        super().__init__("Selector", max_attempts)
        self.fallback_selectors = fallback_selectors or []
        self.base_wait = base_wait
        self.current_selector_index = 0

    def calculate_wait_time(self, attempt: int, context: Dict[str, Any]) -> float:
        """セレクタ変更時は短い待機"""
        return self.base_wait

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """フォールバックセレクタがある限りリトライ"""
        return attempt < self.max_attempts

    def get_next_selector(self, attempt: int) -> Optional[str]:
        """
        次のセレクタを取得

        Args:
            attempt: 現在の試行回数

        Returns:
            次のセレクタ（なければNone）
        """
        if attempt - 1 < len(self.fallback_selectors):
            return self.fallback_selectors[attempt - 1]
        return None


class AuthStrategy(RetryStrategy):
    """
    認証戦略

    認証エラー時の処理（トークンリフレッシュなど）
    """

    def __init__(self, wait_before_refresh: float = 2.0, max_attempts: int = 2):
        """
        Args:
            wait_before_refresh: リフレッシュ前の待機時間
            max_attempts: 最大試行回数（認証は多くリトライしない）
        """
        super().__init__("Auth", max_attempts)
        self.wait_before_refresh = wait_before_refresh
        self.refresh_attempted = False

    def calculate_wait_time(self, attempt: int, context: Dict[str, Any]) -> float:
        """認証リフレッシュのための待機"""
        return self.wait_before_refresh

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """
        認証エラーは1回だけリトライ
        （トークンリフレッシュ後）
        """
        return attempt < self.max_attempts

    async def refresh_credentials(self, context: Dict[str, Any]) -> bool:
        """
        認証情報をリフレッシュ

        Args:
            context: 認証コンテキスト

        Returns:
            リフレッシュ成功したか
        """
        if self.refresh_attempted:
            return False

        print(f"   [{self.name}] 🔄 認証情報をリフレッシュ中...")
        self.refresh_attempted = True

        # 実装例:
        # - トークンの再取得
        # - 再ログイン
        # - セッション再確立

        await asyncio.sleep(0.5)  # リフレッシュシミュレーション
        return True


# ================================================
# 戦略ファクトリー
# ================================================


class StrategyFactory:
    """戦略インスタンスを生成するファクトリー"""

    _strategies = {
        "exponential_backoff": ExponentialBackoffStrategy,
        "timeout_strategy": TimeoutStrategy,
        "rate_limit_strategy": RateLimitStrategy,
        "selector_strategy": SelectorStrategy,
        "auth_strategy": AuthStrategy,
    }

    @classmethod
    def create(cls, strategy_name: str, **kwargs) -> RetryStrategy:
        """
        戦略を生成

        Args:
            strategy_name: 戦略名
            **kwargs: 戦略のコンストラクタ引数

        Returns:
            RetryStrategy インスタンス
        """
        strategy_class = cls._strategies.get(strategy_name)

        if not strategy_class:
            # デフォルトは指数バックオフ
            strategy_class = ExponentialBackoffStrategy

        return strategy_class(**kwargs)

    @classmethod
    def list_strategies(cls) -> List[str]:
        """利用可能な戦略のリストを返す"""
        return list(cls._strategies.keys())
