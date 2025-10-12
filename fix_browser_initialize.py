#!/usr/bin/env python3
"""
SafeBrowserManager の initialize を setup_browser に修正
"""

with open('browser_control/safe_browser_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# initialize() → setup_browser() に変更
content = content.replace(
    'await cls._controller.initialize()',
    'await cls._controller.setup_browser()'
)

with open('browser_control/safe_browser_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ SafeBrowserManager を修正しました")
print("   initialize() → setup_browser() に変更")
