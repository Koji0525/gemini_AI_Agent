#!/usr/bin/env python3
"""
BrowserControllerの初期化修正スクリプト
"""
import os
import re


def fix_browser_initialization(file_path):
    """ファイル内のBrowserController初期化を修正"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 間違った初期化パターンを修正
    old_pattern = r"browser = BrowserController\(\)\s*\n\s*await browser\.initialize\(\)"
    new_pattern = "browser = BrowserController()"

    new_content = re.sub(old_pattern, new_pattern, content)

    if new_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ 修正完了: {file_path}")
        return True
    else:
        print(f"✅ 修正不要: {file_path}")
        return False


# 修正対象ファイル
files_to_fix = [
    "test_integrated_system.py",
    "test_wordpress_agents.py",
    "agents/pm_agent/design_integrated_pm.py",
    "run_wordpress_auto_setup.py",
    "agents/wordpress/wp_orchestrator.py",
]

for file in files_to_fix:
    if os.path.exists(file):
        fix_browser_initialization(file)
    else:
        print(f"⚠️ ファイルが存在しません: {file}")

print("🎉 BrowserController初期化の修正が完了しました")
