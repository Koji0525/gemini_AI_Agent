#!/usr/bin/env python3
"""
SafeBrowserManager の Path インポートと修正
"""

# ファイルを読み込み
with open('browser_control/safe_browser_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Path をインポートに追加（まだなければ）
if 'from pathlib import Path' not in content:
    # import 文の後に追加
    content = content.replace(
        'import asyncio',
        'import asyncio\nfrom pathlib import Path'
    )
    print("✅ Path のインポートを追加")

# BrowserController の引数を Path オブジェクトに修正
content = content.replace(
    'cls._controller = BrowserController(download_folder="downloads")',
    'cls._controller = BrowserController(download_folder=Path("downloads"))'
)

# 保存
with open('browser_control/safe_browser_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ SafeBrowserManager を完全に修正しました")
print("   download_folder=Path('downloads') に変更")
