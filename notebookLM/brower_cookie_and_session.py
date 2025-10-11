# browser_cookie_and_session.py
"""クッキーとセッション管理クラス"""
import json
import time
from pathlib import Path
from typing import Optional, Dict, List
from playwright.async_api import BrowserContext
import logging

from config_utils import ErrorHandler

logger = logging.getLogger(__name__)

class CookieSessionManager:
    """クッキーとセッションの管理を担当"""
    
    def __init__(self, context: BrowserContext, cookies_file: Path):
        self.context = context
        self.cookies_file = cookies_file
    
    async def save_cookies(self) -> None:
        """クッキーを保存（強化版）"""
        try:
            if not self.context or not self.cookies_file:
                logger.warning("クッキー保存: コンテキストまたはファイルパスがありません")
                return
            
            cookies = await self.context.cookies()
            
            if not cookies:
                logger.warning("保存するクッキーがありません")
                return
                
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ クッキーを保存しました: {len(cookies)}個のクッキー")
            
        except Exception as e:
            ErrorHandler.log_error(e, "クッキー保存")
            logger.warning("クッキー保存に失敗しましたが続行します")

    async def load_cookies(self) -> bool:
        """クッキーを読み込み（強化版）"""
        try:
            if not self.cookies_file or not self.cookies_file.exists():
                logger.warning("クッキーファイルが存在しません")
                return False
                
            if not self.context:
                logger.warning("コンテキストが初期化されていません")
                return False
                
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            if not cookies:
                logger.warning("クッキーファイルが空です")
                return False
                
            current_url = "https://gemini.google.com"  # デフォルトURL
            domain_cookies = []
            
            for cookie in cookies:
                if 'domain' in cookie and cookie['domain'].startswith('.'):
                    cookie['domain'] = cookie['domain'][1:]
                
                if 'expires' in cookie and cookie['expires'] < time.time():
                    continue
                    
                domain_cookies.append(cookie)
            
            if domain_cookies:
                await self.context.add_cookies(domain_cookies)
                logger.info(f"✅ クッキーを読み込みました: {len(domain_cookies)}個")
                return True
            else:
                logger.warning("有効なクッキーがありません")
                return False
                
        except Exception as e:
            ErrorHandler.log_error(e, "クッキー読み込み")
            return False
    
    async def check_google_login_status(self) -> bool:
        """Googleログイン状態をチェック（ページが必要な場合に実装）"""
        # このメソッドはページコンテキストが必要なため、
        # 必要に応じてAIChatAgentに移動またはここで実装
        logger.info("Googleログイン状態チェック（実装予定）")
        return False