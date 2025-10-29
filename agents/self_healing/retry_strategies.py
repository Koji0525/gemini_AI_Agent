"""RetryStrategies - リトライ戦略実装"""
import asyncio
import random
from abc import ABC, abstractmethod
from typing import Callable, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class RetryStrategy(ABC):
    """リトライ戦略の基底クラス"""
    def __init__(self, name: str):
        self.name = name
        self.max_wait_time = 300.0
    
    @abstractmethod
    def calculate_wait_time(self, attempt: int) -> float:
        pass
    
    async def wait(self, attempt: int) -> None:
        wait_time = self.calculate_wait_time(attempt)
        wait_time = min(wait_time, self.max_wait_time)
        logger.info(f"[{self.name}] Waiting {wait_time:.2f}s before retry (attempt {attempt + 1})")
        await asyncio.sleep(wait_time)
    
    def should_retry(self, attempt: int, max_attempts: int) -> bool:
        return attempt < max_attempts

class ExponentialBackoffStrategy(RetryStrategy):
    """指数バックオフ戦略"""
    def __init__(self, base_delay: float = 2.0, max_delay: float = 60.0):
        super().__init__("ExponentialBackoff")
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def calculate_wait_time(self, attempt: int) -> float:
        exponential_delay = self.base_delay * (2 ** attempt)
        exponential_delay = min(exponential_delay, self.max_delay)
        jitter = random.uniform(0, exponential_delay * 0.1)
        return exponential_delay + jitter

class TimeoutStrategy(RetryStrategy):
    """タイムアウト戦略"""
    def __init__(self, base_delay: float = 1.0):
        super().__init__("Timeout")
        self.base_delay = base_delay
        self.timeout_increase_factor = 1.5
    
    def calculate_wait_time(self, attempt: int) -> float:
        return self.base_delay + (attempt * 0.5)
    
    def should_increase_timeout(self, attempt: int) -> bool:
        return attempt >= 2
    
    def get_increased_timeout(self, current_timeout: float, attempt: int) -> float:
        return current_timeout * (self.timeout_increase_factor ** attempt)

class RateLimitStrategy(RetryStrategy):
    """レート制限戦略"""
    def __init__(self, reset_wait: float = 60.0):
        super().__init__("RateLimit")
        self.reset_wait = reset_wait
    
    def calculate_wait_time(self, attempt: int) -> float:
        base_wait = self.reset_wait
        additional_wait = attempt * 10
        return base_wait + additional_wait
    
    def parse_retry_after_header(self, headers: Dict[str, str]) -> Optional[float]:
        retry_after = headers.get('Retry-After') or headers.get('retry-after')
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass
        return None

class SelectorStrategy(RetryStrategy):
    """セレクタエラー戦略"""
    def __init__(self, fallback_selectors: Optional[list] = None):
        super().__init__("Selector")
        self.fallback_selectors = fallback_selectors or []
        self.base_delay = 2.0
    
    def calculate_wait_time(self, attempt: int) -> float:
        return self.base_delay + (attempt * 0.5)
    
    def get_next_selector(self, attempt: int) -> Optional[str]:
        if attempt < len(self.fallback_selectors):
            return self.fallback_selectors[attempt]
        return None
    
    def has_fallback(self, attempt: int) -> bool:
        return attempt < len(self.fallback_selectors)

class AuthStrategy(RetryStrategy):
    """認証エラー戦略"""
    def __init__(self):
        super().__init__("Auth")
        self.base_delay = 5.0
    
    def calculate_wait_time(self, attempt: int) -> float:
        return self.base_delay + (attempt * 2.0)
    
    async def refresh_credentials(self, auth_handler: Callable) -> bool:
        try:
            logger.info(f"[{self.name}] Refreshing credentials...")
            await auth_handler()
            logger.info(f"[{self.name}] Credentials refreshed successfully")
            return True
        except Exception as e:
            logger.error(f"[{self.name}] Failed to refresh credentials: {e}")
            return False
    
    def should_retry(self, attempt: int, max_attempts: int) -> bool:
        return attempt < min(max_attempts, 2)

class StrategyFactory:
    """リトライ戦略ファクトリー"""
    @staticmethod
    def create_strategy(error_type: str, **kwargs) -> RetryStrategy:
        strategies = {
            'network': ExponentialBackoffStrategy,
            'timeout': TimeoutStrategy,
            'rate_limit': RateLimitStrategy,
            'selector': SelectorStrategy,
            'auth': AuthStrategy,
        }
        strategy_class = strategies.get(error_type, ExponentialBackoffStrategy)
        return strategy_class(**kwargs)
