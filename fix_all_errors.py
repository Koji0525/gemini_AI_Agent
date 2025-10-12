#!/usr/bin/env python3
"""
すべてのエラーを自動修正
"""
from pathlib import Path
import re

print("=" * 80)
print("🔧 自動修正システム起動")
print("=" * 80)

# 1. wp_agent.py 修正
print("\n1️⃣ wp_agent.py を修正中...")
wp_agent_path = Path("wordpress/wp_agent.py")

with open(wp_agent_path, 'r', encoding='utf-8') as f:
    wp_content = f.read()

# バックアップ
backup = wp_agent_path.with_suffix('.py.auto_backup')
with open(backup, 'w', encoding='utf-8') as f:
    f.write(wp_content)

# 124-127行目の修正
lines = wp_content.split('\n')
fixed_lines = []
skip_count = 0

for i, line in enumerate(lines):
    if skip_count > 0:
        skip_count -= 1
        continue
    
    if 'self.post_editor = WordPressPostEditor(' in line and 'browser_controller' in lines[i+1]:
        # 新しいコードに置き換え
        fixed_lines.append('            self.post_editor = WordPressPostEditor(')
        fixed_lines.append("                wp_url=self.wp_credentials.get('wp_url', '') if self.wp_credentials else '',")
        fixed_lines.append('                sheets_manager=None')
        fixed_lines.append('            )')
        skip_count = 2  # 次の2行をスキップ
        print(f"   ✅ {i+1}行目を修正")
    else:
        fixed_lines.append(line)

with open(wp_agent_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print(f"   💾 バックアップ: {backup}")

# 2. test_tasks_practical.py 修正
print("\n2️⃣ test_tasks_practical.py を修正中...")
test_path = Path("test_tasks_practical.py")

with open(test_path, 'r', encoding='utf-8') as f:
    test_content = f.read()

# sys import を追加（まだなければ）
if 'import sys' not in test_content:
    lines = test_content.split('\n')
    # import asyncio の後に追加
    for i, line in enumerate(lines):
        if 'import asyncio' in line:
            lines.insert(i + 1, 'import sys')
            print(f"   ✅ sys import を追加")
            break
    
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

print("\n" + "=" * 80)
print("🎉 自動修正完了！")
print("=" * 80)
print("\n🔄 テスト再実行中...")
