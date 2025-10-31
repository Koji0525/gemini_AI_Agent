"""WordPress認証・ログイン管理（完全修正版 - クッキー強制ナビゲーション対応）"""

import asyncio
import logging
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from playwright.async_api import Page

logger = logging.getLogger(__name__)


class WordPressAuth:
    """WordPress認証管理（BrowserController統合版 + クッキー強制ナビゲーション対応）"""

    def __init__(self, browser_controller, wp_url: str, wp_user: str, wp_pass: str):
        """
        初期化

        Args:
            browser_controller: BrowserController インスタンス
            wp_url: WordPress サイトURL
            wp_user: ユーザー名
            wp_pass: パスワード
        """
        self.browser = browser_controller
        self.wp_url = wp_url.rstrip("/")
        self.wp_user = wp_user
        self.wp_pass = wp_pass

    async def login(self, page: Page) -> bool:
        """
        WordPressにログイン（クッキー優先 + 強制ナビゲーション版）

        改善点:
        1. クッキー適用後に必ず管理画面URLへナビゲーション
        2. ログイン状態検証の厳格化
        3. 失敗時のフォールバック強化

        Args:
            page: Playwright Page オブジェクト

        Returns:
            bool: ログイン成功時 True
        """
        try:
            logger.info("=" * 60)
            logger.info("WordPress: ログイン開始（クッキー優先 + 強制ナビゲーション）")
            logger.info(f"URL: {self.wp_url}")
            logger.info("=" * 60)

            # ✅ Phase 1: クッキーでのログインを試行
            cookies_loaded = await self.browser.load_wordpress_cookies(self.wp_url)

            if cookies_loaded:
                logger.info("✅ WordPress クッキーを読み込みました")

                # ✅ 重要: クッキー適用後に管理画面に強制ナビゲーション
                admin_url = f"{self.wp_url}/wp-admin/"
                logger.info(f"🔄 管理画面にナビゲーション中: {admin_url}")

                try:
                    await page.goto(admin_url, timeout=30000, wait_until="domcontentloaded")
                    await asyncio.sleep(3)  # セッション確立を待機

                    # ✅ Phase 2: ログイン状態を厳格に検証
                    if await self._verify_login_status(page):
                        logger.info("✅ クッキー認証成功 - 既にログイン済み")

                        # スクリーンショット保存
                        screenshot_path = f"wp_cookie_login_success_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        await page.screenshot(path=screenshot_path)
                        logger.info(f"📸 クッキーログイン成功: {screenshot_path}")

                        return True
                    else:
                        logger.warning("⚠️ クッキー認証失敗 - 手動ログインを実行します")

                except Exception as nav_error:
                    logger.warning(f"⚠️ 管理画面ナビゲーションエラー: {nav_error}")

            # ✅ Phase 3: クッキー認証が失敗した場合は手動ログイン
            return await self.manual_login(page)

        except Exception as e:
            logger.error(f"❌ ログインエラー: {e}")
            # フォールバック: 手動ログイン
            return await self.manual_login(page)

    async def manual_login(self, page: Page) -> bool:
        """
        手動ログイン（ユーザー名/パスワード方式）

        Args:
            page: Playwright Page オブジェクト

        Returns:
            bool: ログイン成功時 True
        """
        try:
            logger.info("🔐 手動ログインを実行します")

            # ログインページに移動
            login_url = f"{self.wp_url}/wp-login.php"
            await page.goto(login_url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(2)

            # ユーザー名入力
            user_field = await page.query_selector("#user_login")
            if not user_field:
                logger.error("❌ ユーザー名入力フィールドが見つかりません")
                return False

            await user_field.fill(self.wp_user)
            await asyncio.sleep(0.5)
            logger.info("✅ ユーザー名入力完了")

            # パスワード入力
            pass_field = await page.query_selector("#user_pass")
            if not pass_field:
                logger.error("❌ パスワード入力フィールドが見つかりません")
                return False

            await pass_field.fill(self.wp_pass)
            await asyncio.sleep(0.5)
            logger.info("✅ パスワード入力完了")

            # ログインボタンをクリック
            login_button = await page.query_selector("#wp-submit")
            if not login_button:
                logger.error("❌ ログインボタンが見つかりません")
                return False

            await login_button.click()
            await asyncio.sleep(5)
            logger.info("✅ ログインボタンをクリックしました")

            # ログイン成功確認
            if await self._verify_login_status(page):
                logger.info("✅ WordPress手動ログイン成功")

                # ✅ ログイン成功時にクッキーを保存
                await self.browser.save_wordpress_cookies(self.wp_url)

                # スクリーンショット保存
                screenshot_path = f"wp_manual_login_success_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await page.screenshot(path=screenshot_path)
                logger.info(f"📸 手動ログイン成功: {screenshot_path}")

                return True
            else:
                logger.error("❌ WordPressログイン失敗")

                # 失敗時のスクリーンショット
                await page.screenshot(path="wp_login_failed.png")

                # エラーメッセージの確認
                error_element = await page.query_selector("#login_error")
                if error_element:
                    error_text = await error_element.text_content()
                    logger.error(f"ログインエラーメッセージ: {error_text}")

                return False

        except Exception as e:
            logger.error(f"❌ 手動ログインエラー: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return False

    async def _verify_login_status(self, page: Page) -> bool:
        """
        WordPressログイン状態を詳細検証（厳格版）

        改善点:
        1. URL確認を最優先
        2. 4つのチェックのうち3つ以上で合格判定
        3. 各チェック結果を詳細にログ出力

        Args:
            page: Playwright Page オブジェクト

        Returns:
            bool: ログイン済みの場合 True
        """
        try:
            checks = []

            # ✅ 1. URL確認（最優先）
            current_url = page.url
            is_admin_page = "/wp-admin/" in current_url and "wp-login.php" not in current_url
            checks.append(("管理ページURL", is_admin_page))

            # ✅ 2. 管理バーの存在チェック
            admin_bar = await page.query_selector("#wpadminbar")
            checks.append(("管理バー", bool(admin_bar)))

            # ✅ 3. ダッシュボード要素チェック
            dashboard = await page.query_selector("#wpbody-content")
            checks.append(("ダッシュボード", bool(dashboard)))

            # ✅ 4. ログインフォームの不在チェック
            login_form = await page.query_selector("#loginform")
            checks.append(("ログインフォーム不在", not bool(login_form)))

            # 結果の集計
            passed_checks = [name for name, passed in checks if passed]
            total_passed = len(passed_checks)

            logger.info(f"🔍 ログイン状態検証: {total_passed}/4 合格")

            # ✅ 詳細ログ出力
            for name, passed in checks:
                status = "✅" if passed else "❌"
                logger.info(f"  {status} {name}")

            if total_passed >= 3:  # 4つのうち3つ以上合格ならログイン成功
                logger.info(f"  ✅ 合格項目: {', '.join(passed_checks)}")
                return True
            else:
                logger.warning(f"  ❌ 不合格が多すぎます（合格: {total_passed}/4）")
                logger.warning(f"  現在URL: {current_url}")
                return False

        except Exception as e:
            logger.warning(f"⚠️ ログイン状態検証エラー: {e}")
            return False
