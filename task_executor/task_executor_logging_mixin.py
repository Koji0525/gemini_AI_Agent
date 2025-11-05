"""
TaskExecutor用のログ記録Mixin
elapsed_time, retry_count, error_type, fix_appliedを記録
"""
import time
from datetime import datetime
from tools.sheets_validator import SheetsValidator

class TaskExecutorLoggingMixin:
    """タスク実行ログ記録のMixin"""
    
    def __init__(self):
        self.validator = SheetsValidator()
        self.task_start_time = None
    
    def start_task_timer(self):
        """タスク実行時間の計測開始"""
        self.task_start_time = time.time()
    
    def stop_task_timer(self):
        """タスク実行時間の計測終了"""
        if self.task_start_time:
            elapsed = time.time() - self.task_start_time
            self.task_start_time = None
            return round(elapsed, 2)
        return 0.0
    
    def create_execution_log(self, task, result, error=None):
        """実行ログデータを作成（14列完全対応）"""
        elapsed_time = self.stop_task_timer()
        
        log_data = {
            "log_id": f"LOG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "task_id": task.get('task_id', 'UNKNOWN'),
            "task_description": task.get('description', '')[:100],  # 100文字まで
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "agent_role": task.get('required_role', 'unknown'),
            "output_summary": result.get('summary', '') if result else 'Error',
            "output_data": str(result.get('data', ''))[:200] if result else '',  # 200文字まで
            "status": "completed" if not error else "failed",
            "Quality_Score": result.get('quality_score', 0) if result else 0,
            "Quality_description": result.get('quality_desc', '') if result else '',
            "elapsed_time": elapsed_time,
            "retry_count": task.get('retry_count', 0),
            "error_type": type(error).__name__ if error else "",
            "fix_applied": task.get('fix_applied', False)
        }
        
        # 検証付きでrow作成
        row = self.validator.create_valid_row("task_execution_log", log_data)
        is_valid, message = self.validator.validate_before_write("task_execution_log", row)
        
        if not is_valid:
            print(f"⚠️ ログデータ検証エラー: {message}")
        
        return row, is_valid

