# test_tasks.py
"""
pm_tasksシートの既存タスクをテスト実行するデバッグスクリプト

使い方:
  python test_tasks.py                    # 全pending タスクを実行
  python test_tasks.py --task-id 5        # 特定のタスクIDのみ実行
  python test_tasks.py --role writer      # 特定の役割のタスクのみ実行
  python test_tasks.py --auto             # 自動実行（確認なし）
"""

import logging
import asyncio
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any 

from config_utils import config, ErrorHandler, PathManager
from sheets_manager import GoogleSheetsManager
from browser_controller import BrowserController

# ロガー設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# TaskExecutor インポートの簡素化
try:
    # まずメインのTaskExecutorを試す
    from task_executor.task_executor import TaskExecutor
    logger.info("✅ メイン TaskExecutor をインポート")
except ImportError as e:
    logger.warning(f"⚠️ メイン TaskExecutor インポート失敗: {e}")
    try:
        # フォールバック: MATaskExecutor
        from task_executor.task_executor_ma import MATaskExecutor as TaskExecutor
        logger.info("✅ MATaskExecutor を TaskExecutor として使用")
    except ImportError as e:
        logger.warning(f"⚠️ MATaskExecutor インポート失敗: {e}")
        try:
            # 最終フォールバック: ContentTaskExecutor
            from task_executor.content_task_executor import ContentTaskExecutor as TaskExecutor
            logger.info("✅ ContentTaskExecutor を TaskExecutor として使用")
        except ImportError as e:
            logger.error(f"❌ 利用可能なTaskExecutorが見つかりません: {e}")
            TaskExecutor = None

