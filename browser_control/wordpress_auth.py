"""
WordPress認証管理
"""
import asyncio
import logging
from typing import Optional, Dict
from browser_control.browser_controller import BrowserController

class WordPressAuthManager:
    """WordPress認証を管理"""
    
    def __init__(self, browser: BrowserController):
        self.browser = browser
        self.logger = logging.getLogger(__name__)
        self.is_logged_in = False
    
    async def login_to_wordpress(self, wp_url: str, username: str, password: str) -> bool:
        """WordPressにログイン"""
        try:
            self.logger.info(f"🔐 WordPressログイン試行: {wp_url}")
            
            # WordPressログインページに移動
            login_url = f"{wp_url.rstrip('/')}/wp-admin"
            await self.browser.page.goto(login_url, wait_until='networkidle')
            
            # ログインフォームを待機
            await self.browser.page.wait_for_selector('#user_login', timeout=10000)
            
            # ユーザー名入力
            await self.browser.page.fill('#user_login', username)
            
            # パスワード入力
            await self.browser.page.fill('#user_pass', password)
            
            # ログインボタンクリック
            await self.browser.page.click('#wp-submit')
            
            # ログイン成功を確認（ダッシュボードにリダイレクトされる）
            await self.browser.page.wait_for_selector('#wpadminbar', timeout=10000)
            
            self.is_logged_in = True
            self.logger.info("✅ WordPressログイン成功")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ WordPressログイン失敗: {e}")
            self.is_logged_in = False
            return False
    
    async def ensure_logged_in(self, wp_url: str, username: str, password: str) -> bool:
        """ログイン状態を確認し、必要ならログイン"""
        if self.is_logged_in:
            # 現在のURLを確認してログイン状態を検証
            try:
                current_url = self.browser.page.url
                if 'wp-admin' in current_url and await self.browser.page.query_selector('#wpadminbar'):
                    return True
            except:
                pass
        
        # ログインしていない場合はログイン実行
        return await self.login_to_wordpress(wp_url, username, password)
    
    async def create_new_post(self, title: str, content: str, category: str = "") -> bool:
        """新しい記事を作成"""
        try:
            # 投稿追加ページに移動
            await self.browser.page.goto(f"{self.browser.page.url.split('/wp-admin')[0]}/wp-admin/post-new.php")
            
            # タイトル入力フィールドを待機
            await self.browser.page.wait_for_selector('#post-title-0', timeout=10000)
            
            # タイトル入力
            await self.browser.page.fill('#post-title-0', title)
            
            # 本文入力（Gutenbergエディタ）
            content_selector = '.block-editor-default-block-appender__content'
            if await self.browser.page.query_selector(content_selector):
                await self.browser.page.click(content_selector)
                await self.browser.page.keyboard.type(content)
            else:
                # 代替方法: 直接本文エリアに入力
                await self.browser.page.keyboard.press('Tab')
                await self.browser.page.keyboard.type(content)
            
            # カテゴリ指定がある場合
            if category:
                await self.browser.page.click('.editor-post-taxonomies__hierarchical-terms-list .components-checkbox-control__input')
                # カテゴリ選択ロジックを追加（必要に応じて）
            
            # 公開ボタンをクリック
            publish_selector = '.editor-post-publish-button__button'
            if await self.browser.page.query_selector(publish_selector):
                await self.browser.page.click(publish_selector)
                
                # 確認ボタンを待機してクリック
                confirm_selector = '.editor-post-publish-panel__header-publish-button button'
                await self.browser.page.wait_for_selector(confirm_selector, timeout=10000)
                await self.browser.page.click(confirm_selector)
                
                # 公開成功を確認
                success_selector = '.post-publish-panel__postpublish-header'
                await self.browser.page.wait_for_selector(success_selector, timeout=10000)
            
            self.logger.info(f"✅ 記事作成成功: {title}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 記事作成失敗: {e}")
            return False
    
    async def logout(self):
        """WordPressからログアウト"""
        try:
            await self.browser.page.goto(f"{self.browser.page.url.split('/wp-admin')[0]}/wp-login.php?action=logout")
            logout_confirm = await self.browser.page.query_selector('//a[contains(text(), "ログアウト")]')
            if logout_confirm:
                await logout_confirm.click()
            self.is_logged_in = False
            self.logger.info("✅ WordPressログアウト完了")
        except Exception as e:
            self.logger.error(f"❌ ログアウト失敗: {e}")

