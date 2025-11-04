# SheetsManagerを完全に修正
import re

with open('tools/sheets_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("ファイルを解析中...")

# 問題のパターンを特定 - 不正な文字列や重複メソッドを検出
problem_patterns = [
    r'!{cell_range} = {value}"\)\s*\n',  # 不正な文字列
    r'def update_cell\([^)]+\):[^{]+{.*?def update_cell',  # 重複メソッド
]

for pattern in problem_patterns:
    if re.search(pattern, content, re.DOTALL):
        print(f"❌ 問題パターン発見: {pattern}")
        # 問題部分を削除
        content = re.sub(pattern, '', content, flags=re.DOTALL)

# update_cellメソッドを完全に正規化
# まずすべてのupdate_cellメソッドを削除
content = re.sub(r'def update_cell\([^)]+\):[^{]+{.*?}\s*', '', content, flags=re.DOTALL)

# 正しいupdate_cellメソッドを追加
correct_method = '''
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

# メソッドを追加する適切な位置を探す (write_rangeの後)
insert_point = content.find('def write_range(')
if insert_point != -1:
    # write_rangeメソッドの終わりを探す
    method_end = content.find('\n\n', insert_point)
    if method_end == -1:
        method_end = content.find('\nclass ', insert_point)
    if method_end == -1:
        method_end = len(content)
    
    content = content[:method_end] + correct_method + content[method_end:]
    print("✅ update_cellメソッドを正常な位置に追加しました")
else:
    print("❌ 挿入位置が見つかりません - 手動での修正が必要")

# 最終的な内容を保存
with open('tools/sheets_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ SheetsManagerの修正完了")
