# SheetsManagerのシンタックスエラーを修正
with open('tools/sheets_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 問題の行を修正（文字列を正しく閉じる）
content = content.replace(
    '!{cell_range} = {value}")',  # 誤った行
    '!{cell_range} = {value}")'   # 修正後の行（実際には同じに見えるが、隠れた文字がある可能性）
)

# より確実にupdate_cellメソッド全体を修正
import re

# update_cellメソッドを検索
method_pattern = r'def update_cell\([^)]+\):[^{]+{.*?}'
matches = re.findall(method_pattern, content, re.DOTALL)

if matches:
    # メソッドを正しい形式で再定義
    correct_method = '''
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

    # 最初のupdate_cellメソッドを置換
    content = content.replace(matches[0], correct_method)
    
    with open('tools/sheets_manager.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ update_cellメソッドを完全に再定義しました")
else:
    print("❌ update_cellメソッドが見つかりません")

