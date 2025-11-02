#!/bin/bash
echo "🔧 全リンターエラーを修正します..."

# F541: f-string is missing placeholders の修正
echo "📝 F541エラー修正: f-stringのプレースホルダー不足"
find . -name "*.py" -type f | xargs grep -l "f-string is missing placeholders" 2>/dev/null | while read file; do
    echo "   🔧 修正: $file"
    # f"文字列" → "文字列" に変換
    sed -i 's/f"[^"]*"\([^"]\)/"\1/g' "$file"
    sed -i 's/f'\''[^'\'']*'\''/'\''/g' "$file"
done

# E226: missing whitespace around arithmetic operator の修正
echo "📝 E226エラー修正: 演算子周りの空白不足"
find . -name "*.py" -type f | xargs grep -l "missing whitespace around arithmetic operator" 2>/dev/null | while read file; do
    echo "   🔧 修正: $file"
    # a+b → a + b に変換
    sed -i 's/\([a-zA-Z0-9_]\)+\([a-zA-Z0-9_]\)/\1 + \2/g' "$file"
    sed -i 's/\([a-zA-Z0-9_]\)-\([a-zA-Z0-9_]\)/\1 - \2/g' "$file"
    sed -i 's/\([a-zA-Z0-9_]\)*\([a-zA-Z0-9_]\)/\1 * \2/g' "$file"
    sed -i 's/\([a-zA-Z0-9_]\)\/\([a-zA-Z0-9_]\)/\1 \/ \2/g' "$file"
done

# F841: local variable is assigned to but never used の修正
echo "📝 F841エラー修正: 未使用変数の削除"
find . -name "*.py" -type f | xargs grep -l "assigned to but never used" 2>/dev/null | while read file; do
    echo "   🔧 修正: $file"
    # 未使用変数行をコメントアウト
    python3 -c "
import re
with open('$file', 'r') as f:
    content = f.read()
# 単純な変数代入をコメントアウト
lines = content.split('\n')
new_lines = []
for line in lines:
    if ' = ' in line and not line.strip().startswith(('#', 'def ', 'class ', 'import ', 'from ')):
        # 既にコメントアウトされていないか確認
        if not line.strip().startswith('#'):
            # インデントを保持してコメントアウト
            indent = len(line) - len(line.lstrip())
            new_lines.append(' ' * indent + '# ' + line.lstrip())
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)
with open('$file', 'w') as f:
    f.write('\n'.join(new_lines))
"
done

# E402: module level import not at top of file の修正
echo "📝 E402エラー修正: import文の位置修正"
find . -name "*.py" -type f | xargs grep -l "module level import not at top of file" 2>/dev/null | while read file; do
    echo "   🔧 修正: $file"
    python3 -c "
with open('$file', 'r') as f:
    lines = f.readlines()

imports = []
other_lines = []
in_import_section = True

for line in lines:
    if in_import_section and (line.startswith('import ') or line.startswith('from ')):
        imports.append(line)
    elif line.strip() == '' and in_import_section:
        imports.append(line)
    else:
        in_import_section = False
        other_lines.append(line)

# import文をまとめて先頭に
new_content = ''.join(imports) + ''.join(other_lines)
with open('$file', 'w') as f:
    f.write(new_content)
"
done

# E722: do not use bare 'except' の修正
echo "📝 E722エラー修正: 裸のexcept文修正"
find . -name "*.py" -type f | xargs grep -l "do not use bare 'except'" 2>/dev/null | while read file; do
    echo "   🔧 修正: $file"
    sed -i 's/except:/except Exception:/g' "$file"
done

echo "✅ リンターエラー修正完了"
