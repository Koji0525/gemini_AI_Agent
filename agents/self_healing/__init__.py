"""
Week 5: 自己修復システム (Self-Healing)

Phase 5の自動修復機能を提供
"""

from .error_classifier import ErrorClassifier
from .sheets_adapter import SheetsAdapter, RetryHistoryManager

__all__ = [
    'ErrorClassifier',
    'SheetsAdapter',
    'RetryHistoryManager',
]
