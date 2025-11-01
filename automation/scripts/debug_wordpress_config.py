"""
WordPress設定デバッグスクリプト
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# プロジェクトルートをパスに追加
project_root = "/workspaces/gemini_AI_Agent"
sys.path.insert(0, project_root)

from browser_control.browser_controller import BrowserController


async def debug_wp_config():
    """WordPress設定をデバッグ"""
    print("🐛 WordPress設定デバッグ")
    print("=" * 50)

    browser = BrowserController()

    try:
        await browser.setup_browser(headless=False)

        # WordPressにログイン
        wp_url = os.getenv("WP_URL")
        wp_user = os.getenv("WP_USER")
        wp_pass = os.getenv("WP_PASS")

        await browser.page.goto(f"{wp_url}/wp-admin")
        await browser.page.fill("#user_login", wp_user)
        await browser.page.fill("#user_pass", wp_pass)
        await browser.page.click("#wp-submit")
        await browser.page.wait_for_selector("#wpadminbar")

        print("✅ WordPressログイン成功")

        # テーマエディターページに移動
        await browser.page.goto(f"{wp_url}/wp-admin/theme-editor.php")

        print(f"📍 現在のURL: {browser.page.url}")
        print(f"📄 ページタイトル: {await browser.page.title()}")

        # ページのHTMLを分析
        content = await browser.page.content()

        # キーワードチェック
        keywords = [
            "theme-editor",
            "ファイル編集",
            "File Editor",
            "DISALLOW_FILE_EDIT",
            "FILE_MODS",
            "権限",
            "permission",
        ]

        print("\n🔍 ページ分析:")
        for keyword in keywords:
            if keyword.lower() in content.lower():
                print(f"✅ '{keyword}' を発見")

        # よくあるエラーメッセージ
        error_patterns = [
            "このサイトではファイル編集は無効になっています",
            "File editing is disabled",
            "インストール済みのテーマがありません",
            "No installed themes",
            "権限がありません",
            "You do not have permission",
        ]

        print("\n🔍 エラーメッセージ検索:")
        for pattern in error_patterns:
            if pattern in content:
                print(f"❌ エラーメッセージ: {pattern}")

        # スクリーンショット保存
        await browser.page.screenshot(path="automation/logs/day2/debug_screenshot.png")
        print("📸 デバッグスクリーンショットを保存")

        print("=" * 50)
        print("🔧 デバッグ完了")

    except Exception as e:
        print(f"❌ デバッグ中にエラー: {e}")
    finally:
        await browser.cleanup()


if __name__ == "__main__":
    asyncio.run(debug_wp_config())
