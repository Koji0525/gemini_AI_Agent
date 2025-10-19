"""
拡張WordPressエージェント - 自動ログイン対応版
"""
import asyncio
import logging
from typing import Dict, Optional
from browser_control.browser_controller import BrowserController
from browser_control.wordpress_auth import WordPressAuthManager
from configuration.wp_config_loader import wp_config_loader

class EnhancedWordPressAgent:
    """拡張WordPressエージェント"""
    
    def __init__(self, browser: BrowserController):
        self.browser = browser
        self.auth_manager = WordPressAuthManager(browser)
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """初期化 - WordPressにログイン"""
        if self.is_initialized:
            return True
        
        if not wp_config_loader.has_valid_config():
            self.logger.error("❌ WordPress設定が不完全です")
            return False
        
        try:
            wp_url = wp_config_loader.get_wp_url()
            username = wp_config_loader.get_wp_username()
            password = wp_config_loader.get_wp_password()
            
            self.logger.info(f"🔐 WordPress初期化: {wp_url}")
            
            # 新しいタブでWordPressを開く
            await self.browser.page.bring_to_front()
            wp_page = await self.browser.context.new_page()
            await wp_page.bring_to_front()
            
            # 一時的にページを切り替えて認証
            original_page = self.browser.page
            self.browser.page = wp_page
            
            # ログイン実行
            success = await self.auth_manager.login_to_wordpress(wp_url, username, password)
            
            # 元のページに戻る
            self.browser.page = original_page
            
            if success:
                self.is_initialized = True
                self.logger.info("✅ WordPressエージェント初期化完了")
            else:
                self.logger.error("❌ WordPressエージェント初期化失敗")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ WordPress初期化エラー: {e}")
            return False
    
    async def create_post(self, title: str, content: str, **kwargs) -> Dict:
        """記事を作成"""
        try:
            if not await self.initialize():
                return {"success": False, "error": "初期化失敗"}
            
            # WordPressタブに切り替え
            wp_tab = self.browser.context.pages[-1]  # 最後のタブ（WordPress）
            original_page = self.browser.page
            self.browser.page = wp_tab
            
            # 記事作成
            success = await self.auth_manager.create_new_post(title, content, kwargs.get('category', ''))
            
            # 元のページに戻る
            self.browser.page = original_page
            
            if success:
                return {
                    "success": True,
                    "message": f"記事 '{title}' を作成しました",
                    "title": title,
                    "content_length": len(content)
                }
            else:
                return {"success": False, "error": "記事作成失敗"}
                
        except Exception as e:
            self.logger.error(f"❌ 記事作成エラー: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_wp_task(self, task_data: Dict) -> Dict:
        """WordPressタスクを実行"""
        task_type = task_data.get('type', 'create_post')
        
        if task_type == 'create_post':
            return await self.create_post(
                title=task_data.get('title', ''),
                content=task_data.get('content', ''),
                category=task_data.get('category', '')
            )
        else:
            return {"success": False, "error": f"未対応のタスクタイプ: {task_type}"}

