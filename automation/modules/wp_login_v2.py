#!/usr/bin/env python3
"""
WordPress自動ログインモジュール v2
環境変数を直接使用
"""
import sys
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# プロジェクトルートを追加
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from browser_control.browser_controller import BrowserController


class WPAutoLogin:
    """WordPress自動ログイン v2"""

    def __init__(self):
        self.browser = BrowserController()

        # 環境変数から直接取得
        self.wp_url = os.getenv("WP_URL")
        self.wp_user = os.getenv("WP_USER")
        self.wp_pass = os.getenv("WP_PASS")

        # 必須チェック
        if not all([self.wp_url, self.wp_user, self.wp_pass]):
            missing = []
            if not self.wp_url:
                missing.append("WP_URL")
            if not self.wp_user:
                missing.append("WP_USER")
            if not self.wp_pass:
                missing.append("WP_PASS")

            raise ValueError(
                f"❌ 環境変数が設定されていません: {', '.join(missing)}\n💡 .envファイルを確認してください"
            )

        print(f"✅ 設定読み込み成功:")
        print(f"   WP_URL: {self.wp_url}")
        print(f"   WP_USER: {self.wp_user}")
        print(f"   WP_PASS: ***")
        print()

        self.cookies_file = project_root / "automation" / "logs" / "wp_cookies.json"

    async def login(self, use_cookies=True):
        """WordPress管理画面にログイン"""

        print("=" * 60)
        print("🌐 WordPress自動ログイン v2")
        print("=" * 60)
        print()

        try:
            # ブラウザセットアップ
            print("🔧 ブラウザ起動中...")
            await self.browser.setup_browser()
            print("✅ ブラウザ起動完了")
            print()

            # Cookie使用を試みる
            if use_cookies and self.cookies_file.exists():
                print("🍪 保存済みCookieを使用...")
                try:
                    await self.browser.load_wordpress_cookies()

                    # ダッシュボードに直接アクセス
                    await self.browser.page.goto(f"{self.wp_url}/wp-admin/")
                    await asyncio.sleep(3)

                    # ログイン状態を確認
                    current_url = self.browser.page.url
                    if "/wp-admin/" in current_url and "/wp-login.php" not in current_url:
                        print("✅ Cookie認証成功")
                        return True
                    else:
                        print("⚠️  Cookie無効、通常ログインに切り替え")
                except Exception as e:
                    print(f"⚠️  Cookie読み込みエラー: {e}")

            # 通常ログイン
            print("🔑 通常ログイン実行...")
            await self._perform_login()

            # Cookie保存
            print("💾 Cookie保存中...")
            await self.browser.save_wordpress_cookies()
            print("✅ Cookie保存完了")

            print()
            print("=" * 60)
            print("🎉 WordPress自動ログイン完了")
            print("=" * 60)

            return True

        except Exception as e:
            print(f"\n❌ ログインエラー: {e}")
            import traceback

            traceback.print_exc()
            return False

    async def _perform_login(self):
        """実際のログイン処理"""

        # ログインページへ移動
        print(f"  🌐 ログインページへ移動: {self.wp_url}/wp-login.php")
        await self.browser.page.goto(f"{self.wp_url}/wp-login.php")
        await asyncio.sleep(2)

        # ユーザー名入力
        await self.browser.page.fill("input#user_login", self.wp_user)
        print(f"  ✅ ユーザー名入力: {self.wp_user}")

        # パスワード入力
        await self.browser.page.fill("input#user_pass", self.wp_pass)
        print("  ✅ パスワード入力")

        # ログインボタンクリック
        await self.browser.page.click("input#wp-submit")
        print("  🖱️  ログインボタンクリック")

        # ダッシュボード読み込み待機
        print("  ⏳ ダッシュボード読み込み待機...")
        await asyncio.sleep(5)

        # ログイン成功確認
        current_url = self.browser.page.url
        print(f"  📍 現在のURL: {current_url}")

        if "/wp-admin/" in current_url:
            print("  ✅ ログイン成功")
        else:
            raise Exception(f"ログイン失敗: {current_url}")

    async def verify_login(self):
        """ログイン状態の確認"""

        current_url = self.browser.page.url

        if "/wp-admin/" in current_url and "/wp-login.php" not in current_url:
            print("✅ ログイン状態: OK")
            return True
        else:
            print("❌ ログイン状態: NG")
            return False

    async def get_dashboard_info(self):
        """ダッシュボード情報を取得"""

        try:
            # ページタイトルを取得
            title = await self.browser.page.title()
            print(f"📄 ページタイトル: {title}")

            # サイト名を取得
            try:
                site_name = await self.browser.page.locator("a.ab-item").first.inner_text()
                print(f"🏠 サイト名: {site_name}")
            except:
                pass

            return True
        except Exception as e:
            print(f"⚠️  ダッシュボード情報取得エラー: {e}")
            return False

    async def cleanup(self):
        """クリーンアップ"""
        await self.browser.cleanup()


async def main():
    """テスト実行"""

    print("=" * 60)
    print("🧪 WPAutoLogin v2 テスト")
    print("=" * 60)
    print()

    login = WPAutoLogin()

    try:
        # ログイン実行
        success = await login.login(use_cookies=False)  # 初回は通常ログイン

        if success:
            # ログイン状態確認
            await login.verify_login()

            # ダッシュボード情報取得
            await login.get_dashboard_info()

            # 5秒待機（確認用）
            print("\n⏳ 5秒待機（確認用）...")
            await asyncio.sleep(5)

            print("\n🎉 テスト成功")
        else:
            print("\n❌ テスト失敗")

    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback

        traceback.print_exc()

    finally:
        print("\n�� クリーンアップ中...")
        await login.cleanup()
        print("✅ クリーンアップ完了")


if __name__ == "__main__":
    asyncio.run(main())
