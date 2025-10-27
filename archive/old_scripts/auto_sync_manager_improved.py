#!/usr/bin/env python3
"""
改良版自動同期マネージャー - 定期的に実際のデータを同期
"""

import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configuration.config_loader import ConfigLoader
import gspread
from google.oauth2.service_account import Credentials

class AutoSyncManagerImproved:
    def __init__(self):
        self.config = ConfigLoader()
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.credentials = Credentials.from_service_account_file(
            self.config.get('service_account_file'), 
            scopes=self.scopes
        )
        self.gc = gspread.authorize(self.credentials)
        self.spreadsheet = self.gc.open_by_key(self.config.get('spreadsheet_id'))
    
    def ensure_headers(self):
        """ヘッダーの存在を保証"""
        try:
            dashboard_sheet = self.spreadsheet.worksheet('progress_dashboard')
            data = dashboard_sheet.get_all_values()
            
            if not data or data[0][0] != 'goal_id':
                correct_headers = [
                    'goal_id', 'goal_name', 'total_tasks', 'completed_tasks',
                    'progress_rate', 'avg_quality', 'last_updated', 'status',
                    'priority', 'assigned_agent', 'start_date', 'due_date',
                    'actual_completion_date', 'blockers', 'risk_level', 'deliverables'
                ]
                dashboard_sheet.update(values=[correct_headers], range_name='A1:P1')
                print("✅ ヘッダーを設定しました")
            
        except Exception as e:
            print(f"❌ ヘッダー確認失敗: {e}")
    
    def sync_latest_progress(self):
        """最新の進捗を同期"""
        print(f"\n🔄 自動同期実行: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            self.ensure_headers()
            
            # 実際のデータを取得して同期（簡易版）
            dashboard_sheet = self.spreadsheet.worksheet('progress_dashboard')
            goals_sheet = self.spreadsheet.worksheet('project_goal')
            tasks_sheet = self.spreadsheet.worksheet('pm_tasks')
            
            # 簡単な進捗計算
            goals_data = goals_sheet.get_all_values()
            tasks_data = tasks_sheet.get_all_values()
            
            active_goals_count = sum(1 for row in goals_data[1:] if len(row) > 2 and row[2].lower() in ['active', '実行中'])
            total_tasks = len(tasks_data) - 1 if len(tasks_data) > 1 else 0
            completed_tasks = sum(1 for row in tasks_data[1:] if len(row) > 4 and row[4].lower() == 'completed')
            progress_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # 新しい進捗行を作成
            new_row = [
                'AUTO-SYNC',
                f'自動同期 - {active_goals_count}個のアクティブゴール',
                str(total_tasks),
                str(completed_tasks),
                f'{progress_rate:.1f}',
                '8.5',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Active',
                '2',
                'Auto Sync System',
                datetime.now().strftime('%Y-%m-%d'),
                (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                '',
                '自動同期中',
                '低',
                '自動進捗レポート'
            ]
            
            # データを追加（ヘッダーは保持）
            dashboard_sheet.append_row(new_row)
            
            print(f"✅ 進捗を同期: {progress_rate:.1f}% ({completed_tasks}/{total_tasks} タスク)")
            return True
            
        except Exception as e:
            print(f"❌ 自動同期失敗: {e}")
            return False
    
    def start_auto_sync(self, interval_minutes=60):
        """自動同期を開始"""
        print("🚀 自動同期マネージャー起動")
        print(f"⏰ 同期間隔: {interval_minutes}分")
        print("🛑 Ctrl+Cで停止")
        print("=" * 50)
        
        sync_count = 0
        try:
            while True:
                success = self.sync_latest_progress()
                if success:
                    sync_count += 1
                
                print(f"⏰ 次の同期まで{interval_minutes}分待機...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print(f"\n✅ 自動同期を停止しました (総同期回数: {sync_count}回)")

from datetime import timedelta

def main():
    manager = AutoSyncManagerImproved()
    
    # 単回テスト実行
    print("🧪 自動同期テスト実行")
    manager.sync_latest_progress()
    
    # 自動同期はコメントアウト（必要に応じて有効化）
    # print("\n🔧 自動同期を開始しますか？ (y/n)")
    # if input().lower() == 'y':
    #     manager.start_auto_sync(interval_minutes=60)

if __name__ == "__main__":
    main()
