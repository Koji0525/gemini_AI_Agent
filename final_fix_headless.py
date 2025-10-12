#!/usr/bin/env python3
"""
最終修正: headless の重複を完全に解消
"""

with open('browser_control/browser_lifecycle.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines, 1):
    # 58行目付近の重複した headless 行を削除
    if i == 58 and 'headless=True' in line:
        print(f"❌ 削除: 行{i}: {line.strip()}")
        continue
    new_lines.append(line)

with open('browser_control/browser_lifecycle.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ 重複行を削除しました")
