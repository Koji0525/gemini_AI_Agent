#!/usr/bin/env python3
"""実用ツール生成版でタスク実行"""
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.task_execution.enhanced_executor_v2_practical import PracticalToolExecutor
from tools.sheets_manager import GoogleSheetsManager

def main():
    task_id = sys.argv[1] if len(sys.argv) > 1 else '469'
    
    # タスク取得
    sheets = GoogleSheetsManager()
    tasks = sheets.read_range('pm_tasks!A2:M1000')
    
    target_task = None
    for row in tasks:
        if row[0] == task_id:
            target_task = {
                'task_id': row[0],
                'description': row[2] if len(row) > 2 else '',
                'required_role': row[3] if len(row) > 3 else 'implementation'
            }
            break
    
    if not target_task:
        print(f"❌ タスク {task_id} が見つかりません")
        sys.exit(1)
    
    # 実用ツール生成版で実行
    executor = PracticalToolExecutor()
    result = executor.execute_task_with_details(target_task)
    
    print(f"\n✅ 実行完了")
    print(f"保存先: {result.get('task_dir')}")
    print(f"\n{result.get('execution_log', '')}")

if __name__ == '__main__':
    main()
