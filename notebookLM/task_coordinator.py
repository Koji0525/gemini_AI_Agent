"""
task_coordinator.py - タスク実行の統合調整レイヤー
既存のTaskExecutorを補完し、タスクの振り分けと結果集約を担当
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# 設定とユーティリティ
from config_utils import ErrorHandler, config

# データ管理
from sheets_manager import GoogleSheetsManager

# 既存のTaskExecutor
from task_executor import TaskExecutor

# 専門実行モジュール（新規）
try:
    from content_task_executor import ContentTaskExecutor
    HAS_CONTENT_EXECUTOR = True
except ImportError:
    HAS_CONTENT_EXECUTOR = False
    ContentTaskExecutor = None

try:
    from system_cli_executor import SystemCLIExecutor
    HAS_CLI_EXECUTOR = True
except ImportError:
    HAS_CLI_EXECUTOR = False
    SystemCLIExecutor = None

try:
    from workflow_executor import WorkflowExecutor
    HAS_WORKFLOW_EXECUTOR = True
except ImportError:
    HAS_WORKFLOW_EXECUTOR = False
    WorkflowExecutor = None

logger = logging.getLogger(__name__)


class TaskCoordinator:
    """
    タスク実行の統合調整レイヤー
    
    既存のTaskExecutorを拡張し、専門実行モジュールへの
    タスク振り分けと結果集約を行う
    """
    
    def __init__(
        self,
        task_executor: TaskExecutor,
        sheets_manager: GoogleSheetsManager,
        browser_controller=None
    ):
        """
        初期化
        
        Args:
            task_executor: 既存のTaskExecutorインスタンス
            sheets_manager: GoogleSheetsManagerインスタンス
            browser_controller: BrowserControllerインスタンス(オプション)
        """
        self.task_executor = task_executor
        self.sheets_manager = sheets_manager
        self.browser = browser_controller
        
        # 統計情報
        self.stats = {
            'total_executed': 0,
            'content_tasks': 0,
            'cli_tasks': 0,
            'workflow_tasks': 0,
            'fallback_tasks': 0,
            'success': 0,
            'failed': 0
        }
        
        logger.info("=" * 60)
        logger.info("🎯 TaskCoordinator 初期化中...")
        logger.info("=" * 60)
        
        # 専門実行モジュールの初期化
        self._initialize_specialized_executors()
        
        logger.info("=" * 60)
        logger.info("✅ TaskCoordinator 初期化完了")
        logger.info("=" * 60)
    
    def _initialize_specialized_executors(self):
        """専門実行モジュールを初期化"""
        
        # コンテンツタスク実行モジュール
        if HAS_CONTENT_EXECUTOR and ContentTaskExecutor:
            try:
                self.content_executor = ContentTaskExecutor(
                    browser_controller=self.browser,
                    sheets_manager=self.sheets_manager
                )
                logger.info("✅ ContentTaskExecutor 初期化完了")
            except Exception as e:
                logger.warning(f"⚠️ ContentTaskExecutor 初期化失敗: {e}")
                self.content_executor = None
        else:
            logger.info("ℹ️ ContentTaskExecutor は利用できません（既存実装を使用）")
            self.content_executor = None
        
        # CLIタスク実行モジュール
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
            logger.info("ℹ️ SystemCLIExecutor は利用できません")
            self.cli_executor = None
        
        # ワークフロー実行モジュール
        if HAS_WORKFLOW_EXECUTOR and WorkflowExecutor:
            try:
                self.workflow_executor = WorkflowExecutor(
                    task_executor=self.task_executor,
                    sheets_manager=self.sheets_manager,
                    browser_controller=self.browser
                )
                logger.info("✅ WorkflowExecutor 初期化完了")
            except Exception as e:
                logger.warning(f"⚠️ WorkflowExecutor 初期化失敗: {e}")
                self.workflow_executor = None
        else:
            logger.info("ℹ️ WorkflowExecutor は利用できません")
            self.workflow_executor = None
            
    def determine_executor_type(self, task: Dict) -> str:
        """
        タスクに最適な実行モジュールを判定
            
        Args:
            task: タスク情報辞書
                
        Returns:
            str: 実行モジュールタイプ ('content', 'cli', 'workflow', 'review', 'fallback')
        """
        description = task.get('description', '').lower()
        role = task.get('required_role', '').lower()
            
        # ========================================
        # 🔍 レビュータスク判定（最優先 - 新規追加）
        # ========================================
        if role == 'review' or 'レビュー' in description or 'review' in description:
            return 'review'
        # ========================================
            
        # ワークフローキーワードチェック（最優先）
        workflow_keywords = [
            '多言語', 'マルチステップ', 'レビュー→修正',
            'シーケンス', 'パイプライン', 'チェーン'
        ]
        if any(kw in description for kw in workflow_keywords):
            return 'workflow'
            
        # コンテンツ生成キーワードチェック
        content_keywords = [
            '記事', '生成', '執筆', 'ライティング', 
            'コンテンツ', 'ai', 'gemini', 'deepseek',
            'プロンプト', '抽出'
        ]
        if any(kw in description for kw in content_keywords):
            return 'content'
            
        # CLIコマンドキーワードチェック
        cli_keywords = [
            'wp-cli', 'acf', 'コマンド実行', 'インポート',
            'ファイル操作', 'システム', 'インフラ'
        ]
        if any(kw in description for kw in cli_keywords):
            return 'cli'
            
        # ロールベース判定
        if role in ['content', 'writer', 'seo']:
            return 'content'
        elif role in ['dev', 'system', 'admin']:
            return 'cli'
            
        # デフォルトは既存実装にフォールバック
        return 'fallback'
    
    async def execute_task_coordinated(self, task: Dict) -> Dict:
        """
        タスクを適切な実行モジュールに振り分けて実行
        
        Args:
            task: タスク情報辞書
            
        Returns:
            Dict: 実行結果
        """
        task_id = task.get('task_id', 'UNKNOWN')
        self.stats['total_executed'] += 1
        
        try:
            # 実行モジュールタイプを判定
            executor_type = self.determine_executor_type(task)
            
            logger.info("=" * 60)
            logger.info(f"📋 タスク振り分け: {task_id}")
            logger.info(f"実行タイプ: {executor_type.upper()}")
            logger.info("=" * 60)
            
            result = None
            
            # ========================================
            # 🔍 レビュータスク実行（新規追加）
            # ========================================
            if executor_type == 'review':
                logger.info("🔍 ReviewAgent で実行")
                
                # TaskExecutor経由でreview_agentを実行
                success = await self.task_executor.execute_task(task)
                result = {
                    'success': success,
                    'executor_type': 'review',
                    'message': 'レビュー実行完了' if success else 'レビュー実行失敗'
                }
            # ========================================
            
            # ワークフロー実行
            elif executor_type == 'workflow' and self.workflow_executor:
                logger.info("🔄 WorkflowExecutor で実行")
                self.stats['workflow_tasks'] += 1
                result = await self.workflow_executor.execute_workflow_task(task)
            
            # コンテンツ生成実行
            elif executor_type == 'content' and self.content_executor:
                logger.info("✍️ ContentTaskExecutor で実行")
                self.stats['content_tasks'] += 1
                result = await self.content_executor.execute_content_task(task)
            
            # CLIタスク実行
            elif executor_type == 'cli' and self.cli_executor:
                logger.info("⚙️ SystemCLIExecutor で実行")
                self.stats['cli_tasks'] += 1
                result = await self.cli_executor.execute_cli_task(task)
            
            # 既存実装へフォールバック
            else:
                logger.info("🔙 既存 TaskExecutor で実行（フォールバック）")
                self.stats['fallback_tasks'] += 1
                success = await self.task_executor.execute_task(task)
                result = {
                    'success': success,
                    'executor_type': 'fallback',
                    'message': '既存実装で実行完了'
                }
            
            # 統計更新
            if result and result.get('success'):
                self.stats['success'] += 1
            else:
                self.stats['failed'] += 1
            
            # 実行情報を結果に追加
            if result:
                result['executor_type'] = executor_type
                result['coordinated_execution'] = True
            
            return result
            
        except Exception as e:
            logger.error(f"❌ タスク調整エラー: {task_id}")
            ErrorHandler.log_error(e, f"TaskCoordinator.execute_task_coordinated({task_id})")
            self.stats['failed'] += 1
            
            return {
                'success': False,
                'error': str(e),
                'executor_type': 'error',
                'coordinated_execution': True
            }
            
        except Exception as e:
            logger.error(f"❌ タスク調整エラー: {task_id}")
            ErrorHandler.log_error(e, f"TaskCoordinator.execute_task_coordinated({task_id})")
            self.stats['failed'] += 1
            
            return {
                'success': False,
                'error': str(e),
                'executor_type': 'error',
                'coordinated_execution': True
            }
    
    async def run_all_tasks_coordinated(
        self,
        auto_continue: bool = False,
        enable_review: bool = True
    ):
        """
        全タスクを調整レイヤー経由で実行
        
        Args:
            auto_continue: 自動継続フラグ
            enable_review: レビュー有効化フラグ
        """
        logger.info("\n" + "=" * 60)
        logger.info("🚀 タスク調整実行開始")
        logger.info("=" * 60)
        
        try:
            iteration = 0
            max_iterations = self.task_executor.max_iterations
            
            while iteration < max_iterations:
                iteration += 1
                
                logger.info(f"\n{'=' * 60}")
                logger.info(f"反復 {iteration}/{max_iterations}")
                logger.info(f"{'=' * 60}")
                
                # 保留中タスクの読み込み
                pending_tasks = await self.task_executor.load_pending_tasks()
                
                if not pending_tasks:
                    logger.info("✅ 全タスク完了または保留タスクなし")
                    break
                
                logger.info(f"📋 実行予定タスク: {len(pending_tasks)}件")
                
                # タスク実行ループ
                for task in pending_tasks:
                    task_id = task.get('task_id', 'UNKNOWN')
                    
                    try:
                        logger.info(f"\n{'─' * 60}")
                        logger.info(f"タスク実行: {task_id}")
                        logger.info(f"{'─' * 60}")
                        
                        # 調整レイヤー経由で実行
                        result = await self.execute_task_coordinated(task)
                        
                        if result and result.get('success'):
                            logger.info(f"✅ タスク {task_id} 成功")
                        else:
                            logger.error(f"❌ タスク {task_id} 失敗")
                        
                        # ユーザー確認（自動継続でない場合）
                        if not auto_continue:
                            continue_task = input(
                                f"\n次のタスクに進みますか? "
                                f"(y/n/a=以降全て実行): "
                            ).lower()
                            
                            if continue_task == 'n':
                                logger.info("ユーザーによる中断")
                                return
                            elif continue_task == 'a':
                                auto_continue = True
                                logger.info("自動実行モードに切り替え")
                        
                        await asyncio.sleep(2)
                        
                    except KeyboardInterrupt:
                        logger.warning("⏸️ ユーザーによる中断")
                        raise
                    
                    except Exception as e:
                        logger.error(f"❌ タスク {task_id} で予期しないエラー")
                        ErrorHandler.log_error(e, f"タスク {task_id} 実行中")
                        
                        if not auto_continue:
                            cont = input(
                                f"\n⚠️ エラーが発生しました。続行しますか? (y/n): "
                            ).lower()
                            if cont != 'y':
                                logger.info("ユーザーによる中断")
                                break
            
            # 最終統計レポート
            self._print_coordination_report()
            
        except KeyboardInterrupt:
            logger.warning("\n⏸️ ユーザーによる中断")
            self._print_coordination_report()
            raise
        
        except Exception as e:
            logger.error("❌ タスク調整実行全体で重大エラー")
            ErrorHandler.log_error(e, "TaskCoordinator.run_all_tasks_coordinated")
            self._print_coordination_report()
            raise
    
    def _print_coordination_report(self):
        """タスク調整の統計レポートを出力"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 タスク調整実行レポート")
        logger.info("=" * 60)
        logger.info(f"総実行数: {self.stats['total_executed']}")
        logger.info(f"  - コンテンツタスク: {self.stats['content_tasks']}")
        logger.info(f"  - CLIタスク: {self.stats['cli_tasks']}")
        logger.info(f"  - ワークフロータスク: {self.stats['workflow_tasks']}")
        logger.info(f"  - フォールバック: {self.stats['fallback_tasks']}")
        logger.info(f"成功: {self.stats['success']}")
        logger.info(f"失敗: {self.stats['failed']}")
        logger.info("=" * 60)
        
        # コンソール出力
        print("\n" + "=" * 60)
        print("📊 タスク調整実行レポート")
        print("=" * 60)
        print(f"総実行数: {self.stats['total_executed']}")
        print(f"  - コンテンツタスク: {self.stats['content_tasks']}")
        print(f"  - CLIタスク: {self.stats['cli_tasks']}")
        print(f"  - ワークフロータスク: {self.stats['workflow_tasks']}")
        print(f"  - フォールバック: {self.stats['fallback_tasks']}")
        print(f"成功: {self.stats['success']}")
        print(f"失敗: {self.stats['failed']}")
        print("=" * 60 + "\n")
    
    def get_stats(self) -> Dict:
        """統計情報を取得"""
        return self.stats.copy()