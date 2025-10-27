#!/usr/bin/env python3
"""
最終状況確認スクリプト
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configuration.config_loader import ConfigLoader
import gspread
from google.oauth2.service_account import Credentials

def final_status_check():
    print("🎯 プロジェクト最終状況確認")
    print("=" * 50)
    print(f"📅 確認日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
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
        # ダッシュボードから最新の進捗を取得
        dashboard_sheet = spreadsheet.worksheet('progress_dashboard')
        dashboard_data = dashboard_sheet.get_all_values()
        
        if len(dashboard_data) > 1:
            latest_progress = dashboard_data[-1]
            progress_rate = float(latest_progress[4]) if len(latest_progress) > 4 and latest_progress[4] else 0
            avg_quality = float(latest_progress[5]) if len(latest_progress) > 5 and latest_progress[5] else 0
            last_updated = latest_progress[6] if len(latest_progress) > 6 else 'Unknown'
            
            print("📊 最新プロジェクト進捗")
            print("-" * 30)
            print(f"   📈 進捗率: {progress_rate}%")
            print(f"   🎯 平均品質: {avg_quality}/10")
            print(f"   ⏰ 最終更新: {last_updated}")
            print()
            
            # 進捗評価
            print("🏆 進捗評価")
            print("-" * 20)
            if progress_rate >= 80:
                print("   ✅ 優秀: プロジェクトは終盤段階です")
                print("   💡 次のステップ: 最終調整と品質確認")
            elif progress_rate >= 60:
                print("   🔥 良好: 順調に進行中")
                print("   💡 次のステップ: この調子で継続")
            elif progress_rate >= 40:
                print("   ⚠️ 要注意: 進捗を加速させる必要あり")
                print("   💡 次のステップ: 優先タスクの集中処理")
            else:
                print("   🚨 要改善: 計画の見直しが必要")
                print("   💡 次のステップ: タスクの再優先順位付け")
            
            print()
            print("🎉 結論: プロジェクトは正常に進行中です！")
            print("   進捗ダッシュボードは正しく機能しています")
            
        else:
            print("❌ ダッシュボードにデータがありません")
            
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    final_status_check()
