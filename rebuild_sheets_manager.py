# SheetsManagerを確実に修正
import re

with open('tools/sheets_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# update_cellメソッドを完全に削除して再追加
# まず既存のupdate_cellメソッドを削除
content = re.sub(r'def update_cell\([^)]+\):[^{]+{.*?}\n', '', content, flags=re.DOTALL)

# クラスの適切な位置に正しいupdate_cellメソッドを追加
# write_rangeメソッドの後に追加するのが安全
insert_point = content.find('def write_range(')
if insert_point != -1:
    # write_rangeメソッドの終了位置を探す
    method_end = content.find('\n\n', insert_point)  # 空行を探す
    if method_end == -1:
        method_end = content.find('\nclass ', insert_point)
    if method_end == -1:
        method_end = len(content)
    
    new_method = '''

    def update_cell(self, sheet_name: str, cell_range: str, value=None, **kwargs):
        """指定したセルを更新する
        
        Args:
            sheet_name: シート名
            cell_range: セル範囲 (例: 'A1')
            value: 設定する値
            **kwargs: 互換性のための追加引数
        """
        # cell_addressが指定された場合はcell_rangeとして使用
        if 'cell_address' in kwargs:
            cell_range = kwargs['cell_address']
        
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id).worksheet(sheet_name)
            sheet.update(cell_range, [[value]])
            self.logger.info(f"📊 セル更新完了: {sheet_name}!{cell_range} = {value}")
            return True
        except Exception as e:
            self.logger.error(f"❌ セル更新失敗: {sheet_name}!{cell_range} - {e}")
            return False
'''

    content = content[:method_end] + new_method + content[method_end:]
    
    with open('tools/sheets_manager.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ update_cellメソッドを確実に追加しました")
else:
    print("❌ 挿入位置が見つかりません")