class TaskTester:
    """既存タスクのテスト実行用クラス"""
    
    def __init__(self, spreadsheet_id: str, service_account_file: str = None):
        self.spreadsheet_id = spreadsheet_id
        self.service_account_file = service_account_file
        self.sheets_manager = None
        self.browser = None
        self.task_executor = None
    
    def safe_import_task_executor():
        """安全なTaskExecutorインポート関数"""
        import logging
        temp_logger = logging.getLogger(__name__)
        
        candidates = [
            # 優先順位1: メインTaskExecutor
            ('task_executor', 'TaskExecutor', 'メイン'),
            # 優先順位2: MATaskExecutor
            ('task_executor.task_executor_ma', 'MATaskExecutor', 'M&A'),
            # 優先順位3: ContentTaskExecutor
            ('task_executor.content_task_executor', 'ContentTaskExecutor', 'コンテンツ'),
        ]
        
        for module_path, class_name, executor_type in candidates:
            try:
                module = __import__(module_path, fromlist=[class_name])
                executor_class = getattr(module, class_name)
                temp_logger.info(f"✅ {executor_type} Executor をインポート: {class_name}")
                return executor_class
            except ImportError as e:
                temp_logger.debug(f"⚠️ {module_path}.{class_name} インポート失敗: {e}")
            except AttributeError as e:
                temp_logger.debug(f"⚠️ {module_path} に {class_name} がありません: {e}")
        
        temp_logger.error("❌ 利用可能なTaskExecutorクラスが見つかりません")
        return None
    
    async def initialize(self):
        """システム初期化"""
        try:
            logger.info("="*60)
            logger.info("タスクテスターを初期化中...")
            logger.info("="*60)
    
            # === パート1: Google Sheets接続と基本設定読み込み ===
            logger.info("📊 Google Sheets接続中...")
    
            # Google Sheets接続
            self.sheets_manager = GoogleSheetsManager(
                self.spreadsheet_id, 
                self.service_account_file
            )
    
            # PC_IDを取得して設定を読み込み
            pc_id = self.sheets_manager.get_current_pc_id()
            settings = self.sheets_manager.load_pc_settings(pc_id)
    
            # === パート2: 出力フォルダとブラウザ設定 ===
            logger.info("📁 出力フォルダ設定中...")
    
            # 出力フォルダの設定
            agent_output = settings.get('agent_output_folder')
            if not agent_output or agent_output.startswith('http'):
                download_folder = Path.home() / "Documents" / "gemini_auto_generate" / "agent_outputs"
                download_folder.mkdir(exist_ok=True, parents=True)
            else:
                download_folder = PathManager.get_safe_path(agent_output)
    
            logger.info(f"出力フォルダ: {download_folder}")
            
            # === パート3: BrowserController初期化 ===
            logger.info("🌐 ブラウザ初期化中...")
            
            # BrowserControllerを初期化
            config.BROWSER_DATA_DIR = settings.get('browser_data_dir')
            config.COOKIES_FILE = settings.get('cookies_file')
            config.GENERATION_MODE = 'text'
            config.SERVICE_TYPE = 'google'
        
            self.browser = BrowserController(
                download_folder, 
                mode='text', 
                service='google'
            )
            await self.browser.setup_browser()
            await self.browser.navigate_to_gemini()
            
            def resolve_task_executor():
                """利用可能なTaskExecutorを動的に解決"""
                available_executors = []

                # MATaskExecutorの確認
                try:
                    from task_executor.task_executor_ma import MATaskExecutor
                    available_executors.append(('ma', MATaskExecutor))
                except ImportError:
                    pass

                # ContentTaskExecutorの確認
                try:
                    from task_executor.content_task_executor import ContentTaskExecutor
                    available_executors.append(('content', ContentTaskExecutor))
                except ImportError:
                    pass

                # TaskCoordinatorの確認
                try:
                    from task_executor.task_coordinator import TaskCoordinator
                    available_executors.append(('coordinator', TaskCoordinator))
                except ImportError:
                    pass

                if available_executors:
                    executor_type, executor_class = available_executors[0]
                    logger.info(f"✅ {executor_type} Executor を使用: {executor_class.__name__}")
                    return executor_class
                else:
                    logger.error("❌ 利用可能なTaskExecutorが見つかりません")
                    return None

            # ========================================
            # === パート4: TaskExecutor初期化（統一版） ===
            # ========================================
            logger.info("⚙️ タスク実行エンジン初期化中...")

            # ステップ1: 利用可能なExecutorを解決
            executor_class = resolve_task_executor()

            # ステップ2: フォールバック処理
            if executor_class is None:
                # resolve_task_executorで見つからなかった場合、TaskExecutorを試す
                if TaskExecutor is None:
                    logger.error("❌ TaskExecutor のインポートに失敗しました")
                    return False
                executor_class = TaskExecutor
                logger.info("⚙️ デフォルトのTaskExecutorを使用します")

            # ステップ3: Executorの初期化
            logger.info(f"🚀 {executor_class.__name__} を初期化中...")
            self.task_executor = executor_class(
                self.sheets_manager,
                self.browser,
                max_iterations=30
            )

            # ステップ4: Executor種別の判定フラグ
            is_ma_executor = 'MATaskExecutor' in executor_class.__name__
            is_standard_executor = 'TaskExecutor' in executor_class.__name__ and not is_ma_executor

            logger.info(f"📝 使用するExecutor: {executor_class.__name__}")
            logger.info(f"   - MATaskExecutor: {is_ma_executor}")
            logger.info(f"   - 標準TaskExecutor: {is_standard_executor}")
        
            # === パート5: 各エージェントの登録 ===
            logger.info("🤖 エージェント登録中...")
                
            # ★★★ 各種エージェントの初期化と登録 ★★★
                
            # 1. Design Agent
            try:
                from design_agent import DesignAgent
                self.design_agent = DesignAgent(self.browser)
                if hasattr(self, 'task_executor') and self.task_executor:
                    self.task_executor.register_agent('design', self.design_agent)
                logger.info("✅ Design Agent初期化完了")
            except ImportError:
                logger.warning("⚠️ design_agent が見つかりません")
                self.design_agent = None

            # 2. Dev Agent
            try:
                from dev_agent import DevAgent
                self.dev_agent = DevAgent(self.browser)
                if hasattr(self, 'task_executor') and self.task_executor:
                    self.task_executor.register_agent('dev', self.dev_agent)
                logger.info("✅ Dev Agent初期化完了")
            except ImportError:
                logger.warning("⚠️ dev_agent が見つかりません")
                self.dev_agent = None

            # 3. Review Agent
            try:
                from review_agent import ReviewAgent
                self.review_agent = ReviewAgent()
                self.review_agent.browser = self.browser
                self.review_agent.sheets_manager = self.sheets_manager
                if hasattr(self, 'task_executor') and self.task_executor:
                    self.task_executor.register_review_agent(self.review_agent)
                logger.info("✅ Review Agent初期化完了")
            except ImportError:
                logger.warning("⚠️ review_agent が見つかりません")
                self.review_agent = None

            # 4. Content Writer Agents
            try:
                from content_writer_agent import ContentWriterAgent
                self.content_writer = ContentWriterAgent(self.browser)
                if hasattr(self, 'task_executor') and self.task_executor:
                    self.task_executor.register_agent('writer', self.content_writer)
                    self.task_executor.register_agent('content', self.content_writer)
                logger.info("✅ Content Writer Agent初期化完了")
            except ImportError:
                logger.warning("⚠️ content_writer_agent が見つかりません")
                self.content_writer = None
                
            # ========================================
            # 5. WordPress Agent（重要！）
            # ========================================
            logger.info("🗄️ WordPress Agent設定中...")
            
            # 認証情報の取得とログ出力
            wp_url = settings.get('wp_url', '').strip()
            wp_user = settings.get('wp_user', '').strip()
            wp_pass = settings.get('wp_pass', '').strip()
            
            # ✅ デバッグ：認証情報の状態を確認
            logger.info("="*60)
            logger.info("📋 WordPress認証情報チェック:")
            logger.info("="*60)
            logger.info(f"   - wp_url: {'✅ 設定済み' if wp_url else '❌ 未設定'} ({len(wp_url)} chars)")
            logger.info(f"   - wp_user: {'✅ 設定済み' if wp_user else '❌ 未設定'}")
            logger.info(f"   - wp_pass: {'✅ 設定済み' if wp_pass else '❌ 未設定'}")
            logger.info("="*60)

            # インスタンス変数として初期化（重要！）
            self.wordpress_agent = None

            if wp_url and wp_user and wp_pass:
                try:
                    logger.info("📦 WordPressAgentクラスをインポート中...")
                    from wordpress.wp_agent import WordPressAgent
            
                    wp_credentials = {
                        'wp_url': wp_url,
                        'wp_user': wp_user,
                        'wp_pass': wp_pass
                    }
            
                    # ✅ self.wordpress_agent として保存
                    logger.info("🔧 WordPressAgentインスタンスを作成中...")
                    self.wordpress_agent = WordPressAgent(self.browser, wp_credentials)
                    logger.info("✅ WordPressAgentインスタンス作成完了")
                    
                    self.wordpress_agent.sheets_manager = self.sheets_manager
                    logger.info("✅ sheets_manager を設定")
            
                    logger.info("🔐 WordPressへのログインを試行中...")
                    wp_login_success = await self.wordpress_agent.initialize_wp_session()
            
                    if wp_login_success:
                        logger.info("✅ WordPressログイン成功")
                        # ✅ 一旦登録（後で再登録される）
                        if hasattr(self, 'task_executor') and self.task_executor:
                            self.task_executor.register_agent('wordpress', self.wordpress_agent)
                            logger.info("✅ WordPressAgent 一時登録完了")
                        logger.info("✅ WordPress Agent初期化完了")
                    else:
                        logger.warning("⚠️ WordPressログイン失敗")
                        logger.warning("⚠️ ログイン失敗でもエージェントは保持します")
                        # ✅ ログイン失敗でもエージェントは保持（重要！）
                        # self.wordpress_agent = None  # ← コメントアウト
            
                except Exception as e:
                    logger.error("="*60)
                    logger.error(f"❌ WordPress Agent初期化エラー: {e}")
                    logger.error("="*60)
                    import traceback
                    logger.error(traceback.format_exc())
                    logger.error("⚠️ エージェントをNoneに設定します")
                    self.wordpress_agent = None
            else:
                logger.warning("="*60)
                logger.warning("⚠️ WordPress認証情報が未設定です")
                logger.warning(f"   - wp_url: {bool(wp_url)}")
                logger.warning(f"   - wp_user: {bool(wp_user)}")
                logger.warning(f"   - wp_pass: {bool(wp_pass)}")
                logger.warning("="*60)
                
            # ========================================
            # 6. WordPress Dev Agent
            # ========================================
            logger.info("🔧 WordPress Dev Agent設定中...")
            self.wp_dev_agent = None
                
            try:
                from wordpress.wp_dev import WordPressDevAgent
                    
                self.wp_dev_agent = WordPressDevAgent(self.browser)
                if hasattr(self.wp_dev_agent, 'sheets_manager'):
                    self.wp_dev_agent.sheets_manager = self.sheets_manager
                    
                if hasattr(self, 'task_executor') and self.task_executor:
                    self.task_executor.register_agent('wp_dev', self.wp_dev_agent)
                logger.info("✅ WordPress Dev Agent (wp_dev) 初期化完了")
            except ImportError as e:
                logger.warning(f"⚠️ wordpress/wp_dev.py のインポート失敗: {e}")
                logger.info("💡 wp_dev タスクは標準 dev エージェントで処理されます")
            except Exception as e:
                logger.warning(f"⚠️ wp_dev エージェント初期化エラー: {e}")
                
            # ========================================
            # 7. WordPress Design Agent
            # ========================================
            logger.info("🎨 WordPress Design Agent設定中...")
            self.wp_design_agent = None
                
            try:
                from wordpress.wp_design import WordPressDesignAgent
                    
                self.wp_design_agent = WordPressDesignAgent(self.browser)
                if hasattr(self.wp_design_agent, 'sheets_manager'):
                    self.wp_design_agent.sheets_manager = self.sheets_manager
                    
                if hasattr(self, 'task_executor') and self.task_executor:
                    self.task_executor.register_agent('wp_design', self.wp_design_agent)
                logger.info("✅ WordPress Design Agent (wp_design) 初期化完了")
            except ImportError as e:
                logger.warning(f"⚠️ wordpress/wp_design.py のインポート失敗: {e}")
                logger.info("💡 wp_design タスクは標準 design エージェントで処理されます")
            except Exception as e:
                logger.warning(f"⚠️ wp_design エージェント初期化エラー: {e}")
                
            # ========================================
            # ✅ システム初期化完了（全エージェント初期化後）
            # ========================================
            logger.info("="*60)
            logger.info("✅ システム初期化完了")
            logger.info("="*60)
            
            # ========================================
            # ✅ デバッグ：is_ma_executor フラグの確認
            # ========================================
            logger.info("\n" + "="*60)
            logger.info("🔍 デバッグ情報")
            logger.info("="*60)
            logger.info(f"Executor種別: {executor_class.__name__}")
            logger.info(f"is_ma_executor フラグ: {is_ma_executor}")
            logger.info(f"wordpress_agent 存在: {hasattr(self, 'wordpress_agent')}")
            if hasattr(self, 'wordpress_agent'):
                logger.info(f"wordpress_agent 値: {self.wordpress_agent}")
                if self.wordpress_agent:
                    logger.info(f"plugin_manager 存在: {hasattr(self.wordpress_agent, 'plugin_manager')}")
                    if hasattr(self.wordpress_agent, 'plugin_manager'):
                        logger.info(f"plugin_manager 値: {self.wordpress_agent.plugin_manager}")
            logger.info("="*60)

            # ========================================
            # ✅ 重要：MATaskExecutor用のエージェント再登録
            # ========================================

            if is_ma_executor:
                logger.info("\n" + "="*60)
                logger.info("🔄 MATaskExecutor用エージェント再登録中...")
                logger.info("="*60)
        
                # インスタンス変数から初期化済みエージェントを収集
                agents_to_register = {}
        
                # design_agentの登録
                if hasattr(self, 'design_agent') and self.design_agent:
                    agents_to_register['design'] = self.design_agent
        
                # dev_agentの登録
                if hasattr(self, 'dev_agent') and self.dev_agent:
                    agents_to_register['dev'] = self.dev_agent
        
                # review_agentの登録
                if hasattr(self, 'review_agent') and self.review_agent:
                    agents_to_register['review'] = self.review_agent
        
                # content_writerの登録
                if hasattr(self, 'content_writer') and self.content_writer:
                    agents_to_register['writer'] = self.content_writer
                    agents_to_register['content'] = self.content_writer
        
                # ========================================
                # ✅ 重要：wordpress_agentの登録（デバッグ強化）
                # ========================================
                logger.info("\n📋 wordpress_agent 登録チェック:")
                logger.info(f"   - hasattr: {hasattr(self, 'wordpress_agent')}")
                if hasattr(self, 'wordpress_agent'):
                    logger.info(f"   - value: {self.wordpress_agent}")
                    logger.info(f"   - is None: {self.wordpress_agent is None}")
                
                if hasattr(self, 'wordpress_agent') and self.wordpress_agent:
                    agents_to_register['wordpress'] = self.wordpress_agent
                    logger.info("  ✅ wordpress_agent を取得")
            
                    # wordpressから派生するサブエージェントも登録
                    if hasattr(self.wordpress_agent, 'plugin_manager'):
                        logger.info(f"  📦 plugin_manager 存在確認: {self.wordpress_agent.plugin_manager is not None}")
                        if self.wordpress_agent.plugin_manager:
                            agents_to_register['plugin'] = self.wordpress_agent.plugin_manager
                            logger.info("  ✅ plugin_manager を取得")
                        else:
                            logger.error("  ❌ plugin_manager is None!")
                    else:
                        logger.error("  ❌ plugin_manager 属性が存在しません!")
                else:
                    logger.error("  ❌ wordpress_agent が見つかりません！")
                    if hasattr(self, 'wordpress_agent'):
                        logger.error(f"     wordpress_agent is None: {self.wordpress_agent is None}")
        
                # wp_dev_agentの登録
                if hasattr(self, 'wp_dev_agent') and self.wp_dev_agent:
                    agents_to_register['wp_dev'] = self.wp_dev_agent
                elif hasattr(self, 'dev_agent') and self.dev_agent:
                    agents_to_register['wp_dev'] = self.dev_agent
                    logger.info("  🔄 wp_dev → dev でフォールバック")
        
                # wp_design_agentの登録
                if hasattr(self, 'wp_design_agent') and self.wp_design_agent:
                    agents_to_register['wp_design'] = self.wp_design_agent
                elif hasattr(self, 'design_agent') and self.design_agent:
                    agents_to_register['wp_design'] = self.design_agent
                    logger.info("  🔄 wp_design → design でフォールバック")
        
                # エージェントを一括登録
                logger.info("\n📝 エージェント登録処理:")
                for agent_name, agent_instance in agents_to_register.items():
                    try:
                        self.task_executor.register_agent(agent_name, agent_instance)
                        logger.info(f"  ✅ {agent_name:15s} 登録完了")
                    except Exception as e:
                        logger.error(f"  ❌ {agent_name:15s} 登録失敗: {e}")
        
                # レビューエージェントの特別登録
                if hasattr(self, 'review_agent') and self.review_agent:
                    try:
                        self.task_executor.register_review_agent(self.review_agent)
                        logger.info(f"  ✅ {'review (専用)':15s} 登録完了")
                    except Exception as e:
                        logger.error(f"  ❌ review (専用) 登録失敗: {e}")
        
                logger.info("="*60)
                logger.info(f"MATaskExecutor エージェント登録完了: {len(agents_to_register)}個")
                logger.info("="*60)
        
                # デバッグ：登録済みエージェント一覧を表示
                logger.info("\n📋 登録済みエージェント一覧:")
                for agent_name in self.task_executor.agents.keys():
                    logger.info(f"  - {agent_name}")
                logger.info("")
            else:
                logger.warning("\n⚠️ MATaskExecutorではないため、再登録処理をスキップします")
                logger.warning(f"   Executor種別: {executor_class.__name__}")
                logger.warning(f"   is_ma_executor: {is_ma_executor}")
                    
            # ========================================
            # ✅ 最後にreturn
            # ========================================
            return True
                
        except Exception as e:
            ErrorHandler.log_error(e, "システム初期化")
            raise
    
    async def test_tasks_by_role(self, role: str, auto: bool = False):
        """特定の役割のタスクをテスト実行"""
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"役割 '{role}' のタスクをテスト実行")
            logger.info(f"{'='*60}\n")
            
            # pm_tasksから該当タスクを取得
            all_tasks = await self.task_executor.load_pending_tasks()
            filtered_tasks = [t for t in all_tasks if t['required_role'].lower() == role.lower()]
            
            if not filtered_tasks:
                logger.error(f"❌ 役割 '{role}' のpendingタスクが見つかりません")
                return
            
            logger.info(f"対象タスク: {len(filtered_tasks)}件\n")
            
            for i, task in enumerate(filtered_tasks, 1):
                logger.info(f"{i}. [{task['task_id']}] {task['description'][:80]}")
            
            if not auto:
                confirm = input(f"\nこれらのタスクを実行しますか？ (y/n): ")
                if confirm.lower() != 'y':
                    logger.info("実行をキャンセルしました")
                    return
            
            # タスクを順番に実行
            completed = 0
            failed = 0
            
            for task in filtered_tasks:
                logger.info(f"\n{'='*60}")
                logger.info(f"タスク {task['task_id']} を実行中...")
                logger.info(f"{'='*60}")
                
                success = await self.task_executor.execute_task(task)
                
                if success:
                    completed += 1
                else:
                    failed += 1
                
                # 次のタスクへの確認
                if not auto and task != filtered_tasks[-1]:
                    choice = input("\n次のアクション: (c)続行 / (q)終了: ").lower()
                    if choice == 'q':
                        break
            
            # サマリー表示
            logger.info(f"\n{'='*60}")
            logger.info("テスト実行完了")
            logger.info(f"{'='*60}")
            logger.info(f"完了: {completed}件")
            logger.info(f"失敗: {failed}件")
            logger.info(f"{'='*60}")
            
        except Exception as e:
            ErrorHandler.log_error(e, f"役割 '{role}' のテスト実行")
    
    async def test_all_pending_tasks(self, auto: bool = False):
        """全てのpendingタスクをテスト実行"""
        try:
            logger.info(f"\n{'='*60}")
            logger.info("全pendingタスクをテスト実行")
            logger.info(f"{'='*60}\n")
            
            # TaskExecutorの通常実行を使用
            await self.task_executor.run_all_tasks(
                auto_continue=auto,
                enable_review=False  # テストモードではレビューなし
            )
            
        except Exception as e:
            ErrorHandler.log_error(e, "全タスクテスト実行")
    
    def _display_task_info(self, task: dict):
        """タスク情報を表示"""
        print("\n" + "="*60)
        print("タスク詳細")
        print("="*60)
        print(f"タスクID: {task['task_id']}")
        print(f"説明: {task['description']}")
        print(f"担当: {task['required_role']}")
        print(f"優先度: {task['priority']}")
        print(f"ステータス: {task['status']}")
        
        if 'language' in task:
            print(f"言語: {task['language']}")
        if 'polylang_lang' in task:
            print(f"Polylang: {task['polylang_lang']}")
        if 'source_task_id' in task:
            print(f"元記事タスクID: {task['source_task_id']}")
        if 'post_action' in task:
            print(f"投稿アクション: {task['post_action']}")
        if 'post_status' in task:
            print(f"投稿ステータス: {task['post_status']}")
        
        print("="*60)
    
    async def cleanup(self):
        """クリーンアップ"""
        if self.browser:
            await self.browser.cleanup()

