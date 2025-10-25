#!/usr/bin/env python3
"""PM Agent自動化 - タスク登録モジュール（最終修正版）"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ['DISPLAY'] = ':1'

from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import get_config


class TaskRegistrationAgent:
    """タスク登録エージェント（最終修正版）"""
    
    # pm_tasksシートの実際のカラム構造（13列）
    SHEET_COLUMNS = [
        'task_id',          # 1 (A)
        'parent_goal_id',   # 2 (B)
        'description',      # 3 (C)
        'required_role',    # 4 (D)
        'status',           # 5 (E)
        'priority',         # 6 (F)
        'estimated_time',   # 7 (G)
        'dependencies',     # 8 (H)
        'created_at',       # 9 (I)
        'batch_id',         # 10 (J)
        '',                 # 11 (K)
        '',                 # 12 (L)
        'execution_type'    # 13 (M)
    ]
    
    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = sheets_manager
        self.config = get_config()
    
    async def register_tasks(
        self, 
        goal_id: str,
        tasks: List[Dict[str, Any]]
    ) -> bool:
        """
        タスクをpm_tasksシートに登録
        
        Args:
            goal_id: 親目標ID
            tasks: 登録するタスクのリスト
        
        Returns:
            登録が成功したかどうか
        """
        try:
            print(f"\n📝 目標{goal_id}のタスク登録を開始...")
            print(f"登録予定: {len(tasks)}件")
            
            # 次のタスクIDを取得
            next_task_id = self._get_next_task_id()
            print(f"✅ 次のタスクID: {next_task_id}")
            
            # タスクをシート形式に変換
            sheet_rows = self._convert_to_sheet_format(
                goal_id, 
                tasks, 
                next_task_id
            )
            
            # pm_tasksシートに追加（範囲指定版）
            success = await self._append_to_sheet_with_range(sheet_rows)
            
            if success:
                print(f"✅ {len(tasks)}件のタスクを登録しました")
                print(f"   タスクID: {next_task_id} 〜 {next_task_id + len(tasks) - 1}")
                return True
            else:
                print("❌ タスク登録に失敗しました")
                return False
            
        except Exception as e:
            print(f"❌ タスク登録エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _get_next_task_id(self) -> int:
        """次のタスクIDを取得"""
        try:
            all_tasks = self.sheets.get_tasks()
            
            if not all_tasks:
                return 1
            
            max_id = 0
            for task in all_tasks:
                task_id = task.get('id') or task.get('task_id')
                if task_id:
                    try:
                        task_id_int = int(task_id)
                        max_id = max(max_id, task_id_int)
                    except (ValueError, TypeError):
                        continue
            
            return max_id + 1
            
        except Exception as e:
            print(f"⚠️ 次のタスクID取得エラー: {e}")
            return 1
    
    def _convert_to_sheet_format(
        self,
        goal_id: str,
        tasks: List[Dict[str, Any]],
        start_id: int
    ) -> List[List[Any]]:
        """タスクをシート形式に変換"""
        sheet_rows = []
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        for i, task in enumerate(tasks):
            task_id = start_id + i
            
            # 実際のシート構造に合わせた順序（13列）
            row = [
                task_id,                                    # 1. task_id (A)
                goal_id,                                    # 2. parent_goal_id (B)
                task.get('title', ''),                      # 3. description (C)
                task.get('required_role', 'pm'),            # 4. required_role (D)
                task.get('status', 'pending'),              # 5. status (E)
                task.get('priority', 'medium'),             # 6. priority (F)
                task.get('estimated_hours', 2),             # 7. estimated_time (G)
                '',                                         # 8. dependencies (H)
                datetime.now().strftime('%Y-%m-%d'),       # 9. created_at (I)
                batch_id,                                   # 10. batch_id (J)
                '',                                         # 11. (K)
                '',                                         # 12. (L)
                'gemini'                                    # 13. execution_type (M)
            ]
            
            sheet_rows.append(row)
        
        return sheet_rows
    
    async def _append_to_sheet_with_range(self, rows: List[List[Any]]) -> bool:
        """
        pm_tasksシートにデータを追加（範囲指定版）
        
        Args:
            rows: 追加するデータ
        
        Returns:
            追加が成功したかどうか
        """
        try:
            spreadsheet = self.sheets.gc.open_by_key(self.config.get("SPREADSHEET_ID"))
            sheet = spreadsheet.worksheet('pm_tasks')
            
            # シートの最終行を取得
            all_values = sheet.get_all_values()
            next_row = len(all_values) + 1
            
            # A列から明示的に範囲を指定して追加
            end_row = next_row + len(rows) - 1
            range_name = f'A{next_row}:M{end_row}'
            
            print(f"📍 追加先: {range_name}")
            
            sheet.update(
                range_name=range_name,
                values=rows
            )
            
            print(f"✅ pm_tasksシートの{next_row}行目以降に正しく追加しました")
            return True
            
        except Exception as e:
            print(f"❌ シート追加エラー: {e}")
            import traceback
            traceback.print_exc()
            return False


# ==
# テスト実行
# ==
async def test_task_registration():
    """タスク登録のテスト"""
    print("="*70)
    print("🧪 PM Agent自動化 - タスク登録テスト（最終修正版）")
    print("="*70)
    print()
    
    config = get_config()
    sheets = GoogleSheetsManager(
        spreadsheet_id=config.get("SPREADSHEET_ID"),
        service_account_file=config.get("SERVICE_ACCOUNT_FILE")
    )
    
    agent = TaskRegistrationAgent(sheets)
    
    # テスト用のモックタスク
    mock_tasks = [
        {
            'title': '[TEST-FINAL] 最終修正版テストタスク1',
            'description': 'A列から正しく追加されるテスト',
            'required_role': 'pm',
            'priority': 'high',
            'estimated_hours': 2,
            'status': 'pending'
        },
        {
            'title': '[TEST-FINAL] 最終修正版テストタスク2',
            'description': '範囲指定で正しいカラムに追加',
            'required_role': 'dev',
            'priority': 'medium',
            'estimated_hours': 3,
            'status': 'pending'
        }
    ]
    
    print("【テスト】タスク登録（最終修正版）")
    print("-"*70)
    print("✅ A列から明示的に範囲指定")
    print("✅ update()メソッドで正確に追加")
    print()
    
    # ユーザー確認
    response = input("続行しますか？ (y/n): ")
    
    if response.lower() != 'y':
        print("❌ テストをキャンセルしました")
        return
    
    # タスク登録
    success = await agent.register_tasks('4', mock_tasks)
    
    if success:
        print("\n✅ テスト成功")
        print("📋 pm_tasksシートを確認してください")
        print("✨ 今度こそA列から正しく追加されているはずです！")
    else:
        print("\n❌ テスト失敗")


if __name__ == "__main__":
    asyncio.run(test_task_registration())
