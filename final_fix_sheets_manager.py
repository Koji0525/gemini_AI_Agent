# SheetsManagerの最終修正
import re

# バックアップ作成
import shutil
shutil.copy2('tools/sheets_manager.py', 'tools/sheets_manager_final_backup.py')

with open('tools/sheets_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 問題の根本原因：不正な文字列パターンを完全に削除
# 行末の不正な文字列を検出して削除
lines = content.split('\n')
clean_lines = []

i = 0
while i < len(lines):
    line = lines[i]
    
    # 問題のパターンを検出
    if '!{cell_range} = {value}")' in line and not line.strip().startswith('self.logger'):
        print(f"❌ 不正な行を削除: {i+1}")
        # この行をスキップ
        i += 1
        continue
    
    # 重複したupdate_cellメソッドの開始を検出
    if 'def update_cell(' in line and i > 0 and 'def update_cell(' in '\n'.join(clean_lines[-10:]):
        print(f"❌ 重複メソッドを削除: {i+1}")
        # このメソッドブロックをスキップ
        while i < len(lines) and (lines[i].strip() or 'def ' not in lines[i]):
            i += 1
        continue
    
    clean_lines.append(line)
    i += 1

# クリーンな内容を結合
clean_content = '\n'.join(clean_lines)

# 正しいupdate_cellメソッドが1つだけあるか確認
update_cell_count = clean_content.count('def update_cell(')
if update_cell_count == 0:
    print("⚠️ update_cellメソッドがありません - 追加します")
    # 正しいメソッドを追加
    correct_method = '''
    def update_cell(self, sheet_name: str, cell_range: str, value=None, **kwargs):
        """指定したセルを更新する"""
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
    # クラス内の適切な位置に追加
    class_start = clean_content.find('class GoogleSheetsManager:')
    if class_start != -1:
        # 最初のメソッドの前に追加
        first_method = clean_content.find('def ', class_start)
        if first_method != -1:
            clean_content = clean_content[:first_method] + correct_method + '\n\n    ' + clean_content[first_method:]
            print("✅ update_cellメソッドを追加しました")
elif update_cell_count > 1:
    print(f"❌ 重複するupdate_cellメソッド: {update_cell_count}個")
    # 1つだけ残して他を削除
    clean_content = re.sub(r'(def update_cell\([^)]+\):[^{]+{.*?})(?=.*def update_cell)', '', clean_content, flags=re.DOTALL)

# 最終保存
with open('tools/sheets_manager.py', 'w', encoding='utf-8') as f:
    f.write(clean_content)

print("✅ SheetsManagerの最終修正完了")
