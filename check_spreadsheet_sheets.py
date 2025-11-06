#!/usr/bin/env python3
"""
📋 スプレッドシートシート確認 v3.0
目的: 必要なシートが存在するか確認
更新: read_sheet メソッドを使用
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.sheets_manager import GoogleSheetsManager
import os
from dotenv import load_dotenv

def check_sheets():
    load_dotenv()
    
    sheets = GoogleSheetsManager()
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    
    sheets.open_spreadsheet(spreadsheet_id)
    
    # 必要なシート
    required_sheets = ["project_goal", "pm_tasks", "task_execution_log"]
    
    print("=" * 60)
    print("📋 スプレッドシートシート確認")
    print("=" * 60)
    
    existing_sheets = []
    missing_sheets = []
    
    for sheet_name in required_sheets:
        try:
            # read_sheet で存在確認（空でもOK）
            data = sheets.read_sheet(sheet_name)
            existing_sheets.append(sheet_name)
            row_count = len(data) if data else 0
            print(f"✅ {sheet_name}: 存在（{row_count}行）")
        except Exception as e:
            # シート名がエラーメッセージに含まれる = シート不足
            error_msg = str(e).lower()
            if sheet_name.lower() in error_msg or "unable to parse" in error_msg:
                missing_sheets.append(sheet_name)
                print(f"❌ {sheet_name}: 不足")
            else:
                print(f"⚠️  {sheet_name}: 確認エラー ({e})")
    
    print()
    print("=" * 60)
    
    if missing_sheets:
        print("🚨 スプレッドシートにシートが不足しています！")
        print()
        print("📝 手動作成が必要なシート:")
        for i, sheet in enumerate(missing_sheets, 1):
            print(f"   {i}. {sheet}")
        print()
        print("🔧 作成手順:")
        print(f"  1. スプレッドシートを開く:")
        print(f"     https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        print()
        print(f"  2. 画面下部の「+」ボタンで新しいシートを{len(missing_sheets)}個作成")
        print()
        print(f"  3. 各シート名を以下に変更:")
        for sheet in missing_sheets:
            print(f"     - {sheet}")
        print()
        print(f"  4. 作成後、再度このスクリプトを実行:")
        print(f"     python3 check_spreadsheet_sheets.py")
        return False
    else:
        print("✅ すべての必要なシートが存在します！")
        print()
        print("📝 次のステップ:")
        print("  1. python3 seed_sample_data.py          # サンプルデータ投入")
        print("  2. python3 test_orchestrator_5min.py    # 5分間テスト")
        return True

if __name__ == '__main__':
    success = check_sheets()
    sys.exit(0 if success else 1)
