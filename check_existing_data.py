#!/usr/bin/env python3
"""
📊 既存データ確認
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.sheets_manager import GoogleSheetsManager
import os
from dotenv import load_dotenv

def check_data():
    load_dotenv()
    
    sheets = GoogleSheetsManager()
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    
    sheets.open_spreadsheet(spreadsheet_id)
    
    print("=" * 60)
    print("📊 既存データ確認")
    print("=" * 60)
    
    # project_goal
    try:
        goals = sheets.read_sheet('project_goal')
        print(f"✅ project_goal: {len(goals)}件")
        if goals:
            print(f"   サンプル: {goals[0] if goals else 'なし'}")
    except Exception as e:
        print(f"⚠️  project_goal: {e}")
    
    # pm_tasks
    try:
        tasks = sheets.read_sheet('pm_tasks')
        print(f"✅ pm_tasks: {len(tasks)}件")
        if tasks:
            print(f"   サンプル: {tasks[0] if tasks else 'なし'}")
    except Exception as e:
        print(f"⚠️  pm_tasks: {e}")
    
    # task_execution_log
    try:
        logs = sheets.read_sheet('task_execution_log')
        print(f"✅ task_execution_log: {len(logs)}件")
        if logs:
            print(f"   サンプル: {logs[0] if logs else 'なし'}")
    except Exception as e:
        print(f"⚠️  task_execution_log: {e}")
    
    print("=" * 60)
    print("✅ データ確認完了")
    print()
    print("📝 次のステップ:")
    print("  python3 test_orchestrator_5min.py  # 5分間テスト実行")

if __name__ == '__main__':
    check_data()
