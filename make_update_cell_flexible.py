# update_cellメソッドを柔軟な引数に対応させる
import re

with open('tools/sheets_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 現在のupdate_cellメソッドを検索
current_method = re.search(r'def update_cell\([^)]+\):[^{]+{[^}]+}', content, re.DOTALL)

if current_method:
    # 柔軟なバージョンに置き換え
    flexible_method = '''
    def update_cell(self, sheet_name: str, cell_range: str, value=None, **kwargs):
        """指定したセルを更新する（柔軟な引数対応）
        
        Args:
            sheet_name: シート名
            cell_range: セル範囲 (例: 'A1')
            value: 設定する値
            **kwargs: 互換性のための追加引数 (cell_addressなど)
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

    content = content.replace(current_method.group(0), flexible_method)
    
    with open('tools/sheets_manager.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ update_cellメソッドを柔軟な引数に対応させました")
else:
    print("❌ update_cellメソッドが見つかりません")
