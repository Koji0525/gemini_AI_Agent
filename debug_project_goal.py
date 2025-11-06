#!/usr/bin/env python3
"""
🔍 project_goal デバッグ
目的: ヘッダーの状態を詳細に確認
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.sheets_manager import GoogleSheetsManager
import os
from dotenv import load_dotenv

def debug_header():
    load_dotenv()
    
    sheets = GoogleSheetsManager()
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    sheets.open_spreadsheet(spreadsheet_id)
    
    print("=" * 60)
    print("🔍 project_goal ヘッダー詳細確認")
    print("=" * 60)
    
    # 生のAPIで1行目を取得
    try:
        # gspread経由で直接取得
        worksheet = sheets.spreadsheet.worksheet('project_goal')
        
        # 1行目全体を取得
        first_row = worksheet.row_values(1)
        
        print(f"✅ 1行目のセル数: {len(first_row)}")
        print()
        print("📋 各セルの内容:")
        for i, cell in enumerate(first_row, 1):
            if cell.strip() == "":
                print(f"   列{i}: [空白] ← 👈 これが問題！")
            else:
                print(f"   列{i}: '{cell}'")
        
        print()
        print("=" * 60)
        print("🔧 対処方法:")
        
        empty_count = sum(1 for cell in first_row if cell.strip() == "")
        if empty_count > 0:
            print(f"  ❌ {empty_count}個の空白列を削除してください")
            print()
            print("  手順:")
            print("  1. スプレッドシートで project_goal シートを開く")
            print("  2. 1行目の空白セルがある列を右クリック → 削除")
            print("  3. 正しいヘッダーのみ残す:")
            print("     A1:goal_id, B1:description, C1:priority, D1:status, E1:created_at")
        else:
            print("  ✅ 空白列は見つかりませんでした")
            print("  他の問題の可能性があります")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        print()
        print("📝 次のステップ:")
        print("  1. スプレッドシートで project_goal シートを確認")
        print("  2. 1行目のヘッダーを手動で確認")
        print("  3. 余分な列を削除")

if __name__ == '__main__':
    debug_header()
