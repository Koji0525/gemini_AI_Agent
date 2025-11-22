"""
スマートタスク選択エージェント
高品質タスクを優先し、completedタスクを除外
"""

import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class SmartTaskSelector:
    """スマートタスク選択エージェント"""
    
    def __init__(self, sheets_manager=None):
        self.sheets = sheets_manager
        
    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """pendingタスクを取得（completedを厳密に除外）"""
        try:
            result = self.sheets.service.spreadsheets().values().get(
                spreadsheetId=self.sheets.spreadsheet_id,
                range="pm_tasks!A2:Z1000"
            ).execute()
            
            values = result.get('values', [])
            
            # pendingタスクのみを抽出
            pending_tasks = []
            for i, row in enumerate(values, 2):  # 2行目から開始
                if len(row) > 4:
                    task_id = row[0]
                    status = row[4]
                    
                    # status='pending'のみを追加
                    if status == 'pending':
                        task = {
                            'row_index': i,
                            'task_id': task_id,
                            'parent_goal_id': row[1] if len(row) > 1 else '',
                            'description': row[2] if len(row) > 2 else '',
                            'required_role': row[3] if len(row) > 3 else '',
                            'status': status,
                            'priority': row[5] if len(row) > 5 else 'medium',
                            'estimated_time': row[6] if len(row) > 6 else '1h',
                            'dependencies': row[7] if len(row) > 7 else '',
                            'created_at': row[8] if len(row) > 8 else '',
                            'batch_id': row[9] if len(row) > 9 else '',
                            'execution_type': row[12] if len(row) > 12 else 'implementation'
                        }
                        pending_tasks.append(task)
            
            print(f"📋 pendingタスク: {len(pending_tasks)}個")
            return pending_tasks
            
        except Exception as e:
            print(f"❌ タスク取得エラー: {e}")
            return []
    
    def prioritize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """タスクを優先順位でソート"""
        def get_priority_score(task: Dict[str, Any]) -> int:
            score = 0
            
            # 1. batch_idで高品質タスクを最優先
            if 'auto_quality' in task.get('batch_id', ''):
                score += 1000
            elif 'auto_integration' in task.get('batch_id', ''):
                score += 900
            
            # 2. 優先度
            priority_map = {'high': 100, 'medium': 50, 'low': 10}
            score += priority_map.get(task.get('priority', 'medium'), 50)
            
            # 3. execution_typeで実行可能なタイプを優先
            executable_types = ['testing', 'implementation', 'design', 'documentation']
            if task.get('execution_type') in executable_types:
                score += 10
            
            # 4. 依存関係なしを優先
            if not task.get('dependencies'):
                score += 5
            
            # 5. 新しいタスクを優先
            created_at = task.get('created_at', '')
            if created_at:
                try:
                    dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    days_old = (datetime.now() - dt).days
                    score += max(0, 10 - days_old)  # 新しいほど高得点
                except:
                    pass
            
            return score
        
        # 優先順位でソート（降順）
        sorted_tasks = sorted(tasks, key=get_priority_score, reverse=True)
        
        print("\n【タスク優先順位】")
        for i, task in enumerate(sorted_tasks[:5], 1):
            score = get_priority_score(task)
            print(f"  {i}. {task['task_id']}")
            print(f"     優先度: {task['priority']} | batch: {task['batch_id']}")
            print(f"     スコア: {score}")
        
        return sorted_tasks
    
    def select_executable_task(self, limit: int = 1) -> List[Dict[str, Any]]:
        """実行可能なタスクを選択"""
        pending_tasks = self.get_pending_tasks()
        
        if not pending_tasks:
            print("\n⚠️  実行可能なpendingタスクがありません")
            return []
        
        # 優先順位でソート
        prioritized_tasks = self.prioritize_tasks(pending_tasks)
        
        # 上位limitタスクを選択
        selected = prioritized_tasks[:limit]
        
        print(f"\n✅ {len(selected)}個のタスクを選択しました")
        return selected

