"""
TaskExecutor への統合例
scripts/task_executor.py の execute_task メソッドに追加
"""

async def execute_task(self, task: Dict) -> bool:
    """
    タスクを実行（Sheets書き戻し統合版）
    """
    task_id = task.get('id', 'unknown')
    
    try:
        # 実行中ステータスに更新
        if self.sheets_manager:
            self.sheets_manager.update_task_status(
                task_id=task_id,
                status="in_progress"
            )
        
        # タスク実行（既存のロジック）
        result = await self._execute_task_logic(task)
        
        # 成功時の書き戻し
        if result.get('success'):
            if self.sheets_manager:
                self.sheets_manager.update_task_status(
                    task_id=task_id,
                    status="completed",
                    result=result,
                    output_file=result.get('output_file')
                )
            return True
        else:
            # 失敗時の書き戻し
            if self.sheets_manager:
                self.sheets_manager.update_task_status(
                    task_id=task_id,
                    status="failed",
                    error_message=result.get('error', 'Unknown error')
                )
            return False
            
    except Exception as e:
        # エラー時の書き戻し
        if self.sheets_manager:
            self.sheets_manager.update_task_status(
                task_id=task_id,
                status="failed",
                error_message=str(e)
            )
        raise

