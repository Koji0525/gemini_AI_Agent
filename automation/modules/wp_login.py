#!/usr/bin/env python3
"""
WordPress自動ログインモジュール
BrowserControllerを使用してWP管理画面にログイン
"""
import sys
import os
import asyncio
from pathlib import Path

# プロジェクトルートを追加
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from browser_control.browser_controller import BrowserController
from configuration.config_loader import ConfigLoader


class WPAutoLogin:
    """WordPress自動ログイン"""

    def __init__(self):
        self.config = ConfigLoader()
        self.browser = BrowserController()

        # 設定値を取得（get()メソッドまたは直接属性アクセス）
        try:
            self.wp_url = self.config.get("WP_URL") if hasattr(self.config, "get") else self.config.WP_URL
            self.wp_user = self.config.get("WP_USER") if hasattr(self.config, "get") else self.config.WP_USER
            self.wp_pass = self.config.get("WP_PASS") if hasattr(self.config, "get") else self.config.WP_PASS
        except AttributeError as e:
            print(f"❌ 設定取得エラー: {e}")
            print("💡 .envファイルを確認してください")
            raise

        self.cookies_file = project_root / "automation" / "logs" / "wp_cookies.json"

    async def login(self, use_cookies=True):
        """WordPress管理画面にログイン"""

        print("=" * 60)
        print("🌐 WordPress自動ログイン")
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
        await asyncio.sleep(5)

        # ログイン成功確認
        current_url = self.browser.page.url
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

    async def cleanup(self):
        """クリーンアップ"""
        await self.browser.cleanup()


async def main():
    """テスト実行"""

    login = WPAutoLogin()

    try:
        # ログイン実行
        success = await login.login(use_cookies=True)

        if success:
            # ログイン状態確認
            await login.verify_login()

            # 5秒待機（確認用）
            print("\n⏳ 5秒待機（確認用）...")
            await asyncio.sleep(5)

    finally:
        await login.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
