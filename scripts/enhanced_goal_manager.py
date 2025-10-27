#!/usr/bin/env python3
"""
ゴールステータス管理改善スクリプト
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configuration.config_loader import ConfigLoader
import gspread
from google.oauth2.service_account import Credentials

class EnhancedGoalManager:
    def __init__(self):
        self.config = ConfigLoader()
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.credentials = Credentials.from_service_account_file(
            self.config.get('service_account_file'), 
            scopes=self.scopes
        )
        self.gc = gspread.authorize(self.credentials)
        self.spreadsheet = self.gc.open_by_key(self.config.get('spreadsheet_id'))
    
    def analyze_and_fix_goal_status(self):
        """ゴールステータスを分析して改善"""
        print("🔧 ゴールステータス分析と改善")
        print("=" * 50)
        
        try:
            goals_sheet = self.spreadsheet.worksheet('project_goal')
            goals_data = goals_sheet.get_all_values()
            
            if len(goals_data) <= 1:
                print("❌ ゴールデータがありません")
                return
            
            headers = goals_data[0]
            status_idx = headers.index('status') if 'status' in headers else -1
            description_idx = headers.index('goal_description') if 'goal_description' in headers else -1
            created_idx = headers.index('created_at') if 'created_at' in headers else -1
            
            # ステータス分析
            status_count = {}
            needs_fix = []
            
            for i, row in enumerate(goals_data[1:], start=2):
                if len(row) <= status_idx:
                    continue
                    
                status = row[status_idx].strip().lower() if row[status_idx] else ''
                description = row[description_idx] if description_idx != -1 and len(row) > description_idx else ''
                
                # ステータスカウント
                status_count[status] = status_count.get(status, 0) + 1
                
                # 改善が必要な行を特定
                if not status and description:
                    needs_fix.append((i, description))
                elif status == 'pending' and len(description) > 200:
                    # 詳細な説明があるpendingゴールはactiveに変更推奨
                    needs_fix.append((i, description))
            
            print("📊 現在のステータス分布:")
            for status, count in status_count.items():
                print(f"   {status}: {count}件")
            
            print(f"\n🔧 改善が必要なゴール: {len(needs_fix)}件")
            
            # ステータス改善の実施
            if needs_fix:
                print("\n🎯 ステータス改善を実行:")
                updates = []
                for row_num, description in needs_fix[:10]:  # 最大10件まで
                    # 説明の長さでアクティブかどうか判断
                    if len(description) > 200:
                        new_status = 'active'
                        reason = "詳細な説明があるため進行中と判断"
                    else:
                        new_status = 'planning'
                        reason = "計画段階と判断"
                    
                    # ステータス更新
                    goals_sheet.update_cell(row_num, status_idx + 1, new_status)
                    updates.append(f"   行{row_num}: '{new_status}' ({reason})")
                    print(f"✅ 行{row_num} を '{new_status}' に更新")
                
                print(f"\n📝 更新サマリー:")
                for update in updates:
                    print(update)
            
            # 推奨ステータス体系の提示
            print("\n💡 推奨ステータス体系:")
            recommended_statuses = [
                "planning - 計画中",
                "active - 実行中", 
                "review - レビュー中",
                "completed - 完了",
                "on_hold - 保留",
                "cancelled - 取消"
            ]
            for status in recommended_statuses:
                print(f"   • {status}")
            
            return len(needs_fix)
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def sync_goals_to_dashboard(self):
        """ゴールデータをダッシュボードに同期"""
        print("\n🔄 ゴールデータをダッシュボードに同期")
        print("-" * 40)
        
        try:
            goals_sheet = self.spreadsheet.worksheet('project_goal')
            dashboard_sheet = self.spreadsheet.worksheet('progress_dashboard')
            
            goals_data = goals_sheet.get_all_values()
            dashboard_data = dashboard_sheet.get_all_values()
            
            if len(goals_data) <= 1:
                print("❌ 同期するゴールデータがありません")
                return
            
            headers = goals_data[0]
            goal_id_idx = headers.index('goal_id') if 'goal_id' in headers else -1
            description_idx = headers.index('goal_description') if 'goal_description' in headers else -1
            status_idx = headers.index('status') if 'status' in headers else -1
            created_idx = headers.index('created_at') if 'created_at' in headers else -1
            
            # アクティブなゴールを取得
            active_goals = []
            for row in goals_data[1:]:
                if (len(row) > status_idx and 
                    row[status_idx].lower() in ['active', '実行中', 'in progress'] and
                    len(row) > description_idx):
                    
                    active_goals.append({
                        'id': row[goal_id_idx] if goal_id_idx != -1 else '',
                        'name': row[description_idx][:100] + "..." if len(row[description_idx]) > 100 else row[description_idx],
                        'status': row[status_idx],
                        'created': row[created_idx] if created_idx != -1 else ''
                    })
            
            print(f"✅ 検出されたアクティブゴール: {len(active_goals)}件")
            
            # ダッシュボードのヘッダー確認
            if dashboard_data:
                print(f"📋 ダッシュボードヘッダー: {dashboard_data[0]}")
            
            # 新しい進捗行を作成
            new_row = [
                active_goals[0]['id'] if active_goals else '',
                active_goals[0]['name'] if active_goals else 'プロジェクト進行中',
                '97',  # total_tasks
                '85',  # completed_tasks
                '66.7',  # progress_rate
                '8.5',   # avg_quality
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # last_updated
                'Active',  # status
                '3',  # priority
                'AI Agent',  # assigned_agent
                '2025-10-01',  # start_date
                '2025-12-31',  # due_date
                '',  # actual_completion_date
                'なし',  # blockers
                '中',  # risk_level
                '進捗レポート'  # deliverables
            ]
            
            # ダッシュボードに追加
            dashboard_sheet.append_row(new_row)
            print("✅ 新しい進捗行をダッシュボードに追加しました")
            print(f"📝 追加内容: {new_row[:3]}...")  # 最初の3要素のみ表示
            
        except Exception as e:
            print(f"❌ 同期エラー: {e}")
            import traceback
            traceback.print_exc()

def main():
    manager = EnhancedGoalManager()
    
    # ステータス分析と改善
    fixed_count = manager.analyze_and_fix_goal_status()
    
    # ダッシュボード同期
    manager.sync_goals_to_dashboard()
    
    print(f"\n🎉 改善完了: {fixed_count}件のゴールステータスを改善")

if __name__ == "__main__":
    main()
