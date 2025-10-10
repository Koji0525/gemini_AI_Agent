"""
強化版エラーハンドラー - マルチエージェントシステム用
"""

import logging
import asyncio
import traceback
import sys
from typing import Optional, Callable, Any
from functools import wraps
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class RetryConfig:
    """リトライ設定"""
    MAX_RETRIES = 3
    INITIAL_DELAY = 2.0  # 秒
    MAX_DELAY = 30.0
    BACKOFF_FACTOR = 2.0


class EnhancedErrorHandler:
    """強化版エラーハンドラー"""
    
    @staticmethod
    def log_error_with_context(error: Exception, context: str = "", 
                               include_traceback: bool = True) -> None:
        """コンテキスト付きエラーログ"""
        logger.error("="*60)
        logger.error(f"❌ エラー発生: {context}")
        logger.error(f"エラータイプ: {type(error).__name__}")
        logger.error(f"エラー内容: {str(error)}")
        
        if include_traceback:
            logger.error("トレースバック:")
            logger.error(traceback.format_exc())
        
        logger.error("="*60)
    
    @staticmethod
    async def retry_async(
        func: Callable,
        *args,
        max_retries: int = RetryConfig.MAX_RETRIES,
        delay: float = RetryConfig.INITIAL_DELAY,
        backoff: float = RetryConfig.BACKOFF_FACTOR,
        exceptions: tuple = (Exception,),
        on_retry: Optional[Callable] = None,
        **kwargs
    ) -> Any:
        """
        非同期関数のリトライラッパー
        
        Args:
            func: 実行する非同期関数
            max_retries: 最大リトライ回数
            delay: 初期遅延時間（秒）
            backoff: バックオフ係数
            exceptions: キャッチする例外のタプル
            on_retry: リトライ時のコールバック関数
        """
        current_delay = delay
        last_exception = None
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"試行 {attempt}/{max_retries}: {func.__name__}")
                result = await func(*args, **kwargs)
                
                if attempt > 1:
                    logger.info(f"✅ 成功（試行 {attempt}）")
                
                return result
                
            except exceptions as e:
                last_exception = e
                
                if attempt == max_retries:
                    logger.error(f"❌ 全リトライ失敗: {func.__name__}")
                    EnhancedErrorHandler.log_error_with_context(
                        e, f"{func.__name__} (試行 {attempt}/{max_retries})"
                    )
                    raise
                
                logger.warning(f"⚠️ 失敗（試行 {attempt}）: {str(e)}")
                logger.info(f"🔄 {current_delay:.1f}秒後に再試行...")
                
                if on_retry:
                    try:
                        await on_retry(attempt, e)
                    except Exception as callback_error:
                        logger.warning(f"リトライコールバック失敗: {callback_error}")
                
                await asyncio.sleep(current_delay)
                current_delay = min(current_delay * backoff, RetryConfig.MAX_DELAY)
        
        raise last_exception
    
    @staticmethod
    def retry_decorator(
        max_retries: int = RetryConfig.MAX_RETRIES,
        delay: float = RetryConfig.INITIAL_DELAY,
        backoff: float = RetryConfig.BACKOFF_FACTOR,
        exceptions: tuple = (Exception,)
    ):
        """リトライデコレーター"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await EnhancedErrorHandler.retry_async(
                    func, *args,
                    max_retries=max_retries,
                    delay=delay,
                    backoff=backoff,
                    exceptions=exceptions,
                    **kwargs
                )
            return wrapper
        return decorator
    
    @staticmethod
    async def safe_cleanup(cleanup_func: Callable, context: str = "") -> bool:
        """安全なクリーンアップ実行"""
        try:
            logger.info(f"🧹 クリーンアップ: {context}")
            
            if asyncio.iscoroutinefunction(cleanup_func):
                await cleanup_func()
            else:
                cleanup_func()
            
            logger.info(f"✅ クリーンアップ完了: {context}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ クリーンアップ失敗（無視）: {context}")
            logger.warning(f"理由: {str(e)}")
            return False
    
    @staticmethod
    def validate_file_path(path: Any, must_exist: bool = False) -> Optional[Path]:
        """ファイルパスのバリデーション"""
        try:
            if not path:
                return None
            
            # 文字列に変換
            path_str = str(path).strip()
            
            # URLの場合はNone
            if path_str.lower().startswith(('http://', 'https://')):
                logger.warning(f"URLが指定されました（ファイルパスではありません）: {path_str}")
                return None
            
            # Pathオブジェクトに変換
            path_obj = Path(path_str)
            
            # 存在確認が必要な場合
            if must_exist and not path_obj.exists():
                logger.error(f"❌ パスが存在しません: {path_obj}")
                return None
            
            # 正規化して返す
            return path_obj.resolve()
            
        except Exception as e:
            logger.error(f"パスバリデーションエラー: {path}")
            EnhancedErrorHandler.log_error_with_context(e, "パスバリデーション")
            return None
    
    @staticmethod
    def handle_import_error(module_name: str, optional: bool = True) -> bool:
        """インポートエラーのハンドリング"""
        try:
            __import__(module_name)
            logger.info(f"✅ モジュールインポート成功: {module_name}")
            return True
            
        except ImportError as e:
            if optional:
                logger.warning(f"⚠️ オプショナルモジュール未検出（スキップ）: {module_name}")
                return False
            else:
                logger.error(f"❌ 必須モジュールが見つかりません: {module_name}")
                EnhancedErrorHandler.log_error_with_context(e, f"インポート: {module_name}")
                raise
    
    @staticmethod
    async def timeout_wrapper(
        coro,
        timeout: float,
        context: str = ""
    ) -> Any:
        """タイムアウト付き実行"""
        try:
            result = await asyncio.wait_for(coro, timeout=timeout)
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"⏱️ タイムアウト（{timeout}秒）: {context}")
            raise TimeoutError(f"{context} がタイムアウトしました（{timeout}秒）")
        
        except Exception as e:
            EnhancedErrorHandler.log_error_with_context(e, context)
            raise


class BrowserErrorHandler:
    """ブラウザ専用エラーハンドラー"""
    
    @staticmethod
    async def handle_browser_crash(browser_controller, max_retries: int = 3):
        """ブラウザクラッシュのハンドリング"""
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"🌐 ブラウザ再起動試行 {attempt}/{max_retries}")
                
                # 既存インスタンスのクリーンアップ
                try:
                    await browser_controller.cleanup()
                except:
                    pass
                
                # 少し待機
                await asyncio.sleep(3)
                
                # 再初期化
                await browser_controller.setup_browser()
                
                # 動作確認
                if browser_controller.page:
                    test_result = await browser_controller.page.evaluate("1 + 1")
                    if test_result == 2:
                        logger.info(f"✅ ブラウザ復旧成功（試行 {attempt}）")
                        return True
                
            except Exception as e:
                logger.warning(f"ブラウザ再起動失敗（試行 {attempt}）: {e}")
                
                if attempt == max_retries:
                    logger.error("❌ ブラウザ復旧不可能")
                    raise Exception("ブラウザの再起動に失敗しました")
                
                await asyncio.sleep(5)
        
        return False
    
    @staticmethod
    async def safe_page_action(page, action_func, context: str = "", timeout: float = 30.0):
        """安全なページ操作"""
        try:
            return await EnhancedErrorHandler.timeout_wrapper(
                action_func(),
                timeout=timeout,
                context=context
            )
            
        except Exception as e:
            logger.error(f"ページ操作失敗: {context}")
            EnhancedErrorHandler.log_error_with_context(e, context)
            raise


class SheetErrorHandler:
    """Google Sheets専用エラーハンドラー"""
    
    @staticmethod
    async def safe_sheet_operation(operation_func, *args, **kwargs):
        """安全なシート操作"""
        try:
            return await EnhancedErrorHandler.retry_async(
                operation_func,
                *args,
                max_retries=3,
                delay=2.0,
                exceptions=(Exception,),
                **kwargs
            )
            
        except Exception as e:
            logger.error("Google Sheets操作が全リトライ失敗")
            EnhancedErrorHandler.log_error_with_context(e, "Sheets操作")
            
            # フォールバック: ローカルキャッシュなど
            logger.warning("⚠️ オフラインモードに切り替え（データ未保存）")
            return None


class TaskErrorHandler:
    """タスク実行専用エラーハンドラー"""
    
    @staticmethod
    async def handle_task_failure(
        task: dict,
        error: Exception,
        sheets_manager,
        retry: bool = True
    ) -> bool:
        """タスク失敗のハンドリング"""
        try:
            logger.error(f"❌ タスク失敗: {task.get('task_id', 'UNKNOWN')}")
            EnhancedErrorHandler.log_error_with_context(
                error,
                f"タスク {task.get('description', 'N/A')[:50]}"
            )
            
            # ステータス更新
            try:
                await sheets_manager.update_task_status(
                    task['task_id'],
                    'failed',
                    error_message=str(error)
                )
            except Exception as update_error:
                logger.warning(f"ステータス更新失敗: {update_error}")
            
            # リトライ可能かチェック
            if retry and TaskErrorHandler.is_retryable_error(error):
                logger.info("🔄 リトライ可能なエラー")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"タスク失敗ハンドリング中のエラー: {e}")
            return False
    
    @staticmethod
    def is_retryable_error(error: Exception) -> bool:
        """リトライ可能なエラーか判定"""
        retryable_patterns = [
            "timeout",
            "network",
            "connection",
            "temporary",
            "rate limit"
        ]
        
        error_str = str(error).lower()
        return any(pattern in error_str for pattern in retryable_patterns)


# 使用例
if __name__ == "__main__":
    async def example_usage():
        # リトライデコレーターの使用例
        @EnhancedErrorHandler.retry_decorator(max_retries=3)
        async def unstable_operation():
            # 不安定な処理
            import random
            if random.random() < 0.7:
                raise Exception("一時的なエラー")
            return "成功"
        
        try:
            result = await unstable_operation()
            print(f"結果: {result}")
        except Exception as e:
            print(f"失敗: {e}")
    
    asyncio.run(example_usage())