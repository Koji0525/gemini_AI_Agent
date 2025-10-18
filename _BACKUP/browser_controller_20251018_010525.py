#!/usr/bin/env python3
"""
EnhancedBrowserController - 完全版
- タイムアウト管理統一
- エラーハンドリング強化
- リトライ機能
- フォールバック機能
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Callable
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

logger = logging.getLogger(__name__)

class BrowserConfig:
    """ブラウザ設定の一元管理"""
    
    # タイムアウト設定（ミリ秒）
    NAVIGATION_TIMEOUT = 60000  # ページ移動: 60秒
    ELEMENT_WAIT_TIMEOUT = 30000  # 要素待機: 30秒
    TEXT_GENERATION_TIMEOUT = 180  # テキスト生成待機: 180秒（秒単位）
    BROWSER_LAUNCH_TIMEOUT = 30000  # ブラウザ起動: 30秒
    
    # リトライ設定
    MAX_RETRIES = 3  # 最大リトライ回数
    RETRY_DELAY = 2  # リトライ間隔（秒）
    
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


class BrowserOperationError(Exception):
    """ブラウザ操作エラー"""
    pass


class EnhancedBrowserController:
    """
    強化版BrowserController
    - 完全非同期化
    - 統一されたタイムアウト管理
    - エラーハンドリング強化
    - リトライ機能
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
        self._operation_count = 0  # 操作カウント（デバッグ用）
        
        logger.info(f"✅ EnhancedBrowserController 初期化")
        logger.info(f"   Mode: {mode}, Service: {service}")
    
    async def _retry_operation(
        self,
        operation: Callable,
        operation_name: str,
        max_retries: int = None,
        *args,
        **kwargs
    ):
        """
        リトライ機能付き操作実行
        
        Args:
            operation: 実行する操作（async関数）
            operation_name: 操作名（ログ用）
            max_retries: 最大リトライ回数
            *args, **kwargs: 操作に渡す引数
            
        Returns:
            操作の結果
            
        Raises:
            BrowserOperationError: 全てのリトライが失敗
        """
        max_retries = max_retries or BrowserConfig.MAX_RETRIES
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = await operation(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"✅ {operation_name} 成功（{attempt + 1}回目）")
                return result
                
            except Exception as e:
                last_error = e
                logger.warning(
                    f"⚠️ {operation_name} 失敗（{attempt + 1}/{max_retries}回目）: {e}"
                )
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(BrowserConfig.RETRY_DELAY)
        
        # 全てのリトライが失敗
        logger.error(f"❌ {operation_name} 完全失敗: {last_error}")
        raise BrowserOperationError(
            f"{operation_name} failed after {max_retries} attempts: {last_error}"
        )
    
    async def setup_browser(self) -> None:
        """ブラウザセットアップ（リトライ付き）"""
        if self._is_initialized:
            logger.info("⚠️ ブラウザ既に初期化済み")
            return
        
        async def _setup():
            logger.info("🚀 ブラウザ起動中...")
            
            # Playwright起動
            self._playwright = await async_playwright().start()
            
            # ブラウザ起動
            self._browser = await self._playwright.chromium.launch(
                headless=BrowserConfig.HEADLESS,
                args=BrowserConfig.get_launch_args(),
                timeout=BrowserConfig.BROWSER_LAUNCH_TIMEOUT
            )
            
            # コンテキスト作成
            self._context = await self._browser.new_context(
                viewport=BrowserConfig.VIEWPORT,
                accept_downloads=True
            )
            
            # ページ作成
            self._page = await self._context.new_page()
            
            # タイムアウト設定
            self._page.set_default_timeout(BrowserConfig.NAVIGATION_TIMEOUT)
            
            self._is_initialized = True
            logger.info("✅ ブラウザ起動完了")
        
        try:
            await self._retry_operation(_setup, "ブラウザセットアップ")
        except BrowserOperationError as e:
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
        """Gemini AIに移動（リトライ付き）"""
        if not self._page:
            raise BrowserOperationError("ブラウザ未初期化")
        
        async def _navigate():
            logger.info("🔗 Gemini AIに移動中...")
            await self._page.goto(
                "https://gemini.google.com/",
                timeout=BrowserConfig.NAVIGATION_TIMEOUT,
                wait_until="domcontentloaded"
            )
            logger.info("✅ Gemini AI到達")
        
        await self._retry_operation(_navigate, "Gemini AI移動")
    
    async def navigate_to_deepseek(self) -> None:
        """DeepSeekに移動（リトライ付き）"""
        if not self._page:
            raise BrowserOperationError("ブラウザ未初期化")
        
        async def _navigate():
            logger.info("🔗 DeepSeekに移動中...")
            await self._page.goto(
                "https://chat.deepseek.com/",
                timeout=BrowserConfig.NAVIGATION_TIMEOUT,
                wait_until="domcontentloaded"
            )
            logger.info("✅ DeepSeek到達")
        
        await self._retry_operation(_navigate, "DeepSeek移動")
    
    async def send_prompt(self, prompt: str) -> bool:
        """
        プロンプト送信（リトライ付き）
        
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
                await self._retry_operation(
                    self._send_prompt_gemini,
                    "Geminiプロンプト送信",
                    max_retries=2,
                    prompt=prompt
                )
            elif self.service == "deepseek":
                await self._retry_operation(
                    self._send_prompt_deepseek,
                    "DeepSeekプロンプト送信",
                    max_retries=2,
                    prompt=prompt
                )
            else:
                logger.error(f"❌ 未対応サービス: {self.service}")
                return False
            
            self._operation_count += 1
            return True
                
        except BrowserOperationError as e:
            logger.error(f"❌ プロンプト送信完全失敗: {e}")
            return False
    
    async def _send_prompt_gemini(self, prompt: str) -> None:
        """Gemini用プロンプト送信（エラー時は例外を投げる）"""
        # 入力欄を探す（優先度順）
        selectors = [
            'div[contenteditable="true"]',
            'textarea.ql-editor',
            'textarea[placeholder*="Enter"]',
            'div.ql-editor[contenteditable="true"]',
            'rich-textarea'
        ]
        
        input_box = None
        for selector in selectors:
            try:
                input_box = await self._page.wait_for_selector(
                    selector,
                    timeout=BrowserConfig.ELEMENT_WAIT_TIMEOUT
                )
                if input_box:
                    logger.debug(f"   入力欄検出: {selector}")
                    break
            except:
                continue
        
        if not input_box:
            # デバッグスクショ
            await self._page.screenshot(path='logs/browser/debug_no_input.png')
            raise BrowserOperationError("入力欄が見つかりません")
        
        # プロンプト入力
        await input_box.click()
        await asyncio.sleep(0.3)
        await input_box.fill(prompt)
        await asyncio.sleep(0.5)
        
        # 送信（Enterキー）
        await input_box.press('Enter')
        logger.info("✅ プロンプト送信完了")
    
    async def _send_prompt_deepseek(self, prompt: str) -> None:
        """DeepSeek用プロンプト送信"""
        raise BrowserOperationError("DeepSeek送信は未実装")
    
    async def wait_for_text_generation(self, max_wait: int = None) -> bool:
        """
        テキスト生成完了を待機
        
        Args:
            max_wait: 最大待機時間（秒）
            
        Returns:
            完了: True, タイムアウト: False
        """
        max_wait = max_wait or BrowserConfig.TEXT_GENERATION_TIMEOUT
        
        if not self._page:
            logger.error("❌ ブラウザ未初期化")
            return False
        
        logger.info(f"⏳ テキスト生成待機中（最大{max_wait}秒）...")
        
        try:
            start_time = asyncio.get_event_loop().time()
            
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > max_wait:
                    logger.warning(f"⚠️ タイムアウト（{max_wait}秒）")
                    return False
                
                # 生成中インジケータ確認
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
            
            # レスポンス要素を探す（優先度順）
            selectors = [
                'div[data-message-author-role="assistant"]',
                'div.model-response-text',
                'div.markdown-content',
                'div.message-content',
                '[data-test-id="model-response"]'
            ]
            
            for selector in selectors:
                try:
                    elements = await self._page.query_selector_all(selector)
                    if elements:
                        last_element = elements[-1]
                        text = await last_element.inner_text()
                        
                        if text and text.strip():
                            logger.info(f"✅ テキスト抽出成功（{len(text)}文字, {selector}）")
                            return text.strip()
                except Exception as e:
                    logger.debug(f"   セレクタ {selector} 失敗: {e}")
                    continue
            
            # セレクタで見つからない場合
            logger.warning("⚠️ セレクタでレスポンスが見つかりません")
            
            # デバッグスクショ
            await self._page.screenshot(path='logs/browser/debug_no_response.png')
            logger.info("   📸 デバッグスクショ: logs/browser/debug_no_response.png")
            
            return None
            
        except Exception as e:
            logger.error(f"❌ テキスト抽出エラー: {e}")
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
        if not await self.send_prompt(prompt):
            return False
        
        await asyncio.sleep(2)
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
