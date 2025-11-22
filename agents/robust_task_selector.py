"""
ロバストタスク選択エージェント
列名に依存せず、列インデックスで直接アクセス
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from typing import List, Dict, Any

class RobustTaskSelector:
    """ロバストタスク選択エージェント"""
    
    # 列インデックスの定義（固定）
    COL_TASK_ID = 0
    COL_PARENT_GOAL_ID = 1
    COL_DESCRIPTION = 2
    COL_REQUIRED_ROLE = 3
    COL_STATUS = 4  # E列
    COL_PRIORITY = 5
    COL_ESTIMATED_TIME = 6
    COL_DEPENDENCIES = 7
    COL_CREATED_AT = 8
    COL_BATCH_ID = 9
    COL_DETAIL_FILE_PATH = 10
    COL_BLANK = 11
    COL_EXECUTION_TYPE = 12
    
    def __init__(self, sheets_manager=None):
        self.sheets = sheets_manager
        
    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """pendingタスクを取得（列インデックスで直接アクセス）"""
        try:
            # データ行を取得（A2:M1000）
            result = self.sheets.service.spreadsheets().values().get(
                spreadsheetId=self.sheets.spreadsheet_id,
                range="pm_tasks!A2:M1000"
            ).execute()
            
            values = result.get('values', [])
            
            pending_tasks = []
            for i, row in enumerate(values, 2):  # 2行目から開始
                # 列数が不足している場合はスキップ
                if len(row) < 5:
                    continue
                
                # status列を取得（列インデックス4）
                status = row[self.COL_STATUS] if len(row) > self.COL_STATUS else ''
                
                # デバッグ出力（最初の3行のみ）
                if i <= 4:
                    task_id = row[self.COL_TASK_ID] if len(row) > self.COL_TASK_ID else ''
                    print(f"  行{i}: task_id='{task_id}', status='{status}'")
                
                # status='pending'のみを追加
                if status == 'pending':
                    task = {
                        'row_index': i,
                        'task_id': row[self.COL_TASK_ID] if len(row) > self.COL_TASK_ID else '',
                        'parent_goal_id': row[self.COL_PARENT_GOAL_ID] if len(row) > self.COL_PARENT_GOAL_ID else '',
                        'description': row[self.COL_DESCRIPTION] if len(row) > self.COL_DESCRIPTION else '',
                        'required_role': row[self.COL_REQUIRED_ROLE] if len(row) > self.COL_REQUIRED_ROLE else '',
                        'status': status,
                        'priority': row[self.COL_PRIORITY] if len(row) > self.COL_PRIORITY else 'medium',
                        'estimated_time': row[self.COL_ESTIMATED_TIME] if len(row) > self.COL_ESTIMATED_TIME else '1h',
                        'dependencies': row[self.COL_DEPENDENCIES] if len(row) > self.COL_DEPENDENCIES else '',
                        'created_at': row[self.COL_CREATED_AT] if len(row) > self.COL_CREATED_AT else '',
                        'batch_id': row[self.COL_BATCH_ID] if len(row) > self.COL_BATCH_ID else '',
                        'execution_type': row[self.COL_EXECUTION_TYPE] if len(row) > self.COL_EXECUTION_TYPE else 'implementation'
                    }
                    pending_tasks.append(task)
            
            print(f"\n📋 pendingタスク: {len(pending_tasks)}個")
            
            # pendingタスクの詳細を表示
            if pending_tasks:
                print("\n【pendingタスク一覧】")
                for i, task in enumerate(pending_tasks[:5], 1):
                    print(f"  {i}. {task['task_id']}")
                    print(f"     行: {task['row_index']}, 優先度: {task['priority']}")
            
            return pending_tasks
            
        except Exception as e:
            print(f"❌ タスク取得エラー: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def select_executable_task(self, limit: int = 1) -> List[Dict[str, Any]]:
        """実行可能なタスクを選択"""
        print("━" * 60)
        print("🔍 pendingタスク検索（ロバスト版）")
        print("━" * 60)
        print()
        
        pending_tasks = self.get_pending_tasks()
        
        if not pending_tasks:
            print("\n⚠️  実行可能なpendingタスクがありません")
            return []
        
        # 優先度でソート（高→中→低）
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        sorted_tasks = sorted(
            pending_tasks,
            key=lambda t: (
                priority_order.get(t.get('priority', 'medium'), 2),
                1000 if 'auto_quality' in t.get('batch_id', '') else 0
            ),
            reverse=True
        )
        
        selected = sorted_tasks[:limit]
        
        print(f"\n✅ {len(selected)}個のタスクを選択しました")
        for i, task in enumerate(selected, 1):
            print(f"  {i}. {task['task_id']}")
        
        return selected

def main():
    """テスト実行"""
    from tools.sheets_manager import GoogleSheetsManager
    
    sheets = GoogleSheetsManager()
    selector = RobustTaskSelector(sheets)
    
    tasks = selector.get_pending_tasks()
    print(f"\n結果: {len(tasks)}個のpendingタスクを発見")
    
    return 0 if tasks else 1

if __name__ == "__main__":
    sys.exit(main())

