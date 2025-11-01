"""ErrorClassifier - エラー分類ユーティリティ"""

import re
from typing import Dict
import traceback


class ErrorClassifier:
    """エラーを種別に分類"""

    ERROR_PATTERNS = {
        "network": [
            r"ConnectionError",
            r"NetworkError",
            r"ConnectionRefusedError",
            r"ConnectionResetError",
            r"Failed to establish",
            r"Connection refused",
        ],
        "timeout": [
            r"TimeoutError",
            r"asyncio\.TimeoutError",
            r"ReadTimeout",
            r"ConnectTimeout",
            r"timeout.*exceeded",
            r"timed out",
        ],
        "rate_limit": [r"429", r"Too Many Requests", r"Rate limit exceeded", r"ResourceExhausted", r"Quota exceeded"],
        "auth": [r"401", r"403", r"Unauthorized", r"Forbidden", r"Authentication failed", r"Invalid credentials"],
        "selector": [r"NoSuchElementException", r"ElementNotFound", r"Selector not found", r"Element .* not found"],
        "api_error": [r"400", r"Bad Request", r"Invalid request", r"Service unavailable", r"Internal server error"],
    }

    def __init__(self):
        self.compiled_patterns = {}
        for error_type, patterns in self.ERROR_PATTERNS.items():
            self.compiled_patterns[error_type] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]

    def classify(self, error: Exception) -> str:
        """エラーを分類"""
        error_message = str(error)
        error_type_name = type(error).__name__
        tb_str = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        full_error_text = f"{error_type_name}: {error_message}\n{tb_str}"

        for error_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(full_error_text):
                    return error_type
        return "unknown"

    def get_error_details(self, error: Exception) -> Dict[str, str]:
        """エラー詳細を取得"""
        error_type = self.classify(error)
        return {
            "error_type": error_type,
            "error_class": type(error).__name__,
            "error_message": str(error),
            "traceback": "".join(traceback.format_exception(type(error), error, error.__traceback__)),
        }

    def is_retryable(self, error: Exception) -> bool:
        """リトライ可能か判定"""
        error_type = self.classify(error)
        retryable_types = ["network", "timeout", "rate_limit", "selector"]
        return error_type in retryable_types

    def get_suggested_wait_time(self, error: Exception) -> float:
        """推奨待機時間を取得"""
        error_type = self.classify(error)
        wait_times = {
            "network": 2.0,
            "timeout": 1.0,
            "rate_limit": 60.0,
            "auth": 5.0,
            "selector": 2.0,
            "api_error": 5.0,
            "unknown": 3.0,
        }
        return wait_times.get(error_type, 3.0)
