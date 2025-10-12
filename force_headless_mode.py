#!/usr/bin/env python3
"""
ブラウザを headless モードで起動するように修正
"""

# browser_lifecycle.py を修正
with open('browser_control/browser_lifecycle.py', 'r', encoding='utf-8') as f:
    content = f.read()

# headless=False を headless=True に変更
content = content.replace('headless=False', 'headless=True')
content = content.replace('headless = False', 'headless = True')

# もし headless の設定がなければ、launch_persistent_context に追加
if 'headless' not in content:
    # launch_persistent_context の引数に headless=True を追加
    content = content.replace(
        'playwright.chromium.launch_persistent_context(',
        'playwright.chromium.launch_persistent_context(\n            headless=True,  # Codespaces 対応\n'
    )

with open('browser_control/browser_lifecycle.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ browser_lifecycle.py を headless モードに修正しました")
