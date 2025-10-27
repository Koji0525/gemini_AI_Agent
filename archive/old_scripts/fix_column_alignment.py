#!/usr/bin/env python3
"""
列揃え修正スクリプト - スプレッドシートの列構造を正確に合わせる
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configuration.config_loader import ConfigLoader
import gspread
from google.oauth2.service_account import Credentials

class ColumnAlignmentFixer:
    def __init__(self):
        self.config = ConfigLoader()
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.credentials = Credentials.from_service_account_file(
            self.config.get('service_account_file'), 
            scopes=self.scopes
        )
        self.gc = gspread.authorize(self.credentials)
        self.spreadsheet = self.gc.open_by_key(self.config.get('spreadsheet_id'))
    
    def fix_dashboard_structure(self):
        """ダッシュボードの列構造を修正"""
        print("🔧 ダッシュボード列構造修正")
        print("=" * 50)
        
        try:
            dashboard_sheet = self.spreadsheet.worksheet('progress_dashboard')
            dashboard_data = dashboard_sheet.get_all_values()
            
            print(f"📊 現在のダッシュボード行数: {len(dashboard_data)}")
            
            if dashboard_data:
                print("📋 現在のヘッダー:")
                for i, header in enumerate(dashboard_data[0], 1):
                    print(f"   {i}. '{header}'")
            
            # 正しい列構造を定義
            correct_structure = [
                'goal_id',           # A列
                'goal_name',         # B列  
                'total_tasks',       # C列
                'completed_tasks',   # D列
                'progress_rate',     # E列
                'avg_quality',       # F列
                'last_updated',      # G列
                'status',            # H列
                'priority',          # I列
                'assigned_agent',    # J列
                'start_date',        # K列
                'due_date',          # L列
                'actual_completion_date',  # M列
                'blockers',          # N列
                'risk_level',        # O列
                'deliverables'       # P列
            ]
            
            print(f"\n✅ 正しい列構造 ({len(correct_structure)}列):")
            for i, col in enumerate(correct_structure, 1):
                print(f"   {i}. {col}")
            
            # ヘッダーを修正
            if len(dashboard_data) > 0:
                dashboard_sheet.update('A1:P1', [correct_structure])
                print("✅ ヘッダー行を修正しました")
            
            # データ行の列数を修正
            if len(dashboard_data) > 1:
                print(f"\n🔧 データ行の修正:")
                for i, row in enumerate(dashboard_data[1:], 2):
                    current_cols = len(row)
                    if current_cols != len(correct_structure):
                        # 列数を合わせる
                        if current_cols < len(correct_structure):
                            # 足りない列を追加
                            fixed_row = row + [''] * (len(correct_structure) - current_cols)
                        else:
                            # 余分な列を削除
                            fixed_row = row[:len(correct_structure)]
                        
                        range_str = f'A{i}:P{i}'
                        dashboard_sheet.update(range_str, [fixed_row])
                        print(f"✅ 行 {i}: {current_cols}列 → {len(fixed_row)}列 に修正")
            
            print("\n🎯 修正完了: 列構造を整えました")
            
        except Exception as e:
            print(f"❌ 修正エラー: {e}")
            import traceback
            traceback.print_exc()
    
    def add_properly_aligned_row(self):
        """正しく揃った新しい行を追加"""
        print("\n📝 正しく揃った新しい行を追加")
        print("-" * 40)
        
        try:
            dashboard_sheet = self.spreadsheet.worksheet('progress_dashboard')
            
            # 正確に揃ったデータ行を作成
            new_row = [
                'SYNC-001',  # A: goal_id
                '自動同期 - プロジェクト進捗',  # B: goal_name
                '97',        # C: total_tasks
                '85',        # D: completed_tasks
                '87.6',      # E: progress_rate
                '8.5',       # F: avg_quality
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # G: last_updated
                'Active',    # H: status
                '2',         # I: priority
                'AI System', # J: assigned_agent
                '2025-10-01', # K: start_date
                '2025-12-31', # L: due_date
                '',          # M: actual_completion_date
                'なし',      # N: blockers
                '低',        # O: risk_level
                '進捗レポート' # P: deliverables
            ]
            
            # 行を追加
            dashboard_sheet.append_row(new_row)
            
            print("✅ 正しく揃った行を追加しました")
            print("📋 追加内容:")
            headers = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
            for i, (header, value) in enumerate(zip(headers, new_row)):
                print(f"   {header}列: {value}")
            
        except Exception as e:
            print(f"❌ 行追加エラー: {e}")
    
    def clean_and_rebuild_dashboard(self):
        """ダッシュボードをクリーンアップして再構築"""
        print("\n🧹 ダッシュボードクリーンアップ")
        print("-" * 40)
        
        try:
            dashboard_sheet = self.spreadsheet.worksheet('progress_dashboard')
            
            # 現在のデータを取得（ヘッダーは保持）
            current_data = dashboard_sheet.get_all_values()
            
            if len(current_data) > 10:  # 行数が多い場合のみクリーンアップ
                # ヘッダーを保持してデータ行をクリア
                headers = current_data[0] if current_data else []
                
                # シートをクリア（ヘッダー以外）
                if len(current_data) > 1:
                    dashboard_sheet.batch_clear([f'A2:P{len(current_data)}'])
                    print(f"✅ データ行をクリアしました ({len(current_data)-1}行)")
                
                # 正しい構造のサンプルデータを追加
                sample_rows = [
                    [
                        '1', 'メインプロジェクト - M&Aポータルサイト開発', '97', '85', '87.6', '8.5',
                        '2025-10-26 00:39:16', 'Active', '1', 'Project Manager', 
                        '2025-10-01', '2025-12-31', '', 'なし', '中', 'プロトタイプ'
                    ],
                    [
                        'AUTO-001', '自動同期 - システム管理', '15', '12', '80.0', '9.0',
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Active', '2', 'Auto System',
                        '2025-10-15', '2025-11-30', '', '自動化テスト中', '低', '管理レポート'
                    ]
                ]
                
                for row in sample_rows:
                    dashboard_sheet.append_row(row)
                
                print("✅ サンプルデータを追加しました")
            
        except Exception as e:
            print(f"❌ クリーンアップエラー: {e}")

def main():
    fixer = ColumnAlignmentFixer()
    
    # 1. 列構造を修正
    fixer.fix_dashboard_structure()
    
    # 2. 正しく揃った行を追加
    fixer.add_properly_aligned_row()
    
    # 3. 必要に応じてクリーンアップ（コメントアウト）
    # fixer.clean_and_rebuild_dashboard()
    
    print("\n�� 列揃え修正完了！")

if __name__ == "__main__":
    main()
