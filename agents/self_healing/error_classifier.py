"""
Week 5: エラー分類システム (完全版)

エラーを種別に自動分類し、適切なリトライ戦略を選択
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ErrorInfo:
    """エラー情報を格納するデータクラス"""

    category: str  # エラーカテゴリ
    severity: str  # 深刻度 (low/medium/high/critical)
    is_retryable: bool  # リトライ可能か
    recommended_strategy: str  # 推奨戦略
    message: str  # エラーメッセージ
    error_class: str  # エラークラス名


class ErrorClassifier:
    """
    エラーを種別に分類するクラス

    エラーカテゴリ:
    - network: ネットワーク関連エラー
    - timeout: タイムアウト
    - rate_limit: APIレート制限
    - auth: 認証エラー
    - selector: セレクタエラー (Playwright等)
    - permission: 権限エラー
    - resource: リソース不足
    - syntax: 構文エラー
    - unknown: 分類不能
    """

    # エラーパターン定義（優先度順）
    ERROR_PATTERNS: Dict[str, List[str]] = {
        "rate_limit": [
            "429",
            "Too Many Requests",
            "Rate limit exceeded",
            "quota exceeded",
            "ResourceExhausted",
            "RATE_LIMIT_EXCEEDED",
            "ThrottlingException",
        ],
        "auth": [
            "401",
            "403",
            "Unauthorized",
            "Forbidden",
            "Authentication failed",
            "Invalid credentials",
            "Token expired",
            "API key",
            "Permission denied",
            "AuthenticationError",
        ],
        "network": [
            "ConnectionError",
            "NetworkError",
            "ConnectionRefusedError",
            "ConnectionResetError",
            "socket.gaierror",
            "requests.exceptions.ConnectionError",
            "urllib3.exceptions.NewConnectionError",
            "Failed to establish connection",
            "Network is unreachable",
            "Connection refused",
            "Name or service not known",
        ],
        "timeout": [
            "TimeoutError",
            "asyncio.TimeoutError",
            "ReadTimeout",
            "ConnectTimeout",
            "requests.exceptions.Timeout",
            "playwright._impl._api_types.TimeoutError",
            "Timeout waiting for",
            "Operation timed out",
            "Request timeout",
        ],
        "selector": [
            "NoSuchElementException",
            "ElementNotFound",
            "Selector not found",
            "Element is not attached",
            "playwright._impl._api_types.Error",
            "ElementNotInteractableException",
            "StaleElementReferenceException",
            "element not found",
            "Unable to locate element",
        ],
        "permission": [
            "PermissionError",
            "Access denied",
            "Permission denied",
            "Insufficient permissions",
            "Read-only file system",
        ],
        "resource": [
            "MemoryError",
            "OutOfMemoryError",
            "Disk quota exceeded",
            "No space left on device",
            "Resource temporarily unavailable",
        ],
        "syntax": [
            "SyntaxError",
            "IndentationError",
            "NameError",
            "TypeError",
            "AttributeError",
            "KeyError",
            "IndexError",
        ],
    }

    # エラーカテゴリごとの特性
    CATEGORY_PROPERTIES = {
        "rate_limit": {"severity": "medium", "is_retryable": True, "recommended_strategy": "rate_limit_strategy"},
        "auth": {"severity": "high", "is_retryable": True, "recommended_strategy": "auth_strategy"},
        "network": {"severity": "medium", "is_retryable": True, "recommended_strategy": "exponential_backoff"},
        "timeout": {"severity": "medium", "is_retryable": True, "recommended_strategy": "timeout_strategy"},
        "selector": {"severity": "medium", "is_retryable": True, "recommended_strategy": "selector_strategy"},
        "permission": {"severity": "high", "is_retryable": False, "recommended_strategy": "none"},
        "resource": {"severity": "critical", "is_retryable": False, "recommended_strategy": "none"},
        "syntax": {"severity": "critical", "is_retryable": False, "recommended_strategy": "none"},
        "unknown": {"severity": "medium", "is_retryable": True, "recommended_strategy": "exponential_backoff"},
    }

    def __init__(self):
        """初期化"""
        self.classification_count = 0
        self.classification_history = []

    def classify(self, error: Exception) -> str:
        """
        エラーをカテゴリに分類

        Args:
            error: 分類するException

        Returns:
            エラーカテゴリ ('network', 'timeout', 'rate_limit',
                           'auth', 'selector', 'permission',
                           'resource', 'syntax', 'unknown')
        """
        error_str = str(error).lower()
        error_type_name = type(error).__name__.lower()

        # パターンマッチング（優先度順）
        for category, patterns in self.ERROR_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in error_str or pattern.lower() in error_type_name:
                    self.classification_count += 1
                    return category

        return "unknown"

    def get_error_info(self, error: Exception) -> ErrorInfo:
        """
        エラーの詳細情報を取得

        Args:
            error: Exception

        Returns:
            ErrorInfo データクラス
        """
        category = self.classify(error)
        props = self.CATEGORY_PROPERTIES.get(category, self.CATEGORY_PROPERTIES["unknown"])

        return ErrorInfo(
            category=category,
            severity=props["severity"],
            is_retryable=props["is_retryable"],
            recommended_strategy=props["recommended_strategy"],
            message=str(error)[:200],
            error_class=type(error).__name__,
        )

    def is_retryable(self, error: Exception) -> bool:
        """
        エラーがリトライ可能か判定

        Args:
            error: Exception

        Returns:
            リトライ可能ならTrue
        """
        info = self.get_error_info(error)
        return info.is_retryable

    def get_recommended_strategy(self, error: Exception) -> str:
        """
        推奨されるリトライ戦略を取得

        Args:
            error: Exception

        Returns:
            戦略名 ('exponential_backoff', 'timeout_strategy', など)
        """
        info = self.get_error_info(error)
        return info.recommended_strategy

    def get_severity(self, error: Exception) -> str:
        """
        エラーの深刻度を取得

        Args:
            error: Exception

        Returns:
            深刻度 ('low', 'medium', 'high', 'critical')
        """
        info = self.get_error_info(error)
        return info.severity

    def add_custom_pattern(
        self,
        category: str,
        patterns: List[str],
        severity: str = "medium",
        is_retryable: bool = True,
        strategy: str = "exponential_backoff",
    ):
        """
        カスタムエラーパターンを追加

        Args:
            category: カテゴリ名
            patterns: パターンリスト
            severity: 深刻度
            is_retryable: リトライ可能か
            strategy: 推奨戦略
        """
        if category not in self.ERROR_PATTERNS:
            self.ERROR_PATTERNS[category] = []

        self.ERROR_PATTERNS[category].extend(patterns)

        if category not in self.CATEGORY_PROPERTIES:
            self.CATEGORY_PROPERTIES[category] = {
                "severity": severity,
                "is_retryable": is_retryable,
                "recommended_strategy": strategy,
            }

    def get_statistics(self) -> Dict:
        """
        分類統計を取得

        Returns:
            統計情報
        """
        return {
            "total_classifications": self.classification_count,
            "categories_defined": len(self.ERROR_PATTERNS),
            "patterns_count": sum(len(p) for p in self.ERROR_PATTERNS.values()),
        }


def create_test_errors() -> List[Exception]:
    """テスト用のエラーを生成"""
    return [
        ConnectionError("Failed to establish connection"),
        TimeoutError("Operation timed out after 30 seconds"),
        Exception("429 Too Many Requests"),
        Exception("401 Unauthorized"),
        Exception("Selector 'div.input' not found"),
        PermissionError("Access denied to file"),
        MemoryError("Out of memory"),
        SyntaxError("Invalid syntax on line 42"),
        ValueError("Some random error"),
    ]


# ================================================
# デモ・テスト用関数
# ================================================


def demo_classifier():
    """分類器のデモンストレーション"""
    print("\n" + "=" * 70)
    print("ErrorClassifier デモンストレーション")
    print("=" * 70)

    classifier = ErrorClassifier()
    test_errors = create_test_errors()

    print(f"\n📊 テストエラー数: {len(test_errors)}\n")

    for i, error in enumerate(test_errors, 1):
        info = classifier.get_error_info(error)

        print(f"{i}. {info.error_class}: {info.message[:50]}...")
        print(f"   カテゴリ: {info.category}")
        print(f"   深刻度: {info.severity}")
        print(f"   リトライ可: {info.is_retryable}")
        print(f"   推奨戦略: {info.recommended_strategy}")
        print()

    print("=" * 70)
    print("統計:")
    stats = classifier.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("=" * 70)


if __name__ == "__main__":
    demo_classifier()
