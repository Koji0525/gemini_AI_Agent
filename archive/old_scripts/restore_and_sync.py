#!/usr/bin/env python3
"""
復元と同期スクリプト - ヘッダーを復元し実際のデータを同期
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configuration.config_loader import ConfigLoader
import gspread
from google.oauth2.service_account import Credentials

class RestoreAndSync:
    def __init__(self):
        self.config = ConfigLoader()
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.credentials = Credentials.from_service_account_file(
            self.config.get('service_account_file'), 
            scopes=self.scopes
        )
        self.gc = gspread.authorize(self.credentials)
        self.spreadsheet = self.gc.open_by_key(self.config.get('spreadsheet_id'))
    
    def restore_headers(self):
        """ヘッダーを復元"""
        print("🔧 ヘッダー復元")
        print("=" * 50)
        
        try:
            dashboard_sheet = self.spreadsheet.worksheet('progress_dashboard')
            
            # 正しいヘッダーを定義
            correct_headers = [
                'goal_id', 'goal_name', 'total_tasks', 'completed_tasks',
                'progress_rate', 'avg_quality', 'last_updated', 'status',
                'priority', 'assigned_agent', 'start_date', 'due_date',
                'actual_completion_date', 'blockers', 'risk_level', 'deliverables'
            ]
            
            # 現在のデータを取得
            current_data = dashboard_sheet.get_all_values()
            
            if current_data and current_data[0] != correct_headers:
                print("⚠️ ヘッダーが不正です。修正します...")
                
                # データがある場合は2行目以降を保持
                if len(current_data) > 1:
                    data_rows = current_data[1:]
                    # ヘッダーとデータを結合して更新
                    new_data = [correct_headers] + data_rows
                    dashboard_sheet.update(values=new_data, range_name='A1:P' + str(len(new_data)))
                    print(f"✅ ヘッダーを修正し、{len(data_rows)}行のデータを保持しました")
                else:
                    # データがない場合はヘッダーのみ設定
                    dashboard_sheet.update(values=[correct_headers], range_name='A1:P1')
                    print("✅ ヘッダーのみ設定しました")
            else:
                print("✅ ヘッダーは正常です")
            
            return True
            
        except Exception as e:
            print(f"❌ ヘッダー復元失敗: {e}")
            return False
    
    def get_actual_goals_data(self):
        """実際のプロジェクトゴールからデータを取得"""
        print("\n📊 実際のゴールデータ取得")
        print("-" * 40)
        
        try:
            goals_sheet = self.spreadsheet.worksheet('project_goal')
            tasks_sheet = self.spreadsheet.worksheet('pm_tasks')
            
            # ゴールデータを取得
            goals_data = goals_sheet.get_all_values()
            if len(goals_data) <= 1:
                print("❌ ゴールデータがありません")
                return []
            
            goals_headers = goals_data[0]
            print(f"📋 ゴールシートヘッダー: {goals_headers}")
            
            # タスクデータを取得して統計を計算
            tasks_data = tasks_sheet.get_all_values()
            tasks_headers = tasks_data[0] if tasks_data else []
            
            # アクティブなゴールを抽出
            active_goals = []
            for i, row in enumerate(goals_data[1:], start=2):
                if len(row) > 2:  # status列があるか確認
                    status = row[2].lower() if row[2] else ''
                    
                    # アクティブなゴールを検出（様々な状態を考慮）
                    if status in ['active', '実行中', 'in progress', 'working'] or (not status and len(row[1]) > 50):
                        goal_id = row[0] if len(row) > 0 else f"ROW_{i}"
                        goal_description = row[1] if len(row) > 1 else "説明なし"
                        
                        # タスク統計を計算
                        total_tasks, completed_tasks = self.calculate_task_stats(tasks_data, goal_id)
                        progress_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                        
                        active_goals.append({
                            'goal_id': goal_id,
                            'goal_name': goal_description[:80] + "..." if len(goal_description) > 80 else goal_description,
                            'total_tasks': total_tasks,
                            'completed_tasks': completed_tasks,
                            'progress_rate': round(progress_rate, 1),
                            'avg_quality': 8.5,  # デフォルト値
                            'status': 'Active',
                            'priority': '1',
                            'assigned_agent': 'AI System'
                        })
            
            print(f"✅ 検出されたアクティブゴール: {len(active_goals)}件")
            for goal in active_goals:
                print(f"   • {goal['goal_id']}: {goal['goal_name']} ({goal['progress_rate']}%)")
            
            return active_goals
            
        except Exception as e:
            print(f"❌ ゴールデータ取得失敗: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def calculate_task_stats(self, tasks_data, goal_id):
        """タスク統計を計算"""
        if len(tasks_data) <= 1:
            return 0, 0
        
        total_tasks = 0
        completed_tasks = 0
        
        for task_row in tasks_data[1:]:
            if len(task_row) > 1 and task_row[1] == goal_id:  # parent_goal_idが一致
                total_tasks += 1
                if len(task_row) > 4 and task_row[4].lower() == 'completed':  # statusがcompleted
                    completed_tasks += 1
        
        return total_tasks, completed_tasks
    
    def sync_actual_data_to_dashboard(self):
        """実際のデータをダッシュボードに同期"""
        print("\n🔄 実際のデータをダッシュボードに同期")
        print("-" * 50)
        
        try:
            # ヘッダーを復元
            if not self.restore_headers():
                return False
            
            # 実際のゴールデータを取得
            active_goals = self.get_actual_goals_data()
            
            if not active_goals:
                print("⚠️ 同期するアクティブゴールがありません")
                return True
            
            dashboard_sheet = self.spreadsheet.worksheet('progress_dashboard')
            
            # 現在のダッシュボードデータを取得（ヘッダーを除く）
            current_data = dashboard_sheet.get_all_values()
            data_start_row = 2 if current_data and len(current_data) > 1 else 1
            
            # 新しいデータ行を作成
            new_rows = []
            for goal in active_goals:
                new_row = [
                    goal['goal_id'],
                    goal['goal_name'],
                    str(goal['total_tasks']),
                    str(goal['completed_tasks']),
                    str(goal['progress_rate']),
                    str(goal['avg_quality']),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    goal['status'],
                    goal['priority'],
                    goal['assigned_agent'],
                    '2025-10-01',  # デフォルト開始日
                    '2025-12-31',  # デフォルト期限
                    '',  # 実際の完了日
                    '自動同期',  # ブロッカー
                    '中',  # リスクレベル
                    '進捗レポート'  # 成果物
                ]
                new_rows.append(new_row)
            
            # データを追加
            if data_start_row == 1:
                # データがない場合はヘッダーの後に追加
                dashboard_sheet.update(values=new_rows, range_name=f'A2:P{1 + len(new_rows)}')
            else:
                # 既存データがある場合は末尾に追加
                start_row = len(current_data) + 1
                dashboard_sheet.update(values=new_rows, range_name=f'A{start_row}:P{start_row + len(new_rows) - 1}')
            
            print(f"✅ {len(new_rows)}件のゴールデータを同期しました")
            
            # 最終確認
            final_data = dashboard_sheet.get_all_values()
            print(f"📊 同期後: {len(final_data)}行（ヘッダー1行 + データ{len(final_data)-1}行）")
            
            return True
            
        except Exception as e:
            print(f"❌ データ同期失敗: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_final_state(self):
        """最終状態を確認"""
        print("\n🔍 最終状態確認")
        print("-" * 30)
        
        try:
            dashboard_sheet = self.spreadsheet.worksheet('progress_dashboard')
            data = dashboard_sheet.get_all_values()
            
            if not data:
                print("❌ データがありません")
                return False
            
            # ヘッダー確認
            expected_headers = [
                'goal_id', 'goal_name', 'total_tasks', 'completed_tasks',
                'progress_rate', 'avg_quality', 'last_updated', 'status',
                'priority', 'assigned_agent', 'start_date', 'due_date',
                'actual_completion_date', 'blockers', 'risk_level', 'deliverables'
            ]
            
            if data[0] == expected_headers:
                print("✅ ヘッダー: 正常")
            else:
                print("❌ ヘッダー: 異常")
                print(f"   期待: {expected_headers}")
                print(f"   実際: {data[0]}")
                return False
            
            # データ行確認
            if len(data) > 1:
                print(f"✅ データ行: {len(data)-1}行")
                for i, row in enumerate(data[1:], 2):
                    print(f"   行{i}: {row[0]} - {row[1][:30]}...")
            else:
                print("⚠️ データ行: 0行")
            
            # 列数確認
            for i, row in enumerate(data, 1):
                if len(row) != 16:
                    print(f"❌ 行{i}の列数が異常: {len(row)}列")
                    return False
            
            print("✅ 列数: すべて16列で正常")
            print("🎉 最終状態: 正常")
            
            return True
            
        except Exception as e:
            print(f"❌ 最終確認失敗: {e}")
            return False

def main():
    restorer = RestoreAndSync()
    
    print("🚀 復元と同期システム起動")
    print("=" * 50)
    
    # 1. 実際のデータを同期
    success = restorer.sync_actual_data_to_dashboard()
    
    if success:
        # 2. 最終状態を確認
        final_success = restorer.verify_final_state()
        
        if final_success:
            print("\n🎉🎉🎉 復元と同期が完了しました！ 🎉🎉🎉")
            print("✅ ヘッダーが復元されました")
            print("✅ 実際のプロジェクトゴールからデータを読み込みました")
            print("✅ 進捗ダッシュボードが正しく更新されました")
            print("🚀 システムは正常に動作しています")
        else:
            print("\n⚠️ 最終確認で問題が検出されました")
    else:
        print("\n❌ 復元と同期に失敗しました")

if __name__ == "__main__":
    main()
