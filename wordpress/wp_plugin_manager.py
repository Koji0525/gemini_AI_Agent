"""
WordPressプラグインマネージャー
"""
import asyncio
import logging
from typing import Dict, List, Optional
from browser_control.browser_controller import BrowserController
from configuration.wp_config_loader_fixed import wp_config_loader

class WordPressPluginManager:
    """WordPressプラグイン管理クラス"""
    
    def __init__(self, browser: BrowserController):
        self.browser = browser
        self.logger = logging.getLogger(__name__)
        self.wp_page = None
        self.is_logged_in = False
    
    async def ensure_login(self) -> bool:
        """ログイン状態を確保"""
        if self.is_logged_in and self.wp_page:
            return True
        
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
    
    async def install_plugin(self, plugin_slug: str, plugin_name: str = "") -> Dict:
        """プラグインをインストール"""
        try:
            if not await self.ensure_login():
                return {"success": False, "error": "ログイン失敗"}
            
            # プラグインページに移動
            await self.wp_page.goto(f"{wp_config_loader.get_wp_url()}/wp-admin/plugin-install.php")
            
            # 検索ボックスにプラグイン名を入力
            search_selector = '#search-plugins'
            await self.wp_page.wait_for_selector(search_selector, timeout=10000)
            await self.wp_page.fill(search_selector, plugin_slug)
            await self.wp_page.keyboard.press('Enter')
            
            # 検索結果を待機
            await asyncio.sleep(3)
            
            # インストールボタンを探す（複数のセレクタを試す）
            install_selectors = [
                f'.plugin-card-{plugin_slug} .install-now',
                f'[data-slug="{plugin_slug}"] .install-now',
                f'button[data-slug="{plugin_slug}"]'
            ]
            
            install_button = None
            for selector in install_selectors:
                install_button = await self.wp_page.query_selector(selector)
                if install_button:
                    break
            
            if install_button:
                # インストール実行
                await install_button.click()
                
                # インストール完了を待機
                await self.wp_page.wait_for_selector(f'.plugin-card-{plugin_slug} .activate-now', timeout=30000)
                
                # 有効化ボタンをクリック
                activate_selector = f'.plugin-card-{plugin_slug} .activate-now'
                activate_button = await self.wp_page.query_selector(activate_selector)
                if activate_button:
                    await activate_button.click()
                    await asyncio.sleep(2)
                
                return {
                    "success": True,
                    "message": f"プラグイン '{plugin_name or plugin_slug}' をインストールして有効化しました",
                    "plugin_slug": plugin_slug
                }
            else:
                return {"success": False, "error": f"プラグイン '{plugin_slug}' が見つかりません"}
                
        except Exception as e:
            return {"success": False, "error": f"インストールエラー: {str(e)}"}
    
    async def configure_plugin(self, plugin_slug: str, settings: Dict) -> Dict:
        """プラグインを設定"""
        try:
            if not await self.ensure_login():
                return {"success": False, "error": "ログイン失敗"}
            
            # 設定ページのURLパターン（一般的なプラグイン用）
            config_urls = [
                f"{wp_config_loader.get_wp_url()}/wp-admin/admin.php?page={plugin_slug}",
                f"{wp_config_loader.get_wp_url()}/wp-admin/options-general.php?page={plugin_slug}",
                f"{wp_config_loader.get_wp_url()}/wp-admin/edit.php?post_type={plugin_slug}"
            ]
            
            # 設定ページを探す
            config_page_found = False
            for url in config_urls:
                await self.wp_page.goto(url)
                if "wp-admin" in self.wp_page.url:
                    config_page_found = True
                    break
            
            if not config_page_found:
                return {"success": False, "error": f"プラグイン '{plugin_slug}' の設定ページが見つかりません"}
            
            # 設定を適用（簡易的な実装）
            settings_applied = 0
            for key, value in settings.items():
                # 各種入力フィールドを試す
                input_selectors = [
                    f'input[name="{key}"]',
                    f'textarea[name="{key}"]',
                    f'select[name="{key}"]',
                    f'#{key}',
                    f'[name="{key}"]'
                ]
                
                for selector in input_selectors:
                    element = await self.wp_page.query_selector(selector)
                    if element:
                        element_type = await self.wp_page.evaluate('el => el.type', element)
                        
                        if element_type in ['text', 'textarea', 'email', 'url']:
                            await element.fill(str(value))
                            settings_applied += 1
                        elif element_type == 'checkbox':
                            is_checked = await self.wp_page.evaluate('el => el.checked', element)
                            if bool(value) != is_checked:
                                await element.click()
                            settings_applied += 1
                        elif element_type == 'select-one':
                            await element.select_option(str(value))
                            settings_applied += 1
                        break
            
            # 保存ボタンを探してクリック
            save_selectors = [
                '#submit',
                '.button-primary',
                'input[type="submit"]',
                'button[type="submit"]'
            ]
            
            for selector in save_selectors:
                save_button = await self.wp_page.query_selector(selector)
                if save_button:
                    await save_button.click()
                    await asyncio.sleep(2)
                    break
            
            return {
                "success": True,
                "message": f"プラグイン '{plugin_slug}' の設定を {settings_applied}件適用しました",
                "settings_applied": settings_applied
            }
            
        except Exception as e:
            return {"success": False, "error": f"設定エラー: {str(e)}"}
    
    async def verify_plugin_installation(self, plugin_slug: str) -> Dict:
        """プラグインのインストール状態を確認"""
        try:
            if not await self.ensure_login():
                return {"success": False, "error": "ログイン失敗"}
            
            # プラグインページに移動
            await self.wp_page.goto(f"{wp_config_loader.get_wp_url()}/wp-admin/plugins.php")
            
            # プラグインの状態を確認
            plugin_row = await self.wp_page.query_selector(f'tr[data-slug="{plugin_slug}"]')
            
            if not plugin_row:
                return {
                    "success": False,
                    "installed": False,
                    "active": False,
                    "message": f"プラグイン '{plugin_slug}' はインストールされていません"
                }
            
            # アクティブ状態を確認
            deactivate_button = await plugin_row.query_selector('.deactivate a')
            is_active = deactivate_button is not None
            
            status = "active" if is_active else "inactive"
            
            return {
                "success": True,
                "installed": True,
                "active": is_active,
                "status": status,
                "message": f"プラグイン '{plugin_slug}' はインストール済み（状態: {status}）"
            }
            
        except Exception as e:
            return {"success": False, "error": f"確認エラー: {str(e)}"}
    
    async def close(self):
        """リソースを解放"""
        if self.wp_page:
            await self.wp_page.close()
            self.wp_page = None
        self.is_logged_in = False

