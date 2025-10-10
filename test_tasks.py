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

            # 使用例
            executor_class = resolve_task_executor()
            if executor_class:
                self.task_executor = executor_class(
                    self.sheets_manager,
                    self.browser,
                    max_iterations=30
                )
            
            # === パート4: TaskExecutor初期化 ===
            logger.info("⚙️ タスク実行エンジン初期化中...")
        
            if TaskExecutor is None:
                logger.error("❌ TaskExecutor のインポートに失敗しました")
                return False
        
            # TaskExecutorを初期化
            self.task_executor = TaskExecutor(
                self.sheets_manager,
                self.browser,
                max_iterations=30
            )
            
            # === パート5: 各エージェントの登録 ===
            logger.info("🤖 エージェント登録中...")
            
            # ★★★ 各種エージェントの初期化と登録 ★★★
            
            # 1. Design Agent
            try:
                from design_agent import DesignAgent
                design_agent = DesignAgent(self.browser)
                self.task_executor.register_agent('design', design_agent)
                logger.info("✅ Design Agent登録完了")
            except ImportError:
                logger.warning("⚠️ design_agent が見つかりません")
            
            # 2. Dev Agent
            try:
                from dev_agent import DevAgent
                dev_agent = DevAgent(self.browser)
                self.task_executor.register_agent('dev', dev_agent)
                logger.info("✅ Dev Agent登録完了")
            except ImportError:
                logger.warning("⚠️ dev_agent が見つかりません")
            
            # 3. Review Agent
            try:
                from review_agent import ReviewAgent
                review_agent = ReviewAgent()
                review_agent.browser = self.browser
                review_agent.sheets_manager = self.sheets_manager
                self.task_executor.register_review_agent(review_agent)
                logger.info("✅ Review Agent登録完了")
            except ImportError:
                logger.warning("⚠️ review_agent が見つかりません")
            
            # 4. Content Writer Agents
            try:
                from content_writer_agent import ContentWriterAgent
                content_writer = ContentWriterAgent(self.browser)
                self.task_executor.register_agent('writer', content_writer)
                self.task_executor.register_agent('content', content_writer)
                logger.info("✅ Content Writer Agent登録完了")
            except ImportError:
                logger.warning("⚠️ content_writer_agent が見つかりません")
            
            # 5. WordPress Agent（重要！）
            logger.info("🗄️ WordPress Agent設定中...")
            wp_url = settings.get('wp_url', '').strip()
            wp_user = settings.get('wp_user', '').strip()
            wp_pass = settings.get('wp_pass', '').strip()
            
            if wp_url and wp_user and wp_pass:
                try:
                    from wordpress.wp_agent import WordPressAgent
                    
                    wp_credentials = {
                        'wp_url': wp_url,
                        'wp_user': wp_user,
                        'wp_pass': wp_pass
                    }
                    
                    wordpress_agent = WordPressAgent(self.browser, wp_credentials)
                    wordpress_agent.sheets_manager = self.sheets_manager
                    
                    logger.info("WordPressへのログインを試行中...")
                    wp_login_success = await wordpress_agent.initialize_wp_session()
                    
                    if wp_login_success:
                        self.task_executor.register_agent('wordpress', wordpress_agent)
                        logger.info("✅ WordPress Agent登録完了")
                    else:
                        logger.warning("⚠️ WordPressログイン失敗")
                        
                except Exception as e:
                    logger.error(f"WordPress Agent初期化エラー: {e}")
            else:
                logger.warning("⚠️ WordPress認証情報が未設定です")
            
            # ========================================
            # ✅ ここに追加: WordPress Dev Agent
            # ========================================
            logger.info("🔧 WordPress Dev Agent設定中...")
            try:
                from wordpress.wp_dev import WordPressDevAgent
                
                wp_dev_agent = WordPressDevAgent(self.browser)
                if hasattr(wp_dev_agent, 'sheets_manager'):
                    wp_dev_agent.sheets_manager = self.sheets_manager
                
                self.task_executor.register_agent('wp_dev', wp_dev_agent)
                logger.info("✅ WordPress Dev Agent (wp_dev) 登録完了")
            except ImportError as e:
                logger.warning(f"⚠️ wordpress/wp_dev.py のインポート失敗: {e}")
                logger.info("💡 wp_dev タスクは標準 dev エージェントで処理されます")
            except Exception as e:
                logger.warning(f"⚠️ wp_dev エージェント初期化エラー: {e}")
            
            # ========================================
            # ✅ WordPress専用エージェント登録（強化版フォールバック）
            # ========================================
            logger.info("🔧 WordPress専用エージェント設定中...")
            
            # WordPress Dev Agent
            wp_dev_registered = False
            try:
                from wordpress.wp_dev import WordPressDevAgent
                wp_dev_agent = WordPressDevAgent(self.browser)
                if hasattr(wp_dev_agent, 'sheets_manager'):
                    wp_dev_agent.sheets_manager = self.sheets_manager
                
                # executeメソッドの確認
                if hasattr(wp_dev_agent, 'execute') or hasattr(wp_dev_agent, 'execute_task'):
                    self.task_executor.register_agent('wp_dev', wp_dev_agent)
                    logger.info("✅ WordPress Dev Agent (wp_dev) 登録完了")
                    wp_dev_registered = True
                else:
                    logger.warning("⚠️ wp_dev に実行メソッドがありません - フォールバック使用")
                    
            except ImportError:
                logger.warning("⚠️ wordpress/wp_dev.py が見つかりません - フォールバック使用")
            except Exception as e:
                logger.warning(f"⚠️ wp_dev 初期化エラー: {e} - フォールバック使用")
            
            # フォールバック: 標準 dev エージェントを使用
            if not wp_dev_registered:
                try:
                    # 既に登録されている dev エージェントを取得
                    if 'dev' in self.task_executor.agents:
                        dev_agent = self.task_executor.agents['dev']
                        
                        # dev エージェントを wp_dev としても登録
                        self.task_executor.register_agent('wp_dev', dev_agent)
                        logger.info("✅ wp_dev → dev エージェントで代替（フォールバック成功）")
                    else:
                        # dev エージェントも存在しない場合、新規作成を試みる
                        from dev_agent import DevAgent
                        fallback_dev_agent = DevAgent(self.browser)
                        self.task_executor.register_agent('wp_dev', fallback_dev_agent)
                        logger.info("✅ wp_dev → 新規 dev エージェントで代替（緊急フォールバック）")
                        
                except Exception as e:
                    logger.error(f"❌ wp_dev フォールバック失敗: {e}")
            
            # WordPress Design Agent（同様のフォールバック）
            wp_design_registered = False
            try:
                from wordpress.wp_design import WordPressDesignAgent
                wp_design_agent = WordPressDesignAgent(self.browser)
                if hasattr(wp_design_agent, 'sheets_manager'):
                    wp_design_agent.sheets_manager = self.sheets_manager
                
                if hasattr(wp_design_agent, 'execute') or hasattr(wp_design_agent, 'execute_task'):
                    self.task_executor.register_agent('wp_design', wp_design_agent)
                    logger.info("✅ WordPress Design Agent (wp_design) 登録完了")
                    wp_design_registered = True
                else:
                    logger.warning("⚠️ wp_design に実行メソッドがありません - フォールバック使用")
                    
            except ImportError:
                logger.warning("⚠️ wordpress/wp_design.py が見つかりません - フォールバック使用")
            except Exception as e:
                logger.warning(f"⚠️ wp_design 初期化エラー: {e} - フォールバック使用")
            
            # フォールバック
            if not wp_design_registered:
                try:
                    if 'design' in self.task_executor.agents:
                        design_agent = self.task_executor.agents['design']
                        self.task_executor.register_agent('wp_design', design_agent)
                        logger.info("✅ wp_design → design エージェントで代替（フォールバック成功）")
                    else:
                        from design_agent import DesignAgent
                        fallback_design_agent = DesignAgent(self.browser)
                        self.task_executor.register_agent('wp_design', fallback_design_agent)
                        logger.info("✅ wp_design → 新規 design エージェントで代替（緊急フォールバック）")
                        
                except Exception as e:
                    logger.error(f"❌ wp_design フォールバック失敗: {e}")
            
            # ========================================
            # ✅ ここに追加: WordPress Design Agent
            # ========================================
            logger.info("🎨 WordPress Design Agent設定中...")
            try:
                from wordpress.wp_design import WordPressDesignAgent
                
                wp_design_agent = WordPressDesignAgent(self.browser)
                if hasattr(wp_design_agent, 'sheets_manager'):
                    wp_design_agent.sheets_manager = self.sheets_manager
                
                self.task_executor.register_agent('wp_design', wp_design_agent)
                logger.info("✅ WordPress Design Agent (wp_design) 登録完了")
            except ImportError as e:
                logger.warning(f"⚠️ wordpress/wp_design.py のインポート失敗: {e}")
                logger.info("💡 wp_design タスクは標準 design エージェントで処理されます")
            except Exception as e:
                logger.warning(f"⚠️ wp_design エージェント初期化エラー: {e}")
            
            logger.info("="*60)
            logger.info("✅ システム初期化完了")
            logger.info("="*60)
            
        except Exception as e:
            ErrorHandler.log_error(e, "システム初期化")
            raise
    
    async def test_specific_task(self, task_id: str):
        """特定のタスクIDをテスト実行"""
        try:
            # === パート1: タスク検索 ===
            logger.info(f"\n{'='*60}")
            logger.info(f"タスクID {task_id} のテスト実行")
            logger.info(f"{'='*60}\n")
            
            # pm_tasksから該当タスクを取得
            tasks = await self.task_executor.load_pending_tasks()
            target_task = None
            
            for task in tasks:
                if str(task['task_id']) == str(task_id):
                    target_task = task
                    break
            
            if not target_task:
                logger.error(f"❌ タスクID {task_id} が見つかりません（statusがpendingか確認してください）")
                return False
            
            # === パート2: タスク情報表示と確認 ===
            # タスク情報を表示
            self._display_task_info(target_task)
            
            # 実行確認
            confirm = input("\nこのタスクを実行しますか？ (y/n): ")
            if confirm.lower() != 'y':
                logger.info("実行をキャンセルしました")
                return False
            
            # === パート3: タスク実行と結果処理 ===
            # タスク実行
            success = await self.task_executor.execute_task(target_task)
            
            if success:
                logger.info(f"\n✅ タスク {task_id} のテスト実行完了")
            else:
                logger.error(f"\n❌ タスク {task_id} のテスト実行失敗")
            
            return success
            
        except Exception as e:
            ErrorHandler.log_error(e, f"タスク {task_id} テスト実行")
            return False
    
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