async def main():
    parser = argparse.ArgumentParser(
        description='pm_tasksの既存タスクをテスト実行（デバッグ用）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python test_tasks.py                    # 全pendingタスクを実行
  python test_tasks.py --task-id 5        # タスクID 5のみ実行
  python test_tasks.py --role writer      # writer タスクのみ実行
  python test_tasks.py --role wordpress --auto  # wordpress タスクを自動実行
        """
    )
    
    parser.add_argument('--task-id', type=str, help='特定のタスクIDのみ実行')
    parser.add_argument('--role', type=str, help='特定の役割のタスクのみ実行 (design, dev, writer, wordpress, etc.)')
    parser.add_argument('--auto', action='store_true', help='自動実行（確認なし）')
    parser.add_argument('--spreadsheet-id', type=str, help='スプレッドシートID（config.pyのデフォルトを上書き）')
    
    args = parser.parse_args()
    
    # スプレッドシートID
    spreadsheet_id = args.spreadsheet_id or config.SPREADSHEET_ID
    
    # service_account.json のパス
    default_service_account = r"C:\Users\color\Documents\gemini_auto_generate\service_account.json"
    service_account_file = default_service_account if Path(default_service_account).exists() else None
    
    # TaskTesterを初期化
    tester = TaskTester(spreadsheet_id, service_account_file)
    
    try:
        await tester.initialize()
        
        # モードに応じて実行
        if args.task_id:
            # 特定のタスクIDをテスト
            await tester.test_specific_task(args.task_id)
        
        elif args.role:
            # 特定の役割のタスクをテスト
            await tester.test_tasks_by_role(args.role, auto=args.auto)
        
        else:
            # 全てのpendingタスクをテスト
            await tester.test_all_pending_tasks(auto=args.auto)
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠️ ユーザーによる中断")
    
    except Exception as e:
        logger.error(f"❌ エラー発生: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await tester.cleanup()
        logger.info("\n👋 タスクテスターを終了しました")


if __name__ == "__main__":
    asyncio.run(main())