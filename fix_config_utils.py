#!/usr/bin/env python3
"""
config_utils.py の setup_optimized_logging を修正
"""

import re

# ファイルを読み込み
with open('configuration/config_utils.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修正1: 関数定義に引数を追加
content = content.replace(
    'def setup_optimized_logging():',
    'def setup_optimized_logging(logger_name=None):'
)

# 修正2: logger の取得を修正
content = content.replace(
    '    # ルートロガー\n    logger = logging.getLogger()',
    '    # ルートロガー\n    logger = logging.getLogger(logger_name) if logger_name else logging.getLogger()'
)

# 修正3: return文を追加（関数の最後）
# まず、関数の終わりを見つけて return logger を追加
lines = content.split('\n')
new_lines = []
in_function = False
indent_level = 0

for i, line in enumerate(lines):
    if 'def setup_optimized_logging' in line:
        in_function = True
        indent_level = len(line) - len(line.lstrip())
    
    new_lines.append(line)
    
    # 関数内で、ハンドラ追加の後に return を追加
    if in_function and 'logger.addHandler(file_handler)' in line:
        # 次の行が関数の外（インデントが同じか少ない）なら return を追加
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            next_indent = len(next_line) - len(next_line.lstrip()) if next_line.strip() else 0
            if next_indent <= indent_level or not next_line.strip():
                new_lines.append('    return logger')
                in_function = False

content = '\n'.join(new_lines)

# ファイルに書き込み
with open('configuration/config_utils.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ configuration/config_utils.py を修正しました")
