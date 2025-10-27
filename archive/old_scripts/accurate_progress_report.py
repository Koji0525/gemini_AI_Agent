#!/usr/bin/env python3
"""
正確な進捗レポート - データ構造を正確に解析
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configuration.config_loader import ConfigLoader
import gspread
from google.oauth2.service_account import Credentials

class AccurateProgressReporter:
    def __init__(self):
        self.config = ConfigLoader()
    
    def generate_report(self):
        print("📈 正確な進捗レポート")
        print("=" * 60)
        
        # Google Sheetsに接続
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = Credentials.from_service_account_file(
            self.config.get('service_account_file'), 
            scopes=scopes
        )
        gc = gspread.authorize(credentials)
        spreadsheet = gc.open_by_key(self.config.get('spreadsheet_id'))
        
        try:
            # シートデータ取得
            goals_sheet = spreadsheet.worksheet('project_goal')
            tasks_sheet = spreadsheet.worksheet('pm_tasks')
            dashboard_sheet = spreadsheet.worksheet('progress_dashboard')
            
            goals_data = goals_sheet.get_all_values()
            tasks_data = tasks_sheet.get_all_values()
            dashboard_data = dashboard_sheet.get_all_values()
            
            print(f"📅 レポート日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            # 詳細なゴール分析
            print("🎯 詳細ゴール分析")
            print("-" * 30)
            
            if len(goals_data) > 1:
                headers = goals_data[0]
                
                # ヘッダーマッピングを作成
                header_map = {}
                for idx, header in enumerate(headers):
                    header_map[header.lower()] = idx
                
                total_goals = len(goals_data) - 1
                active_goals = []
                completed_goals = 0
                
                for row in goals_data[1:]:
                    if 'status' in header_map and len(row) > header_map['status']:
                        status = row[header_map['status']].lower()
                        
                        if status == 'active':
                            goal_name = ''
                            if 'goal_name' in header_map and len(row) > header_map['goal_name']:
                                goal_name = row[header_map['goal_name']]
                            elif 'name' in header_map and len(row) > header_map['name']:
                                goal_name = row[header_map['name']]
                            
                            goal_id = ''
                            if 'goal_id' in header_map and len(row) > header_map['goal_id']:
                                goal_id = row[header_map['goal_id']]
                            elif 'id' in header_map and len(row) > header_map['id']:
                                goal_id = row[header_map['id']]
                            
                            if goal_name:
                                active_goals.append({'id': goal_id, 'name': goal_name})
                        
                        elif status == 'completed':
                            completed_goals += 1
                
                print(f"   📋 総ゴール数: {total_goals}")
                print(f"   🔥 Activeゴール: {len(active_goals)}")
                print(f"   ✅ 完了ゴール: {completed_goals}")
                print(f"   ⏳ その他: {total_goals - len(active_goals) - completed_goals}")
                
                if active_goals:
                    print("\n   📝 Activeゴール詳細:")
                    for i, goal in enumerate(active_goals, 1):
                        display_name = goal['name'][:50] + "..." if len(goal['name']) > 50 else goal['name']
                        goal_id_display = f"[{goal['id']}]" if goal['id'] else ""
                        print(f"      {i}. {goal_id_display} {display_name}")
            
            print()
            
            # 詳細なタスク分析
            print("✅ 詳細タスク分析")
            print("-" * 30)
            
            if len(tasks_data) > 1:
                headers = tasks_data[0]
                
                # ヘッダーマッピングを作成
                header_map = {}
                for idx, header in enumerate(headers):
                    header_map[header.lower()] = idx
                
                total_tasks = len(tasks_data) - 1
                completed_tasks = 0
                in_progress_tasks = 0
                
                for row in tasks_data[1:]:
                    if 'status' in header_map and len(row) > header_map['status']:
                        status = row[header_map['status']].lower()
                        if status == 'completed':
                            completed_tasks += 1
                        elif status in ['in progress', 'active', 'working']:
                            in_progress_tasks += 1
                
                completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                
                print(f"   📝 総タスク数: {total_tasks}")
                print(f"   🎉 完了タスク: {completed_tasks}")
                print(f"   🔄 進行中タスク: {in_progress_tasks}")
                print(f"   ⏳ 未着手タスク: {total_tasks - completed_tasks - in_progress_tasks}")
                print(f"   📊 完了率: {completion_rate:.1f}%")
            
            print()
            
            # ダッシュボードの最新状況
            print("📊 ダッシュボード最新状況")
            print("-" * 30)
            
            if len(dashboard_data) > 1:
                latest_row = dashboard_data[-1]  # 最新の行
                if len(latest_row) >= 7:  # 進捗率まで含むか確認
                    print(f"   📈 最新進捗率: {latest_row[4] if len(latest_row) > 4 else 'N/A'}")
                    print(f"   🎯 平均品質: {latest_row[5] if len(latest_row) > 5 else 'N/A'}")
                    print(f"   ⏰ 最終更新: {latest_row[6] if len(latest_row) > 6 else 'N/A'}")
            
            print("\n🚀 総合評価と推奨アクション")
            print("-" * 35)
            
            if completed_tasks / total_tasks >= 0.85:
                print("   🏆 優秀: プロジェクトは順調に進行中です！")
                print("   💡 推奨: 最終調整と品質確認を実施")
            elif completed_tasks / total_tasks >= 0.5:
                print("   ✅ 良好: 良いペースで進行中です")
                print("   💡 推奨: この調子で継続")
            else:
                print("   ⚠️ 要改善: 進捗を加速させる必要があります")
                print("   💡 推奨: 優先タスクの集中処理")
            
        except Exception as e:
            print(f"❌ レポート生成エラー: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    reporter = AccurateProgressReporter()
    reporter.generate_report()
