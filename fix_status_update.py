#!/usr/bin/env python3
"""ステータス更新問題の修正"""

import re

def fix_status_update_issue():
    # complete_engine_ultimate.py を修正
    with open('agents/complete_engine_ultimate.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ステータス更新部分を検索
    if 'def _update_task_status' not in content:
        print("❌ _update_task_status メソッドが見つかりません - 追加します")
        
        # メソッドを追加する位置を探す（クラスの最後）
        class_end = content.find('class CompleteEngineUltimate')
        if class_end == -1:
            print("❌ CompleteEngineUltimate クラスが見つかりません")
            return False
        
        # クラスの終了位置を探す
        class_content = content[class_end:]
        method_pattern = r'(def \w+\(.*?\):.*?)(?=def|\Z)'
        methods = list(re.finditer(method_pattern, class_content, re.DOTALL))
        
        if methods:
            last_method = methods[-1]
            insert_pos = class_end + last_method.end()
            
            # 新しいメソッドを追加
            new_method = '''
    def _update_task_status(self, task_id: str, new_status: str) -> bool:
        """タスクステータスを更新する"""
        try:
            print(f"🔄 ステータス更新: {task_id} -> {new_status}")
            
            # pm_tasksシートから対象タスクを検索
            tasks = self.safe_sheets.safe_read('pm_tasks!A2:Z1000', default=[])
            
            for i, task in enumerate(tasks):
                if task[0] == task_id:
                    # ステータス列（E列）を更新
                    range_name = f'pm_tasks!E{i+2}'
                    success = self.safe_sheets.safe_update(range_name, [[new_status]])
                    
                    if success:
                        print(f"✅ ステータス更新成功: {task_id} -> {new_status}")
                        return True
                    else:
                        print(f"❌ ステータス更新失敗: {task_id}")
                        return False
            
            print(f"⚠️ タスクが見つかりません: {task_id}")
            return False
            
        except Exception as e:
            print(f"❌ ステータス更新エラー: {e}")
            return False
'''
            
            # メソッドを追加
            content = content[:insert_pos] + new_method + content[insert_pos:]
            print("✅ _update_task_status メソッドを追加")
        else:
            print("❌ メソッドの追加位置が見つかりません")
            return False
    
    # execute_task メソッド内のステータス更新を修正
    if 'success = self._update_task_status' not in content:
        print("🔧 execute_task 内のステータス更新を修正")
        
        # 既存のステータス更新部分を検索して置き換え
        old_update_pattern = r'INFO:tools\.sheets_manager:✅ 更新成功: pm_tasks!E\d+\s*\n\s*✅ ステータス更新: [^\n]+ → completed'
        new_update_code = '''            # ステータス更新
            update_success = self._update_task_status(task_id, "completed")
            if not update_success:
                print("❌ ステータス更新に失敗しました")'''
        
        if re.search(old_update_pattern, content):
            content = re.sub(old_update_pattern, new_update_code, content)
            print("✅ ステータス更新コードを置換")
        else:
            # 既存の更新コードが見つからない場合は追加
            task_complete_pattern = r'(✅ タスク実行完了\n)'
            if re.search(task_complete_pattern, content):
                content = re.sub(
                    task_complete_pattern, 
                    r'\1\n            # ステータス更新\n            update_success = self._update_task_status(task_id, "completed")\n            if not update_success:\n                print("❌ ステータス更新に失敗しました")\n', 
                    content
                )
                print("✅ ステータス更新コードを追加")
            else:
                print("❌ タスク完了位置が見つかりません")
    
    # 修正を保存
    with open('agents/complete_engine_ultimate.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ ステータス更新問題を修正しました")
    return True

if __name__ == "__main__":
    fix_status_update_issue()
