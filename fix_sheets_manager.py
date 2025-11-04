# SheetsManagerのupdate_cellメソッドを確実に追加
import re

with open('tools/sheets_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# update_cellメソッドが既にあるかチェック
if 'def update_cell' in content:
    print("✅ update_cellメソッド: 既に存在します")
else:
    # クラス内の適切な位置にメソッドを追加
    # 既存のメソッドの後に追加するのが安全
    
    # メソッドを追加する位置を探す (write_rangeメソッドの後)
    insert_pattern = r'(def write_range\([^)]+\):[^{]+{[^}]+})'
    match = re.search(insert_pattern, content, re.DOTALL)
    
    if match:
        insert_point = match.end()
        new_method = '''

    def update_cell(self, sheet_name: str, cell_range: str, value):
        """指定したセルを更新する
        
        Args:
            sheet_name: シート名
            cell_range: セル範囲 (例: 'A1')
            value: 設定する値
        """
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id).worksheet(sheet_name)
            sheet.update(cell_range, [[value]])
            self.logger.info(f"📊 セル更新完了: {sheet_name}!{cell_range} = {value}")
            return True
        except Exception as e:
            self.logger.error(f"❌ セル更新失敗: {sheet_name}!{cell_range} - {e}")
            return False
'''
        content = content[:insert_point] + new_method + content[insert_point:]
        
        with open('tools/sheets_manager.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ update_cellメソッドを追加しました")
    else:
        print("❌ 追加位置が見つかりません - 手動で追加してください")
        
        # ファイル末尾に追加するフォールバック
        if 'class GoogleSheetsManager' in content:
            class_end = content.find('class GoogleSheetsManager') + len('class GoogleSheetsManager')
            # クラスの終わりを探す (次のクラスまたはファイル終端)
            next_class = content.find('class ', class_end)
            if next_class == -1:
                next_class = len(content)
            
            # クラス内の最後のメソッドの後に追加
            content = content[:next_class] + '''
    def update_cell(self, sheet_name: str, cell_range: str, value):
        """指定したセルを更新する"""
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id).worksheet(sheet_name)
            sheet.update(cell_range, [[value]])
            self.logger.info(f"📊 セル更新完了: {sheet_name}!{cell_range} = {value}")
            return True
        except Exception as e:
            self.logger.error(f"❌ セル更新失敗: {sheet_name}!{cell_range} - {e}")
            return False
''' + content[next_class:]
            
            with open('tools/sheets_manager.py', 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ ファイル末尾にupdate_cellメソッドを追加しました")
