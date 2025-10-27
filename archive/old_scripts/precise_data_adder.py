#!/usr/bin/env python3
"""
正確なデータ追加スクリプト - 列を1つずつ正確に追加
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configuration.config_loader import ConfigLoader
import gspread
from google.oauth2.service_account import Credentials

class PreciseDataAdder:
    def __init__(self):
        self.config = ConfigLoader()
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.credentials = Credentials.from_service_account_file(
            self.config.get('service_account_file'), 
            scopes=self.scopes
        )
        self.gc = gspread.authorize(self.credentials)
        self.spreadsheet = self.gc.open_by_key(self.config.get('spreadsheet_id'))
    
    def add_precise_row(self):
        """正確に揃った行を追加"""
        print("🎯 正確なデータ行追加")
        print("=" * 50)
        
        try:
            dashboard_sheet = self.spreadsheet.worksheet('progress_dashboard')
            
            # 現在のデータを確認
            current_data = dashboard_sheet.get_all_values()
            print(f"📊 現在の行数: {len(current_data)}")
            
            if current_data:
                print("📋 現在のヘッダー確認:")
                headers = current_data[0]
                for i, header in enumerate(headers, 1):
                    print(f"   {i}. {header}")
            
            # 正確なデータ行を作成（16列完全一致）
            precise_data = {
                'A': 'PRECISE-001',  # goal_id
                'B': '正確なデータテスト - M&Aポータル開発',  # goal_name
                'C': '97',           # total_tasks
                'D': '85',           # completed_tasks
                'E': '87.6',         # progress_rate
                'F': '8.5',          # avg_quality
                'G': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # last_updated
                'H': 'Active',       # status
                'I': '1',            # priority
                'J': 'Quality Checker',  # assigned_agent
                'K': '2025-10-01',   # start_date
                'L': '2025-12-31',   # due_date
                'M': '',             # actual_completion_date
                'N': '列揃え確認',   # blockers
                'O': '低',           # risk_level
                'P': '品質確認レポート'  # deliverables
            }
            
            # 行を追加
            next_row = len(current_data) + 1
            print(f"\n📍 追加位置: 行 {next_row}")
            
            # 各列に正確にデータを設定
            for col_letter, value in precise_data.items():
                cell = f'{col_letter}{next_row}'
                dashboard_sheet.update(cell, value)
                print(f"✅ {cell}: {value}")
            
            print(f"\n🎉 正確なデータ追加完了!")
            print("📋 追加されたデータ:")
            for col, value in precise_data.items():
                print(f"   {col}列: {value}")
                
        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback
            traceback.print_exc()
    
    def verify_alignment(self):
        """列の揃いを確認"""
        print("\n�� 列揃い確認")
        print("-" * 30)
        
        try:
            dashboard_sheet = self.spreadsheet.worksheet('progress_dashboard')
            data = dashboard_sheet.get_all_values()
            
            if not data:
                print("❌ データがありません")
                return
            
            print(f"📊 総行数: {len(data)}")
            print(f"📏 列数: {len(data[0])} (ヘッダー)")
            
            # 各行の列数をチェック
            misaligned_rows = []
            for i, row in enumerate(data, 1):
                if len(row) != len(data[0]):
                    misaligned_rows.append((i, len(row)))
            
            if misaligned_rows:
                print("❌ 揃っていない行:")
                for row_num, col_count in misaligned_rows:
                    print(f"   行 {row_num}: {col_count}列 (期待: {len(data[0])}列)")
            else:
                print("✅ すべての行が正しく揃っています！")
                
        except Exception as e:
            print(f"❌ 確認エラー: {e}")

def main():
    adder = PreciseDataAdder()
    
    # 列揃いを確認
    adder.verify_alignment()
    
    # 正確な行を追加
    adder.add_precise_row()
    
    # 再度確認
    adder.verify_alignment()

if __name__ == "__main__":
    main()
