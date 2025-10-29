"""RetryManager - リトライ管理"""
import asyncio
import uuid
from typing import Callable, Dict, Any, Optional
from datetime import datetime
import logging
from .utils.error_classifier import ErrorClassifier
from .retry_strategies import StrategyFactory

logger = logging.getLogger(__name__)

class RetryManager:
    """リトライ戦略を管理"""
    MAX_RETRY_LIMIT = 10
    
    def __init__(self, sheets_manager: Optional[Any] = None):
        self.sheets = sheets_manager
        self.error_classifier = ErrorClassifier()
        self.strategy_factory = StrategyFactory()
        self.stats = {
            'total_retries': 0,
            'successful_retries': 0,
            'failed_retries': 0,
            'by_error_type': {}
        }
        logger.info("RetryManager initialized")
    
    async def execute_with_retry(
        self, task_func: Callable, task_name: str,
        max_attempts: int = 3, strategy: Optional[Any] = None, **kwargs
    ) -> Dict[str, Any]:
        """タスクをリトライ機能付きで実行"""
        if max_attempts > self.MAX_RETRY_LIMIT:
            logger.warning(f"max_attempts ({max_attempts}) exceeds limit. Setting to {self.MAX_RETRY_LIMIT}")
            max_attempts = self.MAX_RETRY_LIMIT
        
        retry_id = str(uuid.uuid4())[:8]
        start_time = datetime.now()
        logger.info(f"[{retry_id}] Starting task '{task_name}' (max_attempts: {max_attempts})")
        
        errors_encountered = []
        strategies_used = []
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"[{retry_id}] Attempt {attempt + 1}/{max_attempts} for '{task_name}'")
                result = await task_func(**kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(f"[{retry_id}] Task '{task_name}' succeeded on attempt {attempt + 1} ({duration:.2f}s)")
                
                if attempt > 0:
                    self.stats['successful_retries'] += 1
                
                await self._record_retry_history(
                    retry_id, task_name, attempt + 1, max_attempts,
                    None, strategies_used[-1] if strategies_used else None,
                    True, duration, errors_encountered
                )
                
                return {
                    'success': True, 'result': result, 'attempts': attempt + 1,
                    'duration_seconds': duration, 'errors_encountered': errors_encountered,
                    'strategies_used': strategies_used
                }
            
            except Exception as e:
                error_type = self.error_classifier.classify(e)
                error_details = self.error_classifier.get_error_details(e)
                errors_encountered.append({
                    'attempt': attempt + 1, 'error_type': error_type,
                    'error_class': error_details['error_class'],
                    'error_message': error_details['error_message']
                })
                logger.error(f"[{retry_id}] Attempt {attempt + 1} failed: {error_type} - {str(e)}")
                
                if not self.error_classifier.is_retryable(e):
                    logger.error(f"[{retry_id}] Error is not retryable. Aborting.")
                    break
                
                if attempt < max_attempts - 1:
                    if strategy is None:
                        selected_strategy = self.strategy_factory.create_strategy(error_type)
                    else:
                        selected_strategy = strategy
                    
                    strategies_used.append(selected_strategy.name)
                    await selected_strategy.wait(attempt)
                    self.stats['total_retries'] += 1
                    
                    if error_type not in self.stats['by_error_type']:
                        self.stats['by_error_type'][error_type] = 0
                    self.stats['by_error_type'][error_type] += 1
                else:
                    logger.error(f"[{retry_id}] Max attempts ({max_attempts}) reached. Task '{task_name}' failed.")
        
        duration = (datetime.now() - start_time).total_seconds()
        self.stats['failed_retries'] += 1
        
        await self._record_retry_history(
            retry_id, task_name, max_attempts, max_attempts,
            errors_encountered[-1]['error_type'] if errors_encountered else 'unknown',
            strategies_used[-1] if strategies_used else None,
            False, duration, errors_encountered
        )
        
        return {
            'success': False, 'result': None, 'attempts': max_attempts,
            'duration_seconds': duration, 'errors_encountered': errors_encountered,
            'strategies_used': strategies_used
        }
    
    async def _record_retry_history(
        self, retry_id: str, task_name: str, attempt: int, max_attempts: int,
        error_type: Optional[str], strategy_used: Optional[str],
        success: bool, duration: float, errors: list
    ):
        """リトライ履歴をGoogle Sheetsに記録"""
        if self.sheets is None:
            logger.debug("Sheets manager not available. Skipping history recording.")
            return
        
        try:
            timestamp = datetime.now().isoformat()
            record = {
                'retry_id': retry_id, 'timestamp': timestamp, 'task_name': task_name,
                'attempt_number': attempt, 'max_attempts': max_attempts,
                'error_type': error_type or 'N/A',
                'error_message': errors[-1]['error_message'] if errors else 'N/A',
                'strategy_used': strategy_used or 'N/A', 'wait_time': 0.0,
                'success': 'Yes' if success else 'No',
                'total_duration': f"{duration:.2f}",
                'notes': f"Total errors: {len(errors)}"
            }
            await self.sheets.append_row('retry_history', list(record.values()))
            logger.debug(f"[{retry_id}] Retry history recorded to Google Sheets")
        except Exception as e:
            logger.error(f"Failed to record retry history: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        total = self.stats['total_retries']
        successful = self.stats['successful_retries']
        return {
            'total_retries': total, 'successful_retries': successful,
            'failed_retries': self.stats['failed_retries'],
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'by_error_type': self.stats['by_error_type']
        }
    
    def reset_stats(self):
        """統計情報をリセット"""
        self.stats = {
            'total_retries': 0, 'successful_retries': 0,
            'failed_retries': 0, 'by_error_type': {}
        }
        logger.info("Statistics reset")
