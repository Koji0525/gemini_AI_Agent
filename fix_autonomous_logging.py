#!/usr/bin/env python3
"""autonomous_system.py のログ設定を調整"""
from pathlib import Path

file = Path('autonomous_system.py')
content = file.read_text()

# ログレベルをINFOに変更（現在おそらくDEBUG）
content = content.replace(
    'level=logging.DEBUG',
    'level=logging.INFO'
)

content = content.replace(
    'logging.DEBUG',
    'logging.INFO'
)

# フォーマットをシンプルに
old_format = "format='[%(asctime)s] [%(levelname)s] %(message)s'"
new_format = "format='%(message)s'"  # タイムスタンプを削除

if old_format in content:
    content = content.replace(old_format, new_format)

file.write_text(content)
print("✅ autonomous_system.py のログ設定を調整")
