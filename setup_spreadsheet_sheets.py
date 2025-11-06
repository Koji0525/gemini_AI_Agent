#!/usr/bin/env python3
"""
📋 スプレッドシート初期設定
目的: 必要なシート（project_goal, pm_tasks, task_execution_log）を作成
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.sheets_manager import GoogleSheetsManager
import os
from dotenv import load_dotenv

def setup_sheets():
    load_dotenv()
    
    sheets = GoogleSheetsManager()
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    
    sheets.open_spreadsheet(spreadsheet_id)
    
    # 必要なシートとヘッダー
    sheet_configs = {
        "project_goal": [
            ["goal_id", "description", "priority", "status", "created_at"]
        ],
        "pm_tasks": [
            ["task_id", "parent_goal_id", "description", "required_role", 
             "status", "priority", "estimated_time", "dependencies", 
             "created_at", "batch_id"]
        ],
        "task_execution_log": [
            ["task_id", "status", "output", "executed_at", "knowledge_used"]
        ]
    }
    
    print("=" * 60)
    print("📋 スプレッドシート初期設定")
    print("=" * 60)
    
    # 既存シート確認（簡易版）
    try:
        for sheet_name, headers in sheet_configs.items():
            try:
                # シートが存在するか確認
                data = sheets.read_sheet(f"{sheet_name}!A1:Z1")
                
                if not data or len(data) == 0:
                    # ヘッダーが空なら追加
                    sheets.write_sheet(f"{sheet_name}!A1", headers)
                    print(f"✅ {sheet_name}: ヘッダー追加")
                else:
                    print(f"ℹ️  {sheet_name}: 既に存在")
                    
            except Exception as e:
                # シートが存在しない場合
                print(f"⚠️  {sheet_name}: 手動作成が必要")
                print(f"   エラー: {e}")
                print(f"   → スプレッドシートで '{sheet_name}' シートを作成してください")
        
        print("=" * 60)
        print("✅ 設定完了")
        print("\n📝 次のステップ:")
        print("  1. スプレッドシートで不足しているシートを手動作成")
        print("  2. python3 test_orchestrator_5min.py を実行")
        
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == '__main__':
    setup_sheets()
