#!/bin/bash
# auto_task_generator.pyのメソッド名を修正

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 auto_task_generatorの修正"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# バックアップ
cp agents/auto_task_generator.py "agents/auto_task_generator.py.backup_${NOW_JST}"

# 修正版を作成
cat > agents/auto_task_generator.py << 'PYTHON'
"""
自動タスク生成エージェント（修正版）
pendingタスクがない場合に、統合・テスト・動作確認タスクを自動生成
"""

import sys
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class AutoTaskGenerator:
    """自動タスク生成エージェント"""
    
    def __init__(self, sheets_manager=None):
        self.sheets = sheets_manager
        
    def check_pending_tasks(self) -> int:
        """pendingタスクの数を確認（修正版）"""
        try:
            # 正しいメソッド名を使用
            from tools.base_data_accessor import BaseDataAccessor
            
            accessor = BaseDataAccessor(self.sheets)
            tasks = accessor.get_all_tasks()
            
            # pendingタスクをカウント
            pending_count = sum(1 for task in tasks if task.get('status') == 'pending')
            
            print(f"📋 pendingタスク: {pending_count}個")
            return pending_count
            
        except Exception as e:
            print(f"❌ pendingタスク確認エラー: {e}")
            
            # フォールバック: 直接Sheets APIを使用
            try:
                result = self.sheets.service.spreadsheets().values().get(
                    spreadsheetId=self.sheets.spreadsheet_id,
                    range="pm_tasks!A2:Z1000"
                ).execute()
                
                values = result.get('values', [])
                
                # status列（E列、インデックス4）を確認
                pending_count = sum(1 for row in values if len(row) > 4 and row[4] == 'pending')
                
                print(f"📋 pendingタスク: {pending_count}個（フォールバック）")
                return pending_count
                
            except Exception as e2:
                print(f"❌ フォールバックも失敗: {e2}")
                return -1
    
    def generate_integration_tasks(self, goal_id: str = "7") -> List[Dict[str, Any]]:
        """統合タスクを生成"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp = datetime.now().strftime('%H%M%S')
        batch_id = f"auto_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        tasks = [
            {
                "task_id": f"{goal_id}_統合テスト実行_{timestamp}_01",
                "parent_goal_id": goal_id,
                "description": "F1-F10の統合テストを実行し、全機能が正常に動作することを確認する。tests/system_protection/test_core_functions.pyを実行し、85%以上の成功率を確認。",
                "required_role": "tester",
                "status": "pending",
                "priority": "high",
                "estimated_time": "30min",
                "dependencies": "",
                "created_at": now,
                "batch_id": batch_id,
                "detail_file_path": "",
                "blank": "",
                "execution_type": "testing"
            },
            {
                "task_id": f"{goal_id}_動作確認レポート作成_{timestamp}_02",
                "parent_goal_id": goal_id,
                "description": "24時間稼働システムの動作確認レポートを作成する。F1-F10の各機能が実際に連携して動作していることを確認し、MDファイルでレポートを生成。agent_outputs/documentation/に保存。",
                "required_role": "developer",
                "status": "pending",
                "priority": "high",
                "estimated_time": "1h",
                "dependencies": f"{goal_id}_統合テスト実行_{timestamp}_01",
                "created_at": now,
                "batch_id": batch_id,
                "detail_file_path": "",
                "blank": "",
                "execution_type": "documentation"
            },
            {
                "task_id": f"{goal_id}_エンドツーエンドテスト_{timestamp}_03",
                "parent_goal_id": goal_id,
                "description": "ゴール追加からタスク実行、品質評価、ナレッジ蓄積までの一連の流れをエンドツーエンドでテストする。実際に小規模なテストゴールを追加し、完全な自動実行を確認。全ステップの実行ログを記録。",
                "required_role": "tester",
                "status": "pending",
                "priority": "high",
                "estimated_time": "2h",
                "dependencies": f"{goal_id}_統合テスト実行_{timestamp}_01",
                "created_at": now,
                "batch_id": batch_id,
                "detail_file_path": "",
                "blank": "",
                "execution_type": "testing"
            }
        ]
        
        return tasks
    
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
                
                # Google Sheets APIで直接追加
                self.sheets.service.spreadsheets().values().append(
                    spreadsheetId=self.sheets.spreadsheet_id,
                    range="pm_tasks!A:M",
                    valueInputOption="RAW",
                    body={"values": [row_data]}
                ).execute()
                
                print(f"  ✅ タスク追加: {task['task_id']}")
            
            print(f"\n✅ {len(tasks)}個のタスクを追加しました")
            return True
            
        except Exception as e:
            print(f"❌ タスク追加エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def auto_generate_if_needed(self) -> Dict[str, Any]:
        """必要に応じて自動生成"""
        print("━" * 60)
        print("🤖 自動タスク生成チェック")
        print("━" * 60)
        print()
        
        pending_count = self.check_pending_tasks()
        
        if pending_count == 0:
            print("\n📋 pendingタスクが0個です。")
            print("🔧 統合タスクを自動生成します...")
            print()
            
            tasks = self.generate_integration_tasks()
            
            print("【生成タスク】")
            for i, task in enumerate(tasks, 1):
                print(f"  {i}. {task['task_id']}")
                print(f"     {task['description'][:60]}...")
                print()
            
            success = self.add_tasks_to_sheet(tasks)
            
            return {
                "generated": True,
                "task_count": len(tasks),
                "success": success,
                "tasks": [t["task_id"] for t in tasks]
            }
        elif pending_count > 0:
            print(f"\n📋 {pending_count}個のpendingタスクが存在します。")
            print("⏭️  タスク自動生成はスキップします。")
            return {
                "generated": False,
                "pending_count": pending_count,
                "message": "既にpendingタスクが存在"
            }
        else:
            print("\n⚠️  pendingタスクの確認に失敗しました。")
            return {
                "generated": False,
                "error": "タスク確認失敗"
            }

def main():
    """メイン実行"""
    from tools.sheets_manager import GoogleSheetsManager
    
    print("🚀 自動タスク生成エージェント起動")
    print()
    
    try:
        sheets = GoogleSheetsManager()
        generator = AutoTaskGenerator(sheets)
        
        result = generator.auto_generate_if_needed()
        
        print()
        print("━" * 60)
        print("📊 実行結果")
        print("━" * 60)
        
        if result.get("generated"):
            print(f"  ✅ タスク自動生成: 成功")
            print(f"  📝 生成タスク数: {result.get('task_count')}個")
            if result.get("tasks"):
                print("\n  【生成されたタスクID】")
                for task_id in result.get("tasks"):
                    print(f"    - {task_id}")
        else:
            print(f"  ⏭️  タスク自動生成: スキップ")
            if "pending_count" in result:
                print(f"  📋 既存pending: {result['pending_count']}個")
            if "error" in result:
                print(f"  ⚠️  エラー: {result['error']}")
        
        print()
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

PYTHON

echo "✅ 修正版作成: agents/auto_task_generator.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 動作確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "修正版を実行しますか？ [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 agents/auto_task_generator.py
else
    echo "  ⏭️  実行はスキップされました"
    echo "  📋 手動実行: python3 agents/auto_task_generator.py"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 修正完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📄 修正内容:"
echo "  1. BaseDataAccessorを使用してタスク取得"
echo "  2. フォールバック機能追加（直接API使用）"
echo "  3. pending判定の正確性向上"
echo "  4. エラーハンドリング強化"
echo ""
echo "📊 バックアップ: agents/auto_task_generator.py.backup_${NOW_JST}"
echo ""

