# run_multi_agent.py
"""マルチエージェントシステムの統合オーケストレーター（完全修正版）"""
# ========================================
# デバッグ: MATaskExecutor の確認
# ========================================
import sys
import importlib

# キャッシュクリア
if 'task_executor' in sys.modules:
    print("🔄 task_executor モジュールをリロード中...")
    importlib.reload(sys.modules['task_executor'])

from task_executor import MATaskExecutor

# メソッド確認
print("\n" + "="*60)
print("🔍 MATaskExecutor クラスの確認")
print("="*60)
print(f"📁 モジュール場所: {sys.modules['task_executor'].__file__}")
print("\n📋 利用可能なメソッド:")
methods = [m for m in dir(MATaskExecutor) if not m.startswith('_')]
for method in methods:
    print(f"  - {method}")

if 'run_all_tasks' in methods:
    print("\n✅ run_all_tasks メソッドが見つかりました")
else:
    print("\n❌ run_all_tasks メソッドが見つかりません")
    print("\n🚨 緊急パッチを適用します...")
    
    # 緊急パッチを動的にインポート
    exec(open('task_executor.py').read())

print("="*60 + "\n")

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
from pathlib import Path
import argparse

# ===== 最優先: ログ設定 =====
from config_utils import config, ErrorHandler, PathManager

# === パート1: エラーハンドラーのインポートと設定 ===
try:
    from error_handler_enhanced import (
        EnhancedErrorHandler,
        BrowserErrorHandler,
        SheetErrorHandler,
        TaskErrorHandler
    )
    HAS_ENHANCED_HANDLER = True
    logger = logging.getLogger(__name__)
    logger.info("✅ 強化版エラーハンドラー読み込み成功")
except ImportError:
    HAS_ENHANCED_HANDLER = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ error_handler_enhanced.py が見つかりません（標準エラーハンドラー使用）")
    EnhancedErrorHandler = None
    BrowserErrorHandler = None

# === パート2: その他のモジュールをインポート ===
from sheets_manager import GoogleSheetsManager
from browser_controller import BrowserController
from pm_agent import PMAgent
from task_executor import MATaskExecutor
from design_agent import DesignAgent
from dev_agent import DevAgent
from review_agent import ReviewAgent


