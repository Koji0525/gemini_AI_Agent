"""
自動タスク生成エージェント v2（高品質版）
既存の優良タスク定義を活用した高品質タスク生成
"""

import sys
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.task_templates.high_quality_templates import HighQualityTaskTemplates

class AutoTaskGeneratorV2:
    """自動タスク生成エージェント v2（高品質版）"""
    
    def __init__(self, sheets_manager=None):
        self.sheets = sheets_manager
        self.templates = HighQualityTaskTemplates()
        
    def check_pending_tasks(self) -> int:
        """pendingタスクの数を確認"""
        try:
            result = self.sheets.service.spreadsheets().values().get(
                spreadsheetId=self.sheets.spreadsheet_id,
                range="pm_tasks!A2:Z1000"
            ).execute()
            
            values = result.get('values', [])
            pending_count = sum(1 for row in values if len(row) > 4 and row[4] == 'pending')
            
            print(f"📋 pendingタスク: {pending_count}個")
            return pending_count
            
        except Exception as e:
            print(f"⚠️  タスク確認エラー: {e}")
            return -1
    
    def generate_high_quality_tasks(self, goal_id: str = "7") -> List[Dict[str, Any]]:
        """高品質タスクを生成"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        # タスク1: 統合テスト
        task1 = self.templates.get_integration_test_template(goal_id, timestamp)
        
        # タスク2: システム連携確認（タスク1に依存）
        task2 = self.templates.get_system_integration_template(
            goal_id, timestamp, task1["task_id"]
        )
        
        # タスク3: フラッキーテスト検出設計（タスク2に依存）
        task3 = self.templates.get_flaky_test_detection_template(
            goal_id, timestamp, task2["task_id"]
        )
        
        # タスク4: 24時間稼働最終確認（タスク3に依存）
        task4 = self.templates.get_24h_operation_checklist_template(
            goal_id, timestamp, task3["task_id"]
        )
        
        return [task1, task2, task3, task4]
    
    def add_tasks_to_sheet(self, tasks: List[Dict[str, Any]]) -> bool:
        """タスクをGoogle Sheetsに追加"""
        try:
            for task in tasks:
                row_data = [
                    task["task_id"],
                    task["parent_goal_id"],
                    task["description"],
                    task["required_role"],
                    task["status"],
                    task["priority"],
                    task["estimated_time"],
                    task["dependencies"],
                    task["created_at"],
                    task["batch_id"],
                    task["detail_file_path"],
                    task["blank"],
                    task["execution_type"]
                ]
                
                self.sheets.service.spreadsheets().values().append(
                    spreadsheetId=self.sheets.spreadsheet_id,
                    range="pm_tasks!A:M",
                    valueInputOption="RAW",
                    body={"values": [row_data]}
                ).execute()
                
                print(f"  ✅ 高品質タスク追加: {task['task_id']}")
            
            print(f"\n✅ {len(tasks)}個の高品質タスクを追加しました")
            return True
            
        except Exception as e:
            print(f"❌ タスク追加エラー: {e}")
            return False
    
    def auto_generate_if_needed(self) -> Dict[str, Any]:
        """必要に応じて高品質タスクを自動生成"""
        print("━" * 60)
        print("🤖 自動タスク生成チェック（高品質版 v2）")
        print("━" * 60)
        print()
        
        pending_count = self.check_pending_tasks()
        
        if pending_count < 0:
            print("\n⚠️  タスク確認に失敗しました。")
            return {"generated": False, "error": "タスク確認失敗"}
        
        if pending_count == 0:
            print("\n📋 pendingタスクが0個です。")
            print("🔧 高品質タスクを自動生成します...")
            print()
            
            tasks = self.generate_high_quality_tasks()
            
            print("【生成する高品質タスク】")
            for i, task in enumerate(tasks, 1):
                print(f"\n  {i}. {task['task_id']}")
                print(f"     タイプ: {task['execution_type']}")
                print(f"     時間: {task['estimated_time']}")
                print(f"     依存: {task['dependencies'] or 'なし'}")
                desc_lines = task['description'].split('\n')
                print(f"     説明: {desc_lines[0][:60]}...")
            
            print()
            success = self.add_tasks_to_sheet(tasks)
            
            if success:
                print("✅ 高品質タスク自動生成完了")
                print("📝 これらのタスクは既存システムで自動実行されます")
            
            return {
                "generated": True,
                "task_count": len(tasks),
                "success": success,
                "tasks": [t["task_id"] for t in tasks],
                "quality": "high"
            }
            
        else:
            print(f"\n📋 {pending_count}個のpendingタスクが存在します。")
            print("⏭️  タスク自動生成はスキップします。")
            return {
                "generated": False,
                "pending_count": pending_count
            }

def main():
    """メイン実行"""
    from tools.sheets_manager import GoogleSheetsManager
    
    print("🚀 自動タスク生成エージェント v2（高品質版）起動")
    print()
    
    try:
        sheets = GoogleSheetsManager()
        generator = AutoTaskGeneratorV2(sheets)
        
        result = generator.auto_generate_if_needed()
        
        print()
        print("━" * 60)
        print("📊 実行結果")
        print("━" * 60)
        
        if result.get("generated"):
            print(f"  ✅ タスク自動生成: 成功")
            print(f"  📝 生成タスク数: {result.get('task_count')}個")
            print(f"  ⭐ 品質: {result.get('quality', 'standard').upper()}")
            
            if result.get("tasks"):
                print("\n  【生成されたタスクID】")
                for task_id in result.get("tasks"):
                    print(f"    - {task_id}")
            
            print("\n  🎯 次のアクション:")
            print("    bash start_pending_tasks.sh --limit 4")
            
        elif result.get("error"):
            print(f"  ⚠️  エラー: {result['error']}")
            
        else:
            print(f"  ⏭️  タスク自動生成: スキップ")
            if "pending_count" in result:
                print(f"  📋 既存pending: {result['pending_count']}個")
        
        print()
        return 0
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

