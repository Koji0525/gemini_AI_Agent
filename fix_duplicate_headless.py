#!/usr/bin/env python3
"""
重複した headless を修正
**config.BROWSER_CONFIG を展開する前に headless を除外
"""

with open('browser_control/browser_lifecycle.py', 'r', encoding='utf-8') as f:
    content = f.read()

# **config.BROWSER_CONFIG の前に headless を除外する処理を追加
old_code = '''            self.context = await self.playwright.chromium.launch_persistent_context(
            headless=True,  # Codespaces 対応
                user_data_dir=str(self.browser_data_dir),
                viewport={'width': window_width, 'height': window_height},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                accept_downloads=True,
                ignore_https_errors=True,
                no_viewport=False,
                **config.BROWSER_CONFIG
            )'''

new_code = '''            # BROWSER_CONFIG から headless を除外（明示的に指定するため）
            browser_config = {k: v for k, v in config.BROWSER_CONFIG.items() if k != 'headless'}
            
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.browser_data_dir),
                headless=True,  # Codespaces 対応（常に headless）
                viewport={'width': window_width, 'height': window_height},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                accept_downloads=True,
                ignore_https_errors=True,
                no_viewport=False,
                **browser_config
            )'''

content = content.replace(old_code, new_code)

with open('browser_control/browser_lifecycle.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ browser_lifecycle.py を修正しました")
print("   - BROWSER_CONFIG から headless を除外")
print("   - headless=True を明示的に指定")
