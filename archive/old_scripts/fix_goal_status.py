#!/usr/bin/env python3
"""
ゴールステータス修正スクリプト
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configuration.config_loader import ConfigLoader
import gspread
from google.oauth2.service_account import Credentials

def fix_goal_status():
    print("🔧 ゴールステータス修正")
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
        # project_goal シートを取得
        goals_sheet = spreadsheet.worksheet('project_goal')
        goals_data = goals_data = goals_sheet.get_all_values()
        
        print("📋 ゴールデータ分析:")
        print("-" * 30)
        
        if len(goals_data) > 1:
            headers = goals_data[0]
            print(f"ヘッダー: {headers}")
            
            # ステータス列の値を分析
            status_idx = headers.index('status') if 'status' in headers else -1
            goal_id_idx = headers.index('goal_id') if 'goal_id' in headers else -1
            description_idx = headers.index('goal_description') if 'goal_description' in headers else -1
            
            if status_idx != -1:
                status_values = {}
                for row in goals_data[1:]:
                    if len(row) > status_idx:
                        status = row[status_idx].lower()
                        status_values[status] = status_values.get(status, 0) + 1
                
                print(f"ステータス分布: {status_values}")
                
                # アクティブなゴールを特定（様々なステータス値を考慮）
                active_status_keywords = ['active', 'in progress', 'working', 'progress', '実行中', '進行中']
                active_goals = []
                
                for row in goals_data[1:]:
                    if len(row) > status_idx and len(row) > description_idx:
                        status = row[status_idx].lower()
                        description = row[description_idx]
                        
                        # 様々なアクティブ状態を検出
                        is_active = any(keyword in status for keyword in active_status_keywords)
                        
                        # 説明からも判断（長い説明があるものは進行中と判断）
                        if not is_active and len(description) > 100:
                            is_active = True
                        
                        if is_active:
                            goal_id = row[goal_id_idx] if goal_id_idx != -1 and len(row) > goal_id_idx else 'Unknown'
                            active_goals.append({
                                'id': goal_id,
                                'description': description,
                                'status': status
                            })
                
                print(f"🔥 検出されたアクティブゴール: {len(active_goals)}個")
                for i, goal in enumerate(active_goals[:3], 1):
                    short_desc = goal['description'][:80] + "..." if len(goal['description']) > 80 else goal['description']
                    print(f"   {i}. [{goal['id']}] {short_desc}")
                    print(f"      ステータス: {goal['status']}")
            
            print("\n💡 推奨アクション:")
            print("   1. プロジェクトゴールのステータスを明確化")
            print("   2. 'active', 'in progress' など進行中を示すステータスを使用")
            print("   3. 進捗ダッシュボードの goal_name カラムを goal_description にマッピング")
            
        # 進捗ダッシュボードの構造を修正
        print("\n🔧 進捗ダッシュボード修正:")
        print("-" * 30)
        
        dashboard_sheet = spreadsheet.worksheet('progress_dashboard')
        dashboard_data = dashboard_sheet.get_all_values()
        
        if dashboard_data and len(dashboard_data[0]) == 16:
            # 最新のデータ行を確認
            latest_row = dashboard_data[-1] if len(dashboard_data) > 1 else []
            if latest_row:
                print(f"最新の進捗率: {latest_row[4]}")
                print(f"平均品質: {latest_row[5]}")
                print(f"最終更新: {latest_row[6]}")
        
        print("\n✅ 分析完了")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_goal_status()
