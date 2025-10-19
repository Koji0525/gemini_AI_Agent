"""
シンプルWordPressエージェント
"""
import asyncio
import logging
from typing import Dict, Optional
from browser_control.browser_controller import BrowserController
from configuration.wp_config_loader_fixed import wp_config_loader

class SimpleWordPressAgent:
    """シンプルなWordPress操作エージェント"""
    
    def __init__(self, browser: BrowserController):
        self.browser = browser
        self.logger = logging.getLogger(__name__)
        self.wp_page = None
        self.is_logged_in = False
    
    async def ensure_login(self) -> bool:
        """ログイン状態を確保"""
        if self.is_logged_in and self.wp_page:
            return True
        
        if not wp_config_loader.has_valid_config():
            self.logger.error("WordPress設定が不足しています")
            return False
        
        try:
            # 新しいタブでWordPressを開く
            self.wp_page = await self.browser.context.new_page()
            
            # ログイン
            wp_url = wp_config_loader.get_wp_url()
            username = wp_config_loader.get_wp_username()
            password = wp_config_loader.get_wp_password()
            
            login_url = f"{wp_url}/wp-admin"
            await self.wp_page.goto(login_url, wait_until='networkidle')
            
            # ログインフォーム入力
            await self.wp_page.fill('#user_login', username)
            await self.wp_page.fill('#user_pass', password)
            await self.wp_page.click('#wp-submit')
            
            # ログイン成功確認
            await self.wp_page.wait_for_selector('#wpadminbar', timeout=15000)
            
            self.is_logged_in = True
            self.logger.info("WordPressログイン成功")
            return True
            
        except Exception as e:
            self.logger.error(f"WordPressログイン失敗: {e}")
            return False
    
    async def create_post(self, title: str, content: str, category: str = "") -> Dict:
        """記事を作成"""
        try:
            if not await self.ensure_login():
                return {"success": False, "error": "ログイン失敗"}
            
            # 新規投稿ページに移動
            await self.wp_page.goto(f"{wp_config_loader.get_wp_url()}/wp-admin/post-new.php")
            
            # タイトル入力（Gutenberg対応）
            title_selector = '#post-title-0'
            await self.wp_page.wait_for_selector(title_selector, timeout=10000)
            await self.wp_page.fill(title_selector, title)
            
            # 本文入力
            await self.wp_page.click('.block-editor-default-block-appender__content')
            await self.wp_page.keyboard.type(content)
            
            # 公開
            publish_btn = '.editor-post-publish-button__button'
            if await self.wp_page.query_selector(publish_btn):
                await self.wp_page.click(publish_btn)
                
                # 確認
                confirm_btn = '.editor-post-publish-panel__header-publish-button button'
                await self.wp_page.wait_for_selector(confirm_btn, timeout=10000)
                await self.wp_page.click(confirm_btn)
                
                # 成功確認
                await self.wp_page.wait_for_selector('.post-publish-panel__postpublish-header', timeout=10000)
            
            return {
                "success": True,
                "message": f"記事 '{title}' を作成しました",
                "title": title,
                "content_length": len(content)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """リソースを解放"""
        if self.wp_page:
            await self.wp_page.close()
            self.wp_page = None
        self.is_logged_in = False

