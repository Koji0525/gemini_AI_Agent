import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# ===== 設定とユーティリティ =====
from config_utils import ErrorHandler, config

# ===== データ管理 =====
from sheets_manager import GoogleSheetsManager

# ===== エラーハンドラー（オプション） =====
try:
    from error_handler_enhanced import (
        EnhancedErrorHandler,
        TaskErrorHandler
    )
    HAS_ENHANCED_HANDLER = True
except ImportError:
    HAS_ENHANCED_HANDLER = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ error_handler_enhanced未検出（標準エラーハンドラー使用）")

# ===== 分離モジュール =====
try:
    from task_executor_content import ContentTaskExecutor
    from task_executor_ma import MATaskExecutor
    HAS_SPECIALIZED_EXECUTORS = True
except ImportError:
    HAS_SPECIALIZED_EXECUTORS = False
    ContentTaskExecutor = None
    MATaskExecutor = None

# ===== WordPress連携（オプション） =====
try:
    from wordpress.wp_utils import task_router
    HAS_TASK_ROUTER = True
except ImportError:
    HAS_TASK_ROUTER = False
    task_router = None

logger = logging.getLogger(__name__)


class TaskExecutor:
    """タスク実行コントローラー(エラーハンドリング強化版)"""
    
    def __init__(
        self, 
        sheets_manager: GoogleSheetsManager, 
        browser_controller=None, 
        max_iterations: int = None
    ):
        """
        初期化
        
        Args:
            sheets_manager: GoogleSheetsManager インスタンス
            browser_controller: BrowserController インスタンス(オプション)
            max_iterations: 最大反復回数
        """
        self.sheets_manager = sheets_manager
        self.browser = browser_controller
        self.agents = {}
        self.review_agent = None
        
        if max_iterations is None:
            self.max_iterations = config.MAX_ITERATIONS
        else:
            self.max_iterations = max_iterations
        
        self.current_iteration = 0
        
        logger.info(f"TaskExecutor: 最大反復回数 = {self.max_iterations}")
        
        # エージェントを自動初期化
        self._initialize_agents()
        
        # === 分離モジュール初期化 ===
        if HAS_SPECIALIZED_EXECUTORS and ContentTaskExecutor and MATaskExecutor:
            try:
                # 記事生成専用エグゼキュータ
                self.content_executor = ContentTaskExecutor(self.agents)
                logger.info("✅ ContentTaskExecutor 初期化完了")
                
                # M&A専用エグゼキュータ
                self.ma_executor = MATaskExecutor(self.agents)
                logger.info("✅ MATaskExecutor 初期化完了")
                
                logger.info("="*60)
                logger.info("分離モジュール初期化完了")
                logger.info("  - ContentTaskExecutor (記事生成専用)")
                logger.info("  - MATaskExecutor (M&A/企業検索専用)")
                logger.info("="*60)
            except Exception as e:
                logger.warning(f"⚠️ 分離モジュール初期化失敗: {e}")
                self.content_executor = None
                self.ma_executor = None
        else:
            logger.warning("⚠️ 分離モジュールが利用できません")
            self.content_executor = None
            self.ma_executor = None
        
        # === WordPress開発専用エージェント初期化 ===
        logger.info("\n" + "="*60)
        logger.info("🔧 WordPress開発エージェント初期化中...")
        logger.info("="*60)
        
        # WordPress開発エージェント (wp_dev) の初期化
        self.wp_dev_agent = None
        try:
            from wordpress.wp_dev import WordPressDevAgent
            
            if self.browser:
                self.wp_dev_agent = WordPressDevAgent(self.browser)
                if hasattr(self.wp_dev_agent, 'sheets_manager'):
                    self.wp_dev_agent.sheets_manager = self.sheets_manager
                
                self.agents['wp_dev'] = self.wp_dev_agent
                logger.info("✅ WordPressDevAgent (wp_dev) 登録完了")
            else:
                logger.warning("⚠️ ブラウザコントローラー未初期化のため wp_dev スキップ")
                
        except ImportError as e:
            logger.warning(f"⚠️ wordpress/wp_dev.py のインポート失敗: {e}")
            logger.info("💡 WordPress開発タスクは標準 dev エージェントで処理されます")
        except Exception as e:
            logger.warning(f"⚠️ wp_dev エージェント初期化エラー: {e}")
        
        # WordPress設計エージェント (wp_design) の初期化
        self.wp_design_agent = None
        try:
            from wordpress.wp_design import WordPressDesignAgent
            
            if self.browser:
                self.wp_design_agent = WordPressDesignAgent(self.browser)
                if hasattr(self.wp_design_agent, 'sheets_manager'):
                    self.wp_design_agent.sheets_manager = self.sheets_manager
                
                self.agents['wp_design'] = self.wp_design_agent
                logger.info("✅ WordPressDesignAgent (wp_design) 登録完了")
            else:
                logger.warning("⚠️ ブラウザコントローラー未初期化のため wp_design スキップ")
                
        except ImportError as e:
            logger.warning(f"⚠️ wordpress/wp_design.py のインポート失敗: {e}")
            logger.info("💡 WordPress設計タスクは標準 design エージェントで処理されます")
        except Exception as e:
            logger.warning(f"⚠️ wp_design エージェント初期化エラー: {e}")
        
        logger.info("="*60)
        logger.info("WordPress専用エージェント初期化完了")
        if self.wp_dev_agent:
            logger.info("  - WordPressDevAgent (カスタム開発)")
        if self.wp_design_agent:
            logger.info("  - WordPressDesignAgent (テーマ/CSS)")
        logger.info("="*60)

        # ========================================
        # 📦 新規モジュール統合（__init__メソッド内に追加）
        # ========================================

        logger.info("\n" + "="*60)
        logger.info("📦 拡張モジュール統合チェック")
        logger.info("="*60)

        # task_executor.tas__init__ から新規モジュールをインポート
        try:
            from task_executor.tas__init__ import (
                TaskCoordinator,
                ContentTaskExecutor as NewContentExecutor,
                SystemCLIExecutor,
                WorkflowExecutor,
                HAS_COORDINATOR,
                HAS_CONTENT_EXECUTOR,
                HAS_CLI_EXECUTOR,
                HAS_WORKFLOW_EXECUTOR,
                print_module_status
            )
            
            # TaskCoordinator の初期化（オプション）
            if HAS_COORDINATOR:
                try:
                    logger.info("✅ TaskCoordinator 利用可能")
                    self._has_coordinator = True
                except Exception as e:
                    logger.warning(f"⚠️ TaskCoordinator 初期化スキップ: {e}")
                    self._has_coordinator = False
            else:
                logger.info("ℹ️ TaskCoordinator は配置されていません（オプション）")
                self._has_coordinator = False
            
            # 新規 ContentTaskExecutor の初期化（オプション）
            if HAS_CONTENT_EXECUTOR and NewContentExecutor:
                try:
                    self.new_content_executor = NewContentExecutor(
                        browser_controller=self.browser,
                        sheets_manager=self.sheets_manager
                    )
                    logger.info("✅ 新規 ContentTaskExecutor 初期化完了")
                except Exception as e:
                    logger.warning(f"⚠️ 新規 ContentTaskExecutor 初期化失敗: {e}")
                    self.new_content_executor = None
            else:
                logger.info("ℹ️ 新規 ContentTaskExecutor は配置されていません")
                self.new_content_executor = None
            
            # SystemCLIExecutor の初期化（オプション）
            if HAS_CLI_EXECUTOR and SystemCLIExecutor:
                try:
                    self.cli_executor = SystemCLIExecutor(
                        sheets_manager=self.sheets_manager
                    )
                    logger.info("✅ SystemCLIExecutor 初期化完了")
                except Exception as e:
                    logger.warning(f"⚠️ SystemCLIExecutor 初期化失敗: {e}")
                    self.cli_executor = None
            else:
                logger.info("ℹ️ SystemCLIExecutor は配置されていません")
                self.cli_executor = None
            
            # WorkflowExecutor の初期化（オプション）
            if HAS_WORKFLOW_EXECUTOR and WorkflowExecutor:
                try:
                    self.workflow_executor = WorkflowExecutor(
                        task_executor=self,
                        sheets_manager=self.sheets_manager,
                        browser_controller=self.browser
                    )
                    logger.info("✅ WorkflowExecutor 初期化完了")
                except Exception as e:
                    logger.warning(f"⚠️ WorkflowExecutor 初期化失敗: {e}")
                    self.workflow_executor = None
            else:
                logger.info("ℹ️ WorkflowExecutor は配置されていません")
                self.workflow_executor = None
            
            logger.info("="*60)
            logger.info("拡張モジュール統合完了")
            logger.info("="*60)

        except ImportError as e:
            logger.info("="*60)
            logger.info("ℹ️ 拡張モジュール未配置（既存機能のみ使用）")
            logger.info(f"詳細: {e}")
            logger.info("="*60)
            self._has_coordinator = False
            self.new_content_executor = None
            self.cli_executor = None
            self.workflow_executor = None

    def _initialize_agents(self):
        """エージェントの自動初期化"""
        logger.info("エージェントを初期化中...")
        # エージェントは外部から register_agent() で登録される
        logger.info("エージェント初期化完了")

    def register_agent(self, role: str, agent):
        """エージェントを登録"""
        self.agents[role] = agent
        logger.info(f"エージェント '{role}' を登録しました")

    def register_review_agent(self, review_agent):
        """レビューエージェントを登録"""
        self.review_agent = review_agent
        logger.info("レビューエージェントを登録しました")
    
    def register_review_agent(self, review_agent):
        """レビューエージェントを登録"""
        self.review_agent = review_agent
        logger.info("レビューエージェントを登録しました")

    async def execute_task_with_extensions(self, task: Dict) -> bool:
        """
        拡張モジュールを考慮したタスク実行
        
        新規モジュールが利用可能な場合は優先的に使用し、
        そうでなければ既存実装にフォールバック
        
        Args:
            task: タスク情報辞書
            
        Returns:
            bool: 実行成功フラグ
        """
        task_id = task.get('task_id', 'UNKNOWN')
        description = task.get('description', '').lower()
        
        try:
            # CLIタスク判定
            if self.cli_executor and any(kw in description for kw in ['wp-cli', 'acf', 'コマンド実行']):
                logger.info(f"🔧 SystemCLIExecutor でタスク {task_id} を実行")
                result = await self.cli_executor.execute_cli_task(task)
                return result.get('success', False) if isinstance(result, dict) else bool(result)
            
            # ワークフロータスク判定
            if self.workflow_executor and any(kw in description for kw in ['多言語', 'レビュー→修正', 'マルチステップ']):
                logger.info(f"🔄 WorkflowExecutor でタスク {task_id} を実行")
                result = await self.workflow_executor.execute_workflow_task(task)
                return result.get('success', False) if isinstance(result, dict) else bool(result)
            
            # 既存実装にフォールバック
            logger.info(f"🔙 既存実装でタスク {task_id} を実行")
            return await self.execute_task(task)
        
        except Exception as e:
            logger.error(f"❌ 拡張実行エラー: {e}")
            ErrorHandler.log_error(e, f"execute_task_with_extensions({task_id})")
            # エラー時も既存実装にフォールバック
            return await self.execute_task(task)

    async def load_pending_tasks(self) -> List[Dict]:
        """保留中のタスクを読み込む（エラーハンドリング強化版）"""
        try:
            logger.info("📋 保留中のタスクを読み込み中...")
            tasks = await self.sheets_manager.load_tasks_from_sheet('pm_tasks')
            
            if not tasks:
                logger.info("📭 pm_tasksシートにタスクがありません")
                return []
            
            # statusが'pending'のタスクのみをフィルタ
            pending_tasks = [
                task for task in tasks 
                if task.get('status', '').lower() == 'pending'
            ]
            
            logger.info(f"📊 保留中のタスク: {len(pending_tasks)}件")
            
            # デバッグ情報
            if pending_tasks:
                for i, task in enumerate(pending_tasks[:3]):
                    logger.info(f"  {i+1}. {task.get('description', '')[:60]}...")
                if len(pending_tasks) > 3:
                    logger.info(f"  ... 他 {len(pending_tasks)-3}件")
            
            return pending_tasks
            
        except Exception as e:
            logger.error(f"❌ タスク読み込みエラー: {e}")
            return []

    async def update_task_status(self, task: Dict, status: str, error_message: str = None) -> bool:
        """タスクステータスを更新（非同期エラー修正版）"""
        try:
            task_id = task.get('task_id')
            
            if error_message:
                logger.info(f"タスク {task_id} ステータス更新: {status} - エラー: {error_message}")
            else:
                logger.info(f"タスク {task_id} ステータス更新: {status}")
            
            # 非同期関数かどうかを確認して適切に呼び出す
            update_method = self.sheets_manager.update_task_status
            
            import inspect
            if inspect.iscoroutinefunction(update_method):
                result = await update_method(task_id, status)
            else:
                result = update_method(task_id, status)
            
            if result is None:
                logger.warning(f"⚠️ ステータス更新の結果がNoneです - タスク {task_id}")
                return True
                
            return bool(result)
            
        except Exception as e:
            logger.warning(f"⚠️ ステータス更新失敗（続行）: {e}")
            return False

    async def execute_task(self, task: Dict) -> bool:
        """個別タスクを実行"""
        task_id = task.get('task_id', 'UNKNOWN')
        description = task.get('description', '')
        assigned_to = task.get('required_role', task.get('assigned_to', ''))
            
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"🎯 タスク実行開始: {task_id}")
            logger.info(f"📝 内容: {description}")
            logger.info(f"👤 担当: {assigned_to}")
            logger.info(f"{'='*60}\n")
                
            await self.update_task_status(task, 'in_progress')
                
            if assigned_to not in self.agents:
                error_msg = f"エージェント '{assigned_to}' が登録されていません"
                logger.error(f"❌ {error_msg}")
                logger.error(f"📋 登録済みエージェント: {list(self.agents.keys())}")
        
                # 類似エージェントを探す
                similar_agent = None
                if 'wp_dev' in assigned_to and 'dev' in self.agents:
                    similar_agent = 'dev'
                elif 'wp_design' in assigned_to and 'design' in self.agents:
                    similar_agent = 'design'
        
                if similar_agent:
                    logger.warning(f"⚠️ 代替エージェント '{similar_agent}' で実行を試みます")
                    assigned_to = similar_agent
                else:
                    await self.update_task_status(task, 'failed', error_msg)
                    return False
                
            agent = self.agents[assigned_to]
            logger.info(f"🔄 エージェント '{assigned_to}' でタスク実行中...")
                
            if hasattr(agent, 'execute'):
                result = await agent.execute(task)
            elif hasattr(agent, 'execute_task'):
                result = await agent.execute_task(task)
            else:
                error_msg = f"エージェント '{assigned_to}' に実行メソッドがありません"
                logger.error(f"❌ {error_msg}")
                await self.update_task_status(task, 'failed', error_msg)
                return False
                
            if result and (isinstance(result, dict) and result.get('success', False) or result is True):
                logger.info(f"✅ タスク {task_id} 完了")
                await self.update_task_status(task, 'completed')
                return True
            else:
                error_msg = result.get('error', '実行失敗') if isinstance(result, dict) else '実行失敗'
                logger.warning(f"⚠️ タスク {task_id} 失敗: {error_msg}")
                await self.update_task_status(task, 'failed', error_msg)
                return False
                    
        except Exception as e:
            error_msg = f"タスク実行中にエラー: {str(e)}"
            logger.error(f"❌ {error_msg}")
            ErrorHandler.log_error(e, f"execute_task({task_id})")
            await self.update_task_status(task, 'failed', error_msg)
            return False

    async def run_all_tasks(self, auto_continue: bool = True, enable_review: bool = True) -> Dict[str, Any]:
        """全タスクを一括実行"""
        logger.info("\n" + "="*80)
        logger.info("🚀 全タスク実行を開始します")
        logger.info("="*80 + "\n")
            
        summary = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'results': [],
            'start_time': datetime.now(),
            'end_time': None
        }
            
        try:
            logger.info("📋 ペンディングタスクを読み込み中...")
            pending_tasks = await self.load_pending_tasks()
                
            if not pending_tasks:
                logger.info("📭 実行すべきタスクがありません")
                summary['end_time'] = datetime.now()
                return summary
                
            summary['total'] = len(pending_tasks)
            logger.info(f"📊 実行対象タスク: {summary['total']}件\n")
            logger.info(f"👥 登録済みエージェント: {list(self.agents.keys())}\n")
                
            for index, task in enumerate(pending_tasks, 1):
                task_id = task.get('task_id', 'UNKNOWN')
                    
                self.current_iteration += 1
                if self.current_iteration > self.max_iterations:
                    logger.warning(f"⚠️ 最大反復回数 ({self.max_iterations}) に到達")
                    summary['skipped'] = summary['total'] - index + 1
                    break
                    
                logger.info(f"\n{'─'*80}")
                logger.info(f"📌 タスク {index}/{summary['total']}: {task_id}")
                logger.info(f"{'─'*80}")
                    
                try:
                    success = await self.execute_task(task)
                        
                    task_result = {
                        'task_id': task_id,
                        'success': success,
                        'index': index,
                        'timestamp': datetime.now()
                    }
                    summary['results'].append(task_result)
                        
                    if success:
                        summary['success'] += 1
                        logger.info(f"✅ タスク {task_id} 成功 ({index}/{summary['total']})")
                    else:
                        summary['failed'] += 1
                        logger.warning(f"⚠️ タスク {task_id} 失敗 ({index}/{summary['total']})")
                        
                    await asyncio.sleep(1)
                        
                except Exception as e:
                    summary['failed'] += 1
                    logger.error(f"❌ タスク {task_id} エラー: {e}")
                
            summary['end_time'] = datetime.now()
            elapsed_time = (summary['end_time'] - summary['start_time']).total_seconds()
                
            logger.info("\n" + "="*80)
            logger.info("📊 全タスク実行完了")
            logger.info("="*80)
            logger.info(f"  総タスク数:   {summary['total']:>3}件")
            logger.info(f"  ✅ 成功:      {summary['success']:>3}件")
            logger.info(f"  ❌ 失敗:      {summary['failed']:>3}件")
            logger.info(f"  ⏭️  スキップ:  {summary['skipped']:>3}件")
            logger.info(f"  ⏱️  実行時間:  {elapsed_time:.2f}秒")
            logger.info("="*80 + "\n")
                
            if summary['total'] > 0:
                success_rate = (summary['success'] / summary['total']) * 100
                logger.info(f"📈 成功率: {success_rate:.1f}%")
                
            return summary
                
        except Exception as e:
            logger.error(f"❌ 全タスク実行エラー: {e}")
            ErrorHandler.log_error(e, "run_all_tasks")
            summary['end_time'] = datetime.now()
            return summary
            
        finally:
            logger.info("\n🧹 クリーンアップ...")
            self.current_iteration = 0
            logger.info("✅ 完了\n")
    