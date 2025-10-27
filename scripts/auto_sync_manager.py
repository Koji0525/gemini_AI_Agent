#!/usr/bin/env python3
"""
自動同期マネージャー - 定期的なデータ同期
"""

import os
import sys
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configuration.config_loader import ConfigLoader
import gspread
from google.oauth2.service_account import Credentials

class AutoSyncManager:
    def __init__(self):
        self.config = ConfigLoader()
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.credentials = Credentials.from_service_account_file(
            self.config.get('service_account_file'), 
            scopes=self.scopes
        )
        self.gc = gspread.authorize(self.credentials)
        self.spreadsheet = self.gc.open_by_key(self.config.get('spreadsheet_id'))
    
    def get_task_stats(self):
        """タスク統計を取得"""
        try:
            tasks_sheet = self.spreadsheet.worksheet('pm_tasks')
            tasks_data = tasks_sheet.get_all_values()
            
            if len(tasks_data) <= 1:
                return 0, 0, 0
            
            headers = tasks_data[0]
            status_idx = headers.index('status') if 'status' in headers else -1
            
            total_tasks = len(tasks_data) - 1
            completed_tasks = 0
            in_progress_tasks = 0
            
            for row in tasks_data[1:]:
                if len(row) > status_idx:
                    status = row[status_idx].lower()
                    if status == 'completed':
                        completed_tasks += 1
                    elif status in ['in progress', 'active', 'working']:
                        in_progress_tasks += 1
            
            return total_tasks, completed_tasks, in_progress_tasks
            
        except Exception as e:
            print(f"❌ タスク統計取得エラー: {e}")
            return 0, 0, 0
    
    def get_goal_stats(self):
        """ゴール統計を取得"""
        try:
            goals_sheet = self.spreadsheet.worksheet('project_goal')
            goals_data = goals_sheet.get_all_values()
            
            if len(goals_data) <= 1:
                return 0, 0, 0
            
            headers = goals_data[0]
            status_idx = headers.index('status') if 'status' in headers else -1
            
            total_goals = len(goals_data) - 1
            active_goals = 0
            completed_goals = 0
            
            for row in goals_data[1:]:
                if len(row) > status_idx:
                    status = row[status_idx].lower()
                    if status in ['active', 'in progress']:
                        active_goals += 1
                    elif status == 'completed':
                        completed_goals += 1
            
            return total_goals, active_goals, completed_goals
            
        except Exception as e:
            print(f"❌ ゴール統計取得エラー: {e}")
            return 0, 0, 0
    
    def sync_progress_to_dashboard(self):
        """進捗をダッシュボードに同期"""
        print(f"\n🔄 進捗同期実行: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        try:
            # 統計データ取得
            total_tasks, completed_tasks, in_progress_tasks = self.get_task_stats()
            total_goals, active_goals, completed_goals = self.get_goal_stats()
            
            # 進捗率計算
            progress_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            quality_score = 8.5  # 固定値（実際はタスク品質から計算）
            
            print(f"📊 取得統計:")
            print(f"   • ゴール: {active_goals}/{total_goals} アクティブ")
            print(f"   • タスク: {completed_tasks}/{total_tasks} 完了 ({progress_rate:.1f}%)")
            print(f"   • 品質: {quality_score}/10")
            
            # ダッシュボードシート取得
            dashboard_sheet = self.spreadsheet.worksheet('progress_dashboard')
            
            # 新しい行を作成
            new_row = [
                'AUTO',  # goal_id
                f'自動同期 - {active_goals}個のアクティブゴール',  # goal_name
                str(total_tasks),  # total_tasks
                str(completed_tasks),  # completed_tasks
                f'{progress_rate:.1f}',  # progress_rate
                f'{quality_score}',  # avg_quality
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # last_updated
                'Active',  # status
                '2',  # priority
                'Auto-Sync System',  # assigned_agent
                datetime.now().strftime('%Y-%m-%d'),  # start_date
                (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),  # due_date
                '',  # actual_completion_date
                '自動同期中',  # blockers
                '低',  # risk_level
                '自動進捗レポート'  # deliverables
            ]
            
            # ダッシュボードに追加
            dashboard_sheet.append_row(new_row)
            print("✅ 進捗データをダッシュボードに同期しました")
            
            return True
            
        except Exception as e:
            print(f"❌ 同期エラー: {e}")
            return False
    
    def start_auto_sync(self, interval_minutes=60):
        """自動同期を開始"""
        print("🚀 自動同期マネージャー起動")
        print(f"⏰ 同期間隔: {interval_minutes}分")
        print("🛑 Ctrl+Cで停止")
        print("=" * 50)
        
        try:
            sync_count = 0
            while True:
                success = self.sync_progress_to_dashboard()
                if success:
                    sync_count += 1
                
                print(f"⏰ 次の同期まで{interval_minutes}分待機...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print(f"\n✅ 自動同期を停止しました (総同期回数: {sync_count}回)")

def main():
    manager = AutoSyncManager()
    
    # 単回同期のテスト
    print("🧪 単回同期テスト実行")
    manager.sync_progress_to_dashboard()
    
    # 自動同期開始（コメントアウト）
    # print("\n🔧 自動同期を開始しますか？ (y/n)")
    # if input().lower() == 'y':
    #     manager.start_auto_sync(interval_minutes=60)  # 1時間間隔

if __name__ == "__main__":
    main()
