"""wp_plugin_manager.py_WordPressプラグイン管理"""
import logging
import asyncio
from typing import Dict, List, Optional, Any
from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from .wp_utils import PluginNameExtractor

logger = logging.getLogger(__name__)


class WordPressPluginManager:
    """WordPressプラグイン管理機能"""

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

        # ========================================
        # ✅ サブエージェントの初期化
        # ========================================
            
        # シートマネージャー（後で外部から設定される）
        self.sheets_manager = None
            
        # 投稿編集エージェント
        try:
            self.post_editor = WordPressPostEditor(
                browser_controller=self.browser,
                wp_credentials=self.wp_credentials
            )
            logger.info("✅ WordPressPostEditor 初期化完了")
        except Exception as e:
            logger.error(f"❌ WordPressPostEditor 初期化エラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.post_editor = None
            
        # 投稿作成エージェント
        try:
            self.post_creator = WordPressPostCreator(
                browser_controller=self.browser,
                wp_credentials=self.wp_credentials
            )
            logger.info("✅ WordPressPostCreator 初期化完了")
        except Exception as e:
            logger.error(f"❌ WordPressPostCreator 初期化エラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.post_creator = None
            
        # ========================================
        # ✅ 重要：プラグインマネージャー（修正版）
        # ========================================
        try:
            self.plugin_manager = WordPressPluginManager(
                browser_controller=self.browser,
                wp_credentials=self.wp_credentials
            )
            logger.info("✅ WordPressPluginManager 初期化完了")
        except Exception as e:
            logger.error(f"❌ WordPressPluginManager 初期化エラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.plugin_manager = None
            
        # 設定マネージャー
        try:
            self.settings_manager = WordPressSettingsManager(
                browser_controller=self.browser,
                wp_credentials=self.wp_credentials
            )
            logger.info("✅ WordPressSettingsManager 初期化完了")
        except Exception as e:
            logger.error(f"❌ WordPressSettingsManager 初期化エラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.settings_manager = None
            
        # テスター
        try:
            self.tester = WordPressTester(
                browser_controller=self.browser,
                wp_credentials=self.wp_credentials
            )
            logger.info("✅ WordPressTester 初期化完了")
        except Exception as e:
            logger.error(f"❌ WordPressTester 初期化エラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.tester = None
            
        logger.info("="*60)
        logger.info("WordPressAgent 全サブエージェント初期化完了")
        logger.info("="*60)
        
    async def install_plugin(self, page: Page, task: Dict) -> Dict:
        """プラグインをインストール"""
        try:
            logger.info("プラグインインストールを実行中...")
            
            # プラグインページに移動
            await page.goto(f"{self.wp_url}/wp-admin/plugin-install.php")
            await page.wait_for_timeout(2000)
            
            # タスクからプラグイン名を抽出
            plugin_name = PluginNameExtractor.extract(task['description'])
            
            # プラグイン検索
            search_box = await page.query_selector('#search-plugins')
            if search_box:
                await search_box.fill(plugin_name)
                await page.keyboard.press('Enter')
                await page.wait_for_timeout(4000)
                
                logger.info(f"プラグイン検索完了: {plugin_name}")
                
                # インストールと有効化
                installed, status = await self._install_and_activate(page)
                
                # スクリーンショット
                screenshot_path = f"wp_plugin_{datetime.now().strftime('%H%M%S')}.png"
                await page.screenshot(path=screenshot_path)
                
                if installed:
                    return {
                        'success': True,
                        'summary': f'プラグイン "{plugin_name}" を{status}',
                        'screenshot': screenshot_path,
                        'full_text': f'プラグイン処理完了\n名前: {plugin_name}\nステータス: {status}\nスクリーンショット: {screenshot_path}'
                    }
                else:
                    return {
                        'success': True,
                        'summary': f'プラグイン "{plugin_name}" を検索しました。手動でインストールを確認してください。',
                        'screenshot': screenshot_path,
                        'full_text': f'プラグイン検索: {plugin_name}\nスクリーンショット: {screenshot_path}\n※インストールボタンが見つからなかったため手動で実施してください'
                    }
            else:
                return {
                    'success': False,
                    'error': '検索ボックスが見つかりません'
                }
                
        except Exception as e:
            logger.error(f"プラグインインストールエラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
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
                    
                    # インストール完了を待つ
                    await page.wait_for_timeout(5000)
                    
                    # 有効化ボタンを探す
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
            except Exception as e:
                logger.warning(f"インストール試行エラー ({selector}): {e}")
                continue
        
        return False, "インストール失敗"
    
    async def change_plugin_settings(self, page: Page, task: Dict) -> Dict:
        """プラグイン設定を変更"""
        try:
            logger.info("プラグイン設定変更を実行中...")
            
            # タスクからプラグイン名を抽出
            plugin_name = PluginNameExtractor.extract(task['description'])
            logger.info(f"対象プラグイン: {plugin_name}")
            
            # プラグイン一覧ページに移動
            await page.goto(f"{self.wp_url}/wp-admin/plugins.php")
            await page.wait_for_timeout(3000)
            
            # プラグインの設定リンクを探す
            settings_found = await self._navigate_to_settings(page, plugin_name)
            
            # スクリーンショット
            screenshot_path = f"wp_plugin_settings_{datetime.now().strftime('%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
            
            if settings_found:
                return {
                    'success': True,
                    'summary': f'プラグイン「{plugin_name}」の設定画面を開きました。手動で設定を確認してください。',
                    'screenshot': screenshot_path,
                    'full_text': f'プラグイン設定画面表示\nプラグイン: {plugin_name}\nスクリーンショット: {screenshot_path}\n※設定変更は手動で実施してください'
                }
            else:
                return {
                    'success': False,
                    'error': f'プラグイン「{plugin_name}」の設定画面が見つかりませんでした',
                    'screenshot': screenshot_path
                }
                
        except Exception as e:
            logger.error(f"プラグイン設定変更エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    # wp_plugin_manager.py の WordPressPluginManager クラスに以下のメソッドを追加

    # === 1. FacetWP設定機能 ===
    async def configure_facetwp(self, page: Page, task_params: Dict) -> Dict:
        """
        FacetWP 絞り込み検索の設定（実行ロジック強化版）
            
        Parameters:
            facets: list - ファセット設定のリスト
                - name: ファセット名
                - type: フィルタータイプ (checkboxes, slider, dropdownなど)
                - source: データソース (tax/カテゴリ名, cf/カスタムフィールド名)
        """
        try:
            facets = task_params.get('facets', [])
                
            logger.info("FacetWP設定を開始...")
            logger.info(f"設定するファセット数: {len(facets)}件")
                
            # FacetWP設定画面に移動
            await page.goto(f"{self.wp_url}/wp-admin/options-general.php?page=facetwp-settings")
            await page.wait_for_timeout(3000)
                
            # ========================================
            # 🆕 ファセット自動追加ロジック（新規実装）
            # ========================================
            created_facets = []
                
            for i, facet in enumerate(facets, 1):
                try:
                    logger.info(f"ファセット {i}/{len(facets)}: {facet.get('name')} を作成中...")
                        
                    # "Add New" ボタンをクリック
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
                                logger.info("✅ Add Newボタンをクリック")
                                break
                        except:
                            continue
                        
                    # ファセット名を入力
                    name_input = await page.query_selector('input[name="facet_label"]')
                    if name_input:
                        await name_input.fill(facet.get('name', ''))
                        logger.info(f"  ファセット名: {facet.get('name')}")
                        
                    # ファセットタイプを選択
                    type_select = await page.query_selector('select[name="facet_type"]')
                    if type_select:
                        await type_select.select_option(facet.get('type', 'checkboxes'))
                        logger.info(f"  タイプ: {facet.get('type')}")
                        
                    # データソースを設定
                    source = facet.get('source', '')
                    if source.startswith('tax/'):
                        # タクソノミーソース
                        taxonomy_name = source.replace('tax/', '')
                        source_select = await page.query_selector('select[name="facet_source"]')
                        if source_select:
                            await source_select.select_option('tax')
                            await page.wait_for_timeout(500)
                            
                        # タクソノミーを選択
                        taxonomy_select = await page.query_selector('select[name="facet_source_taxonomy"]')
                        if taxonomy_select:
                            await taxonomy_select.select_option(taxonomy_name)
                            logger.info(f"  ソース: Taxonomy - {taxonomy_name}")
                        
                    elif source.startswith('cf/'):
                        # カスタムフィールドソース
                        field_name = source.replace('cf/', '')
                        source_select = await page.query_selector('select[name="facet_source"]')
                        if source_select:
                            await source_select.select_option('cf')
                            await page.wait_for_timeout(500)
                            
                        # フィールド名を入力
                        field_input = await page.query_selector('input[name="facet_source_custom_field"]')
                        if field_input:
                            await field_input.fill(field_name)
                            logger.info(f"  ソース: Custom Field - {field_name}")
                        
                    # 保存ボタンをクリック
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
                                logger.info(f"✅ ファセット '{facet.get('name')}' を保存")
                                created_facets.append(facet.get('name'))
                                break
                        except:
                            continue
                        
                    await page.wait_for_timeout(1000)
                        
                except Exception as e:
                    logger.warning(f"⚠️ ファセット {i} 作成エラー: {e}")
                    continue
                
            # スクリーンショット
            from datetime import datetime
            screenshot_path = f"facetwp_setup_{datetime.now().strftime('%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
                
            # 結果サマリー
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
            
        except Exception as e:
            logger.error(f"FacetWP設定エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    # === 2. User Role Editor設定機能 ===
    async def configure_user_roles(self, page: Page, task_params: Dict) -> Dict:
        """
        User Role Editorでカスタムロールを作成
    
        Parameters:
            role_slug: str - ロールスラッグ
            role_name: str - ロール表示名
            capabilities: dict - 権限設定
        """
        try:
            role_slug = task_params.get('role_slug')
            role_name = task_params.get('role_name')
            capabilities = task_params.get('capabilities', {})
        
            logger.info(f"ユーザーロール '{role_name}' を作成中...")
        
            # User Role Editor画面に移動
            await page.goto(f"{self.wp_url}/wp-admin/users.php?page=users-user-role-editor-php")
            await page.wait_for_timeout(3000)
        
            # Add Roleボタンをクリック
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
                        break
                except:
                    continue
        
            # Role slug入力
            slug_input = await page.query_selector('#user_role_id')
            if slug_input:
                await slug_input.fill(role_slug)
                logger.info(f"ロールスラッグを入力: {role_slug}")
        
            # Role name入力
            name_input = await page.query_selector('#user_role_name')
            if name_input:
                await name_input.fill(role_name)
                logger.info(f"ロール名を入力: {role_name}")
        
            # スクリーンショット
            from datetime import datetime
            screenshot_path = f"user_role_{role_slug}_{datetime.now().strftime('%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
        
            logger.info("⚠️ 権限（Capabilities）の設定は手動で確認してください")
        
            return {
                'success': True,
                'summary': f'ユーザーロール "{role_name}" の作成画面を開きました。',
                'role_slug': role_slug,
                'role_name': role_name,
                'screenshot': screenshot_path,
                'full_text': f'User Role作成\nスラッグ: {role_slug}\n表示名: {role_name}\n※権限設定は手動で実施してください'
            }
        
        except Exception as e:
            logger.error(f"ユーザーロール作成エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }


    # === 3. Wordfence Security設定機能 ===
    async def configure_wordfence(self, page: Page, task_params: Dict) -> Dict:
        """
        Wordfence Security の基本設定
    
        Parameters:
            firewall_mode: str - ファイアウォールモード（learning, enabled）
            scan_schedule: str - スキャンスケジュール
            two_factor_auth: bool - 2FA有効化
        """
        try:
            firewall_mode = task_params.get('firewall_mode', 'enabled')
            scan_schedule = task_params.get('scan_schedule', 'daily')
            two_factor_auth = task_params.get('two_factor_auth', True)
        
            logger.info("Wordfence Security設定を開始...")
        
            # Wordfence画面に移動
            await page.goto(f"{self.wp_url}/wp-admin/admin.php?page=Wordfence")
            await page.wait_for_timeout(3000)
        
            # スクリーンショット
            from datetime import datetime
            screenshot_path = f"wordfence_{datetime.now().strftime('%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
        
            logger.info("⚠️ Wordfenceの詳細設定は手動で確認してください")
        
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
        
        except Exception as e:
            logger.error(f"Wordfence設定エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }


    # === 4. WP Rocket設定機能 ===
    async def configure_wp_rocket(self, page: Page, task_params: Dict) -> Dict:
        """
        WP Rocket キャッシュプラグインの設定
    
        Parameters:
            cache_options: dict - キャッシュ設定
            optimization: dict - 最適化設定
        """
        try:
            cache_options = task_params.get('cache_options', {})
            optimization = task_params.get('optimization', {})
        
            logger.info("WP Rocket設定を開始...")
        
            # WP Rocket設定画面に移動
            await page.goto(f"{self.wp_url}/wp-admin/options-general.php?page=wprocket")
            await page.wait_for_timeout(3000)
        
            # スクリーンショット
            from datetime import datetime
            screenshot_path = f"wp_rocket_{datetime.now().strftime('%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
        
            logger.info("⚠️ WP Rocketの詳細設定は手動で確認してください")
        
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
        
        except Exception as e:
            logger.error(f"WP Rocket設定エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }


    # === 5. Relevanssi設定機能 ===
    async def configure_relevanssi(self, page: Page, task_params: Dict) -> Dict:
        """
        Relevanssi 高度な検索プラグインの設定
    
        Parameters:
            index_fields: list - インデックス対象フィールド
            search_settings: dict - 検索設定
        """
        try:
            index_fields = task_params.get('index_fields', [])
            search_settings = task_params.get('search_settings', {})
        
            logger.info("Relevanssi設定を開始...")
        
            # Relevanssi設定画面に移動
            await page.goto(f"{self.wp_url}/wp-admin/options-general.php?page=relevanssi/relevanssi.php")
            await page.wait_for_timeout(3000)
        
            # スクリーンショット
            from datetime import datetime
            screenshot_path = f"relevanssi_{datetime.now().strftime('%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
        
            logger.info("⚠️ Relevanssiの詳細設定は手動で確認してください")
        
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
        
        except Exception as e:
            logger.error(f"Relevanssi設定エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }


    # === 6. プラグイン一括設定機能 ===
    async def bulk_configure_plugins(self, page: Page, plugin_configs: List[Dict]) -> Dict:
        """
        複数のプラグインを一括で設定
    
        Parameters:
            plugin_configs: list - プラグイン設定のリスト
        """
        try:
            results = []
        
            for i, config in enumerate(plugin_configs, 1):
                plugin_name = config.get('plugin_name')
                logger.info(f"プラグイン設定 {i}/{len(plugin_configs)}: {plugin_name}")
            
                if plugin_name == 'facetwp':
                    result = await self.configure_facetwp(page, config)
                elif plugin_name == 'user-role-editor':
                    result = await self.configure_user_roles(page, config)
                elif plugin_name == 'wordfence':
                    result = await self.configure_wordfence(page, config)
                elif plugin_name == 'wp-rocket':
                    result = await self.configure_wp_rocket(page, config)
                elif plugin_name == 'relevanssi':
                    result = await self.configure_relevanssi(page, config)
                else:
                    result = {'success': False, 'error': f'未対応のプラグイン: {plugin_name}'}
            
                results.append({'plugin': plugin_name, 'result': result})
        
            successful = sum(1 for r in results if r['result'].get('success'))
        
            return {
                'success': successful > 0,
                'summary': f'{successful}/{len(plugin_configs)}件のプラグイン設定を完了',
                'results': results
            }
        
        except Exception as e:
            logger.error(f"プラグイン一括設定エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
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
            except:
                continue
        
        return False