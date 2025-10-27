#!/usr/bin/env python3
"""
安全なデータ追加スクリプト - 列数を厳密に制御
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configuration.config_loader import ConfigLoader
import gspread
from google.oauth2.service_account import Credentials

class SafeDataAdder:
    def __init__(self):
        self.config = ConfigLoader()
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.credentials = Credentials.from_service_account_file(
            self.config.get('service_account_file'), 
            scopes=self.scopes
        )
        self.gc = gspread.authorize(self.credentials)
        self.spreadsheet = self.gc.open_by_key(self.config.get('spreadsheet_id'))
    
    def add_data_safely(self, use_clean_sheet=False):
        """安全にデータを追加"""
        sheet_name = 'progress_dashboard_clean' if use_clean_sheet else 'progress_dashboard'
        
        try:
            if use_clean_sheet:
                worksheet = self.spreadsheet.worksheet(sheet_name)
            else:
                worksheet = self.spreadsheet.worksheet(sheet_name)
            
            print(f"📝 データ追加先: {sheet_name}")
            
            # 現在のデータを取得
            current_data = worksheet.get_all_values()
            next_row = len(current_data) + 1
            
            print(f"📍 追加行: {next_row}")
            
            # 厳密に16列のデータを作成
            new_row = [
                'SAFE-001',  # A: goal_id
                '安全なデータ追加テスト',  # B: goal_name
                '97',        # C: total_tasks
                '85',        # D: completed_tasks
                '87.6',      # E: progress_rate
                '8.5',       # F: avg_quality
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # G: last_updated
                'Active',    # H: status
                '2',         # I: priority
                'Safe Adder', # J: assigned_agent
                '2025-10-01', # K: start_date
                '2025-12-31', # L: due_date
                '',          # M: actual_completion_date
                '安全テスト', # N: blockers
                '低',        # O: risk_level
                '安全レポート' # P: deliverables
            ]
            
            # 範囲を厳密に指定して更新
            range_str = f'A{next_row}:P{next_row}'
            worksheet.update(range_name=range_str, values=[new_row])
            
            print("✅ 安全にデータを追加しました")
            print(f"📋 範囲: {range_str}")
            print("🔒 16列に厳密に制御されています")
            
            # 確認
            updated_data = worksheet.get_all_values()
            last_row = updated_data[-1] if updated_data else []
            print(f"📏 実際の列数: {len(last_row)}列")
            
        except Exception as e:
            print(f"❌ 追加エラー: {e}")
    
    def check_current_sheets(self):
        """現在のシートを確認"""
        print("📋 利用可能なシート:")
        sheets = self.spreadsheet.worksheets()
        for sheet in sheets:
            data = sheet.get_all_values()
            col_count = len(data[0]) if data else 0
            row_count = len(data) if data else 0
            print(f"   📄 {sheet.title}: {row_count}行 × {col_count}列")

def main():
    adder = SafeDataAdder()
    
    # 現在のシートを確認
    adder.check_current_sheets()
    
    print("\n🎯 データ追加方法を選択:")
    print("   1. 既存のprogress_dashboardに追加")
    print("   2. クリーンなシートに追加（推奨）")
    
    choice = input("選択 (1 or 2): ").strip()
    
    if choice == "2":
        adder.add_data_safely(use_clean_sheet=True)
    else:
        adder.add_data_safely(use_clean_sheet=False)

if __name__ == "__main__":
    main()
