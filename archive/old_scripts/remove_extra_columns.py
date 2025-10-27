#!/usr/bin/env python3
"""
余分な列削除スクリプト - Q列以降の不要な列を削除
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configuration.config_loader import ConfigLoader
import gspread
from google.oauth2.service_account import Credentials

class ColumnCleaner:
    def __init__(self):
        self.config = ConfigLoader()
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.credentials = Credentials.from_service_account_file(
            self.config.get('service_account_file'), 
            scopes=self.scopes
        )
        self.gc = gspread.authorize(self.credentials)
        self.spreadsheet = self.gc.open_by_key(self.config.get('spreadsheet_id'))
    
    def analyze_sheet_structure(self):
        """シートの構造を詳細に分析"""
        print("🔍 シート構造詳細分析")
        print("=" * 50)
        
        try:
            dashboard_sheet = self.spreadsheet.worksheet('progress_dashboard')
            
            # より広い範囲でデータを取得
            all_data = dashboard_sheet.get_all_values()
            
            print(f"📊 総行数: {len(all_data)}")
            if all_data:
                print(f"📏 ヘッダーの列数: {len(all_data[0])}")
                print("📋 ヘッダー内容:")
                for i, header in enumerate(all_data[0], 1):
                    col_letter = self.number_to_column_letter(i)
                    print(f"   {col_letter}列 ({i}): '{header}'")
            
            # データ行の列数をチェック
            if len(all_data) > 1:
                print(f"\n📊 データ行の列数:")
                for i, row in enumerate(all_data[1:], 2):
                    print(f"   行 {i}: {len(row)}列")
            
            return all_data
            
        except Exception as e:
            print(f"❌ 分析エラー: {e}")
            return []
    
    def number_to_column_letter(self, n):
        """数値を列文字に変換 (1->A, 2->B, ...)"""
        string = ""
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            string = chr(65 + remainder) + string
        return string
    
    def remove_extra_columns(self):
        """余分な列を削除（Q列以降）"""
        print("\n🗑️ 余分な列の削除")
        print("-" * 40)
        
        try:
            dashboard_sheet = self.spreadsheet.worksheet('progress_dashboard')
            
            # 現在のデータを取得
            all_data = dashboard_sheet.get_all_values()
            
            if not all_data:
                print("❌ データがありません")
                return
            
            # 16列までに制限（A-P列）
            max_columns = 16
            
            if len(all_data[0]) <= max_columns:
                print("✅ 既に列数は適切です")
                return
            
            print(f"🔧 列数を {len(all_data[0])} → {max_columns} に削減")
            
            # データを16列に切り詰める
            truncated_data = []
            for row in all_data:
                truncated_row = row[:max_columns] if len(row) > max_columns else row
                # 16列に満たない場合は空文字で埋める
                while len(truncated_row) < max_columns:
                    truncated_row.append('')
                truncated_data.append(truncated_row)
            
            # シート全体を更新
            dashboard_sheet.update('A1:P' + str(len(truncated_data)), truncated_data)
            
            print("✅ 余分な列を削除しました")
            print(f"📊 更新後のデータ: {len(truncated_data)}行 × {len(truncated_data[0])}列")
            
        except Exception as e:
            print(f"❌ 削除エラー: {e}")
            import traceback
            traceback.print_exc()
    
    def clear_extra_columns_directly(self):
        """直接余分な列をクリア"""
        print("\n🧹 直接クリア方法")
        print("-" * 40)
        
        try:
            dashboard_sheet = self.spreadsheet.worksheet('progress_dashboard')
            
            # Q列以降を直接クリア
            dashboard_sheet.batch_clear(['Q:Z', 'AA:AZ', 'BA:BZ', 'CA:CZ'])
            
            print("✅ Q列以降をクリアしました")
            
        except Exception as e:
            print(f"❌ クリアエラー: {e}")
    
    def create_clean_sheet(self):
        """クリーンなシートを作成（最終手段）"""
        print("\n🆕 クリーンなシートを作成")
        print("-" * 40)
        
        try:
            # 新しいシートを作成
            current_sheets = [sheet.title for sheet in self.spreadsheet.worksheets()]
            new_sheet_name = 'progress_dashboard_clean'
            
            if new_sheet_name in current_sheets:
                # 既存のシートを削除
                sheet_to_delete = self.spreadsheet.worksheet(new_sheet_name)
                self.spreadsheet.del_worksheet(sheet_to_delete)
            
            # 新しいシートを作成
            new_sheet = self.spreadsheet.add_worksheet(title=new_sheet_name, rows=100, cols=16)
            
            # 正しいヘッダーを設定
            correct_headers = [
                'goal_id', 'goal_name', 'total_tasks', 'completed_tasks', 
                'progress_rate', 'avg_quality', 'last_updated', 'status', 
                'priority', 'assigned_agent', 'start_date', 'due_date', 
                'actual_completion_date', 'blockers', 'risk_level', 'deliverables'
            ]
            
            new_sheet.update('A1:P1', [correct_headers])
            
            # サンプルデータを追加
            sample_data = [
                ['CLEAN-001', 'クリーンなダッシュボード', '97', '85', '87.6', '8.5',
                 datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Active', '1', 'System',
                 '2025-10-01', '2025-12-31', '', 'なし', '低', 'テストデータ']
            ]
            
            new_sheet.update('A2:P2', sample_data)
            
            print("✅ クリーンなシートを作成しました")
            print(f"📋 シート名: {new_sheet_name}")
            print("📍 このシートを使用することをお勧めします")
            
        except Exception as e:
            print(f"❌ シート作成エラー: {e}")

def main():
    cleaner = ColumnCleaner()
    
    # 1. 現在の構造を分析
    data = cleaner.analyze_sheet_structure()
    
    # 2. 余分な列を削除
    cleaner.remove_extra_columns()
    
    # 3. 直接クリア（必要に応じて）
    cleaner.clear_extra_columns_directly()
    
    # 4. クリーンなシートを作成（オプション）
    print("\n💡 クリーンなシートを作成しますか？ (y/n)")
    if input().lower() == 'y':
        cleaner.create_clean_sheet()
    
    print("\n🎉 列クリーンアップ完了！")

if __name__ == "__main__":
    main()
