#!/usr/bin/env python3
"""
修正版進捗レポート生成 - 日付処理のバグ修正
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from configuration.config_loader import ConfigLoader
import gspread
from google.oauth2.service_account import Credentials

class FixedProgressReporter:
    """修正版進捗レポート生成クラス"""
    
    def __init__(self):
        self.config = ConfigLoader()
    
    def safe_parse_date(self, date_str):
        """安全な日付パース処理"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                print(f"⚠️ 日付パースエラー: '{date_str}'")
                return None
    
    def generate_daily_report(self):
        """日次進捗レポートを生成"""
        print("📋 日次進捗レポート生成")
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
            # 各シートからデータ取得
            goals_sheet = spreadsheet.worksheet('project_goal')
            tasks_sheet = spreadsheet.worksheet('pm_tasks')
            dashboard_sheet = spreadsheet.worksheet('progress_dashboard')
            
            goals_data = goals_sheet.get_all_values()
            tasks_data = tasks_sheet.get_all_values()
            dashboard_data = dashboard_sheet.get_all_values()
            
            print(f"📅 レポート日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            # ゴール状況分析
            total_goals = len(goals_data) - 1 if len(goals_data) > 1 else 0
            active_goals = []
            
            if len(goals_data) > 1:
                headers = goals_data[0]
                status_idx = headers.index('status') if 'status' in headers else -1
                goal_name_idx = headers.index('goal_name') if 'goal_name' in headers else -1
                
                for row in goals_data[1:]:
                    if status_idx != -1 and len(row) > status_idx:
                        if row[status_idx].lower() == 'active':
                            goal_name = row[goal_name_idx] if goal_name_idx != -1 and len(row) > goal_name_idx else 'Unknown'
                            active_goals.append(goal_name)
            
            # タスク状況分析
            total_tasks = len(tasks_data) - 1 if len(tasks_data) > 1 else 0
            completed_tasks = 0
            
            if len(tasks_data) > 1:
                headers = tasks_data[0]
                status_idx = headers.index('status') if 'status' in headers else -1
                
                for row in tasks_data[1:]:
                    if status_idx != -1 and len(row) > status_idx:
                        if row[status_idx].lower() == 'completed':
                            completed_tasks += 1
            
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            print("📊 進捗サマリー")
            print("-" * 30)
            print()
            
            print("🎯 ゴール状況")
            print("-" * 30)
            print(f"   📋 総ゴール数: {total_goals}")
            print(f"   🔥 Activeゴール: {len(active_goals)}")
            if active_goals:
                print("   📝 Activeゴール一覧:")
                for i, goal in enumerate(active_goals[:3], 1):  # 最大3つ表示
                    display_goal = goal[:80] + "..." if len(goal) > 80 else goal
                    print(f"      {i}. {display_goal}")
            print()
            
            print("✅ タスク状況")
            print("-" * 30)
            print(f"   📝 総タスク数: {total_tasks}")
            print(f"   🎉 完了タスク: {completed_tasks}")
            print(f"   📊 完了率: {completion_rate:.1f}%")
            print()
            
            print("🚀 推奨アクション")
            print("-" * 30)
            if completion_rate < 50:
                print("   💡 タスクの実行を加速させましょう")
            elif completion_rate < 80:
                print("   🎯 順調に進んでいます。この調子で続けましょう")
            else:
                print("   🏆 優秀な進捗です！最終調整を進めましょう")
            print()
            
        except Exception as e:
            print(f"❌ レポート生成エラー: {e}")

if __name__ == "__main__":
    reporter = FixedProgressReporter()
    reporter.generate_daily_report()
