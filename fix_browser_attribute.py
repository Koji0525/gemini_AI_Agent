#!/usr/bin/env python3
"""
safe_browser_manager.py の browser 属性チェックを修正
"""

with open('browser_control/safe_browser_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# browser 属性チェックを context 属性チェックに変更
# または、このチェックを削除
content = content.replace(
    'if cls._controller.browser is None:',
    'if cls._controller.context is None:'
)

# または、チェック自体を削除する場合
# content = content.replace(
#     '''            if cls._controller.browser is None:
#                 logger.error("ブラウザ初期化失敗")
#                 cls._controller = None
#                 return None''',
#     '            # ブラウザ初期化チェック（context で確認）'
# )

with open('browser_control/safe_browser_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ browser 属性チェックを修正しました")
