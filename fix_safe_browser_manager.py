#!/usr/bin/env python3
"""
SafeBrowserManager の BrowserController 初期化を修正
"""
from pathlib import Path

# ファイルを読み込み
with open('browser_control/safe_browser_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修正: download_folder を指定
# BrowserController() → BrowserController(download_folder="downloads")
content = content.replace(
    'cls._controller = BrowserController()',
    'cls._controller = BrowserController(download_folder="downloads")'
)

# 保存
with open('browser_control/safe_browser_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ SafeBrowserManager を修正しました")
print("   BrowserController(download_folder='downloads') を追加")
