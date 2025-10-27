#!/usr/bin/env python3
"""
進捗ダッシュボード構造修正スクリプト
ヘッダーとデータの整合性を修正
"""

import gspread
from google.oauth2.service_account import Credentials
from configuration.config_loader import ConfigLoader

def fix_dashboard_structure():
    print("🔧 進捗ダッシュボード構造修正開始")
    print("=" * 50)
    
    config = ConfigLoader()
    
    # Google Sheetsに接続
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = Credentials.from_service_account_file(
        config.get('service_account_file'), 
        scopes=scopes
    )
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(config.get('spreadsheet_id'))
    
    try:
        # Progress Dashboardシートを取得
        dashboard_sheet = spreadsheet.worksheet('progress_dashboard')
        
        # 現在のデータを取得
        all_data = dashboard_sheet.get_all_values()
        
        print(f"📊 現在のダッシュボード行数: {len(all_data)}")
        
        if len(all_data) > 0:
            print("📋 現在のヘッダー:")
            print(f"   {all_data[0]}")
            
        if len(all_data) > 1:
            print("📊 現在のデータ行:")
            for i, row in enumerate(all_data[1:4], 1):  # 最初の3データ行を表示
                print(f"   {i}. {row}")
        
        # 正しいヘッダー構造を定義
        correct_headers = [
            'goal_id', 'goal_name', 'total_tasks', 'completed_tasks', 
            'progress_rate', 'avg_quality', 'last_updated', 'status', 
            'priority', 'assigned_agent', 'start_date', 'due_date', 
            'actual_completion_date', 'blockers', 'risk_level', 'deliverables'
        ]
        
        print(f"✅ 正しいヘッダー構造: {correct_headers}")
        
        # ヘッダーを修正
        if len(all_data) > 0:
            dashboard_sheet.update('A1:P1', [correct_headers])
            print("✅ ヘッダー行を修正しました")
        
        # データ行の構造を確認して修正
        if len(all_data) > 1:
            print("🔍 データ行の構造を検証中...")
            for i, row in enumerate(all_data[1:], 2):  # 行番号は2から開始
                if len(row) < len(correct_headers):
                    # 不足している列を空文字で埋める
                    padded_row = row + [''] * (len(correct_headers) - len(row))
                    range_str = f'A{i}:P{i}'
                    dashboard_sheet.update(range_str, [padded_row])
                    print(f"✅ 行 {i} の構造を修正しました")
        
        print("🎉 進捗ダッシュボード構造修正完了")
        
    except Exception as e:
        print(f"❌ 修正エラー: {e}")

if __name__ == "__main__":
    fix_dashboard_structure()
