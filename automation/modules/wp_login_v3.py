"""
WordPress自動ログイン - 修正版
Day 1: ConfigLoader修正 & WP自動ログイン実装
"""

import asyncio
import os
import json
from browser_control.browser_controller import BrowserController
from configuration.config_loader import ConfigLoader


class WPAutoLogin:
    """WordPress自動ログインクラス"""

    def __init__(self):
        self.config = ConfigLoader()
        self.browser = None

    async def setup(self):
        """ブラウザセットアップ"""
        try:
            self.browser = BrowserController()
            await self.browser.setup_browser(headless=False)
            print("✅ ブラウザセットアップ完了")
            return True
        except Exception as e:
            print(f"❌ ブラウザセットアップ失敗: {e}")
            return False

    async def login(self, wp_url, username, password):
        """WordPressにログイン"""
        try:
            # ログインページに移動
            await self.browser.page.goto(f"{wp_url}/wp-admin")

            # ユーザー名入力
            await self.browser.page.fill("#user_login", username)

            # パスワード入力
            await self.browser.page.fill("#user_pass", password)

            # ログインボタンクリック
            await self.browser.page.click("#wp-submit")

            # ログイン成功確認
            await self.browser.page.wait_for_selector("#wpadminbar", timeout=10000)
            print("✅ WordPressログイン成功")

            # Cookie保存
            await self.browser.save_wordpress_cookies(wp_url)

            return True

        except Exception as e:
            print(f"❌ ログイン失敗: {e}")
            return False

    async def test_dashboard_access(self):
        """ダッシュボードアクセステスト"""
        try:
            # ダッシュボードに移動
            await self.browser.page.goto(f"{self.config.get('WP_URL')}/wp-admin")

            # ダッシュボード要素を確認
            dashboard_element = await self.browser.page.query_selector(".wp-menu-name")
            if dashboard_element:
                print("✅ ダッシュボードアクセス確認")
                return True
            return False
        except Exception as e:
            print(f"❌ ダッシュボードアクセス失敗: {e}")
            return False

    async def run_full_test(self):
        """完全テスト実行"""
        print("🚀 WordPress自動ログインテスト開始")

        # セットアップ
        if not await self.setup():
            return False

        # ログイン実行
        wp_url = self.config.get("WP_URL")
        username = self.config.get("WP_USER")
        password = self.config.get("WP_PASS")

        if not all([wp_url, username, password]):
            print("❌ 環境変数が設定されていません")
            return False

        login_success = await self.login(wp_url, username, password)

        if login_success:
            # ダッシュボードテスト
            dashboard_success = await self.test_dashboard_access()

            # 結果保存
            result = {
                "login_success": login_success,
                "dashboard_success": dashboard_success,
                "timestamp": asyncio.get_event_loop().time(),
            }

            # ログ保存
            os.makedirs("automation/logs/day1", exist_ok=True)
            with open("automation/logs/day1/login_test_result.json", "w") as f:
                json.dump(result, f, indent=2)

            print("✅ テスト完了 - 結果をログに保存")
            return all([login_success, dashboard_success])

        return False


async def main():
    """メイン実行"""
    login_system = WPAutoLogin()
    success = await login_system.run_full_test()

    if success:
        print("🎉 Day 1: WP自動ログイン 完了！")
    else:
        print("❌ Day 1: テスト失敗")

    # ブラウザを閉じる
    if login_system.browser:
        await login_system.browser.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
