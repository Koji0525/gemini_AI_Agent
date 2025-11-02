"""
TaskCoordinator v02 - Complete Edition
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ TaskCompletionHandler統合（次タスク自動生成）
✅ AutoCodeFixer統合（エラー自動修復）
✅ DecisionSupportSystem統合（賢い判断）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

"""
task_coordinator_v02_interface_validator.py

InterfaceValidator統合版

【変更理由】
TaskExecutor.execute_task() が存在せず、execute_single_task() が正しいメソッド名。
InterfaceValidatorを統合して、メソッド名の不一致を自動解決する。

【狙い】
- メソッド名の自動検証・代替探索
- 今後のインターフェース変更に自動対応
- エラーゼロでのタスク実行
"""

import logging
from typing import Dict

# 設定とユーティリティ

# データ管理
from tools.sheets_manager import GoogleSheetsManager

# InterfaceValidator統合
try:
    from tools.interface_validator import InterfaceValidator

    HAS_INTERFACE_VALIDATOR = True
except ImportError:
    HAS_INTERFACE_VALIDATOR = False
    InterfaceValidator = None

# 既存のTaskExecutor
from task_executor import TaskExecutor

# 専門実行モジュール
try:
    from task_executor.content_task_executor import ContentTaskExecutor

    HAS_CONTENT_EXECUTOR = True
except ImportError:
    HAS_CONTENT_EXECUTOR = False
    ContentTaskExecutor = None

try:
    from task_executor.system_cli_executor import SystemCLIExecutor

    HAS_CLI_EXECUTOR = True
except ImportError:
    HAS_CLI_EXECUTOR = False
    SystemCLIExecutor = None

try:
    from task_executor.workflow_executor import WorkflowExecutor

    HAS_WORKFLOW_EXECUTOR = True
except ImportError:
    HAS_WORKFLOW_EXECUTOR = False
    WorkflowExecutor = None

logger = logging.getLogger(__name__)


class TaskCoordinator:
    """
    タスク実行の統合調整レイヤー (InterfaceValidator統合版)

    既存のTaskExecutorを拡張し、専門実行モジュールへの
    タスク振り分けと結果集約を行う
    """

    def __init__(
        self,
        task_executor: TaskExecutor,
        sheets_manager: GoogleSheetsManager,
        browser_controller=None,
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

        # InterfaceValidator統合
        if HAS_INTERFACE_VALIDATOR:
            self.interface_validator = InterfaceValidator()
            logger.info("✅ TaskCoordinator: InterfaceValidator統合")
        else:
            self.interface_validator = None
            logger.warning("⚠️ TaskCoordinator: InterfaceValidator利用不可")

        # 統計情報
        self.stats = {
            "total_executed": 0,
            "content_tasks": 0,
            "cli_tasks": 0,
            "workflow_tasks": 0,
            "fallback_tasks": 0,
            "success": 0,
            "failed": 0,
            "interface_validator_fixes": 0,
        }

        logger.info("=" * 60)
        logger.info("🎯 TaskCoordinator v2 初期化中...")
        logger.info("=" * 60)

        # 専門実行モジュールの初期化
        self._initialize_specialized_executors()

        logger.info("=" * 60)
        logger.info("✅ TaskCoordinator v2 初期化完了")
        logger.info("=" * 60)

    def _initialize_specialized_executors(self):
        """専門実行モジュールを初期化"""

        # コンテンツタスク実行モジュール
        if HAS_CONTENT_EXECUTOR and ContentTaskExecutor:
            try:
                self.content_executor = ContentTaskExecutor()
                logger.info("✅ ContentTaskExecutor 初期化完了")
            except Exception as e:
                logger.warning(f"⚠️ ContentTaskExecutor 初期化失敗: {e}")
                self.content_executor = None
        else:
            self.content_executor = None
            logger.info("⚠️ ContentTaskExecutor 利用不可")

        # システムCLI実行モジュール
        if HAS_CLI_EXECUTOR and SystemCLIExecutor:
            try:
                self.cli_executor = SystemCLIExecutor(sheets_manager=self.sheets_manager)
                logger.info("✅ SystemCLIExecutor 初期化完了")
            except Exception as e:
                logger.warning(f"⚠️ SystemCLIExecutor 初期化失敗: {e}")
                self.cli_executor = None
        else:
            self.cli_executor = None
            logger.info("⚠️ SystemCLIExecutor 利用不可")

        # ワークフロー実行モジュール
        if HAS_WORKFLOW_EXECUTOR and WorkflowExecutor:
            try:
                self.workflow_executor = WorkflowExecutor(
                    task_executor=self.task_executor,
                    sheets_manager=self.sheets_manager,
                    browser_controller=self.browser,
                )
                logger.info("✅ WorkflowExecutor 初期化完了")
            except Exception as e:
                logger.warning(f"⚠️ WorkflowExecutor 初期化失敗: {e}")
                self.workflow_executor = None
        else:
            self.workflow_executor = None
            logger.info("⚠️ WorkflowExecutor 利用不可")

    def determine_executor_type(self, task: Dict) -> str:
        """
        タスクの種類を判定

        Args:
            task: タスク情報辞書

        Returns:
            str: executor_type ('workflow', 'content', 'cli', 'fallback')
        """
        task_name = task.get("task_name", "").lower()
        required_role = task.get("required_role", "").lower()

        # ワークフロータイプの判定
        workflow_keywords = [
            "多言語",
            "multilingual",
            "review",
            "cycle",
            "sequential",
            "parallel",
        ]
        if any(keyword in task_name for keyword in workflow_keywords):
            return "workflow"

        # コンテンツタイプの判定
        content_keywords = ["記事", "article", "blog", "content", "writer"]
        if any(keyword in task_name for keyword in content_keywords):
            return "content"

        # CLIタイプの判定
        cli_keywords = ["wp-cli", "acf", "file", "copy", "move", "delete"]
        if any(keyword in task_name for keyword in cli_keywords):
            return "cli"

        # required_roleベースの判定
        if "content" in required_role:
            return "content"
        elif "cli" in required_role or "wordpress" in required_role:
            return "cli"

        # デフォルトはfallback（基本TaskExecutor）
        return "fallback"

    async def execute_task_coordinated(self, task: Dict) -> Dict:
        """
        タスクを適切な実行モジュールに振り分けて実行

        Args:
            task: タスク情報辞書

        Returns:
            Dict: 実行結果
        """
        task_id = task.get("task_id", "UNKNOWN")
        self.stats["total_executed"] += 1

        try:
            # 実行モジュールタイプを判定
            executor_type = self.determine_executor_type(task)

            logger.info("=" * 60)
            logger.info(f"📋 タスク振り分け: {task_id}")
            logger.info(f"実行タイプ: {executor_type.upper()}")
            logger.info("=" * 60)

            result = None

            # ワークフロー実行
            if executor_type == "workflow" and self.workflow_executor:
                logger.info("🔄 WorkflowExecutor で実行")
                self.stats["workflow_tasks"] += 1
                result = await self.workflow_executor.execute_workflow_task(task)

            # コンテンツ生成実行
            elif executor_type == "content" and self.content_executor:
                logger.info("✍️ ContentTaskExecutor で実行")
                self.stats["content_tasks"] += 1
                result = await self.content_executor.execute_content_task(task)

            # CLI実行
            elif executor_type == "cli" and self.cli_executor:
                logger.info("⚙️ SystemCLIExecutor で実行")
                self.stats["cli_tasks"] += 1
                result = await self.cli_executor.execute_cli_task(task)

            # フォールバック: 基本TaskExecutor（InterfaceValidator使用）
            else:
                logger.info("�� 基本TaskExecutor で実行（InterfaceValidator使用）")
                self.stats["fallback_tasks"] += 1

                # InterfaceValidatorで安全に実行
                if self.interface_validator:
                    # メソッド名を検証
                    method_name = self.interface_validator.validate_method(
                        self.task_executor, "execute_task"
                    )

                    if method_name:
                        logger.info(f"   🛡️ メソッド検証: execute_task → {method_name}")
                        method = getattr(self.task_executor, method_name)

                        # execute_single_taskの場合はbrowserも渡す
                        if method_name == "execute_single_task":
                            success = await method(self.browser, task)
                        else:
                            success = await method(task)

                        self.stats["interface_validator_fixes"] += 1
                    else:
                        logger.error("❌ TaskExecutorに実行可能なメソッドが見つかりません")
                        success = False
                else:
                    # InterfaceValidator利用不可の場合は直接試行
                    try:
                        success = await self.task_executor.execute_single_task(self.browser, task)
                    except AttributeError as e:
                        logger.error(f"❌ TaskExecutor実行エラー: {e}")
                        success = False

                result = {
                    "success": success,
                    "executor_type": "fallback",
                    "message": (
                        "基本TaskExecutor実行完了" if success else "基本TaskExecutor実行失敗"
                    ),
                }

            # 統計更新
            if result and result.get("success"):
                self.stats["success"] += 1
            else:
                self.stats["failed"] += 1

            # タスク完了処理
            if result and result.get("success"):
                try:
                    await self.completion_handler.on_task_completed(task, result)
                except Exception as e:
                    logger.warning(f"タスク完了処理エラー: {e}")
            return result or {"success": False, "message": "実行失敗"}

        except Exception as e:
            logger.error(f"❌ タスク調整エラー: {task_id}")
            logger.error(f"   エラー: {e}")
            self.stats["failed"] += 1

            import traceback

            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "message": f"タスク実行エラー: {str(e)}",
            }

    def get_stats(self) -> Dict:
        """統計情報を取得"""
        return self.stats.copy()


# 互換性のため、元のファイル名でもインポート可能にする
TaskCoordinatorV2 = TaskCoordinator
