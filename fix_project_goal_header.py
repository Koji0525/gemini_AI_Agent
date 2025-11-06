#!/usr/bin/env python3
"""
project_goal シートのヘッダー修正
問題: 重複ヘッダー（空列）
解決: 正しいヘッダーで上書き
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.sheets_manager import GoogleSheetsManager
import os
from dotenv import load_dotenv

def fix_header():
    load_dotenv()
    
    sheets = GoogleSheetsManager()
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    sheets.open_spreadsheet(spreadsheet_id)
    
    # 正しいヘッダー
    correct_header = [
        ["goal_id", "description", "priority", "status", "created_at"]
    ]
    
    print("=" * 60)
    print("🔧 project_goal ヘッダー修正")
    print("=" * 60)
    
    # ヘッダー上書き
    success = sheets.write_sheet('project_goal!A1:E1', correct_header)
    
    if success:
        print("✅ ヘッダー修正完了")
        print(f"   設定: {correct_header[0]}")
    else:
        print("❌ ヘッダー修正失敗")
    
    print("=" * 60)

if __name__ == '__main__':
    fix_header()
