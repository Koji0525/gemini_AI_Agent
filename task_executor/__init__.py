"""
タスク実行モジュール
"""

from .task_executor_content import ContentTaskExecutor
from .task_executor_ma import MATaskExecutor, WordPressTaskExecutor
from .content_task_executor import ContentTaskExecutor as ContentExecutor

# メインのTaskExecutorをインポート
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from task_executor import TaskExecutor
except ImportError:
    # フォールバック: 直接インポート
    from task_executor_base import TaskExecutor

__all__ = [
    'ContentTaskExecutor',
    'MATaskExecutor', 
    'WordPressTaskExecutor',
    'ContentExecutor',
    'TaskExecutor'
]
