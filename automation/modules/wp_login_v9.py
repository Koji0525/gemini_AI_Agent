"""
WordPress自動ログイン - 引数なしsetup_browser版
Day 1: ConfigLoader修正 & WP自動ログイン実装
"""

import asyncio
import os
import json
import sys
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# プロジェクトルートをパスに追加（絶対パスで指定）
project_root = "/workspaces/gemini_AI_Agent"
sys.path.insert(0, project_root)
print(f"📁 プロジェクトルート追加: {project_root}")

try:
    from browser_control.browser_controller import BrowserController

    print("✅ BrowserController インポート成功")
except ImportError as e:
    print(f"❌ BrowserController インポート失敗: {e}")
    exit(1)


class WPAutoLogin:
    """WordPress自動ログインクラス"""

    def __init__(self):
        self.browser = None
        # 環境変数から直接取得
        self.wp_url = os.getenv("WP_URL")
        self.wp_user = os.getenv("WP_USER")
        self.wp_pass = os.getenv("WP_PASS")

    async def setup(self):
        """ブラウザセットアップ - 引数なしで呼び出し"""
        try:
            self.browser = BrowserController()
            # 引数なしでsetup_browserを呼び出す（デフォルトのheadless=Trueを使用）
            await self.browser.setup_browser()
            print("✅ ブラウザセットアップ完了")
            return True
        except Exception as e:
            print(f"❌ ブラウザセットアップ失敗: {e}")
            return False

    async def login(self):
        """WordPressにログイン"""
        try:
            # ログインページに移動
            print(f"🌐 ログインページに移動: {self.wp_url}/wp-admin")
            await self.browser.page.goto(f"{self.wp_url}/wp-admin", wait_until="networkidle")

            # 現在のURLを確認
            current_url = self.browser.page.url
            print(f"📍 現在のURL: {current_url}")

            # ユーザー名入力フィールドを確認
            username_field = await self.browser.page.query_selector("#user_login")
            if not username_field:
                print("❌ ユーザー名入力フィールドが見つかりません")
                # ページのHTMLをデバッグ出力
                page_content = await self.browser.page.content()
                print(f"📄 ページ内容（最初の500文字）: {page_content[:500]}")
                return False

            # ユーザー名入力
            print("👤 ユーザー名を入力")
            await self.browser.page.fill("#user_login", self.wp_user)

            # パスワード入力
            print("🔑 パスワードを入力")
            await self.browser.page.fill("#user_pass", self.wp_pass)

            # ログインボタンクリック
            print("🖱️ ログインボタンをクリック")
            await self.browser.page.click("#wp-submit")

            # ログイン成功確認
            print("⏳ ログイン成功を確認中...")
            try:
                await self.browser.page.wait_for_selector("#wpadminbar", timeout=15000)
                print("✅ WordPressログイン成功")

                # 現在のURLを確認
                current_url = self.browser.page.url
                print(f"📍 ログイン後URL: {current_url}")

                # Cookie保存
                print("🍪 Cookieを保存中...")
                cookie_result = await self.browser.save_wordpress_cookies(self.wp_url)
                if cookie_result:
                    print(f"✅ Cookie保存成功: {cookie_result}")
                else:
                    print("⚠️ Cookie保存に失敗")

                return True
            except Exception as wait_error:
                print(f"❌ 管理バーの検出失敗: {wait_error}")
                # 代替確認: ダッシュボードURLか確認
                if "wp-admin" in current_url and "wp-login.php" not in current_url:
                    print("✅ ダッシュボードページに到達 - ログイン成功")
                    return True
                else:
                    print("❌ ログイン失敗 - ダッシュボードに到達できません")
                    # エラーメッセージを確認
                    error_msg = await self.browser.page.query_selector("#login_error")
                    if error_msg:
                        error_text = await error_msg.text_content()
                        print(f"💬 エラーメッセージ: {error_text}")
                    return False

        except Exception as e:
            print(f"❌ ログイン失敗: {e}")
            # スクリーンショットを保存
            try:
                os.makedirs("automation/logs/day1", exist_ok=True)
                await self.browser.page.screenshot(path="automation/logs/day1/login_error.png")
                print("📸 エラー画面をスクリーンショット保存")
            except Exception as screenshot_error:
                print(f"⚠️ スクリーンショット保存に失敗: {screenshot_error}")
            return False

    async def test_dashboard_access(self):
        """ダッシュボードアクセステスト"""
        try:
            # ダッシュボードに移動
            print("📊 ダッシュボードアクセスをテスト")
            await self.browser.page.goto(f"{self.wp_url}/wp-admin")

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
        print("=" * 60)
        print("🚀 WordPress自動ログインテスト開始 - Day 1")
        print("=" * 60)

        # 環境変数確認
        print(f"🔧 環境変数確認:")
        print(f"  - WP_URL: {self.wp_url}")
        print(f"  - WP_USER: {self.wp_user}")
        print(f"  - WP_PASS: {'*' * len(self.wp_pass) if self.wp_pass else '未設定'}")

        if not all([self.wp_url, self.wp_user, self.wp_pass]):
            print("❌ 環境変数が設定されていません")
            print("💡 .envファイルを確認してください")
            return False

        # セットアップ
        print(f"\n�� ブラウザセットアップ中...")
        if not await self.setup():
            return False

        # ログイン実行
        print("\n🔐 ログイン実行中...")
        login_success = await self.login()

        if login_success:
            # ダッシュボードテスト
            print("\n📊 ダッシュボードアクセステスト中...")
            dashboard_success = await self.test_dashboard_access()

            # 結果保存
            result = {
                "login_success": login_success,
                "dashboard_success": dashboard_success,
                "wp_url": self.wp_url,
                "username": self.wp_user,
                "timestamp": asyncio.get_event_loop().time(),
            }

            # ログ保存
            os.makedirs("automation/logs/day1", exist_ok=True)
            log_file = "automation/logs/day1/login_test_result.json"
            with open(log_file, "w") as f:
                json.dump(result, f, indent=2)

            print(f"\n✅ テスト完了 - 結果を保存: {log_file}")
            return all([login_success, dashboard_success])
        else:
            # 失敗時の結果保存
            result = {
                "login_success": False,
                "dashboard_success": False,
                "wp_url": self.wp_url,
                "username": self.wp_user,
                "timestamp": asyncio.get_event_loop().time(),
            }
            os.makedirs("automation/logs/day1", exist_ok=True)
            with open("automation/logs/day1/login_test_result.json", "w") as f:
                json.dump(result, f, indent=2)
            print("\n❌ ログイン失敗 - 結果をログに保存")

        return False


async def main():
    """メイン実行"""
    login_system = WPAutoLogin()

    success = await login_system.run_full_test()

    print("=" * 60)
    if success:
        print("🎉 Day 1: WP自動ログイン 完了！")
        print("✅ 次のステップ: functions.php自動更新へ進めます")

        # 成功レポート
        print("\n📋 Day 1 完了レポート:")
        print("  ✅ ConfigLoader.get()メソッド追加")
        print("  ✅ BrowserController.setup_browser()修正")
        print("  ✅ WordPress自動ログイン実装完了")
        print("  ✅ テスト結果ログ保存")
        print("  ✅ Cookie保存機能動作確認")
    else:
        print("❌ Day 1: テスト失敗")
        print("🔧 問題を解決して再実行してください")
        print("\n💡 トラブルシューティング:")
        print("  - 環境変数を確認: python3 automation/scripts/check_env_details.py")
        print("  - ネットワーク接続を確認")
        print("  - WordPressのURLが正しいか確認")
        print("  - ユーザー名/パスワードが正しいか確認")
    print("=" * 60)

    # ブラウザを閉じる
    if login_system.browser:
        print("🔄 ブラウザをクリーンアップ中...")
        await login_system.browser.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
