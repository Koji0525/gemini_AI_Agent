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
        
        # 専門モジュール（後で初期化）
        self.cookie_manager = None
        self.wp_session = None
        
        os.makedirs(self.download_folder, exist_ok=True)
    
    async def setup_browser(self) -> None:
        """ブラウザを初期化"""
        print("🌐 ブラウザを初期化中...")
        
        try:
            self.playwright = await async_playwright().start()
            
            self.browser = await self.playwright.chromium.launch(
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            self.context = await self.browser.new_context(
                viewport=self.config.VIEWPORT,
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            # 専門モジュール初期化
            await self._initialize_managers()
            
            self.page = await self.context.new_page()
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
                context=self.context,
                cookies_file=cookies_file  # Pathオブジェクト
            )
            
            # クッキーを読み込む
            await self.cookie_manager.load_cookies()
            print("✅ CookieSessionManager 初期化完了")
            
        except ImportError as e:
            print(f"⚠️  CookieSessionManager インポートエラー: {e}")
        except Exception as e:
            print(f"⚠️  CookieSessionManager 初期化エラー: {e}")
    
    async def navigate_to_gemini(self) -> bool:
        """Gemini AIに移動"""
        try:
            print("📱 Gemini AIに移動中...")
            await self.page.goto(self.config.GEMINI_URL, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
            
            is_logged_in = await self._check_login_status()
            print(f"{'✅' if is_logged_in else '⚠️ '} ログイン状態: {is_logged_in}")
            
            return is_logged_in
        except Exception as e:
            print(f"❌ Gemini移動エラー: {e}")
            raise BrowserOperationError(f"Gemini移動失敗: {e}")
    
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
    
    async def send_prompt(self, prompt: str) -> bool:
        """プロンプトを送信"""
        try:
            print(f"📝 プロンプト送信: {prompt[:50]}...")
            textarea = self.page.locator("div[contenteditable='true']").first
            await textarea.fill(prompt)
            await asyncio.sleep(0.5)
            await textarea.press("Enter")
            print("✅ プロンプト送信完了")
            return True
        except Exception as e:
            print(f"❌ プロンプト送信エラー: {e}")
            raise BrowserOperationError(f"プロンプト送信失敗: {e}")
    
    async def wait_for_text_generation(self, max_wait: int = 60) -> bool:
        """テキスト生成完了を待機"""
        try:
            print("⏳ レスポンス生成を待機中...")
            
            for i in range(max_wait):
                await asyncio.sleep(1)
                is_generating = await self.page.locator("[data-test-id='generation-in-progress']").count() > 0
                
                if not is_generating:
                    print("✅ レスポンス生成完了")
                    return True
                
                if i % 10 == 0 and i > 0:
                    print(f"   待機中... ({i}秒)")
            
            print("⚠️  タイムアウト")
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
                ".markdown",             # マークダウンレンダラー
                ".response-container",   # レスポンスコンテナ
                "message-content",       # カスタム要素
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


EnhancedBrowserController = BrowserController
