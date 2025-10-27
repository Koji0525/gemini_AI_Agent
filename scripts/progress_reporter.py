#!/usr/bin/env python3
"""
進捗レポート生成 - 詳細な進捗レポートを作成
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from configuration.config_loader import ConfigLoader

class ProgressReporter:
    """進捗レポート生成クラス"""
    
    def __init__(self):
        self.config = ConfigLoader()
    
    def generate_daily_report(self):
        """日次進捗レポートを生成"""
        print("📋 日次進捗レポート生成")
        print("=" * 60)
        
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            
            # Google Sheetsに接続
            scopes = ['https://www.googleapis.com/auth/spreadsheets']
            credentials = Credentials.from_service_account_file(
                self.config.get('service_account_file'), 
                scopes=scopes
            )
            gc = gspread.authorize(credentials)
            spreadsheet = gc.open_by_key(self.config.get('spreadsheet_id'))
            
            # 各シートからデータ取得
            progress_data = self.get_progress_data(spreadsheet)
            goals_data = self.get_goals_data(spreadsheet)
            tasks_data = self.get_tasks_data(spreadsheet)
            
            # レポート生成
            self.print_report(progress_data, goals_data, tasks_data)
            
        except Exception as e:
            print(f"❌ レポート生成エラー: {e}")
    
    def get_progress_data(self, spreadsheet):
        """進捗データを取得"""
        try:
            worksheet = spreadsheet.worksheet('progress_dashboard')
            data = worksheet.get_all_values()
            
            if len(data) > 1:
                # 今日と昨日のデータを取得
                today = datetime.now().date()
                yesterday = today - timedelta(days=1)
                
                today_data = []
                yesterday_data = []
                
                for row in data[1:]:  # ヘッダーをスキップ
                    if len(row) > 0:
                        row_date = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').date()
                        if row_date == today:
                            today_data.append(row)
                        elif row_date == yesterday:
                            yesterday_data.append(row)
                
                return {
                    'today': today_data[0] if today_data else None,
                    'yesterday': yesterday_data[0] if yesterday_data else None,
                    'all_data': data
                }
            return {}
            
        except Exception as e:
            print(f"❌ 進捗データ取得エラー: {e}")
            return {}
    
    def get_goals_data(self, spreadsheet):
        """ゴールデータを取得"""
        try:
            worksheet = spreadsheet.worksheet('project_goal')
            data = worksheet.get_all_values()
            
            active_goals = []
            for row in data[1:]:
                if len(row) > 2 and row[2].lower() == 'active':
                    active_goals.append(row)
            
            return {
                'total': len(data) - 1,
                'active': len(active_goals),
                'active_goals': active_goals
            }
            
        except Exception as e:
            print(f"❌ ゴールデータ取得エラー: {e}")
            return {}
    
    def get_tasks_data(self, spreadsheet):
        """タスクデータを取得"""
        try:
            worksheet = spreadsheet.worksheet('pm_tasks')
            data = worksheet.get_all_values()
            
            completed = 0
            total = len(data) - 1
            
            for row in data[1:]:
                if len(row) > 2 and row[2].lower() in ['completed', '完了', 'done']:
                    completed += 1
            
            return {
                'total': total,
                'completed': completed,
                'completion_rate': round((completed / total * 100), 2) if total > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ タスクデータ取得エラー: {e}")
            return {}
    
    def print_report(self, progress, goals, tasks):
        """レポートを表示"""
        print(f"📅 レポート日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 進捗サマリー
        print("📊 進捗サマリー")
        print("-" * 30)
        if progress.get('today'):
            today = progress['today']
            print(f"   🎯 総合進捗: {today[1]}%")
            print(f"   ✅ Activeゴール: {today[2]}個")
            print(f"   📝 完了タスク: {today[3]}/{today[4]} ({today[5]}%)")
            
            # 前日比
            if progress.get('yesterday'):
                yesterday_progress = float(progress['yesterday'][1])
                today_progress = float(today[1])
                change = today_progress - yesterday_progress
                trend = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                print(f"   {trend} 前日比: {change:+.2f}%")
        print()
        
        # ゴール状況
        print("🎯 ゴール状況")
        print("-" * 30)
        print(f"   📋 総ゴール数: {goals.get('total', 0)}")
        print(f"   🔥 Activeゴール: {goals.get('active', 0)}")
        
        if goals.get('active_goals'):
            print("   📝 Activeゴール一覧:")
            for i, goal in enumerate(goals['active_goals'][:3], 1):  # 最大3つ表示
                title = goal[1][:50] + "..." if len(goal[1]) > 50 else goal[1]
                print(f"      {i}. {title}")
        print()
        
        # タスク状況
        print("✅ タスク状況")
        print("-" * 30)
        print(f"   📝 総タスク数: {tasks.get('total', 0)}")
        print(f"   🎉 完了タスク: {tasks.get('completed', 0)}")
        print(f"   📊 完了率: {tasks.get('completion_rate', 0)}%")
        print()
        
        # 次のステップ
        print("🚀 推奨アクション")
        print("-" * 30)
        if goals.get('active', 0) == 0:
            print("   💡 新しいゴールを設定しましょう")
        elif tasks.get('completion_rate', 0) < 50:
            print("   💡 タスクの実行を加速させましょう")
        else:
            print("   💡 現在のペースを維持しましょう")
        print()

def main():
    """メイン実行"""
    try:
        ConfigLoader.validate_config()
        reporter = ProgressReporter()
        reporter.generate_daily_report()
        
    except Exception as e:
        print(f"❌ レポート生成エラー: {e}")

if __name__ == "__main__":
    main()
