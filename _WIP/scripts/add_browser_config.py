#!/usr/bin/env python3
"""
browser_config の定義を追加
"""

with open('browser_control/browser_lifecycle.py', 'r', encoding='utf-8') as f:
    content = f.read()

# launch_persistent_context の直前に browser_config の定義を追加
old_code = '''            # ブラウザ起動（位置とサイズ指定）
            self.context = await self.playwright.chromium.launch_persistent_context('''

new_code = '''            # ブラウザ起動（位置とサイズ指定）
            # BROWSER_CONFIG から headless を除外（明示的に指定するため）
            browser_config = {k: v for k, v in config.BROWSER_CONFIG.items() if k != 'headless'}
            
            self.context = await self.playwright.chromium.launch_persistent_context('''

content = content.replace(old_code, new_code)

with open('browser_control/browser_lifecycle.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ browser_config の定義を追加しました")
