#!/usr/bin/env python3
"""
👑 プロジェクトマネージャーエージェント - メインロジック（軽量化）
"""

import os
import asyncio
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

from configuration.config_loader import ConfigLoader
from pm_system_prompts import SystemPrompts

# TaskExecutorのインポートを修正
try:
    from task_executor import TaskExecutor
except ImportError:
    print("⚠️ task_executorからTaskExecutorをインポートできません。代替実装を使用します。")
    from task_executor_base import TaskExecutor

class ProjectManagerAgent:
    def __init__(self):
        self.config = ConfigLoader()
        self.prompts = SystemPrompts()
        self.task_executor = TaskExecutor()
        
        # Google Sheets設定
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.credentials = Credentials.from_service_account_file(
            self.config.get('service_account_file'), 
            scopes=self.scopes
        )
        self.gc = gspread.authorize(self.credentials)
        self.spreadsheet = self.gc.open_by_key(self.config.get('spreadsheet_id'))
    
    async def analyze_project_status(self):
        """プロジェクト状態を分析"""
        print("🔍 プロジェクト状態分析中...")
        
        try:
            # シートデータ取得
            goals_sheet = self.spreadsheet.worksheet('project_goal')
            tasks_sheet = self.spreadsheet.worksheet('pm_tasks')
            
            goals_data = goals_sheet.get_all_values()
            tasks_data = tasks_sheet.get_all_values()
            
            # 基本統計計算
            total_goals = len(goals_data) - 1 if len(goals_data) > 1 else 0
            total_tasks = len(tasks_data) - 1 if len(tasks_data) > 1 else 0
            
            active_goals = 0
            completed_tasks = 0
            
            # ゴール分析
            if len(goals_data) > 1:
                headers = goals_data[0]
                status_idx = headers.index('status') if 'status' in headers else -1
                
                for row in goals_data[1:]:
                    if status_idx != -1 and len(row) > status_idx:
                        if row[status_idx].lower() in ['active', '実行中']:
                            active_goals += 1
            
            # タスク分析
            if len(tasks_data) > 1:
                headers = tasks_data[0]
                status_idx = headers.index('status') if 'status' in headers else -1
                
                for row in tasks_data[1:]:
                    if status_idx != -1 and len(row) > status_idx:
                        if row[status_idx].lower() == 'completed':
                            completed_tasks += 1
            
            progress_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            status_report = {
                'total_goals': total_goals,
                'active_goals': active_goals,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'progress_rate': progress_rate,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"�� 分析結果: {active_goals}/{total_goals} アクティブゴール, "
                  f"{completed_tasks}/{total_tasks} 完了タスク ({progress_rate:.1f}%)")
            
            return status_report
            
        except Exception as e:
            print(f"❌ プロジェクト分析エラー: {e}")
            return None
    
    async def identify_priority_tasks(self):
        """優先タスクを特定"""
        print("🎯 優先タスクを特定中...")
        
        try:
            tasks_sheet = self.spreadsheet.worksheet('pm_tasks')
            tasks_data = tasks_sheet.get_all_values()
            
            if len(tasks_data) <= 1:
                print("⚠️ タスクデータがありません")
                return []
            
            headers = tasks_data[0]
            priority_tasks = []
            
            # 優先度の高い未完了タスクを抽出
            for i, row in enumerate(tasks_data[1:], 2):
                if len(row) > 4:  # statusまでデータがある
                    status = row[4].lower() if row[4] else ''
                    priority = row[5] if len(row) > 5 else '3'
                    
                    if status != 'completed' and priority in ['1', '2']:
                        task_info = {
                            'row_number': i,
                            'task_id': row[0] if row[0] else f"ROW_{i}",
                            'description': row[2] if len(row) > 2 else '説明なし',
                            'priority': priority,
                            'execution_type': row[12] if len(row) > 12 else 'general'
                        }
                        priority_tasks.append(task_info)
            
            print(f"✅ 優先タスク {len(priority_tasks)}件を特定")
            for task in priority_tasks[:3]:  # 最大3件表示
                print(f"   • {task['task_id']}: {task['description'][:50]}...")
            
            return priority_tasks
            
        except Exception as e:
            print(f"❌ 優先タスク特定エラー: {e}")
            return []
    
    async def execute_priority_tasks(self, priority_tasks):
        """優先タスクを実行"""
        if not priority_tasks:
            print("⚠️ 実行する優先タスクがありません")
            return []
        
        print(f"⚡ {len(priority_tasks)}件の優先タスクを実行中...")
        
        results = []
        for task in priority_tasks[:5]:  # 最大5件まで実行
            try:
                print(f"   🎯 実行中: {task['task_id']}")
                
                # タスク実行タイプに基づいて実行
                result = await self.task_executor.execute_task(task)
                results.append(result)
                
                if result.get('success'):
                    print(f"   ✅ 完了: {task['task_id']}")
                else:
                    print(f"   ❌ 失敗: {task['task_id']}")
                    
            except Exception as e:
                print(f"   💥 実行エラー: {task['task_id']} - {e}")
                results.append({
                    'task_id': task['task_id'],
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    async def update_progress_dashboard(self):
        """進捗ダッシュボードを更新"""
        print("📈 進捗ダッシュボード更新中...")
        
        try:
            dashboard_sheet = self.spreadsheet.worksheet('progress_dashboard')
            
            # 現在の進捗を取得
            status = await self.analyze_project_status()
            if not status:
                return False
            
            # 新しい進捗行を作成
            new_row = [
                f"AUTO-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                f"自動実行 - {status['active_goals']}個のアクティブゴール",
                str(status['total_tasks']),
                str(status['completed_tasks']),
                f"{status['progress_rate']:.1f}",
                "8.5",  # 平均品質（デフォルト）
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Active',
                '2',
                'PM Agent',
                datetime.now().strftime('%Y-%m-%d'),
                (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                '',
                '自動実行中',
                '低',
                '自動レポート'
            ]
            
            # ダッシュボードに追加
            dashboard_sheet.append_row(new_row)
            print("✅ 進捗ダッシュボードを更新しました")
            
            return True
            
        except Exception as e:
            print(f"❌ ダッシュボード更新エラー: {e}")
            return False
    
    async def generate_execution_report(self, execution_results):
        """実行結果レポートを生成"""
        print("📋 実行結果レポート生成中...")
        
        success_count = sum(1 for result in execution_results if result.get('success'))
        total_count = len(execution_results)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tasks_executed': total_count,
            'successful_tasks': success_count,
            'success_rate': (success_count / total_count * 100) if total_count > 0 else 0,
            'details': execution_results
        }
        
        print(f"📊 実行結果: {success_count}/{total_count} 成功 "
              f"({report['success_rate']:.1f}%)")
        
        return report

if __name__ == "__main__":
    # テスト実行
    async def test():
        agent = ProjectManagerAgent()
        await agent.analyze_project_status()
    
    asyncio.run(test())
