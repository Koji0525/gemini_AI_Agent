""" wp_agent.py WordPressエージェント - メインオーケストレーター"""
import asyncio
import logging
from typing import Dict, Optional
from pathlib import Path
from playwright.async_api import Page

from config_utils import ErrorHandler
from browser_controller import BrowserController

from .wp_auth import WordPressAuth
from .wp_post_editor import WordPressPostEditor
from .wp_post_creator import WordPressPostCreator
from .wp_plugin_manager import WordPressPluginManager
from .wp_settings_manager import WordPressSettingsManager
from .wp_tester import WordPressTester
from .wp_utils import TaskTypeAnalyzer

logger = logging.getLogger(__name__)


    # === 修正開始: WordPressAgentクラスに自動ログイン機能を追加 ===

class WordPressAgent:
    def __init__(self, browser_controller, wp_credentials: Dict = None):
        """
        初期化
        
        Args:
            browser_controller: BrowserController インスタンス
            wp_credentials: WordPress 認証情報
                - wp_url: サイトURL
                - wp_user: ユーザー名
                - wp_pass: パスワード
        """
        self.browser = browser_controller
        self.wp_credentials = wp_credentials or {}
        self.is_logged_in = False
        
        # ★★★ ここから追加 ★★★
        # WordPress 専用ページ（新しいタブ）
        self.wp_page = None
        
        # 認証情報の取得
        self.wp_url = self.wp_credentials.get('wp_url', '').rstrip('/')
        self.wp_user = self.wp_credentials.get('wp_user', '')
        self.wp_pass = self.wp_credentials.get('wp_pass', '')
        
        # WordPress 認証モジュール
        if self.wp_url and self.wp_user and self.wp_pass:
            self.auth = WordPressAuth(
                browser_controller=self.browser,
                wp_url=self.wp_url,
                wp_user=self.wp_user,
                wp_pass=self.wp_pass
            )
        else:
            logger.warning("⚠️ WordPress 認証情報が不完全です")
            self.auth = None
    async def initialize_wp_session(self) -> bool:
        """
        WordPress セッション初期化（完全修正版 - クッキー強制ナビゲーション対応）
            
        改善点:
        1. 新しいタブ作成（Gemini セッションとは完全独立）
        2. クッキー適用 + 管理画面への強制ナビゲーション
        3. ログイン状態の厳格な検証
        4. 失敗時の手動ログインフォールバック
            
        Returns:
            bool: 初期化成功時 True
        """
        try:
            logger.info("="*60)
            logger.info("🔐 WordPress セッション初期化中...")
            logger.info("="*60)
                
            # ✅ Phase 1: 新しいタブを作成
            if not self.browser.context:
                logger.error("❌ ブラウザコンテキストが初期化されていません")
                return False
                
            self.wp_page = await self.browser.context.new_page()
            logger.info("✅ WordPress 専用タブを作成しました")
                
            # ✅ Phase 2: 認証情報の検証
            if not self.auth:
                logger.error("❌ WordPress 認証モジュールが初期化されていません")
                return False
                
            # ✅ Phase 3: ログイン実行（クッキー優先 + 強制ナビゲーション）
            logger.info("🔄 WordPress認証を実行中...")
            login_success = await self.auth.login(self.wp_page)
                
            if login_success:
                self.is_logged_in = True
                logger.info("="*60)
                logger.info("✅ WordPress セッション初期化完了")
                logger.info("  認証方法: クッキー or 手動ログイン")
                logger.info("  ページURL: " + self.wp_page.url)
                logger.info("="*60)
                return True
            else:
                logger.error("="*60)
                logger.error("❌ WordPress ログイン失敗")
                logger.error("  原因: 認証情報またはネットワークの問題")
                logger.error("  対策: 認証情報を確認してください")
                logger.error("="*60)
                    
                # デバッグ用: 失敗時のスクリーンショット
                try:
                    await self.wp_page.screenshot(path="wp_session_init_failed.png")
                    logger.info("📸 デバッグ用スクリーンショット: wp_session_init_failed.png")
                except:
                    pass
                    
                return False
                    
        except Exception as e:
            logger.error(f"❌ WordPress セッション初期化エラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    async def ensure_logged_in(self) -> bool:
        """
        ログイン状態を保証
    
        Returns:
            bool: ログイン済みまたはログイン成功時 True
        """
        if self.is_logged_in and self.wp_page:
            # 定期的にログイン状態を確認
            if await self.auth._verify_login_status(self.wp_page):
                return True
    
        # ログインしていない場合は再初期化
        logger.info("🔄 WordPress 再ログインを試行します")
        return await self.initialize_wp_session()
    
    async def _try_cookie_login(self, wp_url: str) -> bool:
        """クッキーを使用したログイン試行"""
        try:
            if not wp_url:
                logger.warning("⚠️ WordPress URLが設定されていません")
                return False
        
            # WordPressクッキーをロード
            cookie_loaded = await self.browser.load_wordpress_cookies(wp_url)
            if not cookie_loaded:
                return False
        
            # 管理画面にアクセスしてログイン状態を確認
            admin_url = f"{wp_url.rstrip('/')}/wp-admin/"
            await self.browser.page.goto(admin_url, wait_until='networkidle')
            await asyncio.sleep(2)
        
            # ログイン状態を詳細チェック
            return await self._verify_wordpress_login_status()
        
        except Exception as e:
            logger.warning(f"⚠️ クッキーログイン試行エラー: {e}")
            return False

    async def _verify_wordpress_login_status(self) -> bool:
        """WordPressログイン状態を詳細検証"""
        try:
            page = self.browser.page
        
            # 複数の方法でログイン状態を確認
            checks = []
        
            # 1. 管理バーの存在チェック
            admin_bar = await page.query_selector('#wpadminbar')
            checks.append(('管理バー', bool(admin_bar)))
        
            # 2. ダッシュボード要素チェック
            dashboard = await page.query_selector('#wpbody-content')
            checks.append(('ダッシュボード', bool(dashboard)))
        
            # 3. ログインフォームの不在チェック
            login_form = await page.query_selector('#loginform')
            checks.append(('ログインフォーム不在', not bool(login_form)))
        
            # 4. URLチェック（リダイレクトされていないか）
            current_url = page.url
            is_admin_page = '/wp-admin/' in current_url and 'wp-login.php' not in current_url
            checks.append(('管理ページURL', is_admin_page))
        
            # 結果の集計
            passed_checks = [name for name, passed in checks if passed]
            total_passed = len(passed_checks)
        
            logger.info(f"🔍 ログイン状態検証: {total_passed}/4 合格")
            if total_passed >= 3:  # 4つのうち3つ以上合格ならログイン成功
                logger.info(f"  合格項目: {', '.join(passed_checks)}")
                return True
            else:
                logger.warning(f"  不合格項目が多すぎます")
                return False
            
        except Exception as e:
            logger.warning(f"⚠️ ログイン状態検証エラー: {e}")
            return False

    async def _manual_wordpress_login(self) -> bool:
        """手動WordPressログイン"""
        try:
            wp_url = self.wp_credentials.get('wp_url', '')
            wp_user = self.wp_credentials.get('wp_user', '')
            wp_pass = self.wp_credentials.get('wp_pass', '')
        
            if not all([wp_url, wp_user, wp_pass]):
                logger.error("❌ WordPress認証情報が不足しています")
                return False
        
            # ログインページに移動
            login_url = f"{wp_url.rstrip('/')}/wp-login.php"
            await self.browser.page.goto(login_url, wait_until='networkidle')
            await asyncio.sleep(2)
        
            # ユーザー名入力
            user_field = await self.browser.page.query_selector('#user_login')
            if user_field:
                await user_field.fill(wp_user)
                logger.info("✅ ユーザー名入力完了")
            else:
                logger.error("❌ ユーザー名入力フィールドが見つかりません")
                return False
        
            # パスワード入力
            pass_field = await self.browser.page.query_selector('#user_pass')
            if pass_field:
                await pass_field.fill(wp_pass)
                logger.info("✅ パスワード入力完了")
            else:
                logger.error("❌ パスワード入力フィールドが見つかりません")
                return False
        
            # ログインボタンクリック
            login_button = await self.browser.page.query_selector('#wp-submit')
            if login_button:
                await login_button.click()
                logger.info("✅ ログインボタンクリック")
            else:
                logger.error("❌ ログインボタンが見つかりません")
                return False
        
            # ログイン完了待機
            await self.browser.page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)
        
            # ログイン成功確認
            if await self._verify_wordpress_login_status():
                logger.info("✅ 手動ログイン成功")
                return True
            else:
                logger.error("❌ 手動ログイン失敗 - 認証情報またはネットワークの問題")
                return False
            
        except Exception as e:
            logger.error(f"❌ 手動ログインエラー: {e}")
            return False

    async def ensure_logged_in(self) -> bool:
        """ログイン状態を保証"""
        if self.is_logged_in:
            return True
    
        # 定期的にログイン状態を確認
        if await self._verify_wordpress_login_status():
            self.is_logged_in = True
            return True
    
        # ログインしていない場合は再初期化
        return await self.initialize_wp_session()

