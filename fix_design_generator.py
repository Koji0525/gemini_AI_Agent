#!/usr/bin/env python3
"""
wp_design_generator_v01-fix_browser.py の修正スクリプト
"""
import re

with open("agents/wordpress/wp_design_generator_v01-fix_browser.py", "r", encoding="utf-8") as f:
    content = f.read()

# await browser.initialize() を削除
content = re.sub(r"\s*await browser\.initialize\(\)", "", content)

# 正しいBrowserControllerの使用方法に修正
old_test_code = '''async def test_design_generator():
    """設計図生成のテスト"""
    try:
        from browser_control.browser_controller import BrowserController
        
        print("🎨 WordPress設計図生成エージェント テスト開始")
        
        # ブラウザを初期化
        browser = BrowserController()
        
        # 設計図生成エージェントを作成
        generator = WPDesignGenerator(browser)'''

new_test_code = '''async def test_design_generator():
    """設計図生成のテスト"""
    try:
        from browser_control.browser_controller import BrowserController
        
        print("🎨 WordPress設計図生成エージェント テスト開始")
        
        # ブラウザを初期化 - 正しい方法
        browser = BrowserController()
        await browser.setup_browser()
        await browser.navigate_to_gemini()
        
        # 設計図生成エージェントを作成
        generator = WPDesignGenerator(browser)'''

content = content.replace(old_test_code, new_test_code)

with open("agents/wordpress/wp_design_generator_v01-fix_browser.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ wp_design_generator_v01-fix_browser.py を修正しました")
