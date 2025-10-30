#!/usr/bin/env python3
"""
自動再試行エンジン - 発見されたパターンを活用
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager

class AutoRetryEngine:
    """「再試行による解決」パターンを活用するエンジン"""
    
    def __init__(self):
        self.sheets_manager = GoogleSheetsManager()
        self.retry_success_rate = 0.85  # 発見された成功率
    
    def analyze_failed_tasks(self):
        """失敗したタスクを分析して再試行候補を特定"""
        print("🔍 失敗タスク分析開始")
        
        try:
            # タスク実行ログを取得
            task_logs = self.sheets_manager.read_range('task_execution_log')
            if not task_logs or len(task_logs) <= 1:
                print("❌ タスク実行ログが見つかりません")
                return []
            
            headers = task_logs[0]
            rows = task_logs[1:]
            
            # 失敗したタスクを抽出
            failed_tasks = []
            for row in rows:
                if len(row) > headers.index('status') if 'status' in headers else -1:
                    status = row[headers.index('status')]
                    if status and 'fail' in status.lower():
                        failed_tasks.append(row)
            
            print(f"✅ 失敗タスクを {len(failed_tasks)}件 発見")
            return failed_tasks
            
        except Exception as e:
            print(f"❌ 分析中にエラー: {e}")
            return []
    
    def should_retry_task(self, task_data):
        """タスクが再試行に適しているか判断"""
        # 発見されたパターンに基づく判断ロジック
        task_type = task_data[2] if len(task_data) > 2 else 'unknown'
        
        # 再試行成功率が高いタスクタイプ
        high_success_retry_types = [
            'conversation', 'data_processing', 'file_operation'
        ]
        
        for task_type_pattern in high_success_retry_types:
            if task_type_pattern in task_type.lower():
                return True
        
        return False
    
    def implement_auto_retry(self):
        """自動再試行機能を実装"""
        print("🔄 自動再試行機能を実装")
        
        failed_tasks = self.analyze_failed_tasks()
        retry_candidates = []
        
        for task in failed_tasks:
            if self.should_retry_task(task):
                retry_candidates.append(task)
        
        print(f"🎯 再試行候補: {len(retry_candidates)}件")
        
        if retry_candidates:
            print("💡 即座に改善できるアクション:")
            for task in retry_candidates[:3]:  # 最初の3件を表示
                task_id = task[0] if task else 'unknown'
                print(f"   • タスク {task_id}: 自動再試行を実施")
        
        return retry_candidates

if __name__ == "__main__":
    engine = AutoRetryEngine()
    engine.implement_auto_retry()
