"""
Week 5: 自己修復システム (Self-Healing)

Phase 5の自動修復機能を提供
"""

from .utils.error_classifier import ErrorClassifier
from .sheets_adapter import SheetsAdapter, RetryHistoryManager
from .retry_manager import RetryManager, RetryConfig, RetryResult
from .retry_strategies import (
    RetryStrategy,
    ExponentialBackoffStrategy,
    TimeoutStrategy,
    RateLimitStrategy,
    SelectorStrategy,
    AuthStrategy,
    StrategyFactory,
)

__all__ = [
    "ErrorClassifier",
    "ErrorInfo",
    "SheetsAdapter",
    "RetryHistoryManager",
    "RetryManager",
    "RetryConfig",
    "RetryResult",
    "RetryStrategy",
    "ExponentialBackoffStrategy",
    "TimeoutStrategy",
    "RateLimitStrategy",
    "SelectorStrategy",
    "AuthStrategy",
    "StrategyFactory",
]
