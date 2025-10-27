#!/usr/bin/env python3
"""
最終版列修正スクリプト - 列数を完全に16列に固定
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configuration.config_loader import ConfigLoader
import gspread
from google.oauth2.service_account import Credentials

class FinalColumnFixer:
    def __init__(self):
        self.config = ConfigLoader()
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.credentials = Credentials.from_service_account_file(
            self.config.get('service_account_file'), 
            scopes=self.scopes
        )
        self.gc = gspread.authorize(self.credentials)
        self.spreadsheet = self.gc.open_by_key(self.config.get('spreadsheet_id'))
    
    def completely_fix_columns(self):
        """列数を完全に16列に固定"""
        print("🔧 最終版列修正 - 完全な16列固定")
        print("=" * 50)
        
        try:
            dashboard_sheet = self.spreadsheet.worksheet('progress_dashboard')
            
            # 現在のデータを取得
            current_data = dashboard_sheet.get_all_values()
            print(f"📊 修正前: {len(current_data)}行 × {len(current_data[0])}列")
            
            # 16列に厳密に制限したデータを作成
            fixed_data = []
            for row in current_data:
                # 16列に切り詰め、足りない場合は空文字で埋める
                fixed_row = (row[:16] if len(row) > 16 else row) + [''] * (16 - min(len(row), 16))
                fixed_data.append(fixed_row)
            
            # シートを完全にクリアしてから再書き込み
            dashboard_sheet.clear()
            
            # 16列だけのデータを書き込み
            dashboard_sheet.update(values=fixed_data, range_name='A1:P' + str(len(fixed_data)))
            
            # 確認
            verified_data = dashboard_sheet.get_all_values()
            print(f"✅ 修正後: {len(verified_data)}行 × {len(verified_data[0])}列")
            
            if len(verified_data[0]) == 16:
                print("🎉 列数の修正が成功しました！")
            else:
                print("❌ 列数の修正に失敗しました")
                
            return len(verified_data[0]) == 16
            
        except Exception as e:
            print(f"❌ 修正エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def add_final_test_data(self):
        """最終テストデータを追加"""
        print("\n🧪 最終テストデータ追加")
        print("-" * 40)
        
        try:
            dashboard_sheet = self.spreadsheet.worksheet('progress_dashboard')
            
            # 現在のデータを確認
            current_data = dashboard_sheet.get_all_values()
            next_row = len(current_data) + 1
            
            print(f"📍 追加行: {next_row}")
            print(f"📏 現在の列数: {len(current_data[0]) if current_data else 0}列")
            
            # 厳密に16列のテストデータ
            test_row = [
                'FINAL-TEST',  # A: goal_id
                '最終テスト - 列修正確認',  # B: goal_name
                '100',         # C: total_tasks
                '88',          # D: completed_tasks
                '88.0',        # E: progress_rate
                '9.0',         # F: avg_quality
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # G: last_updated
                'Active',      # H: status
                '1',           # I: priority
                'Final Tester', # J: assigned_agent
                '2025-10-26',  # K: start_date
                '2025-12-31',  # L: due_date
                '',            # M: actual_completion_date
                '列数テスト',  # N: blockers
                '低',          # O: risk_level
                '最終確認レポート' # P: deliverables
            ]
            
            # 厳密にA-P列のみに追加
            range_str = f'A{next_row}:P{next_row}'
            dashboard_sheet.update(values=[test_row], range_name=range_str)
            
            print("✅ テストデータを追加しました")
            print(f"📋 範囲: {range_str}")
            
            # 最終確認
            final_data = dashboard_sheet.get_all_values()
            last_row = final_data[-1] if final_data else []
            print(f"🎯 最終列数確認: {len(last_row)}列")
            
            if len(last_row) == 16:
                print("🏆 成功！データは16列に正しく収まっています")
                return True
            else:
                print(f"⚠️ 注意: 列数が {len(last_row)} です。16列になるはず")
                return False
                
        except Exception as e:
            print(f"❌ テストデータ追加エラー: {e}")
            return False

def main():
    fixer = FinalColumnFixer()
    
    # 1. 列数を完全に修正
    success = fixer.completely_fix_columns()
    
    if success:
        # 2. テストデータを追加
        test_success = fixer.add_final_test_data()
        
        if test_success:
            print("\n🎉🎉🎉 すべてのテストが成功しました！ 🎉🎉🎉")
            print("✅ 列数は16列に固定されました")
            print("✅ データは正しくA列からP列までに収まっています")
            print("✅ システムは正常に動作しています")
        else:
            print("\n⚠️ テストデータの追加に問題があります")
    else:
        print("\n❌ 列数の修正に失敗しました")

if __name__ == "__main__":
    main()
