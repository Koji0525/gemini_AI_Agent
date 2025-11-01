#!/usr/bin/env python3
"""
BrowserController診断スクリプト
ページ初期化問題の根本原因を特定
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from browser_control.browser_controller import BrowserController


async def diagnose_browser_controller():
    """BrowserControllerの詳細な診断"""
    print("🔍 BrowserController詳細診断開始")
    print("=" * 50)

    try:
        # 1. インスタンス作成
        print("1. BrowserControllerインスタンス作成...")
        browser = BrowserController()
        print("   ✅ インスタンス作成成功")

        # 2. 属性一覧を表示
        print("\n2. BrowserControllerの属性一覧:")
        attrs = [attr for attr in dir(browser) if not attr.startswith("_")]
        for attr in sorted(attrs):
            value = getattr(browser, attr)
            value_type = type(value).__name__
            value_repr = repr(value)[:100] + "..." if len(repr(value)) > 100 else repr(value)
            print(f"   {attr}: {value_type} = {value_repr}")

        # 3. setup_browser実行
        print("\n3. setup_browser() 実行...")
        await browser.setup_browser(headless=True)
        print("   ✅ setup_browser() 実行成功")

        # 4. セットアップ後の属性状態
        print("\n4. セットアップ後の属性状態:")
        important_attrs = ["page", "browser", "context", "cookies"]
        for attr in important_attrs:
            if hasattr(browser, attr):
                value = getattr(browser, attr)
                status = "✅ 設定済み" if value is not None else "❌ None"
                print(f"   {attr}: {status}")
            else:
                print(f"   {attr}: ❌ 属性が存在しません")

        # 5. ページオブジェクトの詳細診断
        if hasattr(browser, "page") and browser.page:
            print("\n5. ページオブジェクトの詳細:")
            page = browser.page
            try:
                url = page.url
                print(f"   📍 現在のURL: {url}")

                title = await page.title()
                print(f"   📄 ページタイトル: {title}")

                # 簡単な操作テスト
                await page.goto("about:blank", timeout=10000)
                print("   ✅ ページ操作テスト成功")

            except Exception as e:
                print(f"   ❌ ページ操作テスト失敗: {e}")
        else:
            print("\n5. ❌ ページオブジェクトが利用できません")

            # 代替のページオブジェクト探索
            print("\n6. 代替ページオブジェクト探索:")
            all_attrs = dir(browser)
            page_like_attrs = [attr for attr in all_attrs if "page" in attr.lower()]
            for attr in page_like_attrs:
                try:
                    value = getattr(browser, attr)
                    if value is not None:
                        print(f"   🔍 {attr}: {type(value).__name__} = {repr(value)[:100]}")
                except:
                    print(f"   ⚠️ {attr}: アクセスエラー")

        # 7. クリーンアップ
        print("\n7. クリーンアップ...")
        await browser.cleanup()
        print("   ✅ クリーンアップ成功")

        print("\n🎉 診断完了")
        return True

    except Exception as e:
        print(f"❌ 診断中にエラー: {e}")
        import traceback

        print(f"🔍 詳細トレースバック:\n{traceback.format_exc()}")
        return False


if __name__ == "__main__":
    success = asyncio.run(diagnose_browser_controller())
    sys.exit(0 if success else 1)
