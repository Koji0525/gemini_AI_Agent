# browser_controller.py
"""ブラウザ制御クラス（分割リファクタリング版）"""
import asyncio
from pathlib import Path
from typing import Optional, Dict
import logging

from browser_lifecycle import BrowserLifecycleManager
from brower_cookie_and_session import CookieSessionManager  # ファイル名修正
from browser_ai_chat_agent import AIChatAgent
from browser_wp_session_manager import WPSessionManager
from config_utils import config, ErrorHandler

logger = logging.getLogger(__name__)

class BrowserController:
    """ブラウザ制御ファサードクラス"""
    
    def __init__(self, download_folder: Path, mode: str = "image", service: str = "google", credentials: Dict = None):
        self.download_folder = download_folder
        self.mode = mode
        self.service = service.lower()
        self.credentials = credentials or {}
        
        # 設定ファイルのパス
        self.cookies_file = Path(config.COOKIES_FILE) if config.COOKIES_FILE else None
        self.browser_data_dir = Path(config.BROWSER_DATA_DIR) if config.BROWSER_DATA_DIR else None
        self.wp_cookies_file = Path(config.BROWSER_DATA_DIR) / "wp_cookies.json" if config.BROWSER_DATA_DIR else None
        
        # マネージャーの初期化（setup_browserで完全初期化）
        self.lifecycle_manager: Optional[BrowserLifecycleManager] = None
        self.session_manager: Optional[CookieSessionManager] = None
        self.ai_agent: Optional[AIChatAgent] = None
        self.wp_manager: Optional[WPSessionManager] = None
    
    async def setup_browser(self) -> None:
        """ブラウザのセットアップ - すべてのマネージャーを初期化"""
        try:
            # ライフサイクルマネージャーの初期化とセットアップ
            self.lifecycle_manager = BrowserLifecycleManager(
                browser_data_dir=self.browser_data_dir,
                download_folder=self.download_folder
            )
            await self.lifecycle_manager.setup_browser()
            
            # セッションマネージャーの初期化
            self.session_manager = CookieSessionManager(
                context=self.lifecycle_manager.context,
                cookies_file=self.cookies_file
            )
            
            # AIチャットエージェントの初期化
            self.ai_agent = AIChatAgent(
                page=self.lifecycle_manager.page,
                service=self.service,
                credentials=self.credentials
            )
            
            # WordPressセッションマネージャーの初期化
            self.wp_manager = WPSessionManager(
                context=self.lifecycle_manager.context,
                wp_cookies_file=self.wp_cookies_file
            )
            
            logger.info(f"✅ ブラウザ制御ファサード初期化完了（サービス: {self.service}）")
            
        except Exception as e:
            ErrorHandler.log_error(e, "ブラウザファサードセットアップ")
            raise
    
    # プロパティの委譲
    @property
    def context(self):
        return self.lifecycle_manager.context if self.lifecycle_manager else None
    
    @property
    def page(self):
        return self.lifecycle_manager.page if self.lifecycle_manager else None
    
    @property
    def wp_page(self):
        return self.wp_manager.wp_page if self.wp_manager else None
    
    @property
    def is_logged_in(self):
        return self.wp_manager.is_logged_in if self.wp_manager else False
    
    # AIチャット関連メソッドの委譲
    async def navigate_to_gemini(self) -> None:
        """Geminiにナビゲート - AIエージェントに委譲"""
        if not self.ai_agent:
            raise Exception("AIエージェントが初期化されていません")
        await self.ai_agent.navigate_to_gemini()
    
    async def navigate_to_deepseek(self) -> None:
        """DeepSeekにナビゲート - AIエージェントに委譲"""
        if not self.ai_agent:
            raise Exception("AIエージェントが初期化されていません")
        await self.ai_agent.navigate_to_deepseek()
    
    async def send_prompt(self, prompt: str) -> None:
        """プロンプト送信 - AIエージェントに委譲"""
        if not self.ai_agent:
            raise Exception("AIエージェントが初期化されていません")
        await self.ai_agent.send_prompt(prompt)
    
    async def wait_for_text_generation(self, max_wait: int = 120) -> bool:
        """テキスト生成待機 - AIエージェントに委譲"""
        if not self.ai_agent:
            raise Exception("AIエージェントが初期化されていません")
        return await self.ai_agent.wait_for_text_generation(max_wait)
    
    async def extract_latest_text_response(self) -> str:
        """最新のテキスト応答抽出 - AIエージェントに委譲"""
        if not self.ai_agent:
            raise Exception("AIエージェントが初期化されていません")
        return await self.ai_agent.extract_latest_text_response()
    
    async def send_prompt_and_wait(self, prompt: str, max_wait: int = 120) -> bool:
        """プロンプト送信と待機 - AIエージェントに委譲"""
        if not self.ai_agent:
            raise Exception("AIエージェントが初期化されていません")
        return await self.ai_agent.send_prompt_and_wait(prompt, max_wait)
    
    # クッキー管理の委譲
    async def save_cookies(self) -> None:
        """クッキー保存 - セッションマネージャーに委譲"""
        if not self.session_manager:
            raise Exception("セッションマネージャーが初期化されていません")
        await self.session_manager.save_cookies()
    
    async def load_cookies(self) -> bool:
        """クッキー読み込み - セッションマネージャーに委譲"""
        if not self.session_manager:
            logger.warning("セッションマネージャーが初期化されていません")
            return False
        return await self.session_manager.load_cookies()
    
    # WordPress関連メソッドの委譲
    async def initialize_wp_session(self, auth_module=None) -> bool:
        """WordPressセッション初期化 - WPマネージャーに委譲"""
        if not self.wp_manager:
            raise Exception("WordPressマネージャーが初期化されていません")
        return await self.wp_manager.initialize_wp_session(auth_module)
    
    async def save_wordpress_cookies(self, wp_url: str) -> bool:
        """WordPressクッキー保存 - WPマネージャーに委譲"""
        if not self.wp_manager:
            raise Exception("WordPressマネージャーが初期化されていません")
        return await self.wp_manager.save_wordpress_cookies(wp_url)
    
    async def load_wordpress_cookies(self, wp_url: str) -> bool:
        """WordPressクッキー読み込み - WPマネージャーに委譲"""
        if not self.wp_manager:
            raise Exception("WordPressマネージャーが初期化されていません")
        return await self.wp_manager.load_wordpress_cookies(wp_url)
    
    # クリーンアップの委譲
    async def cleanup(self) -> None:
        """リソースクリーンアップ - ライフサイクルマネージャーに委譲"""
        # WordPressセッションを閉じる
        if self.wp_manager:
            await self.wp_manager.close_wp_session()
        
        # メインのブラウザリソースをクリーンアップ
        if self.lifecycle_manager:
            await self.lifecycle_manager.cleanup()
    
    # ユーティリティメソッド
    async def save_text_to_file(self, text: str, filename: str) -> bool:
        """テキストファイル保存 - ユーティリティとして維持"""
        try:
            save_path = self.download_folder / filename
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(text)
            if save_path.exists():
                file_size = save_path.stat().st_size
                logger.info(f"✅ テキスト保存成功: {filename} ({file_size:,} bytes)")
                return True
            else:
                logger.error(f"❌ テキスト保存失敗: {filename}")
                return False
        except Exception as e:
            ErrorHandler.log_error(e, "テキストファイル保存")
            return False
    
    # 後方互換性のためのメソッド
    async def _is_browser_alive(self) -> bool:
        """ブラウザ生存確認 - ライフサイクルマネージャーに委譲"""
        if not self.lifecycle_manager:
            return False
        return await self.lifecycle_manager._is_browser_alive()
    
    async def handle_welcome_screens(self) -> None:
        """ウェルカム画面処理 - AIエージェントに委譲"""
        if not self.ai_agent:
            raise Exception("AIエージェントが初期化されていません")
        await self.ai_agent.handle_welcome_screens()
    
    async def ensure_normal_chat_mode(self) -> None:
        """通常チャットモード確認 - AIエージェントに委譲"""
        if not self.ai_agent:
            raise Exception("AIエージェントが初期化されていません")
        await self.ai_agent.ensure_normal_chat_mode()
    
    # 非推奨メソッド（後方互換性のため）
    async def _wait_for_generation_complete(self, max_wait: int = 120) -> bool:
        """非推奨メソッド - 後方互換性のため維持"""
        logger.warning("⚠️ 非推奨メソッド _wait_for_generation_complete が呼び出されました")
        return await self.wait_for_text_generation(max_wait)