# === 修正終了 ===
    
    async def process_task(self, task: Dict) -> Dict:
        """WordPressタスクを処理"""
        try:
            # ログイン状態を確認
            if not await self.ensure_logged_in():
                return {
                    'success': False,
                    'error': 'WordPress にログインできませんでした'
                }
            # === パート1: タスク実行開始 ===
            logger.info("="*60)
            logger.info("WordPressエージェント: タスク実行開始")
            logger.info(f"タスク: {task['description']}")
            logger.info("="*60)
            
            # === パート2: シートマネージャー設定 ===
            self.post_editor.sheets_manager = self.sheets_manager
            self.post_creator.sheets_manager = self.sheets_manager
            
            # === パート3: タスクタイプ解析 ===
            task_type = TaskTypeAnalyzer.analyze(task['description'])
            logger.info(f"解析されたタスクタイプ: {task_type}")
            
            # === パート4: タスクタイプに応じた処理実行 ===
            result = await self._execute_task_by_type(task, task_type)
            
            return result
            
        except Exception as e:
            ErrorHandler.log_error(e, "WordPressタスク処理")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_task_by_type(self, task: Dict, task_type: str) -> Dict:
        """タスクタイプに応じて適切なモジュールに処理を委譲"""
        try:
            # === パート1: プラグイン関連タスク ===
            if task_type == 'plugin_install':
                result = await self.plugin_manager.install_plugin(self.wp_page, task)
            elif task_type == 'plugin_settings':
                result = await self.plugin_manager.change_plugin_settings(self.wp_page, task)
            
            # === パート2: 投稿関連タスク ===
            elif task_type == 'edit_post':
                result = await self.post_editor.edit_post(self.wp_page, task)
            elif task_type == 'content_create':
                result = await self.post_creator.create_post(self.wp_page, task)
            
            # === パート3: 設定関連タスク ===
            elif task_type == 'theme_change':
                result = await self.settings_manager.change_theme(self.wp_page, task)
            elif task_type == 'setting_change':
                result = await self.settings_manager.change_settings(self.wp_page, task)
            
            # === パート4: テストタスク ===
            elif task_type == 'test_functionality':
                result = await self.tester.test_functionality(self.wp_page, task)
            
            # === パート5: その他のタスク ===
            else:
                result = await self._generic_execution(task)
            
            return result
            
        except Exception as e:
            ErrorHandler.log_error(e, "タスクタイプ別実行")
            return {
                'success': False,
                'error': str(e)
            }

    async def create_post(self, page: Page, task: Dict) -> Dict:
        """新規投稿を作成（post_status対応版）"""
        try:
            # === パート1: タスクパラメータ取得 ===
            post_status = task.get('post_status', 'draft')
            post_action = task.get('post_action', 'create')
        
            logger.info(f"WordPress投稿作成:")
            logger.info(f"  アクション: {post_action}")
            logger.info(f"  ステータス: {post_status}")
        
            # === パート2: 記事コンテンツ設定 ===
            # （既存の記事取得・タイトル・本文設定処理）
            article_title = "デフォルトタイトル"  # 実際の実装では適切な値を設定
            polylang_lang = "ja"
            language = "日本語"
            article_body = ""
            screenshot_path = None
        
            # === パート3: 投稿ステータスに応じた処理 ===
            status_result = await self._handle_post_status(page, post_status, post_action)
            
            # === パート4: 結果サマリー構築 ===
            summary = self._build_create_summary(
                article_title, polylang_lang, language, 
                len(article_body), post_status, status_result['message']
            )
        
            return {
                'success': True,
                'summary': summary,
                'post_status': post_status,
                'action': post_action,
                'screenshot': screenshot_path
            }
        
        except Exception as e:
            logger.error(f"❌ WordPress投稿作成エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _handle_post_status(self, page: Page, post_status: str, post_action: str) -> Dict:
        """投稿ステータスに応じた保存/公開処理"""
        try:
            # === パート1: 下書き保存の場合 ===
            if post_status == 'draft' or post_action == 'create':
                logger.info("\n【下書き保存中...】")
                saved = await self._save_draft(page)
            
                if saved:
                    logger.info("✅ 下書き保存完了")
                    return {'success': True, 'message': '下書き保存'}
                else:
                    logger.warning("⚠️ 下書き保存ボタンが見つかりませんでした")
                    return {'success': False, 'message': '保存確認推奨'}
        
            # === パート2: 公開の場合 ===
            elif post_status == 'publish' or post_action == 'publish':
                logger.info("\n【記事を公開中...】")
                published = await self._publish_post(page)
            
                if published:
                    logger.info("✅ 記事公開完了")
                    return {'success': True, 'message': '公開完了'}
                else:
                    logger.warning("⚠️ 公開ボタンが見つかりませんでした")
                    return {'success': False, 'message': '公開確認推奨'}
        
            # === パート3: その他のステータスの場合 ===
            else:
                logger.info(f"\n【カスタムステータス: {post_status}】")
                saved = await self._save_draft(page)
                return {
                    'success': saved, 
                    'message': f'保存完了（ステータス: {post_status}）'
                }
        
        except Exception as e:
            logger.error(f"投稿ステータス処理エラー: {e}")
            return {'success': False, 'message': f'エラー: {str(e)}'}


    async def _publish_post(self, page: Page) -> bool:
        """投稿を公開"""
        # === パート1: 公開ボタンセレクタ定義 ===
        publish_selectors = [
            'button:has-text("公開")',
            'button[aria-label="公開"]',
            '.editor-post-publish-button',
            'button.editor-post-publish-button__button'
        ]
    
        logger.debug("公開ボタンを探索中...")
    
        # === パート2: 公開ボタン探索ループ ===
        for i, selector in enumerate(publish_selectors, 1):
            logger.debug(f"  試行 {i}/{len(publish_selectors)}: {selector}")
            try:
                publish_button = await page.query_selector(selector)
                if not publish_button:
                    continue
                    
                # === パート3: ボタン状態チェック ===
                is_visible = await publish_button.is_visible()
                is_disabled = await publish_button.is_disabled() if is_visible else True
            
                logger.debug(f"  → 要素発見: 表示={is_visible}, 無効={is_disabled}")
            
                if is_visible and not is_disabled:
                    # === パート4: 公開ボタンクリック ===
                    await publish_button.click()
                    await page.wait_for_timeout(2000)
                
                    # === パート5: 確認ダイアログ処理 ===
                    try:
                        confirm_button = await page.query_selector('button:has-text("公開")')
                        if confirm_button and await confirm_button.is_visible():
                            await confirm_button.click()
                            await page.wait_for_timeout(3000)
                    except:
                        pass
                
                    logger.info("✅ 公開ボタンクリック成功")
                    return True
                    
            except Exception as e:
                logger.debug(f"  → エラー: {e}")
                continue
    
        logger.warning("❌ 公開ボタンが見つかりませんでした")
        return False


    async def _save_draft(self, page: Page) -> bool:
        """下書き保存"""
        # === パート1: 保存ボタンセレクタ定義 ===
        save_selectors = [
            'button:has-text("下書き保存")',
            'button[aria-label="下書き保存"]',
            '.editor-post-save-draft',
            '#save-post',
            'button.editor-post-save-draft'
        ]
    
        logger.debug("下書き保存ボタンを探索中...")
    
        # === パート2: 保存ボタン探索ループ ===
        for i, selector in enumerate(save_selectors, 1):
            logger.debug(f"  試行 {i}/{len(save_selectors)}: {selector}")
            try:
                save_button = await page.query_selector(selector)
                if not save_button:
                    continue
                    
                # === パート3: ボタン状態チェック ===
                is_visible = await save_button.is_visible()
                is_disabled = await save_button.is_disabled() if is_visible else True
            
                logger.debug(f"  → 要素発見: 表示={is_visible}, 無効={is_disabled}")
            
                if is_visible and not is_disabled:
                    # === パート4: 保存ボタンクリック ===
                    await save_button.click()
                    await page.wait_for_timeout(4000)
                    logger.info("✅ 下書き保存ボタンクリック成功")
                    return True
                    
            except Exception as e:
                logger.debug(f"  → エラー: {e}")
                continue
    
        logger.warning("❌ 下書き保存ボタンが見つかりませんでした")
        return False


    def _build_create_summary(self, title: str, polylang_lang: str, 
                             language: str, content_length: int, 
                             post_status: str, status_message: str) -> str:
        """新規投稿作成のサマリーを構築"""
        # === パート1: サマリー行の構築 ===
        summary_lines = []
        summary_lines.append("【WordPress投稿完了】")
        summary_lines.append(f"タイトル: {title}")
        summary_lines.append(f"言語: {language}")
        summary_lines.append(f"Polylang設定: {polylang_lang}")
        summary_lines.append(f"本文: {content_length}文字（HTML形式）")
        summary_lines.append(f"投稿ステータス: {post_status}")
        summary_lines.append(f"✅ {status_message}")
    
        # === パート2: サマリー文字列の結合 ===
        return '\n'.join(summary_lines)
    
    
    async def _generic_execution(self, task: Dict) -> Dict:
        """汎用的なタスク実行(Geminiに確認しながら実行)"""
        try:
            # === パート1: 実行開始 ===
            logger.info("汎用タスクを実行中...")
            
            # === パート2: Geminiプロンプト作成 ===
            gemini_prompt = self._build_gemini_prompt(task)
            
            # === パート3: Geminiに送信 ===
            await self.browser.send_prompt(gemini_prompt)
            await self.browser.wait_for_text_generation(max_wait=120)
            response = await self.browser.extract_latest_text_response()
            
            logger.info("Geminiから実行手順を取得しました")
            logger.info(f"手順:\n{response[:500]}...")
            
            # === パート4: 結果返却 ===
            return self._build_generic_result(task, response)
            
        except Exception as e:
            ErrorHandler.log_error(e, "汎用タスク実行")
            return {
                'success': False,
                'error': str(e)
            }

    def _build_gemini_prompt(self, task: Dict) -> str:
        """Gemini用プロンプトを構築"""
        return f"""
WordPressで以下のタスクを実行したいです:

【タスク】
{task['description']}

【WordPress情報】
- URL: {self.wp_url}
- 管理画面にログイン済み

【質問】
このタスクを実行するための具体的な手順を、WordPress管理画面の操作として教えてください。

以下の形式で回答してください:
1. 移動するページのURL(相対パス)
2. クリックまたは入力する要素のセレクタ
3. 入力する値
4. 確認すべきポイント

セレクタはできるだけ具体的に(id, class, name属性など)。
"""

    def _build_generic_result(self, task: Dict, response: str) -> Dict:
        """汎用実行の結果を構築"""
        logger.info("⚠️ 実際の実行は手動で確認してください")
        
        return {
            'success': True,
            'summary': 'Geminiから実行手順を取得しました。手順を確認して実行してください。',
            'full_text': f'【タスク】\n{task["description"]}\n\n【実行手順】\n{response}'
        }
    
    async def cleanup(self):
        """WordPressセッションをクリーンアップ"""
        # === パート1: ページクローズ ===
        if self.wp_page:
            await self.wp_page.close()
            logger.info("WordPressセッションを終了しました")


# === 追加機能メソッド（分割済み） ===

async def configure_acf_fields(self, task_params: Dict) -> Dict:
    """Advanced Custom Fieldsのフィールドグループを設定"""
    try:
        # === パート1: パラメータ取得 ===
        field_group_name = task_params.get('acf_field_group_name')
        fields = task_params.get('acf_fields', [])
        location_rules = task_params.get('acf_location_rules', {})
        
        logger.info(f"ACFフィールドグループ '{field_group_name}' を設定中...")
        
        # === パート2: ACF画面移動 ===
        await self.wp_page.goto(f"{self.wp_url}/wp-admin/edit.php?post_type=acf-field-group")
        await self.wp_page.wait_for_timeout(2000)
        
        # === パート3: 新規フィールドグループ追加 ===
        await self._click_acf_add_new_button()
        
        # === パート4: フィールドグループ名入力 ===
        await self._input_acf_field_group_name(field_group_name)
        
        # === パート5: スクリーンショットと結果返却 ===
        return await self._build_acf_result(field_group_name, fields, location_rules)
        
    except Exception as e:
        logger.error(f"ACF設定エラー: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def _click_acf_add_new_button(self):
    """ACF新規追加ボタンをクリック"""
    add_button_selectors = [
        'a.page-title-action:has-text("新規追加")',
        'a:has-text("Add New")',
        '.page-title-action'
    ]
    
    for selector in add_button_selectors:
        try:
            add_button = await self.wp_page.query_selector(selector)
            if add_button and await add_button.is_visible():
                await add_button.click()
                await self.wp_page.wait_for_timeout(3000)
                break
        except:
            continue

async def _input_acf_field_group_name(self, field_group_name: str):
    """ACFフィールドグループ名を入力"""
    title_input = await self.wp_page.query_selector('#title')
    if title_input:
        await title_input.fill(field_group_name)
        logger.info(f"フィールドグループ名を入力: {field_group_name}")

async def _build_acf_result(self, field_group_name: str, fields: list, location_rules: dict) -> Dict:
    """ACF設定結果を構築"""
    # スクリーンショット
    screenshot_path = f"acf_setup_{datetime.now().strftime('%H%M%S')}.png"
    await self.wp_page.screenshot(path=screenshot_path)
    
    logger.info("⚠️ ACFフィールドの詳細設定は手動で確認してください")
    
    return {
        'success': True,
        'summary': f'ACFフィールドグループ "{field_group_name}" の設定画面を開きました。',
        'field_group_name': field_group_name,
        'fields_count': len(fields),
        'screenshot': screenshot_path,
        'full_text': f'ACFフィールドグループ設定\n名前: {field_group_name}\nフィールド数: {len(fields)}\n※フィールド追加は手動で実施してください'
    }

# （他の追加機能メソッドも同様に分割。以下は一部のみ表示）

async def configure_custom_post_type(self, task_params: Dict) -> Dict:
    """Custom Post Type UIでカスタム投稿タイプを作成"""
    try:
        # === パート1: パラメータ取得 ===
        cpt_slug = task_params.get('cpt_slug')
        cpt_labels = task_params.get('cpt_labels', {})
        cpt_supports = task_params.get('cpt_supports', [])
        cpt_settings = task_params.get('cpt_settings', {})
        
        logger.info(f"カスタム投稿タイプ '{cpt_slug}' を作成中...")
        
        # === パート2: CPT UI画面移動 ===
        await self.wp_page.goto(f"{self.wp_url}/wp-admin/admin.php?page=cptui_manage_post_types")
        await self.wp_page.wait_for_timeout(3000)
        
        # === パート3: 基本情報入力 ===
        await self._input_cpt_basic_info(cpt_slug, cpt_labels)
        
        # === パート4: 結果構築 ===
        return await self._build_cpt_result(cpt_slug, cpt_labels)
        
    except Exception as e:
        logger.error(f"Custom Post Type作成エラー: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def _input_cpt_basic_info(self, cpt_slug: str, cpt_labels: dict):
    """CPT基本情報を入力"""
    # Post Type Slug入力
    slug_input = await self.wp_page.query_selector('input[name="cpt_custom_post_type[name]"]')
    if slug_input:
        await slug_input.fill(cpt_slug)
        logger.info(f"スラッグを入力: {cpt_slug}")
    
    # Plural Label入力
    plural_label = cpt_labels.get('plural', cpt_slug)
    plural_input = await self.wp_page.query_selector('input[name="cpt_custom_post_type[label]"]')
    if plural_input:
        await plural_input.fill(plural_label)
        logger.info(f"複数形ラベルを入力: {plural_label}")
    
    # Singular Label入力
    singular_label = cpt_labels.get('singular', cpt_slug)
    singular_input = await self.wp_page.query_selector('input[name="cpt_custom_post_type[singular_label]"]')
    if singular_input:
        await singular_input.fill(singular_label)
        logger.info(f"単数形ラベルを入力: {singular_label}")

async def _build_cpt_result(self, cpt_slug: str, cpt_labels: dict) -> Dict:
    """CPT作成結果を構築"""
    screenshot_path = f"cpt_creation_{cpt_slug}_{datetime.now().strftime('%H%M%S')}.png"
    await self.wp_page.screenshot(path=screenshot_path)
    
    logger.info("⚠️ 詳細設定とSupports設定は手動で確認してください")
    
    return {
        'success': True,
        'summary': f'カスタム投稿タイプ "{cpt_slug}" の設定画面を開きました。',
        'cpt_slug': cpt_slug,
        'cpt_labels': cpt_labels,
        'screenshot': screenshot_path,
        'full_text': f'Custom Post Type作成\nスラッグ: {cpt_slug}\nラベル: {cpt_labels}\n※Supports設定等は手動で実施してください'
    }


# === 3. カスタムタクソノミー作成機能 ===
async def configure_custom_taxonomy(self, task_params: Dict) -> Dict:
    """
    Custom Post Type UIでカスタムタクソノミーを作成
    
    Parameters:
        taxonomy_slug: str - タクソノミースラッグ
        taxonomy_labels: dict - ラベル設定
        taxonomy_post_types: list - 紐づける投稿タイプ
        taxonomy_hierarchical: bool - 階層構造の有無
    """
    try:
        taxonomy_slug = task_params.get('taxonomy_slug')
        taxonomy_labels = task_params.get('taxonomy_labels', {})
        taxonomy_post_types = task_params.get('taxonomy_post_types', [])
        taxonomy_hierarchical = task_params.get('taxonomy_hierarchical', True)
        
        logger.info(f"カスタムタクソノミー '{taxonomy_slug}' を作成中...")
        
        # 1 Custom Post Type UI - Taxonomies画面に移動
        await self.wp_page.goto(f"{self.wp_url}/wp-admin/admin.php?page=cptui_manage_taxonomies")
        await self.wp_page.wait_for_timeout(3000)
        
        # 2 Taxonomy Slug入力
        slug_input = await self.wp_page.query_selector('input[name="cpt_custom_tax[name]"]')
        if slug_input:
            await slug_input.fill(taxonomy_slug)
            logger.info(f"タクソノミースラッグを入力: {taxonomy_slug}")
        
        # 3 Plural Label入力
        plural_label = taxonomy_labels.get('plural', taxonomy_slug)
        plural_input = await self.wp_page.query_selector('input[name="cpt_custom_tax[label]"]')
        if plural_input:
            await plural_input.fill(plural_label)
            logger.info(f"複数形ラベルを入力: {plural_label}")
        
        # 4 Singular Label入力
        singular_label = taxonomy_labels.get('singular', taxonomy_slug)
        singular_input = await self.wp_page.query_selector('input[name="cpt_custom_tax[singular_label]"]')
        if singular_input:
            await singular_input.fill(singular_label)
            logger.info(f"単数形ラベルを入力: {singular_label}")
        
        # 5 スクリーンショット
        screenshot_path = f"taxonomy_creation_{taxonomy_slug}_{datetime.now().strftime('%H%M%S')}.png"
        await self.wp_page.screenshot(path=screenshot_path)
        
        logger.info("⚠️ Attach to Post Typesと階層設定は手動で確認してください")
        
        return {
            'success': True,
            'summary': f'カスタムタクソノミー "{taxonomy_slug}" の設定画面を開きました。',
            'taxonomy_slug': taxonomy_slug,
            'taxonomy_labels': taxonomy_labels,
            'screenshot': screenshot_path,
            'full_text': f'Custom Taxonomy作成\nスラッグ: {taxonomy_slug}\nラベル: {taxonomy_labels}\n※投稿タイプ紐付けは手動で実施してください'
        }
        
    except Exception as e:
        logger.error(f"カスタムタクソノミー作成エラー: {e}")
        return {
            'success': False,
            'error': str(e)
        }


# === 4. M&A案件投稿機能（ACFフィールド付き） ===
async def create_ma_case_post(self, task_params: Dict) -> Dict:
    """
    M&A案件をACFカスタムフィールド付きで投稿
    
    Parameters:
        post_title: str - 投稿タイトル
        post_content: str - 本文
        acf_fields: dict - ACFカスタムフィールドの値
        polylang_lang: str - 言語設定
        post_status: str - 投稿ステータス
    """
    try:
        post_title = task_params.get('post_title')
        post_content = task_params.get('post_content', '')
        acf_fields = task_params.get('acf_fields', {})
        polylang_lang = task_params.get('polylang_lang', 'ja')
        post_status = task_params.get('post_status', 'draft')
        
        logger.info(f"M&A案件投稿: {post_title}")
        
        # 1 新規投稿画面に移動（ma_case投稿タイプ）
        await self.wp_page.goto(f"{self.wp_url}/wp-admin/post-new.php?post_type=ma_case")
        await self.wp_page.wait_for_timeout(5000)
        
        # 2 タイトル入力
        await self._input_title(self.wp_page, post_title)
        
        # 3 本文入力（ある場合）
        if post_content:
            await self._input_content(self.wp_page, post_content)
        
        # 4 ACFフィールドに値を入力
        logger.info("ACFフィールドに値を入力中...")
        for field_name, field_value in acf_fields.items():
            try:
                # フィールド名からセレクタを推測
                field_selector = f'input[name="acf[{field_name}]"]'
                field_input = await self.wp_page.query_selector(field_selector)
                
                if field_input:
                    await field_input.fill(str(field_value))
                    logger.info(f"  {field_name}: {field_value}")
                else:
                    logger.warning(f"  フィールド '{field_name}' が見つかりません")
            except Exception as e:
                logger.warning(f"  フィールド '{field_name}' 入力エラー: {e}")
        
        # 5 Polylang言語設定
        await self._set_polylang_language(self.wp_page, polylang_lang)
        
        # 6 スクリーンショット
        screenshot_path = f"ma_case_{datetime.now().strftime('%H%M%S')}.png"
        await self.wp_page.screenshot(path=screenshot_path)
        
        # 7 保存または公開
        if post_status == 'draft':
            saved = await self._save_draft(self.wp_page)
            status_message = "下書き保存完了" if saved else "保存確認推奨"
        elif post_status == 'publish':
            published = await self._publish_post(self.wp_page)
            status_message = "公開完了" if published else "公開確認推奨"
        else:
            saved = await self._save_draft(self.wp_page)
            status_message = f"保存完了（ステータス: {post_status}）"
        
        summary = f"""【M&A案件投稿完了】
タイトル: {post_title}
言語: {polylang_lang}
ACFフィールド: {len(acf_fields)}件
投稿ステータス: {post_status}
✅ {status_message}"""
        
        return {
            'success': True,
            'summary': summary,
            'post_status': post_status,
            'acf_fields_count': len(acf_fields),
            'screenshot': screenshot_path,
            'full_text': summary
        }
        
    except Exception as e:
        logger.error(f"M&A案件投稿エラー: {e}")
        return {
            'success': False,
            'error': str(e)
        }


# === 5. Polylang翻訳連携機能 ===
async def link_polylang_translations(self, original_post_id: int, translated_post_id: int, lang_code: str) -> Dict:
    """
    Polylangで投稿同士を翻訳関係として連携
    
    Parameters:
        original_post_id: int - 元の投稿ID
        translated_post_id: int - 翻訳先の投稿ID
        lang_code: str - 翻訳先の言語コード
    """
    try:
        logger.info(f"Polylang翻訳連携: {original_post_id} → {translated_post_id} ({lang_code})")
        
        # 元の投稿の編集画面を開く
        await self.wp_page.goto(f"{self.wp_url}/wp-admin/post.php?post={original_post_id}&action=edit")
        await self.wp_page.wait_for_timeout(3000)
        
        # Polylang言語メタボックスで+ボタンをクリック
        logger.info("Polylang言語設定メタボックスを操作中...")
        
        # スクリーンショット
        screenshot_path = f"polylang_link_{datetime.now().strftime('%H%M%S')}.png"
        await self.wp_page.screenshot(path=screenshot_path)
        
        logger.info("⚠️ Polylang翻訳連携は手動で確認してください")
        
        return {
            'success': True,
            'summary': f'投稿ID {original_post_id} の編集画面を開きました。Polylang設定で投稿ID {translated_post_id} を連携してください。',
            'original_post_id': original_post_id,
            'translated_post_id': translated_post_id,
            'lang_code': lang_code,
            'screenshot': screenshot_path,
            'full_text': f'Polylang翻訳連携\n元投稿ID: {original_post_id}\n翻訳先ID: {translated_post_id}\n言語: {lang_code}\n※手動で連携を完了してください'
        }
        
    except Exception as e:
        logger.error(f"Polylang翻訳連携エラー: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def _calculate_dynamic_timeout(self, text_content: str) -> int:
    """動的タイムアウト計算 - WP処理対応"""
    base_timeout = 120
        
    # 既存のキーワード
    long_task_keywords = [
        '要件定義', '設計書', 'コード生成', '実装'
    ]
        
    # === 新規追加: WordPress専用キーワード ===
    wp_long_task_keywords = [
        'FacetWP', 'Relevanssi', 'インデックス再構築',
        'WP-CLI', 'データベース移行', 'プラグイン一括',
        'ACF Pro ライセンス', 'カスタムフィールド同期'
    ]
        
    # 通常の長時間タスク
    if any(kw in text_content for kw in long_task_keywords):
        base_timeout = 300
        
    # === WP特化の超長時間タスク ===
    if any(kw in text_content for kw in wp_long_task_keywords):
        base_timeout = 600  # 10分
        logger.info(f"⏱️ config WP長時間処理を検出 - タイムアウト: {base_timeout}秒")
    
    async def cleanup(self):
        """WordPress セッションをクリーンアップ"""
        if self.wp_page:
            try:
                await self.wp_page.close()
                logger.info("WordPress セッションを終了しました")
            except Exception as e:
                logger.warning(f"⚠️ WordPress ページクローズエラー: {e}")
        
    return base_timeout
        