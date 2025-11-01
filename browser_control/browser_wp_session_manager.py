# browser_wp_session_manager.py
"""WordPressセッション管理クラス"""
import json
import time
from pathlib import Path
from typing import Optional, Dict
from playwright.async_api import Page, BrowserContext
import logging

from configuration.config_utils import ErrorHandler

logger = logging.getLogger(__name__)


class WPSessionManager:
    """WordPressセッションの管理を担当"""

    def __init__(self, context: BrowserContext, wp_cookies_file: Path):
        self.context = context
        self.wp_cookies_file = wp_cookies_file
        self.wp_page: Optional[Page] = None
        self.is_logged_in = False

    async def initialize_wp_session(self, auth_module=None) -> bool:
        """
        WordPress セッション初期化（完全修正版 - クッキー強制ナビゲーション対応）

        Args:
            auth_module: WordPress認証モジュール（任意）

        Returns:
            bool: 初期化成功時 True
        """
        try:
            logger.info("=" * 60)
            logger.info("🔐 WordPress セッション初期化中...")
            logger.info("=" * 60)

            # Phase 1: 新しいタブを作成
            if not self.context:
                logger.error("❌ ブラウザコンテキストが初期化されていません")
                return False

            self.wp_page = await self.context.new_page()
            logger.info("✅ WordPress 専用タブを作成しました")

            # Phase 2: 認証情報の検証
            if not auth_module:
                logger.warning("⚠️ WordPress 認証モジュールが提供されていません")
                logger.info("手動ログインが必要になる可能性があります")

            # Phase 3: ログイン実行（クッキー優先 + 強制ナビゲーション）
            logger.info("🔄 WordPress認証を実行中...")

            if auth_module:
                login_success = await auth_module.login(self.wp_page)
            else:
                # 認証モジュールがない場合は手動ログインを促す
                login_success = await self._manual_wp_login()

            if login_success:
                self.is_logged_in = True
                logger.info("=" * 60)
                logger.info("✅ WordPress セッション初期化完了")
                logger.info("  認証方法: クッキー or 手動ログイン")
                logger.info("  ページURL: " + self.wp_page.url)
                logger.info("=" * 60)
                return True
            else:
                logger.error("=" * 60)
                logger.error("❌ WordPress ログイン失敗")
                logger.error("  原因: 認証情報またはネットワークの問題")
                logger.error("  対策: 認証情報を確認してください")
                logger.error("=" * 60)

                # デバッグ用: 失敗時のスクリーンショット
                try:
                    await self.wp_page.screenshot(path="wp_session_init_failed.png")
                    logger.info("📸 デバッグ用スクリーンショット: wp_session_init_failed.png")
                except:
                    pass

                return False

        except Exception as e:
            logger.error(f"❌ WordPress セッション初期化エラー: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return False

    async def _manual_wp_login(self) -> bool:
        """手動WordPressログイン処理"""
        try:
            logger.info("=" * 60)
            logger.info("🔐 手動WordPressログインが必要です")
            logger.info("=" * 60)
            logger.info("")
            logger.info("📌 ログイン手順：")
            logger.info("1. ブラウザでWordPress管理画面を開く")
            logger.info("2. ユーザー名/パスワードでログイン")
            logger.info("3. ダッシュボードが表示されたらこのコンソールに戻る")
            logger.info("4. Enterキーを押して続行")
            logger.info("")
            logger.info("💡 ヒント：")
            logger.info("  - ログイン後はこのタブを閉じないでください")
            logger.info("  - セッションはCookieで維持されます")
            logger.info("=" * 60)

            # 一般的なWordPressログインURLに移動
            await self.wp_page.goto("/wp-admin", wait_until="domcontentloaded")

            input("\n✅ ログイン完了後、Enterキーを押してください: ")

            # ログイン成功を確認
            current_url = self.wp_page.url
            if "wp-admin" in current_url or "dashboard" in current_url.lower():
                logger.info("✅ WordPressログイン成功を確認")
                return True
            else:
                logger.warning("⚠️ WordPress管理画面に到達していない可能性があります")
                return False

        except Exception as e:
            logger.error(f"手動ログイン処理エラー: {e}")
            return False

    async def save_wordpress_cookies(self, wp_url: str) -> bool:
        """WordPress専用のクッキーを保存"""
        try:
            if not self.context or not self.wp_cookies_file:
                logger.warning("⚠️ クッキー保存: コンテキストまたはファイルパスがありません")
                return False

            # 現在のクッキーを取得
            cookies = await self.context.cookies()

            if not cookies:
                logger.warning("保存するクッキーがありません")
                return False

            # WordPress関連のクッキーをフィルタリング
            wp_domain = wp_url.replace("https://", "").replace("http://", "").split("/")[0]
            wp_cookies = [c for c in cookies if wp_domain in c.get("domain", "")]

            if not wp_cookies:
                logger.warning("WordPress関連のクッキーが見つかりません")
                return False

            # 既存のクッキーファイルを読み込み
            all_cookies = {}
            if self.wp_cookies_file.exists():
                try:
                    with open(self.wp_cookies_file, "r", encoding="utf-8") as f:
                        all_cookies = json.load(f)
                except Exception as e:
                    logger.warning(f"既存クッキー読み込みエラー: {e}")
                    all_cookies = {}

            # WordPress クッキーを更新
            wp_key = f"wp_{wp_domain.replace('.', '_')}"
            all_cookies[wp_key] = {"cookies": wp_cookies, "timestamp": time.time(), "domain": wp_url}

            # ファイルに保存
            self.wp_cookies_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.wp_cookies_file, "w", encoding="utf-8") as f:
                json.dump(all_cookies, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ WordPress クッキー保存完了: {len(wp_cookies)}個")
            return True

        except Exception as e:
            logger.error(f"❌ WordPress クッキー保存エラー: {e}")
            return False

    async def load_wordpress_cookies(self, wp_url: str) -> bool:
        """WordPress専用のクッキーを読み込み"""
        try:
            if not self.wp_cookies_file or not self.wp_cookies_file.exists():
                logger.warning("WordPress クッキーファイルが存在しません")
                return False

            if not self.context:
                logger.warning("コンテキストが初期化されていません")
                return False

            # クッキーファイルを読み込み
            with open(self.wp_cookies_file, "r", encoding="utf-8") as f:
                all_cookies = json.load(f)

            # WordPress クッキーを取得
            wp_domain = wp_url.replace("https://", "").replace("http://", "").split("/")[0]
            wp_key = f"wp_{wp_domain.replace('.', '_')}"

            if wp_key not in all_cookies:
                logger.warning(f"WordPress クッキーが見つかりません: {wp_key}")
                return False

            wp_cookie_data = all_cookies[wp_key]
            cookies = wp_cookie_data.get("cookies", [])

            if not cookies:
                logger.warning("有効な WordPress クッキーがありません")
                return False

            # 有効期限をチェック
            valid_cookies = []
            for cookie in cookies:
                if "expires" in cookie:
                    if cookie["expires"] > time.time():
                        valid_cookies.append(cookie)
                else:
                    # expires がないクッキーはセッションクッキー
                    valid_cookies.append(cookie)

            if not valid_cookies:
                logger.warning("有効期限切れのクッキーのみ存在します")
                return False

            # クッキーをコンテキストに追加
            await self.context.add_cookies(valid_cookies)
            logger.info(f"✅ WordPress クッキー読み込み完了: {len(valid_cookies)}個")

            return True

        except Exception as e:
            logger.error(f"❌ WordPress クッキー読み込みエラー: {e}")
            return False

    async def close_wp_session(self) -> None:
        """WordPressセッションを閉じる"""
        try:
            if self.wp_page:
                await self.wp_page.close()
                self.wp_page = None
                self.is_logged_in = False
                logger.info("✅ WordPressセッションを閉じました")
        except Exception as e:
            logger.warning(f"WordPressセッションクローズ中の警告: {e}")
