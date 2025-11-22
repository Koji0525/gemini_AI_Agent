"""
堅牢なエラーハンドリング
多層的なエラー処理と自動復旧
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Callable

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class RobustErrorHandler:
    """堅牢なエラーハンドリング"""
    
    ERROR_TYPES = {
        'network': ['ConnectionError', 'Timeout', 'URLError'],
        'api': ['403', '429', '500', '502', '503'],
        'resource': ['MemoryError', 'DiskFull', 'IOError'],
        'unknown': ['Exception']
    }
    
    def __init__(self):
        self.error_log_file = Path("logs/errors.json")
        self.error_log_file.parent.mkdir(exist_ok=True, parents=True)
        
    def handle_with_retry(
        self, 
        func: Callable, 
        max_retries: int = 3,
        *args, 
        **kwargs
    ):
        """リトライ付きエラーハンドリング"""
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
                
            except Exception as e:
                error_type = self._classify_error(e)
                
                print(f"❌ エラー発生（試行 {attempt + 1}/{max_retries}）")
                print(f"   タイプ: {error_type}")
                print(f"   詳細: {str(e)}")
                
                if attempt < max_retries - 1:
                    wait_time = self._get_wait_time(error_type, attempt)
                    print(f"   {wait_time}秒後にリトライ...")
                    time.sleep(wait_time)
                else:
                    print(f"   最大リトライ回数到達")
                    self._log_error(e, error_type)
                    raise
    
    def _classify_error(self, error: Exception) -> str:
        """エラーを分類"""
        error_str = str(type(error).__name__)
        error_msg = str(error)
        
        for error_type, patterns in self.ERROR_TYPES.items():
            for pattern in patterns:
                if pattern in error_str or pattern in error_msg:
                    return error_type
        
        return 'unknown'
    
    def _get_wait_time(self, error_type: str, attempt: int) -> int:
        """待機時間を取得（指数バックオフ）"""
        base_wait = {
            'network': 5,
            'api': 10,
            'resource': 15,
            'unknown': 5
        }
        
        wait = base_wait.get(error_type, 5)
        
        # 指数バックオフ
        return wait * (2 ** attempt)
    
    def _log_error(self, error: Exception, error_type: str):
        """エラーをログに記録"""
        import json
        
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'error_class': type(error).__name__,
            'message': str(error)
        }
        
        # 既存のログを読み込み
        if self.error_log_file.exists():
            with open(self.error_log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(error_entry)
        
        # 最新100件のみ保持
        logs = logs[-100:]
        
        with open(self.error_log_file, 'w') as f:
            json.dump(logs, f, indent=2)

