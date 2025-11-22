#!/bin/bash
# auto_task_generatorを既存システムと完全統合

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 auto_task_generator最終修正（エラーなし版）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# 最終版を作成
cat > agents/auto_task_generator.py << 'PYTHON'
"""
自動タスク生成エージェント（最終版 - エラーなし）
既存システムと完全統合、pendingタスクが0の場合に統合タスクを自動生成
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
        """pendingタスクの数を確認（既存システム活用）"""
        try:
            # Google Sheets APIを直接使用（最も確実な方法）
            result = self.sheets.service.spreadsheets().values().get(
                spreadsheetId=self.sheets.spreadsheet_id,
                range="pm_tasks!A2:Z1000"
            ).execute()
            
            values = result.get('values', [])
            
            # status列（E列、インデックス4）でpendingを確認
            pending_count = 0
            for row in values:
                if len(row) > 4 and row[4] == 'pending':
                    pending_count += 1
            
            print(f"📋 pendingタスク: {pending_count}個")
            return pending_count
            
        except Exception as e:
            print(f"⚠️  タスク確認エラー: {e}")
            # エラー時は-1を返して安全側に倒す
            return -1
    
    def generate_integration_tasks(self, goal_id: str = "7") -> List[Dict[str, Any]]:
        """統合タスクを生成（システム全体の連携確認）"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp = datetime.now().strftime('%H%M%S')
        batch_id = f"auto_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        tasks = [
            {
                "task_id": f"{goal_id}_統合テスト実行_{timestamp}_01",
                "parent_goal_id": goal_id,
                "description": (
                    "F1-F10の統合テストを実行し、全機能が正常に動作することを確認する。"
                    "tests/system_protection/test_core_functions.pyを実行し、"
                    "85%以上の成功率を確認。各機能の存在確認とナレッジシステムの動作テストを実施。"
                ),
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
                "task_id": f"{goal_id}_システム連携確認_{timestamp}_02",
                "parent_goal_id": goal_id,
                "description": (
                    "CompleteEngineUltimateにF1-F10が正しく統合されていることを確認。"
                    "各機能のメソッドが存在し、相互に連携して動作することを検証。"
                    "Google Sheets、ナレッジDB、エージェント間の連携を確認し、"
                    "agent_outputs/documentation/に詳細レポートを生成。"
                ),
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
                "task_id": f"{goal_id}_エンドツーエンド動作確認_{timestamp}_03",
                "parent_goal_id": goal_id,
                "description": (
                    "実際の運用フローをシミュレーション。"
                    "1) 新しいテストゴールを追加（F1）、"
                    "2) タスク自動実行（F2）、"
                    "3) 品質評価（F3）、"
                    "4) ナレッジ蓄積（F4）、"
                    "5) 進捗確認（F5）の一連の流れが自動で完了することを確認。"
                    "全ステップの実行ログと成果物を記録。"
                ),
                "required_role": "tester",
                "status": "pending",
                "priority": "high",
                "estimated_time": "2h",
                "dependencies": f"{goal_id}_システム連携確認_{timestamp}_02",
                "created_at": now,
                "batch_id": batch_id,
                "detail_file_path": "",
                "blank": "",
                "execution_type": "testing"
            },
            {
                "task_id": f"{goal_id}_24時間稼働準備確認_{timestamp}_04",
                "parent_goal_id": goal_id,
                "description": (
                    "24時間自律稼働システムの準備状況を最終確認。"
                    "F7（自己修復）、F8（自己進化）、F9（人間連携）、F10（健全性チェック）"
                    "が正しく動作することを確認。エラー発生時の自動修復、"
                    "学習サイクル、人間への通知機能が正常に機能することを検証。"
                    "MD/にチェックリストと確認結果を記録。"
                ),
                "required_role": "developer",
                "status": "pending",
                "priority": "high",
                "estimated_time": "1h",
                "dependencies": f"{goal_id}_エンドツーエンド動作確認_{timestamp}_03",
                "created_at": now,
                "batch_id": batch_id,
                "detail_file_path": "",
                "blank": "",
                "execution_type": "documentation"
            }
        ]
        
        return tasks
    
    def add_tasks_to_sheet(self, tasks: List[Dict[str, Any]]) -> bool:
        """タスクをGoogle Sheetsに追加（既存システム活用）"""
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
                
                # Google Sheets APIで追加
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
            return False
    
    def auto_generate_if_needed(self) -> Dict[str, Any]:
        """必要に応じて自動生成"""
        print("━" * 60)
        print("🤖 自動タスク生成チェック")
        print("━" * 60)
        print()
        
        pending_count = self.check_pending_tasks()
        
        # エラー時（-1）は生成しない
        if pending_count < 0:
            print("\n⚠️  タスク確認に失敗しました。安全のため生成をスキップします。")
            return {
                "generated": False,
                "error": "タスク確認失敗"
            }
        
        if pending_count == 0:
            print("\n📋 pendingタスクが0個です。")
            print("🔧 システム統合・動作確認タスクを自動生成します...")
            print()
            
            tasks = self.generate_integration_tasks()
            
            print("【生成タスク】")
            for i, task in enumerate(tasks, 1):
                print(f"  {i}. {task['task_id']}")
                print(f"     優先度: {task['priority']} | 時間: {task['estimated_time']}")
                print(f"     目的: {task['description'][:80]}...")
                print()
            
            success = self.add_tasks_to_sheet(tasks)
            
            if success:
                print("✅ タスク自動生成完了")
                print("📝 これらのタスクは次のサイクルで自動実行されます")
            
            return {
                "generated": True,
                "task_count": len(tasks),
                "success": success,
                "tasks": [t["task_id"] for t in tasks]
            }
            
        else:
            print(f"\n📋 {pending_count}個のpendingタスクが存在します。")
            print("⏭️  タスク自動生成はスキップします。")
            return {
                "generated": False,
                "pending_count": pending_count,
                "message": "既にpendingタスクが存在"
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
            
            print("\n  🎯 次のアクション:")
            print("    bash start_pending_tasks.sh --limit 4")
            print("    または")
            print("    bash sh/run_autonomous_24h_v3.sh")
            
        elif result.get("error"):
            print(f"  ⚠️  エラー: {result['error']}")
            
        else:
            print(f"  ⏭️  タスク自動生成: スキップ")
            if "pending_count" in result:
                print(f"  📋 既存pending: {result['pending_count']}個")
        
        print()
        return 0 if result.get("generated") or result.get("pending_count", 0) > 0 else 1
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

PYTHON

echo "✅ 最終版作成: agents/auto_task_generator.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 動作確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 agents/auto_task_generator.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 最終修正完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 改善内容:"
echo "  1. ❌ エラーメッセージを排除"
echo "  2. ✅ Google Sheets APIを直接使用（最も確実）"
echo "  3. ✅ 既存システムと完全統合"
echo "  4. ✅ 4個の統合タスクを生成"
echo "  5. ✅ 依存関係を正しく設定"
echo ""
echo "📝 生成されるタスク:"
echo "  1. 統合テスト実行（F1-F10検証）"
echo "  2. システム連携確認（統合レポート）"
echo "  3. エンドツーエンド動作確認（全フロー）"
echo "  4. 24時間稼働準備確認（最終チェック）"
echo ""
echo "🎯 次のステップ:"
echo "  bash start_pending_tasks.sh --limit 4"
echo ""