class MultiAgentOrchestrator:
    """マルチエージェントシステムの統合オーケストレーター"""

    def __init__(self, pc_id: int = None, max_iterations: int = None):
        # === パート1: 基本パラメータの初期化 ===
        self.pc_id = pc_id or 1
        self.max_iterations = max_iterations
        
        # === パート2: コンポーネント変数の初期化 ===
        self.sheets_manager = None
        self.browser = None
        self.pm_agent = None
        self.task_executor = None
        self.design_agent = None
        self.dev_agent = None
        self.review_agent = None
        self.content_writer = None
        self.wordpress_agent = None
        self.output_folder = None
        self.initialization_success = False

    def _is_url(self, path_str: str) -> bool:
        """文字列がURLかどうかを判定"""
        # === パート1: 入力値の検証 ===
        if not path_str:
            return False
        
        # === パート2: URLパターンの判定 ===
        path_lower = path_str.lower().strip()
        return path_lower.startswith('http://') or path_lower.startswith('https://')

    async def _find_service_account_file(self) -> str:
        """サービスアカウントファイルを探す"""
        logger.info("📁 サービスアカウントファイルを検索中...")
        
        # === パート1: 検索パスの定義 ===
        possible_paths = [
            Path.cwd() / "service_account.json",
            Path.home() / "Documents" / "gemini_auto_generate" / "service_account.json",
            Path.home() / "Documents" / "AI_Agent" / "service_account.json",
            Path.home() / "Documents" / "gemini_AI_Agent" / "service_account.json",
            Path(__file__).parent / "service_account.json",
        ]
        
        # === パート2: 環境変数からのパス取得 ===
        env_path = os.environ.get('SERVICE_ACCOUNT_FILE')
        if env_path:
            possible_paths.insert(0, Path(env_path))
        
        # === パート3: バリデーション付きで検索 ===
        for path in possible_paths:
            if not path:
                continue
            
            if HAS_ENHANCED_HANDLER and EnhancedErrorHandler:
                validated_path = EnhancedErrorHandler.validate_file_path(path, must_exist=True)
                if validated_path:
                    logger.info(f"✅ サービスアカウントファイル発見: {validated_path}")
                    return str(validated_path)
            else:
                if path.exists():
                    logger.info(f"✅ サービスアカウントファイル発見: {path}")
                    return str(path)
        
        # === パート4: ファイルが見つからない場合のエラー処理 ===
        raise FileNotFoundError(
            "サービスアカウントファイルが見つかりません。\n"
            "以下の場所を確認してください:\n" +
            "\n".join(f"  - {p}" for p in possible_paths if p)
        )

    async def initialize(self):
        """システムの初期化"""
        try:
            print("="*60)
            print("🚀 マルチエージェントシステム起動中...")
            print("="*60)
    
            # === パート1: サービスアカウントファイルの取得 ===
            service_account_file = await self._find_service_account_file()
        
            # === パート2: Google Sheets Managerの初期化 ===
            logger.info("📊 Google Sheets 接続を初期化中...")
            self.sheets_manager = GoogleSheetsManager(config.SPREADSHEET_ID, service_account_file)
    
            # === パート3: PC設定の読み込み ===
            if self.pc_id is None:
                self.pc_id = self.sheets_manager.get_current_pc_id()
                logger.info(f"PC_ID={self.pc_id} をスプレッドシートから取得")
    
            logger.info(f"⚙️ PC_ID={self.pc_id} の設定を読み込み中...")
            # ⭐ ここで settings を定義
            settings = self.sheets_manager.load_pc_settings(self.pc_id)
        
            # === パート4: 設定の適用 ===
            config.BROWSER_DATA_DIR = settings.get('browser_data_dir')
            config.COOKIES_FILE = settings.get('cookies_file')
            config.GENERATION_MODE = 'text'
            config.SERVICE_TYPE = 'google'
        
            # === パート5: 出力フォルダの設定 ===
            agent_output_setting = settings.get('agent_output_folder', '').strip()
        
            if not agent_output_setting or self._is_url(agent_output_setting):
                if agent_output_setting:
                    logger.warning(f"⚠️ B14がURL形式のため、デフォルトフォルダを使用")
                user_docs = Path.home() / "Documents" / "gemini_auto_generate" / "agent_outputs"
                self.output_folder = user_docs
                self.output_folder.mkdir(exist_ok=True, parents=True)
                logger.info(f"📁 Agent出力先: {self.output_folder}")
            else:
                config.AGENT_OUTPUT_FOLDER = agent_output_setting
                self.output_folder = PathManager.get_safe_path(config.AGENT_OUTPUT_FOLDER)
                logger.info(f"📁 Agent出力先(B14から取得): {self.output_folder}")
        
            config.MAX_ITERATIONS = settings.get('max_iterations', 3)
        
            if self.max_iterations is None:
                self.max_iterations = config.MAX_ITERATIONS
    
            # === パート6: ブラウザの初期化(リトライ付き) ===
            browser_success = await self._initialize_browser_with_retry(max_retries=3)
        
            if not browser_success:
                raise Exception("ブラウザの初期化に失敗しました")
        
            # === パート7: Geminiサイトへのナビゲーション ===
            logger.info("="*60)
            logger.info("🌐 Geminiサイトへのナビゲーション開始...")
            logger.info("="*60)
        
            if HAS_ENHANCED_HANDLER and EnhancedErrorHandler:
                await EnhancedErrorHandler.timeout_wrapper(
                    self.browser.navigate_to_gemini(),
                    timeout=60.0,
                    context="Geminiナビゲーション"
                )
            else:
                await asyncio.wait_for(self.browser.navigate_to_gemini(), timeout=60.0)
    
            # === パート8: WordPress認証情報の取得 ===
            # ⭐ settings は既に定義済みなので使用可能
            wp_url = settings.get('wp_url', '').strip()
            wp_user = settings.get('wp_user', '').strip()
            wp_pass = settings.get('wp_pass', '').strip()
    
            # === パート9: 基本エージェントの初期化 ===
            logger.info("="*60)
            logger.info("🤖 AIエージェント初期化開始...")
            logger.info("="*60)
    
            self.pm_agent = PMAgent(self.sheets_manager, self.browser)
            self.task_executor = MATaskExecutor(
                self.sheets_manager, 
                self.browser,
                max_iterations=self.max_iterations
            )

            self.design_agent = DesignAgent(self.browser, output_folder=self.output_folder)
            self.dev_agent = DevAgent(self.browser, output_folder=self.output_folder)
    
            # ReviewAgentの初期化
            self.review_agent = ReviewAgent(self.browser, self.sheets_manager)

            # エージェント登録
            self.task_executor.register_agent('design', self.design_agent)
            self.task_executor.register_agent('dev', self.dev_agent)
            self.task_executor.register_review_agent(self.review_agent)
    
            logger.info("✅ 基本エージェント登録完了")
        
            # === パート10: WordPress 専用エージェントの初期化 ===
            logger.info("\n" + "="*60)
            logger.info("🌐 WordPress 専用エージェント初期化中...")
            logger.info("="*60)
        
            if wp_url and wp_user and wp_pass:
                # WordPress エージェントの初期化
                self.wordpress_agent = await self._initialize_wordpress_agent(wp_url, wp_user, wp_pass)
            
                if self.wordpress_agent:
                    logger.info("✅ WordPress エージェント初期化成功")
                else:
                    logger.warning("⚠️ WordPress エージェント初期化失敗（タスク実行に影響なし）")
            else:
                logger.info("⚠️ WordPress 認証情報が未設定です（スキップ）")
                self.wordpress_agent = None
        
            # === パート11: その他のエージェント初期化 ===
            # （content_writers, MA エージェントなど）
            # ... 既存のコードを維持 ...
        
            # === パート12: 初期化完了 ===
            logger.info("="*60)
            logger.info("✅ マルチエージェントシステム初期化完了")
            logger.info("="*60)
            logger.info(f"⚙️ 最大反復回数: {self.max_iterations}")
            logger.info(f"🆔 使用中の PC_ID: {self.pc_id}")
        
            self.initialization_success = True
        
        except Exception as e:
            logger.error("❌ システム初期化失敗")
            if HAS_ENHANCED_HANDLER and EnhancedErrorHandler:
                EnhancedErrorHandler.log_error_with_context(e, "システム初期化")
            else:
                ErrorHandler.log_error(e, "システム初期化")
            raise

    async def validate_system_health(self) -> bool:
        """システム健全性チェック（追加）"""
        try:
            logger.info("🔍 システム健全性チェック中...")
            
            # 1. スプレッドシート接続確認
            if not self.sheets_manager or not self.sheets_manager.gc:
                logger.error("❌ Google Sheets接続が確立されていません")
                return False
            
            # 2. シート構造検証
            if not self.sheets_manager.validate_sheet_structure():
                logger.error("❌ シート構造が不正です")
                return False
            
            # 3. タスクシートの基本検証
            try:
                tasks = await self.sheets_manager.load_tasks_from_sheet('pm_tasks')
                logger.info(f"📊 タスクシート読み込み: {len(tasks)}件")
                
                # タスクIDの重複チェック
                task_ids = [task.get('task_id') for task in tasks if task.get('task_id')]
                unique_ids = set(task_ids)
                if len(task_ids) != len(unique_ids):
                    logger.warning(f"⚠️ タスクID重複検出: {len(task_ids)} -> {len(unique_ids)}ユニーク")
                
            except Exception as e:
                logger.warning(f"⚠️ タスクシート検証エラー: {e}")
            
            logger.info("✅ システム健全性チェック完了")
            return True
            
        except Exception as e:
            logger.error(f"❌ 健全性チェックエラー: {e}")
            return False


    async def _initialize_wordpress_agent(self, wp_url: str, wp_user: str, wp_pass: str):
        """
        WordPress エージェント初期化（完全修正版）
    
        シーケンス:
        1. WordPress エージェントのインスタンス化
        2. WordPress セッション初期化（新しいタブで）
        3. タスクエグゼキュータへの登録
    
        Args:
            wp_url: WordPress サイトURL
            wp_user: ユーザー名
            wp_pass: パスワード
        
        Returns:
            WordPressAgent or None
        """
        try:
            # WordPress エージェントモジュールのインポート
            if HAS_ENHANCED_HANDLER and EnhancedErrorHandler:
                has_module = EnhancedErrorHandler.handle_import_error(
                    'wordpress.wp_agent',
                    optional=True
                )
                if not has_module:
                    logger.warning("⚠️ WordPress モジュールが見つかりません")
                    return None
        
            from wordpress.wp_agent import WordPressAgent
        
            # 認証情報の設定
            wp_credentials = {
                'wp_url': wp_url,
                'wp_user': wp_user,
                'wp_pass': wp_pass
            }
        
            logger.info("🌐 WordPress エージェント初期化中...")
        
            # ステップ1: インスタンス化
            wordpress_agent = WordPressAgent(self.browser, wp_credentials)
            wordpress_agent.sheets_manager = self.sheets_manager
        
            # ステップ2: WordPress セッション初期化（新しいタブで）
            logger.info("🔐 WordPress セッション初期化中...")
        
            if HAS_ENHANCED_HANDLER and EnhancedErrorHandler:
                wp_login_success = await EnhancedErrorHandler.timeout_wrapper(
                    wordpress_agent.initialize_wp_session(),
                    timeout=90.0,
                    context="WordPress セッション初期化"
                )
            else:
                wp_login_success = await asyncio.wait_for(
                    wordpress_agent.initialize_wp_session(),
                    timeout=90.0
                )
        
            # ステップ3: 初期化結果の処理
            if wp_login_success:
                # タスクエグゼキュータに登録
                self.task_executor.register_agent('wordpress', wordpress_agent)
                logger.info("✅ WordPress エージェント登録完了")
            
                # クッキー保存状態をログ出力
                wp_cookies_file = self.browser.wp_cookies_file
                if wp_cookies_file and wp_cookies_file.exists():
                    logger.info(f"🍪 WordPress クッキー: {wp_cookies_file}")
                else:
                    logger.info("🍪 WordPress クッキー: 新規作成済み")
            
                return wordpress_agent
            else:
                logger.error("❌ WordPress セッション初期化失敗")
                return None
            
        except Exception as e:
            logger.error(f"WordPress エージェント初期化エラー: {e}")
            if HAS_ENHANCED_HANDLER and EnhancedErrorHandler:
                EnhancedErrorHandler.log_error_with_context(e, "WordPress 初期化")
            return None

    def _print_browser_troubleshooting(self):
        """ブラウザトラブルシューティングガイド"""
        # === パート1: トラブルシューティング情報の表示 ===
        logger.error("\n📋 トラブルシューティング:")
        logger.error("1. ✅ 既存のChromeプロセスを全て終了")
        logger.error("2. 📁 ブラウザデータディレクトリの権限確認")
        logger.error(f"     → {config.BROWSER_DATA_DIR}")
        logger.error("3. 🔧 Playwrightの再インストール:")
        logger.error("     → playwright install chromium")
        logger.error("4. 🗑️ ブラウザキャッシュのクリア:")
        logger.error(f"     → {config.BROWSER_DATA_DIR} を削除")
        logger.error("5. 🔄 システムの再起動")

    # === 修正開始: MultiAgentOrchestratorのWordPress初期化を強化 ===

    async def _initialize_wordpress_agent(self, wp_url: str, wp_user: str, wp_pass: str):
        """WordPressエージェント初期化（クッキー管理対応版）"""
        try:
            # インポートチェック
            if HAS_ENHANCED_HANDLER and EnhancedErrorHandler:
                has_module = EnhancedErrorHandler.handle_import_error(
                    'wordpress.wp_agent',
                    optional=True
                )
                if not has_module:
                    logger.warning("⚠️ WordPressモジュールが見つかりません")
                    return None
        
            from wordpress.wp_agent import WordPressAgent
        
            # 認証情報の設定
            wp_credentials = {
                'wp_url': wp_url,
                'wp_user': wp_user,
                'wp_pass': wp_pass
            }
        
            logger.info("🌐 WordPressエージェント初期化中...")
            self.wordpress_agent = WordPressAgent(self.browser, wp_credentials)
            self.wordpress_agent.sheets_manager = self.sheets_manager
        
            # WordPressセッション初期化（クッキー優先）
            logger.info("🔐 WordPressセッション初期化中...")
        
            # タイムアウト付き初期化
            if HAS_ENHANCED_HANDLER and EnhancedErrorHandler:
                wp_login_success = await EnhancedErrorHandler.timeout_wrapper(
                    self.wordpress_agent.initialize_wp_session(),
                    timeout=90.0,  # 90秒に延長
                    context="WordPressセッション初期化"
                )
            else:
                wp_login_success = await asyncio.wait_for(
                    self.wordpress_agent.initialize_wp_session(),
                    timeout=90.0
                )
        
            # 初期化結果の処理
            if wp_login_success:
                self.task_executor.register_agent('wordpress', self.wordpress_agent)
                logger.info("✅ WordPressエージェント登録完了")
            
                # クッキー保存状態をログ出力
                wp_cookies_file = self.browser.wp_cookies_file
                if wp_cookies_file.exists():
                    logger.info(f"📁 WordPressクッキー: {wp_cookies_file}")
                else:
                    logger.info("📁 WordPressクッキー: 新規作成済み")
                
                return self.wordpress_agent
            else:
                logger.error("❌ WordPressセッション初期化失敗")
                return None
            
        except Exception as e:
            logger.error(f"WordPressエージェント初期化エラー: {e}")
            if HAS_ENHANCED_HANDLER and EnhancedErrorHandler:
                EnhancedErrorHandler.log_error_with_context(e, "WordPress初期化")
            return None


    async def initialize(self):
        """システムの初期化"""
        try:
            print("="*60)
            print("🚀 マルチエージェントシステム起動中...")
            print("="*60)
        
            # === パート1: サービスアカウントファイルの取得 ===
            service_account_file = await self._find_service_account_file()
            
            # === パート2: Google Sheets Managerの初期化 ===
            logger.info("📊 Google Sheets 接続を初期化中...")
            self.sheets_manager = GoogleSheetsManager(config.SPREADSHEET_ID, service_account_file)
        
            health_ok = await self.validate_system_health()
            if not health_ok:
                logger.warning("⚠️ システム健全性チェックで警告が検出されました")
        
            # === パート3: PC設定の読み込み ===
            if self.pc_id is None:
                self.pc_id = self.sheets_manager.get_current_pc_id()
                logger.info(f"PC_ID={self.pc_id} をスプレッドシートから取得")
        
            logger.info(f"⚙️ PC_ID={self.pc_id} の設定を読み込み中...")
            settings = self.sheets_manager.load_pc_settings(self.pc_id)
            
            # === パート4: 設定の適用 ===
            config.BROWSER_DATA_DIR = settings.get('browser_data_dir')
            config.COOKIES_FILE = settings.get('cookies_file')
            config.GENERATION_MODE = 'text'
            config.SERVICE_TYPE = 'google'
            
            # === パート5: 出力フォルダの設定 ===
            agent_output_setting = settings.get('agent_output_folder', '').strip()
            
            if not agent_output_setting or self._is_url(agent_output_setting):
                if agent_output_setting:
                    logger.warning(f"⚠️ B14がURL形式のため、デフォルトフォルダを使用")
                user_docs = Path.home() / "Documents" / "gemini_auto_generate" / "agent_outputs"
                self.output_folder = user_docs
                self.output_folder.mkdir(exist_ok=True, parents=True)
                logger.info(f"📁 Agent出力先: {self.output_folder}")
            else:
                config.AGENT_OUTPUT_FOLDER = agent_output_setting
                self.output_folder = PathManager.get_safe_path(config.AGENT_OUTPUT_FOLDER)
                logger.info(f"📁 Agent出力先(B14から取得): {self.output_folder}")
            
            config.MAX_ITERATIONS = settings.get('max_iterations', 3)
            
            if self.max_iterations is None:
                self.max_iterations = config.MAX_ITERATIONS
        
            # === パート6: ブラウザの初期化（リトライ付き） ===
            browser_success = await self._initialize_browser_with_retry(max_retries=3)
            
            if not browser_success:
                raise Exception("ブラウザの初期化に失敗しました")
            
            # === パート7: Geminiサイトへのナビゲーション ===
            logger.info("="*60)
            logger.info("🌐 Geminiサイトへのナビゲーション開始...")
            logger.info("="*60)
            
            if HAS_ENHANCED_HANDLER and EnhancedErrorHandler:
                await EnhancedErrorHandler.timeout_wrapper(
                    self.browser.navigate_to_gemini(),
                    timeout=60.0,
                    context="Geminiナビゲーション"
                )
            else:
                await asyncio.wait_for(self.browser.navigate_to_gemini(), timeout=60.0)
        
            # === パート8: WordPress認証情報の取得 ===
            wp_url = settings.get('wp_url', '').strip()
            wp_user = settings.get('wp_user', '').strip()
            wp_pass = settings.get('wp_pass', '').strip()
        
            # === パート9: 基本エージェントの初期化 ===
            logger.info("="*60)
            logger.info("🤖 AIエージェント初期化開始...")
            logger.info("="*60)
        
            self.pm_agent = PMAgent(self.sheets_manager, self.browser)
            self.task_executor = MATaskExecutor(
                self.sheets_manager, 
                self.browser,
                max_iterations=self.max_iterations
            )
    
            self.design_agent = DesignAgent(self.browser, output_folder=self.output_folder)
            self.dev_agent = DevAgent(self.browser, output_folder=self.output_folder)
        
            # ReviewAgentの初期化
            self.review_agent = ReviewAgent(self.browser, self.sheets_manager)
    
            # エージェント登録
            self.task_executor.register_agent('design', self.design_agent)
            self.task_executor.register_agent('dev', self.dev_agent)
            self.task_executor.register_review_agent(self.review_agent)
        
            logger.info("✅ 基本エージェント登録完了")

            # === パート10: WordPress専用エージェントの初期化 ===
            logger.info("\n" + "="*60)
            logger.info("🌐 WordPress専用エージェントを初期化中...")
            logger.info("="*60)
            
            # WordPress認証情報の取得
            wp_credentials = {
                'wp_url': wp_url,
                'wp_user': wp_user,
                'wp_pass': wp_pass
            }
            
            # === WordPress設計AIエージェント (wp_design) ===
            try:
                from wordpress.wp_design import WordPressDesignAgent
                wp_design_agent = WordPressDesignAgent(
                    self.browser, 
                    output_folder=self.output_folder
                )
                wp_design_agent.sheets_manager = self.sheets_manager
                self.task_executor.register_agent('wp_design', wp_design_agent)
                logger.info("✅ WordPress設計AIエージェント登録完了")
            except ImportError:
                logger.warning("⚠️ wordpress/wp_design.py が見つかりません")
            except Exception as e:
                logger.warning(f"⚠️ WordPress設計AIエージェント登録失敗: {e}")
            
            # === WordPress開発AIエージェント (wp_dev) ===
            try:
                from wordpress.wp_dev import WordPressDevAgent
                
                # WordPressDevAgent のインスタンス化
                wp_dev_agent = WordPressDevAgent(
                    self.browser,
                    wp_credentials=wp_credentials,
                    output_folder=self.output_folder
                )
                wp_dev_agent.sheets_manager = self.sheets_manager
                
                # タスクエグゼキューターに登録
                self.task_executor.register_agent('wp_dev', wp_dev_agent)
                logger.info("✅ WordPress開発AIエージェント(wp_dev)登録完了")
                
                # 標準 dev エージェントのバックアップ登録も維持
                if self.dev_agent:
                    # 既存の dev エージェントは維持（要件定義用）
                    logger.info("✅ 標準 dev エージェントも維持（要件定義タスク用）")
                
            except ImportError:
                logger.warning("⚠️ wordpress/wp_dev.py が見つかりません")
                logger.info("💡 WordPress開発タスクは標準 dev エージェントで処理されます")
                
                # フォールバック: 標準 dev エージェントを wp_dev としても登録
                if self.dev_agent:
                    self.task_executor.register_agent('wp_dev', self.dev_agent)
                    logger.info("🔄 標準 dev エージェントを wp_dev としても登録しました")
                    
            except Exception as e:
                logger.warning(f"⚠️ WordPress開発AIエージェント初期化失敗: {e}")
                
                # エラー時のフォールバック
                if self.dev_agent:
                    self.task_executor.register_agent('wp_dev', self.dev_agent)
                    logger.info("🔄 エラーのため標準 dev エージェントで代替")


            # === パート11: M&A専用エージェントの初期化 ===
            logger.info("\n" + "="*60)
            logger.info("📊 M&A専用エージェントを初期化中...")
            logger.info("="*60)
            
            try:
                from task_executor_ma import MATaskExecutor
                ma_task_executor = MATaskExecutor(self.task_executor.agents)
                self.task_executor.register_agent('ma', ma_task_executor)
                self.task_executor.register_agent('wordpress_ma', ma_task_executor)
                
                # ⭐ 重要: dev エージェントを wp_dev としても登録（バックアップ）
                # wp_dev 専用エージェントが登録されていない場合のフォールバック
                if 'wp_dev' not in self.task_executor.agents and self.dev_agent:
                    self.task_executor.register_agent('wp_dev', self.dev_agent)
                    logger.info("✅ dev エージェントを wp_dev フォールバックとして登録")
                
                logger.info("✅ M&A専用タスク実行エージェント登録完了")
            except ImportError:
                logger.warning("⚠️ task_executor_ma.py が見つかりません")
            except Exception as e:
                logger.warning(f"⚠️ M&A専用エージェント登録失敗: {e}")
            
            # === パート12: 多言語ライターエージェントの初期化 ===
            logger.info("\n" + "="*60)
            logger.info("多言語ライターエージェントを初期化中...")
            logger.info("="*60)
            
            try:
                from content_writers import (
                    JapaneseWriterAgent,
                    EnglishWriterAgent,
                    RussianWriterAgent,
                    UzbekWriterAgent,
                    ChineseWriterAgent,
                    KoreanWriterAgent,
                    TurkishWriterAgent
                )
                
                # 日本語ライター
                ja_writer = JapaneseWriterAgent(self.browser, output_folder=self.output_folder)
                self.task_executor.register_agent('writer_ja', ja_writer)
                logger.info("✅ 日本語ライターエージェント登録完了")
                
                # 英語ライター
                en_writer = EnglishWriterAgent(self.browser, output_folder=self.output_folder)
                self.task_executor.register_agent('writer_en', en_writer)
                logger.info("✅ 英語ライターエージェント登録完了")
                
                # ロシア語ライター
                ru_writer = RussianWriterAgent(self.browser, output_folder=self.output_folder)
                self.task_executor.register_agent('writer_ru', ru_writer)
                logger.info("✅ ロシア語ライターエージェント登録完了")
                
                # ウズベク語ライター
                uz_writer = UzbekWriterAgent(self.browser, output_folder=self.output_folder)
                self.task_executor.register_agent('writer_uz', uz_writer)
                logger.info("✅ ウズベク語ライターエージェント登録完了")
                
                # 中国語ライター
                zh_writer = ChineseWriterAgent(self.browser, output_folder=self.output_folder)
                self.task_executor.register_agent('writer_zh', zh_writer)
                logger.info("✅ 中国語ライターエージェント登録完了")
                
                # 韓国語ライター
                ko_writer = KoreanWriterAgent(self.browser, output_folder=self.output_folder)
                self.task_executor.register_agent('writer_ko', ko_writer)
                logger.info("✅ 韓国語ライターエージェント登録完了")
                
                # トルコ語ライター
                tr_writer = TurkishWriterAgent(self.browser, output_folder=self.output_folder)
                self.task_executor.register_agent('writer_tr', tr_writer)
                logger.info("✅ トルコ語ライターエージェント登録完了")
                
            except Exception as e:
                logger.warning(f"⚠️ コンテンツライターエージェント登録失敗: {e}")
            
            # === パート13: WordPress投稿管理エージェントの初期化 ===
            if wp_url and wp_user and wp_pass:
                self.wordpress_agent = await self._initialize_wordpress_agent(wp_url, wp_user, wp_pass)
            else:
                logger.info("⚠️ WordPress認証情報が未設定です(スキップ)")
                self.wordpress_agent = None
        
            # === パート14: 初期化完了の確認 ===
            logger.info("="*60)
            logger.info("✅ マルチエージェントシステム初期化完了")
            logger.info("="*60)
            logger.info(f"⚙️ 最大反復回数: {self.max_iterations}")
            logger.info(f"🆔 使用中のPC_ID: {self.pc_id}")
            
            self.initialization_success = True
        
        except Exception as e:
            logger.error("❌ システム初期化失敗")
            if HAS_ENHANCED_HANDLER and EnhancedErrorHandler:
                EnhancedErrorHandler.log_error_with_context(e, "システム初期化")
            else:
                ErrorHandler.log_error(e, "システム初期化")
            raise

    async def run_full_workflow(self, goal: str = None, auto_continue: bool = False, enable_review: bool = True):
        """完全なワークフローを実行"""
        # === パート1: 初期化状態の確認 ===
        if not self.initialization_success:
            raise Exception("システムが初期化されていません")
        
        try:
            # === パート2: PM AIによるタスク分解フェーズ ===
            print("\n" + "="*60)
            print("📋 フェーズ1: PM AIによるタスク分解")
            print("="*60)
            
            if goal:
                goal_description = goal
                logger.info(f"🎯 指定された目標: {goal_description}")
            else:
                goal_data = await self.pm_agent.load_project_goal()
                if not goal_data:
                    print("\n❌ エラー: 目標が見つかりません")
                    print("--goal オプションで目標を指定するか、")
                    print("スプレッドシートの'project_goal'シートに目標を設定してください")
                    return
                goal_description = goal_data['description']
            
            task_plan = await self.pm_agent.analyze_and_create_tasks(goal_description)
            self.pm_agent.display_task_summary(task_plan)
            
            # === パート3: タスク保存の確認 ===
            if not auto_continue:
                save = input("\n💾 タスクをスプレッドシートに保存しますか? (y/n): ")
                if save.lower() != 'y':
                    print("⏸️ 実行をキャンセルしました")
                    return
            
            await self.pm_agent.save_tasks_to_sheet(task_plan)
            
            # === パート4: タスク実行フェーズ ===
            print("\n" + "="*60)
            print("⚙️ フェーズ2: タスクの実行")
            print("="*60)
            
            if enable_review:
                print("✅ レビューAI: 有効")
            else:
                print("⏭️ レビューAI: 無効")
            
            if not auto_continue:
                execute = input("\n▶️ タスクの実行を開始しますか? (y/n): ")
                if execute.lower() != 'y':
                    print("⏸️ タスク実行をスキップしました")
                    return
            
            # === パート5: タスク実行の実行 ===
            await self.task_executor.run_all_tasks(
                auto_continue=auto_continue,
                enable_review=enable_review
            )
            
            # === パート6: 完了メッセージの表示 ===
            print("\n" + "="*60)
            print("🎉 ワークフロー完了")
            print("="*60)
            print(f"📁 出力フォルダ: {self.output_folder}")
            print("📊 スプレッドシートで結果を確認してください")
            
        except Exception as e:
            logger.error("ワークフロー実行エラー")
            if HAS_ENHANCED_HANDLER and EnhancedErrorHandler:
                EnhancedErrorHandler.log_error_with_context(e, "ワークフロー実行")
            else:
                ErrorHandler.log_error(e, "ワークフロー実行")
            raise

    async def run_tasks_only(self, auto_continue: bool = False, enable_review: bool = True):
        """既存のタスクのみを実行"""
        # === パート1: 初期化状態の確認 ===
        if not self.initialization_success:
            raise Exception("システムが初期化されていません")
        
        try:
            # === パート2: 実行開始の表示 ===
            print("\n" + "="*60)
            print("⚙️ 既存タスクの実行")
            print("="*60)
            
            if enable_review:
                print("✅ レビューAI: 有効")
            else:
                print("⏭️ レビューAI: 無効")
            
            # === パート3: タスク実行の実行 ===
            await self.task_executor.run_all_tasks(
                auto_continue=auto_continue,
                enable_review=enable_review
            )
            
            # === パート4: 完了メッセージの表示 ===
            print("\n" + "="*60)
            print("🎉 タスク実行完了")
            print("="*60)
            
        except Exception as e:
            logger.error("タスク実行エラー")
            if HAS_ENHANCED_HANDLER and EnhancedErrorHandler:
                EnhancedErrorHandler.log_error_with_context(e, "タスク実行")
            else:
                ErrorHandler.log_error(e, "タスク実行")
            raise

    async def cleanup(self):
        """リソースのクリーンアップ（強化版）"""
        logger.info("🧹 クリーンアップ開始...")
        
        cleanup_tasks = []
        
        # ブラウザのクリーンアップ
        if self.browser:
            cleanup_tasks.append(self._safe_cleanup_browser())
        
        # WordPressエージェントのクリーンアップ
        if self.wordpress_agent:
            cleanup_tasks.append(self._safe_cleanup_wordpress())
        
        # その他のエージェントのクリーンアップ
        if hasattr(self, 'dev_agent') and self.dev_agent:
            cleanup_tasks.append(self._safe_cleanup_agent(self.dev_agent, "dev_agent"))
        
        if hasattr(self, 'design_agent') and self.design_agent:
            cleanup_tasks.append(self._safe_cleanup_agent(self.design_agent, "design_agent"))
        
        # 並行してクリーンアップ実行
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        logger.info("✅ 全リソースクリーンアップ完了")

    async def _safe_cleanup_browser(self):
        """安全なブラウザクリーンアップ"""
        try:
            if self.browser:
                await self.browser.cleanup()
                logger.info("✅ ブラウザクリーンアップ完了")
        except Exception as e:
            logger.warning(f"⚠️ ブラウザクリーンアップ失敗: {e}")

    async def _safe_cleanup_wordpress(self):
        """安全なWordPressエージェントクリーンアップ"""
        try:
            if self.wordpress_agent and hasattr(self.wordpress_agent, 'cleanup'):
                await self.wordpress_agent.cleanup()
                logger.info("✅ WordPressエージェントクリーンアップ完了")
        except Exception as e:
            logger.warning(f"⚠️ WordPressエージェントクリーンアップ失敗: {e}")

    async def _safe_cleanup_agent(self, agent, agent_name: str):
        """安全なエージェントクリーンアップ"""
        try:
            if agent and hasattr(agent, 'cleanup'):
                await agent.cleanup()
                logger.info(f"✅ {agent_name} クリーンアップ完了")
        except Exception as e:
            logger.warning(f"⚠️ {agent_name} クリーンアップ失敗: {e}")


