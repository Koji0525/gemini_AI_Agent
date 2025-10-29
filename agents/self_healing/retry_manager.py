"""
Week 5: RetryManager - リトライ戦略管理システム

エラー分類に基づいて最適なリトライ戦略を選択・実行
"""

import asyncio
import time
from typing import Callable, Dict, Any, Optional, List
from datetime import datetime
import traceback

from .error_classifier import ErrorClassifier
from .logging.context_logger import ContextLogger, DecisionContext
from .sheets_adapter import SheetsAdapter


class RetryConfig:
    """リトライ設定"""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


class RetryResult:
    """リトライ実行結果"""

    def __init__(self):
        self.success: bool = False
        self.result: Any = None
        self.total_attempts: int = 0
        self.total_duration: float = 0.0
        self.errors_encountered: List[Dict] = []
        self.strategies_used: List[str] = []
        self.final_error: Optional[Exception] = None


class RetryManager:
    """
    リトライ戦略を管理するマネージャー

    機能:
    - エラーの自動分類
    - 最適な戦略の選択
    - リトライの実行
    - 履歴の記録
    """

    def __init__(self, sheets_manager=None, config: Optional[RetryConfig] = None):
        """
        Args:
            sheets_manager: GoogleSheetsManagerインスタンス (オプション)
            config: リトライ設定
        """
        self.error_classifier = ErrorClassifier()
        self.context_logger = ContextLogger(sheets_manager) if sheets_manager else None
        self.config = config or RetryConfig()

        # Sheets連携（オプション）
        self.sheets_adapter = None
        if sheets_manager:
            self.sheets_adapter = SheetsAdapter(sheets_manager)

        # 統計
        self.total_retries = 0
        self.successful_retries = 0
        self.failed_retries = 0

    async def execute_with_retry(
        self, task_func: Callable, task_name: str, max_attempts: Optional[int] = None, **kwargs
    ) -> RetryResult:
        """
        タスクをリトライ機能付きで実行

        Args:
            task_func: 実行する関数（同期/非同期）
            task_name: タスク名
            max_attempts: 最大試行回数（Noneの場合はconfig使用）
            **kwargs: task_funcに渡す引数

        Returns:
            RetryResult
        """
        max_attempts = max_attempts or self.config.max_attempts
        result = RetryResult()
        start_time = time.time()

        print(f"\n🔄 [{task_name}] リトライ実行開始 (最大{max_attempts}回)")

        for attempt in range(1, max_attempts + 1):
            attempt_start = time.time()

            try:
                print(f"   試行 {attempt}/{max_attempts}...", end=" ")

                # 関数実行（同期/非同期対応）
                if asyncio.iscoroutinefunction(task_func):
                    task_result = await task_func(**kwargs)
                else:
                    task_result = task_func(**kwargs)

                # 成功
                attempt_duration = time.time() - attempt_start
                print(f"✅ 成功 ({attempt_duration:.2f}秒)")

                result.success = True
                result.result = task_result
                result.total_attempts = attempt

                # 成功時の記録
                if self.sheets_adapter and attempt > 1:
                    await self._record_success(task_name, attempt, attempt_duration)

                self.successful_retries += 1
                break

            except Exception as error:
                attempt_duration = time.time() - attempt_start

                # エラー分類
                error_info = self.error_classifier.get_error_info(error)

                print(f"❌ エラー ({error_info.category})")
                print(f"      メッセージ: {str(error)[:80]}...")

                # エラー記録
                result.errors_encountered.append(
                    {
                        "attempt": attempt,
                        "error": error,
                        "category": error_info.category,
                        "severity": error_info.severity,
                        "duration": attempt_duration,
                    }
                )

                # 最後の試行か？
                if attempt >= max_attempts:
                    print(f"   ⚠️  最大試行回数に到達")
                    result.final_error = error
                    self.failed_retries += 1
                    break

                # リトライ可能か判定
                if not error_info.is_retryable:
                    print(f"   ⚠️  リトライ不可能なエラー ({error_info.severity})")
                    result.final_error = error
                    self.failed_retries += 1
                    break

                # 戦略選択と待機
                strategy = error_info.recommended_strategy
                wait_time = self._calculate_wait_time(attempt, error_info.category)

                result.strategies_used.append(strategy)

                print(f"   戦略: {strategy} | 待機: {wait_time:.1f}秒")

                # 履歴記録（非同期）
                if self.sheets_adapter:
                    await self._record_retry_attempt(
                        task_name=task_name,
                        attempt=attempt,
                        error_info=error_info,
                        strategy=strategy,
                        wait_time=wait_time,
                        success=False,
                        duration=attempt_duration,
                    )

                # 待機
                await asyncio.sleep(wait_time)

        result.total_duration = time.time() - start_time
        result.total_attempts = attempt

        self.total_retries += 1

        # サマリー表示
        self._print_summary(task_name, result)

        return result

    def _calculate_wait_time(self, attempt: int, error_category: str) -> float:
        """
        待機時間を計算

        Args:
            attempt: 現在の試行回数
            error_category: エラーカテゴリ

        Returns:
            待機時間（秒）
        """
        import random

        if error_category == "rate_limit":
            # レート制限: 長めの待機
            base_wait = 60.0
            wait_time = base_wait + (attempt * 10)

        elif error_category == "timeout":
            # タイムアウト: 短めの待機
            wait_time = 1.0 + (attempt * 0.5)

        elif error_category == "auth":
            # 認証: 少し待つ
            wait_time = 5.0

        else:
            # デフォルト: 指数バックオフ
            wait_time = min(
                self.config.base_delay * (self.config.exponential_base ** (attempt - 1)), self.config.max_delay
            )

        # ジッター追加
        if self.config.jitter:
            jitter = random.uniform(0, min(1.0, wait_time * 0.1))
            wait_time += jitter

        return wait_time

    async def _record_retry_attempt(
        self,
        task_name: str,
        attempt: int,
        error_info: Dict[str, Any],
        strategy: str,
        wait_time: float,
        success: bool,
        duration: float,
    ):
        """リトライ試行を記録"""
        try:
            self.sheets_adapter.record_retry(
                task_name=task_name,
                attempt=attempt,
                error_type=error_info.category,
                error_message=error_info.message,
                strategy_used=strategy,
                wait_time=wait_time,
                success=success,
                duration=duration,
            )
        except Exception as e:
            print(f"   ⚠️  履歴記録エラー: {e}")

    async def _record_success(self, task_name: str, attempt: int, duration: float):
        """成功時の記録"""
        try:
            self.sheets_adapter.record_retry(
                task_name=task_name,
                attempt=attempt,
                error_type="none",
                error_message="Success after retry",
                strategy_used="retry_succeeded",
                wait_time=0.0,
                success=True,
                duration=duration,
            )
        except Exception as e:
            print(f"   ⚠️  成功記録エラー: {e}")

    def _print_summary(self, task_name: str, result: RetryResult):
        """実行サマリーを表示"""
        print(f"\n{'='*70}")
        print(f"📊 [{task_name}] 実行サマリー")
        print(f"{'='*70}")
        print(f"結果: {'✅ 成功' if result.success else '❌ 失敗'}")
        print(f"試行回数: {result.total_attempts}回")
        print(f"総実行時間: {result.total_duration:.2f}秒")

        if result.errors_encountered:
            print(f"\n遭遇したエラー:")
            for err_info in result.errors_encountered:
                print(
                    f"  試行{err_info['attempt']}: "
                    f"{err_info['category']} "
                    f"({err_info['severity']}) - "
                    f"{err_info['duration']:.2f}秒"
                )

        if result.strategies_used:
            print(f"\n使用した戦略:")
            for i, strategy in enumerate(result.strategies_used, 1):
                print(f"  {i}. {strategy}")

        print(f"{'='*70}\n")

    def get_statistics(self) -> Dict[str, Any]:
        """
        統計情報を取得

        Returns:
            統計データ
        """
        success_rate = 0.0
        if self.total_retries > 0:
            success_rate = (self.successful_retries / self.total_retries) * 100

        return {
            "total_retries": self.total_retries,
            "successful_retries": self.successful_retries,
            "failed_retries": self.failed_retries,
            "success_rate": f"{success_rate:.1f}%",
            "classifier_stats": self.error_classifier.get_statistics(),
        }
