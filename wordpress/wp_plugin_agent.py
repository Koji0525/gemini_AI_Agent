"""
WordPressプラグインタスク実行エージェント
"""
import asyncio
import logging
from typing import Dict, List, Optional
from browser_control.browser_controller import BrowserController
from wordpress.wp_plugin_manager import WordPressPluginManager

class WordPressPluginAgent:
    """WordPressプラグインタスク実行エージェント"""
    
    def __init__(self, browser: BrowserController):
        self.browser = browser
        self.plugin_manager = WordPressPluginManager(browser)
        self.logger = logging.getLogger(__name__)
    
    async def execute_plugin_task(self, task_description: str) -> Dict:
        """プラグイン関連タスクを実行"""
        try:
            print("🔧 プラグインタスクを解析中...")
            
            # タスクからプラグイン情報を抽出
            plugin_info = self._parse_plugin_task(task_description)
            
            if not plugin_info:
                return {
                    "success": False,
                    "error": "タスクからプラグイン情報を抽出できませんでした",
                    "task_type": "unknown"
                }
            
            task_type = plugin_info.get('task_type')
            plugin_slug = plugin_info.get('plugin_slug')
            plugin_name = plugin_info.get('plugin_name', plugin_slug)
            settings = plugin_info.get('settings', {})
            
            print(f"🎯 検出したタスク: {task_type}")
            print(f"📦 プラグイン: {plugin_name} ({plugin_slug})")
            
            results = {}
            
            if task_type == 'install':
                # プラグインインストール
                install_result = await self.plugin_manager.install_plugin(plugin_slug, plugin_name)
                results['installation'] = install_result
                
                if install_result['success'] and settings:
                    # 設定も実行
                    config_result = await self.plugin_manager.configure_plugin(plugin_slug, settings)
                    results['configuration'] = config_result
            
            elif task_type == 'configure':
                # 設定のみ実行
                config_result = await self.plugin_manager.configure_plugin(plugin_slug, settings)
                results['configuration'] = config_result
            
            elif task_type == 'verify':
                # 確認のみ実行
                verify_result = await self.plugin_manager.verify_plugin_installation(plugin_slug)
                results['verification'] = verify_result
            
            # 最終確認
            verify_result = await self.plugin_manager.verify_plugin_installation(plugin_slug)
            results['final_verification'] = verify_result
            
            # 結果をまとめる
            success = all(
                result.get('success', False) 
                for result in results.values() 
                if 'success' in result
            )
            
            return {
                "success": success,
                "task_type": task_type,
                "plugin_slug": plugin_slug,
                "plugin_name": plugin_name,
                "results": results,
                "final_status": verify_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"プラグインタスク実行エラー: {str(e)}",
                "task_type": "error"
            }
    
    def _parse_plugin_task(self, task_description: str) -> Optional[Dict]:
        """タスク説明からプラグイン情報を解析"""
        description_lower = task_description.lower()
        
        # 一般的なWordPressプラグインのマッピング
        plugin_mapping = {
            'advanced custom fields': {'slug': 'advanced-custom-fields', 'name': 'Advanced Custom Fields'},
            'acf': {'slug': 'advanced-custom-fields', 'name': 'Advanced Custom Fields'},
            'woocommerce': {'slug': 'woocommerce', 'name': 'WooCommerce'},
            'yoast seo': {'slug': 'wordpress-seo', 'name': 'Yoast SEO'},
            'contact form 7': {'slug': 'contact-form-7', 'name': 'Contact Form 7'},
            'elementor': {'slug': 'elementor', 'name': 'Elementor'},
            'gravity forms': {'slug': 'gravityforms', 'name': 'Gravity Forms'},
            'members': {'slug': 'members', 'name': 'Members'},
            'user role editor': {'slug': 'user-role-editor', 'name': 'User Role Editor'},
        }
        
        # タスクタイプを判定
        task_type = 'install'
        if '設定' in task_description or 'configure' in description_lower:
            task_type = 'configure'
        elif '確認' in task_description or 'verify' in description_lower:
            task_type = 'verify'
        elif 'インストール' in task_description or 'install' in description_lower:
            task_type = 'install'
        
        # プラグインを検出
        detected_plugin = None
        for plugin_key, plugin_info in plugin_mapping.items():
            if plugin_key in description_lower:
                detected_plugin = plugin_info.copy()
                break
        
        if not detected_plugin:
            # 明示的なプラグイン名がなければ、一般的なタスクと判断
            return {
                'task_type': task_type,
                'plugin_slug': 'general',
                'plugin_name': 'General WordPress',
                'settings': {}
            }
        
        # 設定の抽出（簡易的な実装）
        settings = {}
        if 'メール通知' in task_description or 'email' in description_lower:
            settings['email_notification'] = True
        if '権限' in task_description or 'permission' in description_lower:
            settings['enable_permissions'] = True
        
        detected_plugin.update({
            'task_type': task_type,
            'settings': settings
        })
        
        return detected_plugin
    
    async def close(self):
        """リソースを解放"""
        await self.plugin_manager.close()

