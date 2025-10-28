#!/usr/bin/env python3
"""
正しいBrowserControllerの使用例
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from browser_control.browser_controller import BrowserController


async def correct_browser_usage():
    """正しいBrowserControllerの使用方法"""
    print("🔧 正しいBrowserController使用例")

    # 正しい初期化方法
    browser = BrowserController()

    try:
        # ブラウザ操作の例
        print("✅ BrowserControllerの初期化完了")

        # 実際の使用例（必要に応じてコメントアウト）
        # await browser.page.goto("https://example.com")
        # print("🌐 ページに移動しました")

        print("🎉 BrowserControllerの使用例が正常に完了")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # クリーンアップ
        await browser.cleanup()
        print("🧹 ブラウザをクリーンアップしました")


if __name__ == "__main__":
    asyncio.run(correct_browser_usage())
