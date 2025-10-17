#!/usr/bin/env python3
"""
Enhanced BrowserController - 完全非同期版（修正版）
downloads_pathパラメータエラーを修正
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

logger = logging.getLogger(__name__)

class BrowserConfig:
    """ブラウザ設定の一元管理"""
    
    # タイムアウト設定（秒）
    NAVIGATION_TIMEOUT = 60  # ページ移動
    ELEMENT_WAIT_TIMEOUT = 30  # 要素待機
    TEXT_GENERATION_TIMEOUT = 180  # テキスト生成待機
    BROWSER_LAUNCH_TIMEOUT = 30  # ブラウザ起動
    
    # ブラウザ設定
    VIEWPORT = {'width': 1150, 'height': 650}
    HEADLESS = True
    
    @classmethod
    def get_launch_args(cls) -> list:
        """ブラウザ起動引数取得"""
        return [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled'
        ]


class EnhancedBrowserController:
    """
    強化版BrowserController
    - 完全非同期化
    - 統一されたエラーハンドリング
    - タイムアウト管理の一元化
    """
    
    def __init__(
        self,
        download_folder: Path,
        mode: str = "image",
        service: str = "google",
        credentials: Dict = None
    ):
        """
        初期化
        
        Args:
            download_folder: ダウンロードフォルダ
            mode: 動作モード ("image", "text", "hybrid")
            service: 使用サービス ("google", "deepseek")
            credentials: 認証情報
        """
        self.download_folder = Path(download_folder)
        self.download_folder.mkdir(parents=True, exist_ok=True)
        
        self.mode = mode
        self.service = service
        self.credentials = credentials or {}
        
        # Playwright インスタンス
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        
        # 状態管理
        self._is_initialized = False
        self._is_logged_in = False
        
        logger.info(f"✅ EnhancedBrowserController 初期化")
        logger.info(f"   Mode: {mode}, Service: {service}")
    
    async def setup_browser(self) -> None:
        """ブラウザセットアップ"""
        if self._is_initialized:
            logger.info("⚠️ ブラウザ既に初期化済み")
            return
        
        try:
            logger.info("🚀 ブラウザ起動中...")
            
            # Playwright起動
            self._playwright = await async_playwright().start()
            
            # ブラウザ起動
            self._browser = await self._playwright.chromium.launch(
                headless=BrowserConfig.HEADLESS,
                args=BrowserConfig.get_launch_args()
            )
            
            # コンテキスト作成（修正: downloads_pathを削除）
            self._context = await self._browser.new_context(
                viewport=BrowserConfig.VIEWPORT,
                accept_downloads=True
                # downloads_path は使用しない（Playwrightで非対応）
            )
            
            # ページ作成
            self._page = await self._context.new_page()
            
            # タイムアウト設定
            self._page.set_default_timeout(
                BrowserConfig.NAVIGATION_TIMEOUT * 1000
            )
            
            self._is_initialized = True
            logger.info("✅ ブラウザ起動完了")
            
        except Exception as e:
            logger.error(f"❌ ブラウザ起動失敗: {e}")
            await self.cleanup()
            raise
    
    @property
    def page(self) -> Optional[Page]:
        """現在のページ取得"""
        return self._page
    
    @property
    def context(self) -> Optional[BrowserContext]:
        """現在のコンテキスト取得"""
        return self._context
    
    @property
    def is_initialized(self) -> bool:
        """初期化状態"""
        return self._is_initialized
    
    async def navigate_to_gemini(self) -> None:
        """Gemini AIに移動"""
        if not self._page:
            raise RuntimeError("ブラウザ未初期化")
        
        logger.info("🔗 Gemini AIに移動中...")
        await self._page.goto(
            "https://gemini.google.com/",
            timeout=BrowserConfig.NAVIGATION_TIMEOUT * 1000,
            wait_until="domcontentloaded"
        )
        logger.info("✅ Gemini AI到達")
    
    async def navigate_to_deepseek(self) -> None:
        """DeepSeekに移動"""
        if not self._page:
            raise RuntimeError("ブラウザ未初期化")
        
        logger.info("🔗 DeepSeekに移動中...")
        await self._page.goto(
            "https://chat.deepseek.com/",
            timeout=BrowserConfig.NAVIGATION_TIMEOUT * 1000,
            wait_until="domcontentloaded"
        )
        logger.info("✅ DeepSeek到達")
    
    async def send_prompt(self, prompt: str) -> bool:
        """
        プロンプト送信
        
        Args:
            prompt: 送信するプロンプト
            
        Returns:
            送信成功: True, 失敗: False
        """
        if not self._page:
            logger.error("❌ ブラウザ未初期化")
            return False
        
        try:
            logger.info(f"📝 プロンプト送信: {prompt[:50]}...")
            
            # サービスに応じた処理
            if self.service == "google":
                return await self._send_prompt_gemini(prompt)
            elif self.service == "deepseek":
                return await self._send_prompt_deepseek(prompt)
            else:
                logger.error(f"❌ 未対応サービス: {self.service}")
                return False
                
        except Exception as e:
            logger.error(f"❌ プロンプト送信失敗: {e}")
            return False
    
    async def _send_prompt_gemini(self, prompt: str) -> bool:
        """Gemini用プロンプト送信"""
        try:
            # 入力欄を探す（複数のセレクタを試行）
            selectors = [
                'textarea.ql-editor',
                'div[contenteditable="true"]',
                'textarea[placeholder*="Enter"]',
                'div.ql-editor[contenteditable="true"]',
                'rich-textarea'
            ]
            
            input_box = None
            for selector in selectors:
                try:
                    input_box = await self._page.wait_for_selector(
                        selector,
                        timeout=BrowserConfig.ELEMENT_WAIT_TIMEOUT * 1000
                    )
                    if input_box:
                        logger.info(f"   ✅ 入力欄検出: {selector}")
                        break
                except:
                    continue
            
            if not input_box:
                logger.error("❌ 入力欄が見つかりません")
                # デバッグ: ページ内容を確認
                await self._page.screenshot(path='logs/browser/debug_no_input.png')
                logger.info("   📸 デバッグスクショ保存: logs/browser/debug_no_input.png")
                return False
            
            # プロンプト入力
            await input_box.click()  # フォーカス
            await asyncio.sleep(0.3)
            await input_box.fill(prompt)
            await asyncio.sleep(0.5)
            
            # 送信（Enterキー）
            await input_box.press('Enter')
            logger.info("✅ プロンプト送信完了")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Geminiプロンプト送信エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _send_prompt_deepseek(self, prompt: str) -> bool:
        """DeepSeek用プロンプト送信"""
        try:
            # DeepSeek用の実装
            logger.warning("⚠️ DeepSeek送信は未実装")
            return False
            
        except Exception as e:
            logger.error(f"❌ DeepSeekプロンプト送信エラー: {e}")
            return False
    
    async def wait_for_text_generation(self, max_wait: int = 180) -> bool:
        """
        テキスト生成完了を待機
        
        Args:
            max_wait: 最大待機時間（秒）
            
        Returns:
            完了: True, タイムアウト: False
        """
        if not self._page:
            logger.error("❌ ブラウザ未初期化")
            return False
        
        logger.info(f"⏳ テキスト生成待機中（最大{max_wait}秒）...")
        
        try:
            # 生成中インジケータの消失を待つ
            start_time = asyncio.get_event_loop().time()
            
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > max_wait:
                    logger.warning(f"⚠️ タイムアウト（{max_wait}秒）")
                    return False
                
                # 生成中インジケータ確認（複数パターン）
                generating_selectors = [
                    'button[aria-label*="Stop"]',
                    'button[aria-label*="stop"]',
                    '.generating-indicator',
                    '[data-test-id="stop-button"]'
                ]
                
                is_generating = False
                for selector in generating_selectors:
                    try:
                        element = await self._page.query_selector(selector)
                        if element and await element.is_visible():
                            is_generating = True
                            break
                    except:
                        pass
                
                if not is_generating:
                    logger.info("✅ テキスト生成完了")
                    return True
                
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ 待機エラー: {e}")
            return False
    
    async def extract_latest_text_response(
        self,
        allow_partial: bool = True
    ) -> Optional[str]:
        """
        最新のテキストレスポンス抽出
        
        Args:
            allow_partial: 部分的なレスポンスも許可
            
        Returns:
            抽出されたテキスト、失敗時None
        """
        if not self._page:
            logger.error("❌ ブラウザ未初期化")
            return None
        
        try:
            logger.info("📄 レスポンステキスト抽出中...")
            
            # レスポンス要素を探す（複数パターン）
            selectors = [
                'div.model-response-text',
                'div[data-message-author-role="assistant"]',
                'div.markdown-content',
                'div.message-content',
                '[data-test-id="model-response"]'
            ]
            
            for selector in selectors:
                try:
                    elements = await self._page.query_selector_all(selector)
                    if elements:
                        # 最後の要素のテキスト取得
                        last_element = elements[-1]
                        text = await last_element.inner_text()
                        
                        if text and text.strip():
                            logger.info(f"✅ テキスト抽出成功（{len(text)}文字, {selector}）")
                            return text.strip()
                except Exception as e:
                    logger.debug(f"   セレクタ {selector} 失敗: {e}")
                    continue
            
            # セレクタで見つからない場合、ページ全体から抽出を試みる
            logger.warning("⚠️ セレクタでレスポンスが見つかりません。ページ全体を確認...")
            body_text = await self._page.inner_text('body')
            logger.info(f"   ページテキスト（最初の200文字）: {body_text[:200]}")
            
            # デバッグスクショ
            await self._page.screenshot(path='logs/browser/debug_response.png')
            logger.info("   📸 デバッグスクショ: logs/browser/debug_response.png")
            
            return None
            
        except Exception as e:
            logger.error(f"❌ テキスト抽出エラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def send_prompt_and_wait(
        self,
        prompt: str,
        max_wait: int = 120
    ) -> bool:
        """
        プロンプト送信して完了を待機
        
        Args:
            prompt: 送信するプロンプト
            max_wait: 最大待機時間
            
        Returns:
            成功: True, 失敗: False
        """
        # 送信
        if not await self.send_prompt(prompt):
            return False
        
        # 待機
        await asyncio.sleep(2)  # 送信完了待ち
        return await self.wait_for_text_generation(max_wait)
    
    async def save_text_to_file(
        self,
        text: str,
        filename: str
    ) -> bool:
        """
        テキストをファイルに保存
        
        Args:
            text: 保存するテキスト
            filename: ファイル名
            
        Returns:
            成功: True, 失敗: False
        """
        try:
            file_path = Path(filename)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(text, encoding='utf-8')
            logger.info(f"✅ テキスト保存: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ ファイル保存エラー: {e}")
            return False
    
    async def cleanup(self) -> None:
        """クリーンアップ"""
        logger.info("🧹 ブラウザクリーンアップ中...")
        
        try:
            if self._page:
                await self._page.close()
                self._page = None
            
            if self._context:
                await self._context.close()
                self._context = None
            
            if self._browser:
                await self._browser.close()
                self._browser = None
            
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
            
            self._is_initialized = False
            logger.info("✅ クリーンアップ完了")
            
        except Exception as e:
            logger.error(f"⚠️ クリーンアップエラー: {e}")


# 後方互換性のためのエイリアス
BrowserController = EnhancedBrowserController
