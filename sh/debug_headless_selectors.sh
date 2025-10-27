#!/bin/bash
set -e

echo "=========================================="
echo "🔍 ヘッドレスモードでのページ診断"
echo "=========================================="

export DISPLAY=:1

DISPLAY=:1 python3 << 'DEBUG_PY'
import asyncio
from browser_control.browser_controller import BrowserController

async def debug_page():
    print("\n🎯 ページ構造の詳細診断")
    
    async with BrowserController(download_folder="./downloads") as browser:
        print("✅ ブラウザ初期化完了")
        
        # Geminiにアクセス
        logged_in = await browser.navigate_to_gemini()
        print(f"ログイン状態: {logged_in}")
        
        if not logged_in:
            print("⚠️  ログインが必要です")
            return
        
        # ページが完全に読み込まれるまで待機
        print("\n⏳ ページ読み込み待機中（10秒）...")
        await asyncio.sleep(10)
        
        # ページのHTMLを取得
        print("\n📄 ページHTML構造を取得中...")
        
        # すべてのinput/textareaを探す
        print("\n🔍 input要素の検索:")
        inputs = await browser.page.locator("input").all()
        print(f"   見つかったinput要素: {len(inputs)}個")
        
        print("\n🔍 textarea要素の検索:")
        textareas = await browser.page.locator("textarea").all()
        print(f"   見つかったtextarea要素: {len(textareas)}個")
        
        # contenteditable要素を探す
        print("\n🔍 contenteditable要素の検索:")
        editables = await browser.page.locator("[contenteditable]").all()
        print(f"   見つかったcontenteditable要素: {len(editables)}個")
        
        for i, elem in enumerate(editables[:5]):
            try:
                is_visible = await elem.is_visible()
                tag = await elem.evaluate("el => el.tagName")
                editable = await elem.get_attribute("contenteditable")
                aria_label = await elem.get_attribute("aria-label") or "なし"
                
                print(f"\n   [{i+1}] {tag}")
                print(f"       contenteditable: {editable}")
                print(f"       visible: {is_visible}")
                print(f"       aria-label: {aria_label}")
            except Exception as e:
                print(f"   [{i+1}] エラー: {e}")
        
        # role=textbox要素を探す
        print("\n🔍 role=textbox要素の検索:")
        textboxes = await browser.page.locator("[role='textbox']").all()
        print(f"   見つかったtextbox要素: {len(textboxes)}個")
        
        for i, elem in enumerate(textboxes[:3]):
            try:
                is_visible = await elem.is_visible()
                tag = await elem.evaluate("el => el.tagName")
                aria_label = await elem.get_attribute("aria-label") or "なし"
                
                print(f"\n   [{i+1}] {tag}")
                print(f"       visible: {is_visible}")
                print(f"       aria-label: {aria_label}")
            except Exception as e:
                print(f"   [{i+1}] エラー: {e}")
        
        # スクリーンショット保存
        print("\n📸 スクリーンショット保存中...")
        await browser.page.screenshot(path="debug_headless_page.png", full_page=True)
        print("✅ 保存: debug_headless_page.png")
        
        # ページのタイトルとURL
        print(f"\n�� ページ情報:")
        print(f"   URL: {browser.page.url}")
        print(f"   タイトル: {await browser.page.title()}")

asyncio.run(debug_page())

DEBUG_PY

echo ""
echo "=========================================="
echo "✅ 診断完了"
echo "=========================================="
echo ""
echo "生成されたファイル:"
echo "  - debug_headless_page.png"
echo ""

