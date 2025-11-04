# SheetsManagerにupdate_cellメソッドを追加
import re

with open('tools/sheets_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# update_cellメソッドが既にあるかチェック
if 'def update_cell(' in content:
    print("✅ update_cellメソッド: 既に存在します")
else:
    # メソッドを追加する位置を探す（他のセル操作メソッドの近く）
    insert_point = content.find('def update_task_status(')
    if insert_point == -1:
        insert_point = content.find('def get_active_tasks(')
    
    if insert_point != -1:
        # update_cellメソッドを追加
        new_method = '''
    def update_cell(self, sheet_name: str, cell_range: str, value: any):
        """指定したセルを更新する
        
        Args:
            sheet_name: シート名
            cell_range: セル範囲 (例: 'A1', 'B2:C5')
            value: 設定する値
        """
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id).worksheet(sheet_name)
            sheet.update(cell_range, [[value]])
            logger.info(f"📊 セル更新完了: {sheet_name}!{cell_range} = {value}")
            return True
        except Exception as e:
            logger.error(f"❌ セル更新失敗: {sheet_name}!{cell_range} - {e}")
            return False
'''

        # メソッドを挿入
        content = content[:insert_point] + new_method + content[insert_point:]
        
        with open('tools/sheets_manager.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ update_cellメソッドを追加しました")
    else:
        print("❌ メソッド追加位置が見つかりませんでした")
