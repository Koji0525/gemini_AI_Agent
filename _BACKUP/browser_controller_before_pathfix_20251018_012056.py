"""
BrowserController - 既存仕様準拠版
既存のCookieSessionManager等との正しい統合
"""

import asyncio
import os
from pathlib import Path
from typing import Optional, Dict
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from dataclasses import dataclass


# ====================================================================
# カスタム例外（__init__.pyで期待されている）
# ====================================================================
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
            self.VIEWPORT = {"width": 1150, "height": 650}


class BrowserController:
    """
    ブラウザ制御のファサード
    
    既存の専門モジュールは初期化時ではなく、
    contextが利用可能になった後に初期化する
    """
    
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
            
            # contextが利用可能になった後に専門モジュールを初期化
            await self._initialize_managers()
            
            self.page = await self.context.new_page()
            self.page.set_default_timeout(self.config.NAVIGATION_TIMEOUT)
            
            print("✅ ブラウザ初期化完了")
            
        except Exception as e:
            print(f"❌ ブラウザ初期化エラー: {e}")
            await self.cleanup()
            raise BrowserOperationError(f"ブラウザ初期化失敗: {e}")
    
    async def _initialize_managers(self):
        """専門モジュールを初期化（contextが必要）"""
        try:
            # CookieSessionManagerを初期化
            from .brower_cookie_and_session import CookieSessionManager
            
            cookies_file = "./gemini_cookies.json"
            self.cookie_manager = CookieSessionManager(
                context=self.context,
                cookies_file=cookies_file
            )
            
            # クッキーを読み込む
            await self.cookie_manager.load_cookies()
            print("✅ CookieSessionManager 初期化完了")
            
        except ImportError as e:
            print(f"⚠️  CookieSessionManager インポートエラー: {e}")
        except Exception as e:
            print(f"⚠️  CookieSessionManager 初期化エラー: {e}")
        
        # WPSessionManager は必要に応じて初期化
        # （WordPressタスク実行時など）
    
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
        """ログイン状態をチェック"""
        try:
            prompt_box = await self.page.locator("textarea").count()
            return prompt_box > 0
        except:
            return False
    
    async def send_prompt(self, prompt: str) -> bool:
        """プロンプトを送信"""
        try:
            print(f"📝 プロンプト送信: {prompt[:50]}...")
            textarea = self.page.locator("textarea").first
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
                
                # 生成中インジケータをチェック
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
    
    async def extract_latest_text_response(self) -> str:
        """最新のテキストレスポンスを抽出"""
        try:
            response_elements = await self.page.locator("[data-test-id='conversation-turn-content']").all()
            
            if not response_elements:
                print("⚠️  レスポンスが見つかりません")
                return ""
            
            last_response = response_elements[-1]
            text = await last_response.inner_text()
            print(f"✅ レスポンス取得: {len(text)}文字")
            return text
        except Exception as e:
            print(f"❌ レスポンス抽出エラー: {e}")
            return ""
    
    async def cleanup(self) -> None:
        """リソースをクリーンアップ"""
        try:
            print("🧹 ブラウザをクリーンアップ中...")
            
            # クッキーを保存
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


# 後方互換性
EnhancedBrowserController = BrowserController
