#!/usr/bin/env python3
"""真の問題を修正：タスク実行失敗時のステータス管理"""

import re

def fix_task_execution_flow():
    """タスク実行フローを修正"""
    
    # 1. task_executor_enhanced.py のテンプレートエラーを修正
    with open('agents/task_executor_enhanced.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # テンプレート文字列のエスケープ問題を修正
    template_errors = [
        # 単一の } をエスケープ
        (r"f\"アイテム追加: {{item}}\"", r"f\"アイテム追加: {{item}}\""),
        (r"f\"全アイテム: {{obj.get_items()}}\"", r"f\"全アイテム: {{obj.get_items()}}\""),
    ]
    
    for old, new in template_errors:
        if old in content:
            content = content.replace(old, new)
            print(f"✅ テンプレートエラー修正: {old} → {new}")
    
    # 2. complete_engine_ultimate.py のエラーハンドリングを強化
    with open('agents/complete_engine_ultimate.py', 'r', encoding='utf-8') as f:
        engine_content = f.read()
    
    # タスク実行失敗時のステータス更新ロジックを修正
    old_execute_pattern = r'def execute_task\(.*?\):.*?try:.*?result = self\.task_executor\.execute_task\(detailed_task\).*?except Exception as e:.*?return self\._create_error_result'
    
    new_execute_logic = '''def execute_task(self, task: Dict) -> Dict:
        """タスク実行 - エラーハンドリング強化版"""
        task_id = task.get("task_id", "")
        
        try:
            print(f"🚀 タスク実行開始: {task_id}")
            
            # 詳細タスク定義の生成
            detailed_task = self._create_detailed_task_definition(task)
            
            # タスク実行
            result = self.task_executor.execute_task(detailed_task)
            
            # 実行結果の検証
            if result.get("status") == "completed":
                print(f"✅ タスク実行成功: {task_id}")
                # ステータス更新
                self._update_task_status(task_id, "completed")
                return result
            else:
                print(f"❌ タスク実行失敗: {task_id} - {result.get('error', '不明なエラー')}")
                # 失敗時のステータス更新
                self._update_task_status(task_id, "failed")
                return self._create_error_result(f"タスク実行失敗: {result.get('error', '不明なエラー')}")
                
        except Exception as e:
            print(f"❌ タスク実行例外: {task_id} - {e}")
            # 例外時のステータス更新
            self._update_task_status(task_id, "failed")
            return self._create_error_result(f"実行例外: {str(e)}")'''
    
    if re.search(old_execute_pattern, engine_content, re.DOTALL):
        engine_content = re.sub(old_execute_pattern, new_execute_logic, engine_content, flags=re.DOTALL)
        print("✅ タスク実行フローを修正")
    else:
        print("⚠️ 既存のexecute_taskメソッドが見つかりません - 新しいロジックで上書き")
    
    # ファイル保存
    with open('agents/task_executor_enhanced.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    with open('agents/complete_engine_ultimate.py', 'w', encoding='utf-8') as f:
        f.write(engine_content)
    
    print("🎯 真の問題を修正しました")
    return True

if __name__ == "__main__":
    fix_task_execution_flow()
