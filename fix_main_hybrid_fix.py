#!/usr/bin/env python3
"""
main_hybrid_fix.py の構文エラーを修正
"""
import re

# ファイルを読み込む
with open('main_hybrid_fix.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1行目の不正なインデントを削除
lines = content.split('\n')
if lines and lines[0].startswith(' '):
    # 先頭の空白を削除
    lines[0] = lines[0].lstrip()
    print(f"✅ 1行目のインデントを修正")

# バックアップ
with open('main_hybrid_fix.py.backup', 'w', encoding='utf-8') as f:
    f.write(content)
print(f"💾 バックアップ作成: main_hybrid_fix.py.backup")

# 修正版を保存
with open('main_hybrid_fix.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f"✅ main_hybrid_fix.py を修正")

# 確認
print("\n📝 修正後の最初の5行:")
with open('main_hybrid_fix.py', 'r') as f:
    for i, line in enumerate(f, 1):
        if i <= 5:
            print(f"  {i}: {repr(line)}")
