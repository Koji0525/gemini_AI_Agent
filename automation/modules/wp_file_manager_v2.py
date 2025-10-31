"""
WordPressファイルマネージャー V2 - 構文エラー修正版
"""

import asyncio
import os
import sys
import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from browser_control.browser_controller import BrowserController


class WPFileManagerV2:
    """WordPressファイルマネージャー V2"""

    def __init__(self):
        self.browser: Optional[BrowserController] = None
        self.wp_url = os.getenv("WP_URL")
        self.wp_user = os.getenv("WP_USER")
        self.wp_pass = os.getenv("WP_PASS")

    async def setup(self) -> bool:
        """ブラウザセットアップ"""
        try:
            self.browser = BrowserController()
            await self.browser.setup_browser(headless=True)
            return True
        except Exception as e:
            print(f"❌ ブラウザセットアップ失敗: {e}")
            return False

    async def login_to_wordpress(self) -> bool:
        """WordPressにログイン"""
        try:
            await self.browser.page.goto(f"{self.wp_url}/wp-admin", wait_until="networkidle")

            if "wp-login.php" in self.browser.page.url:
                await self.browser.page.fill("#user_login", self.wp_user)
                await self.browser.page.fill("#user_pass", self.wp_pass)
                await self.browser.page.click("#wp-submit")
                await self.browser.page.wait_for_selector("#wpadminbar", timeout=15000)

            return True
        except Exception as e:
            print(f"❌ WordPressログイン失敗: {e}")
            return False

    async def run(self):
        """メイン実行"""
        try:
            if not await self.setup():
                return False

            if not await self.login_to_wordpress():
                return False

            print("✅ WordPressファイルマネージャー実行完了")
            return True

        except Exception as e:
            print(f"❌ 実行エラー: {e}")
            return False
        finally:
            if self.browser:
                await self.browser.cleanup()


async def main():
    """メイン実行"""
    manager = WPFileManagerV2()
    result = await manager.run()

    if result:
        print("🎉 正常終了")
    else:
        print("❌ 異常終了")


if __name__ == "__main__":
    asyncio.run(main())
