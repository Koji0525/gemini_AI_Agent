#!/usr/bin/env python3
"""
ブラウザ環境セットアップテスト
全ての依存関係と基本機能を確認
"""

import asyncio
import sys
from pathlib import Path

async def test_browser_setup():
    """ブラウザセットアップの完全テスト"""
    
    print("🧪 ブラウザ環境テスト開始")
    print("=" * 60)
    
    # 1. Playwrightインポートテスト
    print("\n📦 Test 1/6: Playwright インポート")
    try:
        from playwright.async_api import async_playwright
        print("   ✅ Playwright インポート成功")
    except ImportError as e:
        print(f"   ❌ Playwright インポート失敗: {e}")
        return False
    
    # 2. 環境変数確認
    print("\n🔍 Test 2/6: 環境変数確認")
    import os
    display = os.environ.get('DISPLAY')
    if display:
        print(f"   ✅ DISPLAY設定済み: {display}")
    else:
        print("   ⚠️ DISPLAY未設定、設定中...")
        os.environ['DISPLAY'] = ':1'
        print(f"   ✅ DISPLAY設定: :1")
    
    # 3. ディレクトリ確認
    print("\n📁 Test 3/6: ディレクトリ構造")
    required_dirs = [
        'browser_data',
        'temp_workspace/downloads',
        'agent_outputs/pm',
        'logs/browser'
    ]
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"   ✅ {dir_path}")
        else:
            print(f"   ⚠️ {dir_path} - 作成中...")
            path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ {dir_path} 作成完了")
    
    # 4. ブラウザ起動テスト
    print("\n🌐 Test 4/6: ブラウザ起動テスト")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            print("   ✅ Chromium起動成功")
            
            context = await browser.new_context(
                viewport={'width': 1150, 'height': 650}
            )
            print("   ✅ コンテキスト作成成功")
            
            page = await context.new_page()
            print("   ✅ ページ作成成功")
            
            # 5. ナビゲーションテスト
            print("\n🔗 Test 5/6: ナビゲーションテスト")
            await page.goto('https://www.google.com', timeout=30000)
            title = await page.title()
            print(f"   ✅ Google アクセス成功: {title}")
            
            # 6. スクリーンショットテスト
            print("\n📸 Test 6/6: スクリーンショット保存")
            screenshot_path = Path('logs/browser/test_screenshot.png')
            await page.screenshot(path=str(screenshot_path))
            print(f"   ✅ スクリーンショット保存: {screenshot_path}")
            
            await browser.close()
            print("   ✅ ブラウザクローズ成功")
            
    except Exception as e:
        print(f"   ❌ ブラウザテスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ 全テスト完了！環境は正常に動作しています")
    print("=" * 60)
    return True

if __name__ == "__main__":
    result = asyncio.run(test_browser_setup())
    sys.exit(0 if result else 1)
