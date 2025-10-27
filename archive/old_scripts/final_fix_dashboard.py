#!/usr/bin/env python3
"""
最終修正スクリプト - モジュールパスとデータ取得の問題を解決
"""

import os
import sys
import gspread
from google.oauth2.service_account import Credentials

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configuration.config_loader import ConfigLoader

def final_fix_dashboard():
    print("🔧 最終修正: ダッシュボード構造とデータ取得")
    print("=" * 60)
    
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
        # 各シートのデータ構造を確認
        print("📊 シート構造確認:")
        print("-" * 30)
        
        # project_goal シートの確認
        goals_sheet = spreadsheet.worksheet('project_goal')
        goals_data = goals_sheet.get_all_values()
        print(f"✅ project_goal: {len(goals_data)}行")
        if goals_data:
            print(f"   ヘッダー: {goals_data[0]}")
            if len(goals_data) > 1:
                print(f"   最初のデータ行: {goals_data[1][:3]}...")  # 最初の3列のみ表示
        
        # pm_tasks シートの確認
        tasks_sheet = spreadsheet.worksheet('pm_tasks')
        tasks_data = tasks_sheet.get_all_values()
        print(f"✅ pm_tasks: {len(tasks_data)}行")
        if tasks_data:
            print(f"   ヘッダー: {tasks_data[0]}")
        
        # progress_dashboard シートの確認と修正
        dashboard_sheet = spreadsheet.worksheet('progress_dashboard')
        dashboard_data = dashboard_sheet.get_all_values()
        print(f"✅ progress_dashboard: {len(dashboard_data)}行")
        
        if dashboard_data:
            print(f"   現在のヘッダー: {dashboard_data[0]}")
            
            # 正しいヘッダー構造
            correct_headers = [
                'goal_id', 'goal_name', 'total_tasks', 'completed_tasks', 
                'progress_rate', 'avg_quality', 'last_updated', 'status', 
                'priority', 'assigned_agent', 'start_date', 'due_date', 
                'actual_completion_date', 'blockers', 'risk_level', 'deliverables'
            ]
            
            # ヘッダーを修正
            if len(dashboard_data[0]) != len(correct_headers):
                dashboard_sheet.update('A1:P1', [correct_headers])
                print("✅ ヘッダーを修正しました")
            
            # データ行の構造を修正
            if len(dashboard_data) > 1:
                for i, row in enumerate(dashboard_data[1:], 2):
                    if len(row) < len(correct_headers):
                        padded_row = row + [''] * (len(correct_headers) - len(row))
                        range_str = f'A{i}:P{i}'
                        dashboard_sheet.update(range_str, [padded_row])
                        print(f"✅ 行 {i} を修正しました")
        
        print("\n🎯 Activeゴール詳細分析:")
        print("-" * 30)
        
        # 正確なゴール名取得のテスト
        if len(goals_data) > 1:
            headers = goals_data[0]
            print(f"利用可能なヘッダー: {headers}")
            
            # ヘッダーのインデックスを探す
            status_idx = -1
            goal_name_idx = -1
            goal_id_idx = -1
            
            for idx, header in enumerate(headers):
                if 'status' in header.lower():
                    status_idx = idx
                elif 'name' in header.lower():
                    goal_name_idx = idx
                elif 'id' in header.lower():
                    goal_id_idx = idx
            
            print(f"ステータス列インデックス: {status_idx}")
            print(f"ゴール名列インデックス: {goal_name_idx}")
            print(f"ゴールID列インデックス: {goal_id_idx}")
            
            active_goals = []
            for row in goals_data[1:]:
                if (status_idx != -1 and len(row) > status_idx and 
                    row[status_idx].lower() == 'active'):
                    
                    goal_name = row[goal_name_idx] if goal_name_idx != -1 and len(row) > goal_name_idx else '名前不明'
                    goal_id = row[goal_id_idx] if goal_id_idx != -1 and len(row) > goal_id_idx else 'ID不明'
                    
                    active_goals.append({
                        'id': goal_id,
                        'name': goal_name
                    })
            
            print(f"🔥 検出されたActiveゴール: {len(active_goals)}個")
            for i, goal in enumerate(active_goals[:5], 1):  # 最大5つ表示
                display_name = goal['name'][:60] + "..." if len(goal['name']) > 60 else goal['name']
                print(f"   {i}. [{goal['id']}] {display_name}")
        
        print("\n✅ 最終修正完了")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    final_fix_dashboard()
