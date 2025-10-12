#!/usr/bin/env python3
"""
シンプルに headless の重複を解消
"""

with open('browser_control/browser_lifecycle.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 50行目の headless=True の行を削除
content = content.replace(
    '''            self.context = await self.playwright.chromium.launch_persistent_context(
            headless=True,  # Codespaces 対応
                user_data_dir=str(self.browser_data_dir),''',
    '''            # BROWSER_CONFIG から headless を除外
            browser_config = {k: v for k, v in config.BROWSER_CONFIG.items() if k != 'headless'}
            
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.browser_data_dir),'''
)

# **config.BROWSER_CONFIG を修正
content = content.replace(
    '                **config.BROWSER_CONFIG',
    '                headless=True,  # Codespaces 対応\n                **browser_config'
)

with open('browser_control/browser_lifecycle.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 修正完了")
