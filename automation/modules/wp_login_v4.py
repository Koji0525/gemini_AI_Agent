"""
WordPress自動ログイン - インポート修正版
Day 1: ConfigLoader修正 & WP自動ログイン実装
"""

import asyncio
import os
import json
import sys

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from browser_control.browser_controller import BrowserController

    print("✅ BrowserController インポート成功")
except ImportError as e:
    print(f"❌ BrowserController インポート失敗: {e}")
    # 代替パスを試す
    try:
        sys.path.append("/workspaces/gemini_AI_Agent")
        from browser_control.browser_controller import BrowserController

        print("✅ BrowserController インポート成功（代替パス）")
    except ImportError as e2:
        print(f"❌ 代替パスでもインポート失敗: {e2}")
        exit(1)

try:
    from configuration.config_loader import ConfigLoader

    print("✅ ConfigLoader インポート成功")
except ImportError as e:
    print(f"❌ ConfigLoader インポート失敗: {e}")
    # 代替パスを試す
    try:
        from config.config_loader import ConfigLoader

        print("✅ ConfigLoader インポート成功（代替パス）")
    except ImportError as e2:
        print(f"❌ 代替パスでもインポート失敗: {e2}")
        exit(1)


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
            print(f"🌐 ログインページに移動: {wp_url}/wp-admin")
            await self.browser.page.goto(f"{wp_url}/wp-admin", wait_until="networkidle")

            # ユーザー名入力
            print("👤 ユーザー名を入力")
            await self.browser.page.fill("#user_login", username)

            # パスワード入力
            print("🔑 パスワードを入力")
            await self.browser.page.fill("#user_pass", password)

            # ログインボタンクリック
            print("🖱️ ログインボタンをクリック")
            await self.browser.page.click("#wp-submit")

            # ログイン成功確認
            print("⏳ ログイン成功を確認中...")
            await self.browser.page.wait_for_selector("#wpadminbar", timeout=15000)
            print("✅ WordPressログイン成功")

            # Cookie保存
            print("🍪 Cookieを保存中...")
            await self.browser.save_wordpress_cookies(wp_url)

            return True

        except Exception as e:
            print(f"❌ ログイン失敗: {e}")
            # スクリーンショットを保存
            await self.browser.page.screenshot(path="automation/logs/day1/login_error.png")
            return False

    async def test_dashboard_access(self, wp_url):
        """ダッシュボードアクセステスト"""
        try:
            # ダッシュボードに移動
            print("📊 ダッシュボードアクセスをテスト")
            await self.browser.page.goto(f"{wp_url}/wp-admin")

            # ダッシュボード要素を確認
            dashboard_element = await self.browser.page.query_selector("#wpadminbar")
            if dashboard_element:
                print("✅ ダッシュボードアクセス確認")
                return True

            # 代替確認: 管理メニューの存在
            admin_menu = await self.browser.page.query_selector("#adminmenu")
            if admin_menu:
                print("✅ 管理メニュー確認")
                return True

            return False
        except Exception as e:
            print(f"❌ ダッシュボードアクセス失敗: {e}")
            return False

    async def run_full_test(self):
        """完全テスト実行"""
        print("=" * 50)
        print("�� WordPress自動ログインテスト開始")
        print("=" * 50)

        # セットアップ
        if not await self.setup():
            return False

        # ログイン実行
        wp_url = self.config.get("WP_URL")
        username = self.config.get("WP_USER")
        password = self.config.get("WP_PASS")

        print(f"🔧 設定値: URL={wp_url}, USER={username}")

        if not all([wp_url, username, password]):
            print("❌ 環境変数が設定されていません")
            return False

        login_success = await self.login(wp_url, username, password)

        if login_success:
            # ダッシュボードテスト
            dashboard_success = await self.test_dashboard_access(wp_url)

            # 結果保存
            result = {
                "login_success": login_success,
                "dashboard_success": dashboard_success,
                "wp_url": wp_url,
                "timestamp": asyncio.get_event_loop().time(),
            }

            # ログ保存
            os.makedirs("automation/logs/day1", exist_ok=True)
            with open("automation/logs/day1/login_test_result.json", "w") as f:
                json.dump(result, f, indent=2)

            print("✅ テスト完了 - 結果をログに保存")
            return all([login_success, dashboard_success])
        else:
            # 失敗時の結果保存
            result = {
                "login_success": False,
                "dashboard_success": False,
                "wp_url": wp_url,
                "timestamp": asyncio.get_event_loop().time(),
            }
            os.makedirs("automation/logs/day1", exist_ok=True)
            with open("automation/logs/day1/login_test_result.json", "w") as f:
                json.dump(result, f, indent=2)

        return False


async def main():
    """メイン実行"""
    login_system = WPAutoLogin()
    success = await login_system.run_full_test()

    print("=" * 50)
    if success:
        print("🎉 Day 1: WP自動ログイン 完了！")
    else:
        print("❌ Day 1: テスト失敗")
    print("=" * 50)

    # ブラウザを閉じる
    if login_system.browser:
        await login_system.browser.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
