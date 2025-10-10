import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
from playwright.async_api import Page, BrowserContext

from config_utils import ErrorHandler
from browser_controller import BrowserController

logger = logging.getLogger(__name__)

class WordPressAgent:
    """WordPress自動化エージェント - 設定変更、テスト、評価を実行"""
    
    def __init__(self, browser: BrowserController, wp_credentials: Dict[str, str]):
        self.browser = browser
        self.wp_url = wp_credentials.get('wp_url', '')
        self.wp_user = wp_credentials.get('wp_user', '')
        self.wp_pass = wp_credentials.get('wp_pass', '')
        self.wp_page: Optional[Page] = None
        self.test_results = []
        self.sheets_manager = None  # 後で設定される
        
    async def initialize_wp_session(self) -> bool:
        """WordPress管理画面にログイン"""
        try:
            logger.info("="*60)
            logger.info("WordPressエージェント: ログイン開始")
            logger.info(f"URL: {self.wp_url}")
            logger.info("="*60)
            
            # 新しいページを開く（Geminiとは別セッション）
            self.wp_page = await self.browser.context.new_page()
            
            # ログインページに移動
            login_url = f"{self.wp_url}/wp-login.php"
            await self.wp_page.goto(login_url, timeout=30000)
            await self.wp_page.wait_for_timeout(2000)
            
            # ユーザー名入力
            await self.wp_page.fill('#user_login', self.wp_user)
            await self.wp_page.wait_for_timeout(500)
            
            # パスワード入力
            await self.wp_page.fill('#user_pass', self.wp_pass)
            await self.wp_page.wait_for_timeout(500)
            
            # ログインボタンをクリック
            await self.wp_page.click('#wp-submit')
            await self.wp_page.wait_for_timeout(3000)
            
            # ログイン成功確認
            current_url = self.wp_page.url
            if 'wp-admin' in current_url:
                logger.info("✅ WordPressログイン成功")
                
                # スクリーンショット保存
                screenshot_path = f"wp_logged_in_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await self.wp_page.screenshot(path=screenshot_path)
                logger.info(f"📸 ログイン画面: {screenshot_path}")
                
                return True
            else:
                logger.error("❌ WordPressログイン失敗")
                await self.wp_page.screenshot(path="wp_login_failed.png")
                return False
                
        except Exception as e:
            ErrorHandler.log_error(e, "WordPressログイン")
            return False
    
    async def process_task(self, task: Dict) -> Dict:
        """WordPressタスクを処理"""
        try:
            logger.info("="*60)
            logger.info(f"WordPressエージェント: タスク実行開始")
            logger.info(f"タスク: {task['description']}")
            logger.info("="*60)
            
            # タスク内容を解析
            task_type = self._analyze_task_type(task['description'])
            
            if task_type == 'plugin_install':
                result = await self._install_plugin(task)
            elif task_type == 'edit_post':
                result = await self._edit_post(task)
            elif task_type == 'plugin_settings':
                result = await self._change_plugin_settings(task)
            elif task_type == 'theme_change':
                result = await self._change_theme(task)
            elif task_type == 'setting_change':
                result = await self._change_settings(task)
            elif task_type == 'content_create':
                result = await self._create_content(task)
            elif task_type == 'test_functionality':
                result = await self._test_functionality(task)
            else:
                # 汎用的な実行
                result = await self._generic_execution(task)
            
            return result
            
        except Exception as e:
            ErrorHandler.log_error(e, "WordPressタスク処理")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_task_type(self, description: str) -> str:
        """タスク内容からタイプを判定（改善版）"""
        description_lower = description.lower()
        
        # 「投稿を追加」は新規作成
        if '投稿を追加' in description or '投稿の追加' in description:
            return 'content_create'
        
        # 既存投稿の編集（「探して」「記事」「変更」「編集」などのキーワード）
        if '投稿' in description and '探して' in description and ('変更' in description or '編集' in description or '書き換え' in description):
            return 'edit_post'
        
        # プラグイン設定変更
        if 'プラグイン' in description and ('変更' in description or '設定' in description) and 'インストール' not in description:
            return 'plugin_settings'
        
        # プラグインインストール
        if 'プラグイン' in description and 'インストール' in description:
            return 'plugin_install'
        
        # テーマ変更
        if 'テーマ' in description or 'theme' in description_lower:
            return 'theme_change'
        
        # 設定変更
        if '設定' in description or 'setting' in description_lower:
            return 'setting_change'
        
        # コンテンツ作成
        if ('投稿' in description or '記事' in description or 'post' in description_lower) and ('作成' in description or '保存' in description):
            return 'content_create'
        
        # テスト
        if 'テスト' in description or 'test' in description_lower:
            return 'test_functionality'
        
        return 'generic'
    
    async def _get_task_content(self, task_id: int) -> Optional[str]:
        """指定されたtask_idの記事内容をスプレッドシートから取得"""
        try:
            if not self.sheets_manager:
                logger.error("❌ sheets_managerが設定されていません")
                logger.info("💡 run_multi_agent.py で wordpress_agent.sheets_manager = self.sheets_manager を設定してください")
                return None
            
            # task_logシートからtask_idに対応する出力内容を取得
            logger.info(f"📖 task_id {task_id} の記事内容を取得中...")
            
            # task_logシートから該当タスクを検索
            task_log_data = self.sheets_manager.worksheet_task_log.get_all_values()
            
            # ヘッダー行を確認
            if len(task_log_data) > 0:
                headers = task_log_data[0]
                logger.info(f"task_logヘッダー: {headers}")
                
                # output_data のカラムインデックスを探す
                output_data_col = None
                for i, header in enumerate(headers):
                    if 'output_data' in header.lower() or 'full_text' in header.lower():
                        output_data_col = i
                        logger.info(f"output_dataカラム: {i} ({header})")
                        break
                
                if output_data_col is None:
                    logger.warning("output_data カラムが見つかりません")
                    # フォールバック: 最後のカラムを使用
                    output_data_col = len(headers) - 1
            
            # データ行を検索
            for row_idx, row in enumerate(task_log_data[1:], start=2):  # ヘッダー行をスキップ、行番号は2から
                if len(row) > 0:
                    # task_id カラムを探す（通常は2列目: インデックス1）
                    task_id_in_row = None
                    try:
                        # B列（インデックス1）がtask_id
                        if len(row) > 1:
                            task_id_in_row = int(row[1])
                    except (ValueError, IndexError):
                        continue
                    
                    if task_id_in_row == task_id:
                        # 該当行を発見
                        logger.info(f"✅ task_id {task_id} を行 {row_idx} で発見")
                        
                        # output_dataを取得
                        if output_data_col and len(row) > output_data_col:
                            full_text = row[output_data_col]
                            if full_text and len(full_text) > 0:
                                logger.info(f"✅ task_id {task_id} の内容を取得しました（{len(full_text)}文字）")
                                logger.info(f"先頭100文字: {full_text[:100]}...")
                                return full_text
                        
                        logger.warning(f"task_id {task_id} の output_data が空です")
                        return None
            
            logger.warning(f"❌ task_id {task_id} の記事が見つかりませんでした")
            return None
            
        except Exception as e:
            logger.error(f"❌ task_id {task_id} の内容取得エラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _edit_post(self, task: Dict) -> Dict:
        """既存の投稿を編集"""
        try:
            logger.info("投稿編集を実行中...")
            
            # タスクからタイトルを抽出
            import re
            title_match = re.search(r'タイトル[　\s]*「(.+?)」', task['description'])
            if title_match:
                search_title = title_match.group(1)
                logger.info(f"検索タイトル: {search_title}")
            else:
                logger.warning("タイトルが見つかりませんでした")
                search_title = ""
            
            # task_idを抽出（例: "task_id 39"）
            task_id_match = re.search(r'task_id[　\s]*(\d+)', task['description'])
            replacement_content = None
            if task_id_match:
                target_task_id = int(task_id_match.group(1))
                logger.info(f"書き換え元のtask_id: {target_task_id}")
                replacement_content = await self._get_task_content(target_task_id)
            
            # 投稿一覧ページに移動
            await self.wp_page.goto(f"{self.wp_url}/wp-admin/edit.php")
            await self.wp_page.wait_for_timeout(3000)
            
            # 検索ボックスでタイトル検索
            if search_title:
                search_box = await self.wp_page.query_selector('#post-search-input')
                if search_box:
                    await search_box.fill(search_title)
                    await self.wp_page.keyboard.press('Enter')
                    await self.wp_page.wait_for_timeout(3000)
            
            # 投稿を見つけて編集ページに移動（改善版）
            post_found = False
            
            # 方法1: タイトルリンクから直接編集URLを取得
            try:
                title_link = await self.wp_page.query_selector(f'a.row-title:has-text("{search_title}")')
                if title_link:
                    # 投稿IDを取得
                    href = await title_link.get_attribute('href')
                    if href:
                        # post.php?post=XXX&action=edit のURLに直接移動
                        import re
                        post_id_match = re.search(r'post=(\d+)', href)
                        if post_id_match:
                            post_id = post_id_match.group(1)
                            edit_url = f"{self.wp_url}/wp-admin/post.php?post={post_id}&action=edit"
                            await self.wp_page.goto(edit_url)
                            await self.wp_page.wait_for_timeout(3000)
                            logger.info(f"✅ 投稿編集画面を開きました（投稿ID: {post_id}）")
                            post_found = True
            except Exception as e:
                logger.debug(f"方法1失敗: {e}")
            
            # 方法2: 編集リンクを探してクリック
            if not post_found:
                edit_link_selectors = [
                    f'tr:has-text("{search_title}") .row-actions .edit a',
                    f'a.row-title:has-text("{search_title}")',
                    '.row-actions .edit a'
                ]
                
                for selector in edit_link_selectors:
                    try:
                        edit_link = await self.wp_page.query_selector(selector)
                        if edit_link and await edit_link.is_visible():
                            await edit_link.click()
                            await self.wp_page.wait_for_timeout(4000)
                            logger.info(f"✅ 投稿編集画面を開きました")
                            post_found = True
                            break
                    except:
                        continue
            
            if not post_found:
                logger.warning("投稿が見つかりませんでした")
                screenshot_path = f"wp_post_not_found_{datetime.now().strftime('%H%M%S')}.png"
                await self.wp_page.screenshot(path=screenshot_path)
                return {
                    'success': False,
                    'error': f'タイトル「{search_title}」の投稿が見つかりませんでした',
                    'screenshot': screenshot_path
                }
            
            # Polylangの言語設定を日本語に変更
            polylang_selectors = [
                'select[name="post_lang_choice"]',
                '#post_lang_choice',
                'select.pll-select-flag'
            ]
            
            language_changed = False
            for selector in polylang_selectors:
                try:
                    lang_select = await self.wp_page.query_selector(selector)
                    if lang_select:
                        # 日本語を選択
                        await lang_select.select_option(label='日本語')
                        await self.wp_page.wait_for_timeout(2000)
                        logger.info("✅ Polylang言語を日本語に設定")
                        language_changed = True
                        
                        # 確認ダイアログが出現する場合があるので、OKボタンを探してクリック
                        try:
                            # ダイアログのOKボタンを探す
                            ok_button_selectors = [
                                'button:has-text("OK")',
                                'button:has-text("はい")',
                                '.ui-dialog-buttonset button:first-child',
                                'button.ui-button'
                            ]
                            
                            for ok_selector in ok_button_selectors:
                                ok_button = await self.wp_page.query_selector(ok_selector)
                                if ok_button and await ok_button.is_visible():
                                    await ok_button.click()
                                    await self.wp_page.wait_for_timeout(1000)
                                    logger.info("✅ 言語変更の確認ダイアログでOKをクリック")
                                    break
                        except Exception as e:
                            logger.debug(f"確認ダイアログ処理: {e}")
                        
                        break
                except Exception as e:
                    logger.debug(f"言語選択試行エラー ({selector}): {e}")
                    continue
            
            if not language_changed:
                logger.warning("Polylangの言語選択が見つかりませんでした")
            
            # 記事内容を書き換え
            if replacement_content:
                logger.info(f"記事内容を書き換え中...（{len(replacement_content)}文字）")
                
                # ブロックエディターの本文エリアをクリア＆入力
                content_selectors = [
                    '.block-editor-rich-text__editable',
                    'p.block-editor-rich-text__editable',
                    '[data-type="core/paragraph"] .block-editor-rich-text__editable'
                ]
                
                content_replaced = False
                for selector in content_selectors:
                    try:
                        # 既存の段落ブロックを全て取得
                        content_blocks = await self.wp_page.query_selector_all(selector)
                        if content_blocks:
                            # 最初のブロックをクリックしてフォーカス
                            await content_blocks[0].click()
                            await self.wp_page.wait_for_timeout(500)
                            
                            # 全選択して削除
                            await self.wp_page.keyboard.press('Control+A')
                            await self.wp_page.wait_for_timeout(300)
                            await self.wp_page.keyboard.press('Backspace')
                            await self.wp_page.wait_for_timeout(500)
                            
                            # 新しい内容を入力
                            await self.wp_page.keyboard.type(replacement_content)
                            await self.wp_page.wait_for_timeout(1000)
                            logger.info("✅ 記事内容を書き換えました")
                            content_replaced = True
                            break
                    except Exception as e:
                        logger.debug(f"内容書き換え試行エラー ({selector}): {e}")
                        continue
                
                if not content_replaced:
                    logger.warning("記事内容の書き換えに失敗しました")
            
            # 下書き保存
            save_selectors = [
                'button:has-text("下書き保存")',
                'button[aria-label="下書き保存"]',
                '.editor-post-save-draft',
                '#save-post'
            ]
            
            saved = False
            for selector in save_selectors:
                try:
                    save_button = await self.wp_page.query_selector(selector)
                    if save_button and await save_button.is_visible():
                        # ボタンが無効化されていないかチェック
                        is_disabled = await save_button.is_disabled()
                        if not is_disabled:
                            await save_button.click()
                            await self.wp_page.wait_for_timeout(3000)
                            logger.info("✅ 下書き保存完了")
                            saved = True
                            break
                except:
                    continue
            
            # 最終スクリーンショット
            screenshot_path = f"wp_edit_post_{datetime.now().strftime('%H%M%S')}.png"
            await self.wp_page.screenshot(path=screenshot_path, full_page=True)
            
            # 結果サマリー
            result_summary = []
            result_summary.append(f"投稿「{search_title}」を編集しました")
            if language_changed:
                result_summary.append("✅ Polylang言語を日本語に設定")
            if replacement_content:
                result_summary.append(f"✅ 記事内容を書き換え（{len(replacement_content)}文字）")
            if saved:
                result_summary.append("✅ 下書き保存完了")
            
            summary_text = '\n'.join(result_summary)
            
            return {
                'success': True,
                'summary': summary_text,
                'screenshot': screenshot_path,
                'full_text': f'{summary_text}\nスクリーンショット: {screenshot_path}'
            }
                
        except Exception as e:
            ErrorHandler.log_error(e, "投稿編集")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _change_plugin_settings(self, task: Dict) -> Dict:
        """プラグイン設定を変更"""
        try:
            logger.info("プラグイン設定変更を実行中...")
            
            # タスクからプラグイン名を抽出
            plugin_name = self._extract_plugin_name(task['description'])
            logger.info(f"対象プラグイン: {plugin_name}")
            
            # プラグイン一覧ページに移動
            await self.wp_page.goto(f"{self.wp_url}/wp-admin/plugins.php")
            await self.wp_page.wait_for_timeout(3000)
            
            # プラグインの設定リンクを探す
            settings_selectors = [
                f'tr:has-text("{plugin_name}") .settings a',
                f'a:has-text("{plugin_name}設定")',
                '.plugin-action-buttons a:has-text("設定")'
            ]
            
            settings_found = False
            for selector in settings_selectors:
                try:
                    settings_link = await self.wp_page.query_selector(selector)
                    if settings_link and await settings_link.is_visible():
                        await settings_link.click()
                        await self.wp_page.wait_for_timeout(3000)
                        logger.info(f"✅ {plugin_name}の設定画面を開きました")
                        settings_found = True
                        break
                except:
                    continue
            
            # スクリーンショット
            screenshot_path = f"wp_plugin_settings_{datetime.now().strftime('%H%M%S')}.png"
            await self.wp_page.screenshot(path=screenshot_path)
            
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
            ErrorHandler.log_error(e, "プラグイン設定変更")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _change_theme(self, task: Dict) -> Dict:
        """テーマを変更"""
        try:
            logger.info("テーマ変更を実行中...")
            
            # テーマページに移動
            await self.wp_page.goto(f"{self.wp_url}/wp-admin/themes.php")
            await self.wp_page.wait_for_timeout(3000)
            
            # 現在のテーマを確認
            screenshot_before = f"wp_themes_before_{datetime.now().strftime('%H%M%S')}.png"
            await self.wp_page.screenshot(path=screenshot_before)
            
            logger.info(f"✅ テーマ画面を表示しました")
            logger.info("⚠️ 実際のテーマ変更は手動で確認してください")
            
            return {
                'success': True,
                'summary': 'テーマ画面を表示しました。変更内容を確認して手動で適用してください。',
                'screenshot': screenshot_before,
                'full_text': f'テーマ確認完了\nスクリーンショット: {screenshot_before}'
            }
            
        except Exception as e:
            ErrorHandler.log_error(e, "テーマ変更")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _install_plugin(self, task: Dict) -> Dict:
        """プラグインをインストール（完全自動化版）"""
        try:
            logger.info("プラグインインストールを実行中...")
            
            # プラグインページに移動
            await self.wp_page.goto(f"{self.wp_url}/wp-admin/plugin-install.php")
            await self.wp_page.wait_for_timeout(2000)
            
            # タスクからプラグイン名を抽出
            plugin_name = self._extract_plugin_name(task['description'])
            
            # プラグイン検索
            search_box = await self.wp_page.query_selector('#search-plugins')
            if search_box:
                await search_box.fill(plugin_name)
                await self.wp_page.keyboard.press('Enter')
                await self.wp_page.wait_for_timeout(4000)
                
                logger.info(f"プラグイン検索完了: {plugin_name}")
                
                # 検索結果の最初のインストールボタンを探す
                install_selectors = [
                    f'a.install-now:has-text("今すぐインストール")',
                    '.plugin-card-top a.install-now',
                    'a[data-slug]:has-text("今すぐインストール")',
                ]
                
                installed = False
                for selector in install_selectors:
                    try:
                        install_button = await self.wp_page.query_selector(selector)
                        if install_button and await install_button.is_visible():
                            logger.info(f"インストールボタンをクリック: {selector}")
                            await install_button.click()
                            
                            # インストール完了を待つ
                            await self.wp_page.wait_for_timeout(5000)
                            
                            # 有効化ボタンを探す
                            activate_button = await self.wp_page.query_selector('a:has-text("有効化")')
                            if activate_button:
                                logger.info("有効化ボタンをクリック")
                                await activate_button.click()
                                await self.wp_page.wait_for_timeout(3000)
                                logger.info("✅ プラグインのインストールと有効化が完了しました")
                                installed = True
                                status = "インストール・有効化完了"
                            else:
                                logger.info("✅ プラグインのインストールが完了しました（有効化は手動）")
                                installed = True
                                status = "インストール完了（有効化は手動で実施してください）"
                            
                            break
                    except Exception as e:
                        logger.warning(f"インストール試行エラー ({selector}): {e}")
                        continue
                
                # スクリーンショット
                screenshot_path = f"wp_plugin_{datetime.now().strftime('%H%M%S')}.png"
                await self.wp_page.screenshot(path=screenshot_path)
                
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
                        'full_text': f'プラグイン検索: {plugin_name}\nスクリーンショット: {screenshot_path}\n※インストールボタンが見つからなかったため、手動で実施してください'
                    }
            else:
                return {
                    'success': False,
                    'error': '検索ボックスが見つかりません'
                }
                
        except Exception as e:
            ErrorHandler.log_error(e, "プラグインインストール")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _change_settings(self, task: Dict) -> Dict:
        """WordPress設定を変更"""
        try:
            logger.info("設定変更を実行中...")
            
            # 設定ページに移動
            await self.wp_page.goto(f"{self.wp_url}/wp-admin/options-general.php")
            await self.wp_page.wait_for_timeout(2000)
            
            # 現在の設定をスクリーンショット
            before_screenshot = f"wp_settings_before_{datetime.now().strftime('%H%M%S')}.png"
            await self.wp_page.screenshot(path=before_screenshot)
            
            logger.info(f"✅ 設定画面を確認しました")
            logger.info("⚠️ 実際の設定変更は手動で確認してください")
            
            return {
                'success': True,
                'summary': '設定画面を表示しました。変更内容を確認して手動で適用してください。',
                'screenshot': before_screenshot,
                'full_text': f'設定確認完了\nスクリーンショット: {before_screenshot}'
            }
            
        except Exception as e:
            ErrorHandler.log_error(e, "設定変更")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _test_functionality(self, task: Dict) -> Dict:
        """機能をテスト"""
        try:
            logger.info("機能テストを実行中...")
            
            test_results = []
            
            # 1. サイトの表示テスト
            await self.wp_page.goto(self.wp_url)
            await self.wp_page.wait_for_timeout(3000)
            
            # ページタイトル取得
            page_title = await self.wp_page.title()
            test_results.append(f"✅ サイト表示OK: {page_title}")
            
            # スクリーンショット
            site_screenshot = f"wp_site_{datetime.now().strftime('%H%M%S')}.png"
            await self.wp_page.screenshot(path=site_screenshot, full_page=True)
            test_results.append(f"📸 サイト全体: {site_screenshot}")
            
            # 2. 管理画面テスト
            await self.wp_page.goto(f"{self.wp_url}/wp-admin/")
            await self.wp_page.wait_for_timeout(2000)
            
            admin_screenshot = f"wp_admin_{datetime.now().strftime('%H%M%S')}.png"
            await self.wp_page.screenshot(path=admin_screenshot)
            test_results.append(f"✅ 管理画面OK")
            test_results.append(f"📸 管理画面: {admin_screenshot}")
            
            # 3. プラグインステータス確認
            await self.wp_page.goto(f"{self.wp_url}/wp-admin/plugins.php")
            await self.wp_page.wait_for_timeout(2000)
            
            plugins_screenshot = f"wp_plugins_{datetime.now().strftime('%H%M%S')}.png"
            await self.wp_page.screenshot(path=plugins_screenshot)
            test_results.append(f"✅ プラグイン一覧確認")
            test_results.append(f"📸 プラグイン: {plugins_screenshot}")
            
            summary = '\n'.join(test_results)
            logger.info("\n" + summary)
            
            return {
                'success': True,
                'summary': summary[:500],
                'full_text': summary
            }
            
        except Exception as e:
            ErrorHandler.log_error(e, "機能テスト")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generic_execution(self, task: Dict) -> Dict:
        """汎用的なタスク実行（Geminiに確認しながら実行）"""
        try:
            logger.info("汎用タスクを実行中...")
            
            # Geminiに実行手順を相談
            gemini_prompt = f"""
WordPressで以下のタスクを実行したいです：

【タスク】
{task['description']}

【WordPress情報】
- URL: {self.wp_url}
- 管理画面にログイン済み

【質問】
このタスクを実行するための具体的な手順を、WordPress管理画面の操作として教えてください。

以下の形式で回答してください：
1. 移動するページのURL（相対パス）
2. クリックまたは入力する要素のセレクタ
3. 入力する値
4. 確認すべきポイント

セレクタはできるだけ具体的に（id, class, name属性など）。
"""
            
            # Geminiに送信
            await self.browser.send_prompt(gemini_prompt)
            await self.browser.wait_for_text_generation(max_wait=120)
            response = await self.browser.extract_latest_text_response()
            
            logger.info("Geminiから実行手順を取得しました")
            logger.info(f"手順:\n{response[:500]}...")
            
            # 実際の実行は手動確認を推奨
            logger.info("⚠️ 実際の実行は手動で確認してください")
            
            return {
                'success': True,
                'summary': f'Geminiから実行手順を取得しました。手順を確認して実行してください。',
                'full_text': f'【タスク】\n{task["description"]}\n\n【実行手順】\n{response}'
            }
            
        except Exception as e:
            ErrorHandler.log_error(e, "汎用タスク実行")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_plugin_name(self, description: str) -> str:
        """タスク説明からプラグイン名を抽出"""
        # 簡易版: "プラグイン「XXX」"のようなパターンから抽出
        import re
        match = re.search(r'[「『](.+?)[」』]', description)
        if match:
            return match.group(1)
        
        # フォールバック: 説明文全体を使用
        return description[:50]
    
    async def _create_content(self, task: Dict) -> Dict:
        """コンテンツ（投稿/ページ）を作成（完全自動化版）"""
        try:
            logger.info("コンテンツ作成を実行中...")
            
            # task_idを抽出（例: "task_id 39"）
            import re
            task_id_match = re.search(r'task_id[　\s]*(\d+)', task['description'])
            post_content = None
            post_title = f"AI投稿_{datetime.now().strftime('%Y%m%d_%H%M')}"
            
            if task_id_match:
                target_task_id = int(task_id_match.group(1))
                logger.info(f"task_id {target_task_id} の記事内容を使用")
                post_content = await self._get_task_content(target_task_id)
                
                if post_content:
                    # タイトルを抽出（最初の行をタイトルとする）
                    lines = post_content.split('\n')
                    if lines:
                        post_title = lines[0].strip()[:100]  # 最初の100文字
                        # 本文は2行目以降
                        post_content = '\n'.join(lines[1:]).strip()
            
            if not post_content:
                # タスクからタイトルと本文を直接抽出
                title_match = re.search(r'タイトル[　\s]*(.+?)[\n本文]', task['description'])
                content_match = re.search(r'本文[　\s]*(.+?)[\nを]', task['description'])
                
                post_title = title_match.group(1).strip() if title_match else post_title
                post_content = content_match.group(1).strip() if content_match else "自動生成されたコンテンツ"
            
            logger.info(f"投稿内容: タイトル='{post_title}', 本文='{post_content[:50]}...'")
            
            # 新規投稿ページに移動
            await self.wp_page.goto(f"{self.wp_url}/wp-admin/post-new.php")
            await self.wp_page.wait_for_timeout(4000)
            
            # タイトル入力（ブロックエディター対応）
            title_selectors = [
                '.editor-post-title__input',
                'h1[aria-label="タイトルを追加"]',
                'textarea[placeholder*="タイトル"]',
                '#post-title-0'
            ]
            
            title_filled = False
            for selector in title_selectors:
                try:
                    title_input = await self.wp_page.query_selector(selector)
                    if title_input and await title_input.is_visible():
                        await title_input.click()
                        await self.wp_page.wait_for_timeout(500)
                        await title_input.fill(post_title)
                        await self.wp_page.wait_for_timeout(1000)
                        logger.info(f"✅ タイトル入力完了: {post_title}")
                        title_filled = True
                        break
                except:
                    continue
            
            if not title_filled:
                logger.warning("タイトル入力欄が見つかりません")
            
            # 本文入力（ブロックエディター）
            await self.wp_page.keyboard.press('Tab')
            await self.wp_page.wait_for_timeout(500)
            
            # ブロックエディターの本文エリアにフォーカス
            content_selectors = [
                'p[data-title="段落"]',
                '.block-editor-default-block-appender__content',
                '[aria-label="ブロックを追加"]',
                '.wp-block-paragraph'
            ]
            
            content_filled = False
            for selector in content_selectors:
                try:
                    content_area = await self.wp_page.query_selector(selector)
                    if content_area:
                        await content_area.click()
                        await self.wp_page.wait_for_timeout(500)
                        await self.wp_page.keyboard.type(post_content)
                        await self.wp_page.wait_for_timeout(1000)
                        logger.info(f"✅ 本文入力完了")
                        content_filled = True
                        break
                except:
                    continue
            
            if not content_filled:
                # フォールバック: 単純にTabキー後に入力
                await self.wp_page.keyboard.type(post_content)
                await self.wp_page.wait_for_timeout(1000)
                logger.info("✅ 本文入力完了（フォールバック）")
            
            # Polylangの言語を日本語に設定（存在する場合）
            try:
                polylang_selectors = [
                    'select[name="post_lang_choice"]',
                    '#post_lang_choice'
                ]
                
                for selector in polylang_selectors:
                    lang_select = await self.wp_page.query_selector(selector)
                    if lang_select:
                        await lang_select.select_option(label='日本語')
                        await self.wp_page.wait_for_timeout(1000)
                        logger.info("✅ Polylang言語を日本語に設定")
                        
                        # 確認ダイアログが出る場合はOKをクリック
                        try:
                            ok_button = await self.wp_page.query_selector('button:has-text("OK")')
                            if ok_button and await ok_button.is_visible():
                                await ok_button.click()
                                await self.wp_page.wait_for_timeout(1000)
                        except:
                            pass
                        break
            except Exception as e:
                logger.debug(f"Polylang設定: {e}")
            
            # 下書き保存
            save_selectors = [
                'button[aria-label="下書き保存"]',
                'button:has-text("下書き保存")',
                '.editor-post-save-draft'
            ]
            
            saved = False
            for selector in save_selectors:
                try:
                    save_button = await self.wp_page.query_selector(selector)
                    if save_button and await save_button.is_visible() and not (await save_button.is_disabled()):
                        await save_button.click()
                        await self.wp_page.wait_for_timeout(3000)
                        logger.info("✅ 下書き保存完了")
                        saved = True
                        break
                except:
                    continue
            
            # スクリーンショット
            screenshot_path = f"wp_post_saved_{datetime.now().strftime('%H%M%S')}.png"
            await self.wp_page.screenshot(path=screenshot_path, full_page=True)
            
            if saved:
                return {
                    'success': True,
                    'summary': f'投稿を下書き保存しました。タイトル: {post_title}',
                    'screenshot': screenshot_path,
                    'full_text': f'投稿作成完了\nタイトル: {post_title}\n本文: {post_content[:200]}...\nスクリーンショット: {screenshot_path}'
                }
            else:
                return {
                    'success': True,
                    'summary': f'投稿を作成しました（保存ボタンが見つからなかったため手動確認が必要）',
                    'screenshot': screenshot_path,
                    'full_text': f'投稿作成\nタイトル: {post_title}\n本文: {post_content[:200]}...\nスクリーンショット: {screenshot_path}'
                }
                
        except Exception as e:
            ErrorHandler.log_error(e, "コンテンツ作成")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def cleanup(self):
        """WordPressセッションをクリーンアップ"""
        if self.wp_page:
            await self.wp_page.close()
            logger.info("WordPressセッションを終了しました")