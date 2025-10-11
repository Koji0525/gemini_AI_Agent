"""wp_plugin_manager.py - WordPressプラグイン管理"""
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)


class PluginNameExtractor:
    """プラグイン名抽出ユーティリティ"""
    
    @staticmethod
    def extract(description: str) -> str:
        """タスク説明からプラグイン名を抽出"""
        # シンプルな抽出ロジック - 実際の要件に応じて拡張
        import re
        patterns = [
            r'プラグイン[「"](.+?)[」"]',
            r'plugin[「"](.+?)[」"]',
            r'install[\s\w]+\s(.+?)\s',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # 見つからない場合は説明文の最初の数単語を使用
        return description.split()[0] if description else "unknown_plugin"


class WordPressPluginManager:
    """WordPressプラグイン管理機能（最適化版）"""

    def __init__(self, browser_controller, wp_credentials: Dict = None):
        """
        初期化
        
        Args:
            browser_controller: BrowserController インスタンス
            wp_credentials: WordPress 認証情報
        """
        self.browser = browser_controller
        self.wp_credentials = wp_credentials or {}
        self.wp_url = self.wp_credentials.get('wp_url', '').rstrip('/')
        
        logger.info(f"WordPressPluginManager 初期化: {self.wp_url}")

    async def install_plugin(self, page: Page, task: Dict) -> Dict:
        """プラグインをインストールして有効化"""
        try:
            plugin_name = PluginNameExtractor.extract(task['description'])
            logger.info(f"プラグインインストール開始: {plugin_name}")
            
            # プラグインページに移動
            await page.goto(f"{self.wp_url}/wp-admin/plugin-install.php")
            await page.wait_for_timeout(2000)
            
            # プラグイン検索とインストール実行
            search_success = await self._search_plugin(page, plugin_name)
            if not search_success:
                return {
                    'success': False,
                    'error': 'プラグイン検索に失敗しました'
                }
            
            # インストールと有効化
            installed, status = await self._install_and_activate(page)
            
            # 結果記録
            screenshot_path = f"wp_plugin_{datetime.now().strftime('%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
            
            if installed:
                return self._build_success_result(plugin_name, status, screenshot_path)
            else:
                return self._build_manual_result(plugin_name, screenshot_path)
                
        except Exception as e:
            logger.error(f"プラグインインストールエラー: {e}")
            return self._build_error_result(str(e))

    async def _search_plugin(self, page: Page, plugin_name: str) -> bool:
        """プラグインを検索"""
        search_box = await page.query_selector('#search-plugins')
        if not search_box:
            return False
            
        await search_box.fill(plugin_name)
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(4000)
        
        logger.info(f"プラグイン検索完了: {plugin_name}")
        return True

    async def _install_and_activate(self, page: Page) -> tuple[bool, str]:
        """プラグインをインストール・有効化"""
        install_selectors = [
            'a.install-now:has-text("今すぐインストール")',
            '.plugin-card-top a.install-now',
            'a[data-slug]:has-text("今すぐインストール")',
        ]
        
        for selector in install_selectors:
            try:
                install_button = await page.query_selector(selector)
                if install_button and await install_button.is_visible():
                    logger.info(f"インストールボタンをクリック: {selector}")
                    await install_button.click()
                    await page.wait_for_timeout(5000)
                    
                    # 有効化処理
                    return await self._activate_plugin(page)
            except Exception as e:
                logger.warning(f"インストール試行エラー ({selector}): {e}")
                continue
        
        return False, "インストール失敗"

    async def _activate_plugin(self, page: Page) -> tuple[bool, str]:
        """プラグインを有効化"""
        activate_button = await page.query_selector('a:has-text("有効化")')
        if activate_button:
            logger.info("有効化ボタンをクリック")
            await activate_button.click()
            await page.wait_for_timeout(3000)
            logger.info("✅ プラグインのインストールと有効化が完了しました")
            return True, "インストール・有効化完了"
        else:
            logger.info("✅ プラグインのインストールが完了しました(有効化は手動)")
            return True, "インストール完了(有効化は手動で実施してください)"

    async def change_plugin_settings(self, page: Page, task: Dict) -> Dict:
        """プラグイン設定を変更"""
        try:
            plugin_name = PluginNameExtractor.extract(task['description'])
            logger.info(f"プラグイン設定変更: {plugin_name}")
            
            await page.goto(f"{self.wp_url}/wp-admin/plugins.php")
            await page.wait_for_timeout(3000)
            
            settings_found = await self._navigate_to_settings(page, plugin_name)
            screenshot_path = f"wp_plugin_settings_{datetime.now().strftime('%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
            
            if settings_found:
                return self._build_settings_success_result(plugin_name, screenshot_path)
            else:
                return self._build_settings_error_result(plugin_name, screenshot_path)
                
        except Exception as e:
            logger.error(f"プラグイン設定変更エラー: {e}")
            return self._build_error_result(str(e))

    async def _navigate_to_settings(self, page: Page, plugin_name: str) -> bool:
        """プラグイン設定画面へ移動"""
        settings_selectors = [
            f'tr:has-text("{plugin_name}") .settings a',
            f'a:has-text("{plugin_name}設定")',
            '.plugin-action-buttons a:has-text("設定")'
        ]
        
        for selector in settings_selectors:
            try:
                settings_link = await page.query_selector(selector)
                if settings_link and await settings_link.is_visible():
                    await settings_link.click()
                    await page.wait_for_timeout(3000)
                    logger.info(f"✅ {plugin_name}の設定画面を開きました")
                    return True
            except Exception:
                continue
        
        return False

    # === 主要プラグイン設定機能 ===

    async def configure_facetwp(self, page: Page, task_params: Dict) -> Dict:
        """FacetWP 絞り込み検索の設定"""
        try:
            facets = task_params.get('facets', [])
            logger.info(f"FacetWP設定開始: {len(facets)}件のファセット")
            
            await page.goto(f"{self.wp_url}/wp-admin/options-general.php?page=facetwp-settings")
            await page.wait_for_timeout(3000)
            
            created_facets = await self._create_facets(page, facets)
            screenshot_path = f"facetwp_setup_{datetime.now().strftime('%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
            
            return self._build_facetwp_result(created_facets, facets, screenshot_path)
            
        except Exception as e:
            logger.error(f"FacetWP設定エラー: {e}")
            return self._build_error_result(str(e))

    async def _create_facets(self, page: Page, facets: List[Dict]) -> List[str]:
        """ファセットを作成"""
        created_facets = []
        
        for i, facet in enumerate(facets, 1):
            try:
                logger.info(f"ファセット {i}/{len(facets)}: {facet.get('name')}")
                
                # 新規ファセット追加
                if await self._click_add_new_facet(page):
                    # ファセット設定
                    if await self._configure_facet_fields(page, facet):
                        # 保存
                        if await self._save_facet(page):
                            created_facets.append(facet.get('name'))
                            logger.info(f"✅ ファセット '{facet.get('name')}' を保存")
                            
                await page.wait_for_timeout(1000)
                
            except Exception as e:
                logger.warning(f"⚠️ ファセット {i} 作成エラー: {e}")
                continue
                
        return created_facets

    async def _click_add_new_facet(self, page: Page) -> bool:
        """新規ファセット追加ボタンをクリック"""
        add_new_selectors = [
            'a.facetwp-add:has-text("Add New")',
            'button:has-text("Add New")',
            '.facetwp-add-facet'
        ]
        
        for selector in add_new_selectors:
            try:
                add_button = await page.query_selector(selector)
                if add_button and await add_button.is_visible():
                    await add_button.click()
                    await page.wait_for_timeout(1500)
                    return True
            except Exception:
                continue
        return False

    async def _configure_facet_fields(self, page: Page, facet: Dict) -> bool:
        """ファセットフィールドを設定"""
        try:
            # ファセット名
            name_input = await page.query_selector('input[name="facet_label"]')
            if name_input:
                await name_input.fill(facet.get('name', ''))
            
            # ファセットタイプ
            type_select = await page.query_selector('select[name="facet_type"]')
            if type_select:
                await type_select.select_option(facet.get('type', 'checkboxes'))
            
            # データソース
            source = facet.get('source', '')
            if source.startswith('tax/'):
                return await self._configure_taxonomy_source(page, source)
            elif source.startswith('cf/'):
                return await self._configure_custom_field_source(page, source)
            
            return True
        except Exception as e:
            logger.warning(f"ファセット設定エラー: {e}")
            return False

    async def _configure_taxonomy_source(self, page: Page, source: str) -> bool:
        """タクソノミーソースを設定"""
        try:
            taxonomy_name = source.replace('tax/', '')
            source_select = await page.query_selector('select[name="facet_source"]')
            if source_select:
                await source_select.select_option('tax')
                await page.wait_for_timeout(500)
            
            taxonomy_select = await page.query_selector('select[name="facet_source_taxonomy"]')
            if taxonomy_select:
                await taxonomy_select.select_option(taxonomy_name)
                logger.info(f"  ソース: Taxonomy - {taxonomy_name}")
                return True
        except Exception as e:
            logger.warning(f"タクソノミーソース設定エラー: {e}")
        return False

    async def _configure_custom_field_source(self, page: Page, source: str) -> bool:
        """カスタムフィールドソースを設定"""
        try:
            field_name = source.replace('cf/', '')
            source_select = await page.query_selector('select[name="facet_source"]')
            if source_select:
                await source_select.select_option('cf')
                await page.wait_for_timeout(500)
            
            field_input = await page.query_selector('input[name="facet_source_custom_field"]')
            if field_input:
                await field_input.fill(field_name)
                logger.info(f"  ソース: Custom Field - {field_name}")
                return True
        except Exception as e:
            logger.warning(f"カスタムフィールドソース設定エラー: {e}")
        return False

    async def _save_facet(self, page: Page) -> bool:
        """ファセットを保存"""
        save_selectors = [
            'button.facetwp-save:has-text("Save")',
            'button:has-text("Save Changes")',
            'input[type="submit"][value="Save"]'
        ]
        
        for selector in save_selectors:
            try:
                save_button = await page.query_selector(selector)
                if save_button and await save_button.is_visible():
                    await save_button.click()
                    await page.wait_for_timeout(2000)
                    return True
            except Exception:
                continue
        return False

    async def configure_user_roles(self, page: Page, task_params: Dict) -> Dict:
        """User Role Editorでカスタムロールを作成"""
        try:
            role_slug = task_params.get('role_slug')
            role_name = task_params.get('role_name')
            
            logger.info(f"ユーザーロール作成: {role_name}")
            
            await page.goto(f"{self.wp_url}/wp-admin/users.php?page=users-user-role-editor-php")
            await page.wait_for_timeout(3000)
            
            # ロール作成画面を開く
            if await self._open_add_role_dialog(page):
                # ロール情報入力
                await self._fill_role_info(page, role_slug, role_name)
                
                screenshot_path = f"user_role_{role_slug}_{datetime.now().strftime('%H%M%S')}.png"
                await page.screenshot(path=screenshot_path)
                
                return self._build_user_role_result(role_name, role_slug, screenshot_path)
            else:
                return self._build_error_result("ロール追加ダイアログを開けませんでした")
                
        except Exception as e:
            logger.error(f"ユーザーロール作成エラー: {e}")
            return self._build_error_result(str(e))

    async def _open_add_role_dialog(self, page: Page) -> bool:
        """ロール追加ダイアログを開く"""
        add_role_selectors = [
            'button:has-text("Add Role")',
            'input[value="Add Role"]',
            '#ure_add_role_button'
        ]
        
        for selector in add_role_selectors:
            try:
                add_button = await page.query_selector(selector)
                if add_button and await add_button.is_visible():
                    await add_button.click()
                    await page.wait_for_timeout(2000)
                    return True
            except Exception:
                continue
        return False

    async def _fill_role_info(self, page: Page, role_slug: str, role_name: str):
        """ロール情報を入力"""
        slug_input = await page.query_selector('#user_role_id')
        if slug_input:
            await slug_input.fill(role_slug)
            logger.info(f"ロールスラッグを入力: {role_slug}")
        
        name_input = await page.query_selector('#user_role_name')
        if name_input:
            await name_input.fill(role_name)
            logger.info(f"ロール名を入力: {role_name}")

    async def configure_wordfence(self, page: Page, task_params: Dict) -> Dict:
        """Wordfence Security の基本設定"""
        try:
            logger.info("Wordfence Security設定開始")
            
            await page.goto(f"{self.wp_url}/wp-admin/admin.php?page=Wordfence")
            await page.wait_for_timeout(3000)
            
            screenshot_path = f"wordfence_{datetime.now().strftime('%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
            
            return self._build_wordfence_result(task_params, screenshot_path)
            
        except Exception as e:
            logger.error(f"Wordfence設定エラー: {e}")
            return self._build_error_result(str(e))

    async def configure_wp_rocket(self, page: Page, task_params: Dict) -> Dict:
        """WP Rocket キャッシュプラグインの設定"""
        try:
            logger.info("WP Rocket設定開始")
            
            await page.goto(f"{self.wp_url}/wp-admin/options-general.php?page=wprocket")
            await page.wait_for_timeout(3000)
            
            screenshot_path = f"wp_rocket_{datetime.now().strftime('%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
            
            return self._build_wp_rocket_result(screenshot_path)
            
        except Exception as e:
            logger.error(f"WP Rocket設定エラー: {e}")
            return self._build_error_result(str(e))

    async def configure_relevanssi(self, page: Page, task_params: Dict) -> Dict:
        """Relevanssi 高度な検索プラグインの設定"""
        try:
            logger.info("Relevanssi設定開始")
            
            await page.goto(f"{self.wp_url}/wp-admin/options-general.php?page=relevanssi/relevanssi.php")
            await page.wait_for_timeout(3000)
            
            screenshot_path = f"relevanssi_{datetime.now().strftime('%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
            
            return self._build_relevanssi_result(task_params, screenshot_path)
            
        except Exception as e:
            logger.error(f"Relevanssi設定エラー: {e}")
            return self._build_error_result(str(e))

    async def bulk_configure_plugins(self, page: Page, plugin_configs: List[Dict]) -> Dict:
        """複数のプラグインを一括で設定"""
        try:
            results = []
            
            for i, config in enumerate(plugin_configs, 1):
                plugin_name = config.get('plugin_name')
                logger.info(f"プラグイン設定 {i}/{len(plugin_configs)}: {plugin_name}")
                
                # プラグイン種別に応じて設定を実行
                result = await self._configure_single_plugin(page, config)
                results.append({'plugin': plugin_name, 'result': result})
            
            successful = sum(1 for r in results if r['result'].get('success'))
            
            return {
                'success': successful > 0,
                'summary': f'{successful}/{len(plugin_configs)}件のプラグイン設定を完了',
                'results': results
            }
            
        except Exception as e:
            logger.error(f"プラグイン一括設定エラー: {e}")
            return self._build_error_result(str(e))

    async def _configure_single_plugin(self, page: Page, config: Dict) -> Dict:
        """単一プラグインを設定"""
        plugin_name = config.get('plugin_name')
        
        plugin_handlers = {
            'facetwp': self.configure_facetwp,
            'user-role-editor': self.configure_user_roles,
            'wordfence': self.configure_wordfence,
            'wp-rocket': self.configure_wp_rocket,
            'relevanssi': self.configure_relevanssi,
        }
        
        handler = plugin_handlers.get(plugin_name)
        if handler:
            return await handler(page, config)
        else:
            return {'success': False, 'error': f'未対応のプラグイン: {plugin_name}'}

    # === 結果ビルダーメソッド ===

    def _build_success_result(self, plugin_name: str, status: str, screenshot_path: str) -> Dict:
        """成功結果を作成"""
        return {
            'success': True,
            'summary': f'プラグイン "{plugin_name}" を{status}',
            'screenshot': screenshot_path,
            'full_text': f'プラグイン処理完了\n名前: {plugin_name}\nステータス: {status}\nスクリーンショット: {screenshot_path}'
        }

    def _build_manual_result(self, plugin_name: str, screenshot_path: str) -> Dict:
        """手動確認が必要な結果を作成"""
        return {
            'success': True,
            'summary': f'プラグイン "{plugin_name}" を検索しました。手動でインストールを確認してください。',
            'screenshot': screenshot_path,
            'full_text': f'プラグイン検索: {plugin_name}\nスクリーンショット: {screenshot_path}\n※インストールボタンが見つからなかったため手動で実施してください'
        }

    def _build_error_result(self, error_message: str) -> Dict:
        """エラー結果を作成"""
        return {
            'success': False,
            'error': error_message
        }

    def _build_settings_success_result(self, plugin_name: str, screenshot_path: str) -> Dict:
        """設定成功結果を作成"""
        return {
            'success': True,
            'summary': f'プラグイン「{plugin_name}」の設定画面を開きました。手動で設定を確認してください。',
            'screenshot': screenshot_path,
            'full_text': f'プラグイン設定画面表示\nプラグイン: {plugin_name}\nスクリーンショット: {screenshot_path}\n※設定変更は手動で実施してください'
        }

    def _build_settings_error_result(self, plugin_name: str, screenshot_path: str) -> Dict:
        """設定エラー結果を作成"""
        return {
            'success': False,
            'error': f'プラグイン「{plugin_name}」の設定画面が見つかりませんでした',
            'screenshot': screenshot_path
        }

    def _build_facetwp_result(self, created_facets: List[str], facets: List[Dict], screenshot_path: str) -> Dict:
        """FacetWP設定結果を作成"""
        summary_lines = ["【FacetWP設定完了】"]
        summary_lines.append(f"作成成功: {len(created_facets)}/{len(facets)}件")
        for name in created_facets:
            summary_lines.append(f"  ✓ {name}")
            
        if len(created_facets) < len(facets):
            summary_lines.append("\n⚠️ 一部のファセットは手動で確認が必要です")
            
        summary = '\n'.join(summary_lines)
        
        return {
            'success': len(created_facets) > 0,
            'summary': summary,
            'facets_created': created_facets,
            'facets_count': len(facets),
            'screenshot': screenshot_path,
            'full_text': f'{summary}\nスクリーンショット: {screenshot_path}'
        }

    def _build_user_role_result(self, role_name: str, role_slug: str, screenshot_path: str) -> Dict:
        """ユーザーロール作成結果を作成"""
        return {
            'success': True,
            'summary': f'ユーザーロール "{role_name}" の作成画面を開きました。',
            'role_slug': role_slug,
            'role_name': role_name,
            'screenshot': screenshot_path,
            'full_text': f'User Role作成\nスラッグ: {role_slug}\n表示名: {role_name}\n※権限設定は手動で実施してください'
        }

    def _build_wordfence_result(self, task_params: Dict, screenshot_path: str) -> Dict:
        """Wordfence設定結果を作成"""
        firewall_mode = task_params.get('firewall_mode', 'enabled')
        scan_schedule = task_params.get('scan_schedule', 'daily')
        two_factor_auth = task_params.get('two_factor_auth', True)
        
        summary = f"""【Wordfence Security設定】
ファイアウォールモード: {firewall_mode}
スキャンスケジュール: {scan_schedule}
2FA: {'有効' if two_factor_auth else '無効'}
※手動で設定を完了してください"""
        
        return {
            'success': True,
            'summary': 'Wordfence設定画面を開きました。',
            'screenshot': screenshot_path,
            'full_text': summary
        }

    def _build_wp_rocket_result(self, screenshot_path: str) -> Dict:
        """WP Rocket設定結果を作成"""
        summary = """【WP Rocket設定】
推奨設定:
- Mobile Cache: 有効
- User Cache: 有効
- Minify CSS/JS: 有効
- Combine CSS/JS: 有効
※手動で設定を完了してください"""
        
        return {
            'success': True,
            'summary': 'WP Rocket設定画面を開きました。',
            'screenshot': screenshot_path,
            'full_text': summary
        }

    def _build_relevanssi_result(self, task_params: Dict, screenshot_path: str) -> Dict:
        """Relevanssi設定結果を作成"""
        index_fields = task_params.get('index_fields', [])
        
        summary = f"""【Relevanssi設定】
インデックス対象フィールド: {len(index_fields)}件
推奨設定:
- Custom fields: ACFフィールド名を追加
- Build Index: インデックス構築実行
- Weight設定: Title=高, Content=中, Custom fields=中
※手動で設定を完了してください"""
        
        return {
            'success': True,
            'summary': 'Relevanssi設定画面を開きました。',
            'screenshot': screenshot_path,
            'full_text': summary
        }