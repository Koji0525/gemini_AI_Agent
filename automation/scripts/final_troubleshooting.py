"""
最終問題解決チェックリスト
"""

import sys
import os
import asyncio

# プロジェクトルートをパスに追加
project_root = "/workspaces/gemini_AI_Agent"
sys.path.insert(0, project_root)


async def final_check():
    print("🐛 最終問題解決チェックリスト")
    print("=" * 50)

    # 1. 環境変数チェック
    print("1. 🔧 環境変数チェック:")
    from dotenv import load_dotenv

    load_dotenv()

    wp_url = os.getenv("WP_URL")
    wp_user = os.getenv("WP_USER")
    wp_pass = os.getenv("WP_PASS")

    print(f"   WP_URL: {wp_url}")
    print(f"   WP_USER: {wp_user}")
    print(f"   WP_PASS: {'*' * len(wp_pass) if wp_pass else '未設定'}")
    print(f"   すべて設定: {all([wp_url, wp_user, wp_pass])}")

    # 2. モジュールインポートチェック
    print("\n2. 📦 モジュールインポートチェック:")
    try:
        from browser_control.browser_controller import BrowserController

        print("   ✅ BrowserController インポート成功")
    except ImportError as e:
        print(f"   ❌ BrowserController インポート失敗: {e}")

    # 3. setup_browserメソッドチェック
    print("\n3. 🔍 setup_browserメソッドチェック:")
    try:
        from browser_control.browser_controller import BrowserController
        import inspect

        method = getattr(BrowserController, "setup_browser")
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        print(f"   メソッドシグネチャ: {sig}")
        if "headless" in params:
            print("   ✅ headless引数あり")
        else:
            print("   ❌ headless引数なし")

    except Exception as e:
        print(f"   ❌ チェック失敗: {e}")

    # 4. Playwrightブラウザチェック
    print("\n4. 🌐 Playwrightブラウザチェック:")
    try:
        from playwright.async_api import async_playwright

        print("   ✅ Playwright インポート成功")

        # ブラウザの存在確認
        import subprocess

        result = subprocess.run(["which", "playwright"], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Playwright CLI 利用可能")
        else:
            print("   ❌ Playwright CLI が見つかりません")

    except ImportError as e:
        print(f"   ❌ Playwright インポート失敗: {e}")

    # 5. ネットワーク接続チェック
    print("\n5. 🌐 ネットワーク接続チェック:")
    try:
        import urllib.request

        with urllib.request.urlopen("https://uzbek-ma.com", timeout=10) as response:
            status = response.getcode()
            print(f"   ✅ WordPressサイト接続可能 (ステータス: {status})")
    except Exception as e:
        print(f"   ❌ WordPressサイト接続失敗: {e}")

    print("=" * 50)
    print("🔧 最終チェック完了")


if __name__ == "__main__":
    asyncio.run(final_check())
