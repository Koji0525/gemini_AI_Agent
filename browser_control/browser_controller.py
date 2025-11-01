"""
BrowserController - 完全修正版
- Pathオブジェクト使用
- VNC解像度 1150x600
- 既存モジュール正しく統合
"""

import asyncio
import os
from pathlib import Path
from typing import Optional, Dict
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from dataclasses import dataclass


class BrowserOperationError(Exception):
    """ブラウザ操作エラー"""

    pass


@dataclass
class BrowserConfig:
    """ブラウザ設定"""

    GEMINI_URL: str = "https://gemini.google.com/app"
    NAVIGATION_TIMEOUT: int = 60000
    VIEWPORT: Dict[str, int] = None

    def __post_init__(self):
        if self.VIEWPORT is None:
            # 正しい解像度: 1150x600
            self.VIEWPORT = {"width": 1150, "height": 600}


class BrowserController:
    """ブラウザ制御のファサード（完全修正版）"""

    def __init__(self, download_folder: str = None):
        self.config = BrowserConfig()
        self.download_folder = download_folder or "./downloads"

        # Playwright関連
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.gemini_page: Optional[Page] = None  # Gemini専用ページ

        # 専門モジュール（後で初期化）
        self.cookie_manager = None
        self.wp_session = None

        os.makedirs(self.download_folder, exist_ok=True)

    async def setup_browser(self, headless=True) -> None:
        """ブラウザを初期化"""
        print("🌐 ブラウザを初期化中...")

        try:
            self.playwright = await async_playwright().start()

            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                ],
            )

            self.context = await self.browser.new_context(
                viewport=self.config.VIEWPORT, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )

            # 専門モジュール初期化
            await self._initialize_managers()

            self.page = await self.context.new_page()
            self.gemini_page = self.page  # Gemini専用ページとして保存
            self.page.set_default_timeout(self.config.NAVIGATION_TIMEOUT)

            print("✅ ブラウザ初期化完了")

        except Exception as e:
            print(f"❌ ブラウザ初期化エラー: {e}")
            await self.cleanup()
            raise BrowserOperationError(f"ブラウザ初期化失敗: {e}")

    async def _initialize_managers(self):
        """専門モジュールを初期化（修正版：Pathオブジェクト使用）"""
        try:
            from .brower_cookie_and_session import CookieSessionManager

            # 重要：Pathオブジェクトとして渡す
            cookies_file = Path("./gemini_cookies.json")

            self.cookie_manager = CookieSessionManager(
                context=self.context, cookies_file=cookies_file  # Pathオブジェクト
            )

            # クッキーを読み込む
            await self.cookie_manager.load_cookies()
            print("✅ CookieSessionManager 初期化完了")

        except ImportError as e:
            print(f"⚠️  CookieSessionManager インポートエラー: {e}")
        except Exception as e:
            print(f"⚠️  CookieSessionManager 初期化エラー: {e}")

    async def navigate_to_gemini(self, max_retries: int = 3) -> bool:
        """
        Gemini AIに移動（リトライ機能付き）

        Args:
            max_retries: 最大リトライ回数

        Returns:
            bool: ログイン状態
        """
        for attempt in range(max_retries):
            try:
                print(f"📱 Gemini AIに移動中... (試行 {attempt + 1}/{max_retries})")

                # タイムアウトを段階的に増加（30秒 → 60秒 → 90秒）
                timeout = 30000 + (attempt * 30000)

                await self.page.goto(
                    "https://gemini.google.com/app",
                    timeout=timeout,
                    wait_until="domcontentloaded",  # networkidle より軽い
                )

                # ページ読み込み待機
                await asyncio.sleep(3)

                # ログイン状態確認
                is_logged_in = await self._check_login_status()

                if is_logged_in:
                    print("✅ ログイン状態: True")
                    return True
                else:
                    print("⚠️  ログインが必要です")
                    return False

            except Exception as e:
                print(f"⚠️  試行 {attempt + 1} 失敗: {e}")

                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"   {wait_time}秒後に再試行...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"❌ {max_retries}回試行しましたが失敗しました")
                    raise

    async def _check_login_status(self) -> bool:
        """ログイン状態をチェック（修正版）"""
        try:
            # Geminiの新しいUI: contenteditable div
            contenteditable = await self.page.locator("[contenteditable='true']").count()
            if contenteditable > 0:
                return True

            # 古いUI: textarea（念のため）
            textarea = await self.page.locator("div[contenteditable='true']").count()
            if textarea > 0:
                return True

            # ログインボタンがあれば未ログイン
            login_button = await self.page.locator("text=Sign in").count()
            if login_button > 0:
                return False

            return False
        except:
            return False

    async def send_prompt(self, prompt: str, timeout: int = 60000, max_retries: int = 3) -> None:
        """
        Geminiにプロンプトを送信（.ql-editor使用版）

        Args:
            prompt: 送信するプロンプト
            timeout: タイムアウト時間（ミリ秒）
            max_retries: 最大リトライ回数
        """
        page = self.gemini_page if self.gemini_page else self.page

        for attempt in range(max_retries):
            try:
                print(f"📝 プロンプト送信: {prompt[:80]}...")

                # .ql-editorを直接使用（rich-textareaの内部要素）
                textarea = await page.locator(".ql-editor").first

                if not await textarea.is_visible():
                    if attempt < max_retries - 1:
                        wait_time = 3 * (attempt + 1)
                        print(f"⚠️  試行 {attempt + 1}/{max_retries} 失敗: 入力欄が見えません")
                        print(f"   {wait_time}秒後に再試行...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise Exception("入力欄が見つかりません")

                print(f"✅ 入力欄発見: .ql-editor")

                # クリックしてフォーカス
                await textarea.click()
                await asyncio.sleep(0.5)

                # クリア（Ctrl+A → Delete）
                await page.keyboard.press("Control+A")
                await asyncio.sleep(0.2)
                await page.keyboard.press("Backspace")
                await asyncio.sleep(0.3)

                # テキスト入力（type使用）
                await textarea.type(prompt, delay=50)
                await asyncio.sleep(0.5)

                # Enter送信
                await page.keyboard.press("Enter")

                print("✅ プロンプト送信完了")
                return

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    print(f"⚠️  エラー発生（試行 {attempt + 1}/{max_retries}）: {e}")
                    print(f"   {wait_time}秒後に再試行...")
                    await asyncio.sleep(wait_time)
                else:
                    await page.screenshot(path="error_send_prompt.png")
                    raise Exception(f"プロンプト送信失敗: {e}")

    async def wait_for_text_generation(self, max_wait: int = 120, min_stable_time: int = 7) -> bool:
        """
        Geminiのテキスト生成完了を待機（長文対応版）

        Args:
            max_wait: 最大待機時間（秒）デフォルト120秒
            min_stable_time: 安定判定の回数（秒）デフォルト7秒

        Returns:
            bool: 生成完了したかどうか

        判定ロジック:
        - 1秒ごとに文字数をチェック
        - 短文（1,000文字未満）: 3秒安定で完了
        - 中文（1,000-3,000文字）: 5秒安定で完了
        - 長文（3,000文字以上）: 7秒安定で完了
        """
        try:
            print("⏳ レスポンス生成を待機中...")

            start_time = asyncio.get_event_loop().time()
            last_length = 0
            stable_count = 0
            max_length_seen = 0  # これまでの最大文字数

            while (asyncio.get_event_loop().time() - start_time) < max_wait:
                # レスポンス要素を探す
                selectors = [".response-container", ".model-response-text", ".markdown"]

                current_text = ""

                for selector in selectors:
                    try:
                        elements = await self.page.locator(selector).all()
                        if elements:
                            last_elem = elements[-1]
                            if await last_elem.is_visible():
                                current_text = await last_elem.text_content() or ""
                                break
                    except:
                        continue

                current_length = len(current_text.strip())

                # 最大文字数を記録
                if current_length > max_length_seen:
                    max_length_seen = current_length

                # 50文字以上なら実際のレスポンス
                if current_length > 50:
                    # 文字数に応じて必要な安定時間を決定
                    if current_length < 1000:
                        required_stable = 3  # 短文: 3秒
                    elif current_length < 3000:
                        required_stable = 5  # 中文: 5秒
                    else:
                        required_stable = 7  # 長文: 7秒

                    # 文字数が安定しているか確認
                    if current_length == last_length:
                        stable_count += 1

                        # 必要な安定時間に達したら完了
                        if stable_count >= required_stable:
                            print(f"✅ レスポンス生成完了（{current_length} 文字、{required_stable}秒安定）")
                            return True
                        else:
                            # 安定中の表示
                            if stable_count % 2 == 0:  # 2秒ごとに表示
                                print(f"   安定確認中... {current_length} 文字（{stable_count}/{required_stable}秒）")
                    else:
                        # 文字数が増えた
                        stable_count = 0
                        last_length = current_length

                        # 進捗表示（100文字ごと）
                        if current_length % 100 < 50 and current_length > 100:
                            print(f"   生成中... {current_length} 文字")

                # 1秒待機
                await asyncio.sleep(1)

            # タイムアウト
            elapsed = int(asyncio.get_event_loop().time() - start_time)
            print(f"⚠️  待機タイムアウト（{elapsed}秒）")

            # タイムアウトでも50文字以上あれば部分的に成功
            if max_length_seen > 50:
                print(f"   ただし、{max_length_seen}文字のレスポンスを取得済み")
                print(f"   最終的な文字数: {last_length}")
                return True

            return False

        except Exception as e:
            print(f"❌ 待機エラー: {e}")
            return False

    async def extract_latest_text_response(self):
        """
        最新のレスポンステキストを取得

        Returns:
            str: レスポンステキスト（取得できない場合は空文字列）
        """
        try:
            print("📖 レスポンステキスト取得中...")

            # 優先順位の高いセレクタから順に試行
            selectors = [
                ".model-response-text",  # 最も確実
                ".markdown",  # マークダウンレンダラー
                ".response-container",  # レスポンスコンテナ
                "message-content",  # カスタム要素
            ]

            for selector in selectors:
                try:
                    elements = await self.page.locator(selector).all()
                    if elements:
                        # 最後の要素（最新のレスポンス）を取得
                        last_element = elements[-1]

                        # 表示されているか確認
                        is_visible = await last_element.is_visible()
                        if is_visible:
                            text = await last_element.text_content()
                            if text and len(text.strip()) > 10:  # 10文字以上
                                print(f"✅ レスポンス取得成功: {selector} ({len(text)} 文字)")
                                return text.strip()
                except Exception as e:
                    # デバッグ用（オプション）
                    # print(f"   {selector} で取得失敗: {e}")
                    continue

            print("⚠️  レスポンスが見つかりません")
            return ""

        except Exception as e:
            print(f"❌ レスポンス取得エラー: {e}")
            return ""

    async def cleanup(self) -> None:
        """リソースをクリーンアップ"""
        try:
            print("🧹 ブラウザをクリーンアップ中...")

            if self.cookie_manager:
                try:
                    await self.cookie_manager.save_cookies()
                except Exception as e:
                    print(f"⚠️  クッキー保存エラー: {e}")

            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()

            print("✅ クリーンアップ完了")
        except Exception as e:
            print(f"⚠️  クリーンアップエラー: {e}")

    async def __aenter__(self):
        await self.setup_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    async def load_wordpress_cookies(self, wp_url: str) -> bool:
        """
        WordPressのクッキーを読み込み

        Args:
            wp_url: WordPress サイトURL

        Returns:
            bool: 読み込み成功時 True
        """
        try:
            import json

            cookies_file = Path("wordpress_cookies.json")
            if not cookies_file.exists():
                print("📝 WordPressクッキーファイルが見つかりません")
                return False

            with open(cookies_file, "r") as f:
                cookies = json.load(f)

            if not cookies:
                print("📝 クッキーが空です")
                return False

            if self.context:
                await self.context.add_cookies(cookies)
                print(f"✅ WordPressクッキーを読み込みました: {len(cookies)}個")
                return True
            else:
                print("❌ コンテキストが初期化されていません")
                return False

        except Exception as e:
            print(f"❌ WordPressクッキー読み込みエラー: {e}")
            return False

    async def save_wordpress_cookies(self, wp_url: str) -> bool:
        """
        WordPressのクッキーを保存

        Args:
            wp_url: WordPress サイトURL

        Returns:
            bool: 保存成功時 True
        """
        try:
            import json
            from urllib.parse import urlparse

            if not self.context:
                print("❌ コンテキストが初期化されていません")
                return False

            # 現在のクッキーを取得
            cookies = await self.context.cookies()

            # WordPressドメインのクッキーのみフィルタ
            wp_domain = urlparse(wp_url).netloc
            wp_cookies = [c for c in cookies if wp_domain in c.get("domain", "")]

            # 保存
            cookies_file = Path("wordpress_cookies.json")
            with open(cookies_file, "w") as f:
                json.dump(wp_cookies, f, indent=2)

            print(f"✅ WordPressクッキーを保存しました: {len(wp_cookies)}個")
            return True

        except Exception as e:
            print(f"❌ WordPressクッキー保存エラー: {e}")
            return False


EnhancedBrowserController = BrowserController