async def main():
    """メイン実行関数"""
    # === パート1: コマンドライン引数の解析 ===
    parser = argparse.ArgumentParser(description='マルチエージェントシステム')
    parser.add_argument('--goal', type=str, help='プロジェクト目標を直接指定')
    parser.add_argument('--tasks-only', action='store_true', help='既存タスクのみ実行(PM AIスキップ)')
    parser.add_argument('--auto', action='store_true', help='自動実行(確認なし)')
    parser.add_argument('--no-review', action='store_true', help='レビュー機能を無効化')
    parser.add_argument('--max-iterations', type=int, default=3, help='最大反復回数(デフォルト: 3)')
    parser.add_argument('--pc-id', type=int, help='PC_IDを指定')
    
    args = parser.parse_args()
    
    # === パート2: オーケストレーターの初期化 ===
    orchestrator = MultiAgentOrchestrator(
        pc_id=args.pc_id,
        max_iterations=args.max_iterations
    )
    
    try:
        # === パート3: システム初期化 ===
        await orchestrator.initialize()
        
        # === パート4: ワークフローの実行 ===
        if args.tasks_only:
            await orchestrator.run_tasks_only(
                auto_continue=args.auto,
                enable_review=not args.no_review
            )
        else:
            await orchestrator.run_full_workflow(
                goal=args.goal,
                auto_continue=args.auto,
                enable_review=not args.no_review
            )
        
    except KeyboardInterrupt:
        # === パート5: ユーザー中断の処理 ===
        logger.warning("\n⏸️ ユーザーによる中断")
    except Exception as e:
        # === パート6: エラー処理 ===
        logger.error(f"❌ 致命的エラー: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # === パート7: クリーンアップ ===
        await orchestrator.cleanup()
        logger.info("\n👋 マルチエージェントシステムを終了しました")


if __name__ == "__main__":
    asyncio.run(main())
