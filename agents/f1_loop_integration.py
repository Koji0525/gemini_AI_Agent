"""
F1タスク分解のループ統合
pendingタスクが0の場合、自動的にタスク生成
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.smart_task_selector import SmartTaskSelector
from agents.auto_task_generator import AutoTaskGeneratorV2

class F1LoopIntegration:
    """F1タスク分解のループ統合"""
    
    def __init__(self, sheets_manager=None):
        self.sheets = sheets_manager
        self.task_selector = SmartTaskSelector(sheets_manager)
        self.task_generator = AutoTaskGeneratorV2(sheets_manager)
        
    def ensure_tasks_available(self) -> bool:
        """タスクが利用可能であることを保証"""
        print("━" * 60)
        print("🔄 F1: タスク可用性チェック")
        print("━" * 60)
        print()
        
        # pendingタスクを確認
        pending_tasks = self.task_selector.get_pending_tasks()
        
        if len(pending_tasks) == 0:
            print("⚠️  pendingタスクが0個です")
            print("🔧 F1: 自動タスク生成を起動します...")
            print()
            
            # 自動タスク生成
            result = self.task_generator.auto_generate_if_needed()
            
            if result.get('generated') and result.get('success'):
                print("✅ F1: 高品質タスクの生成に成功しました")
                print(f"   生成数: {result.get('task_count')}個")
                return True
            else:
                print("❌ F1: タスク生成に失敗しました")
                return False
        else:
            print(f"✅ {len(pending_tasks)}個のpendingタスクが存在します")
            return True

def main():
    """メイン実行"""
    from tools.sheets_manager import GoogleSheetsManager
    
    sheets = GoogleSheetsManager()
    f1_loop = F1LoopIntegration(sheets)
    
    success = f1_loop.ensure_tasks_available()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

