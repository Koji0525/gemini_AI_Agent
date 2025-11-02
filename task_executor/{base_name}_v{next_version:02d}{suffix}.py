"""
TaskCoordinator v02 - 完全版
タスクの実行を統括し、適切なExecutorに振り分ける
"""

import logging
from typing import Dict
from datetime import datetime

try:
    from task_executor import TaskExecutor
except ImportError:
    TaskExecutor = None

try:
    from agents.wordpress.specialized.wp_content_executor import WordPressContentExecutor
except ImportError:
    WordPressContentExecutor = None

try:
    from agents.marketing.specialized.ma_executor import MarketingAutomationExecutor
except ImportError:
    MarketingAutomationExecutor = None

logger = logging.getLogger(__name__)


class TaskCoordinator:
    """タスク実行の統括クラス"""

    def __init__(
        self, sheets_manager, browser_controller=None, llm_client=None, completion_handler=None
    ):
        self.sheets_manager = sheets_manager
        self.browser_controller = browser_controller
        self.llm_client = llm_client
        self.completion_handler = completion_handler

        self.stats = {"total": 0, "success": 0, "failed": 0, "by_type": {}}

        self.specialized_executors = {}
        self._initialize_specialized_executors()

        self.general_executor = (
            TaskExecutor(
                sheets_manager=sheets_manager,
                browser_controller=browser_controller,
                llm_client=llm_client,
            )
            if TaskExecutor
            else None
        )

        logger.info("TaskCoordinator v02 初期化完了")

    def _initialize_specialized_executors(self):
        if WordPressContentExecutor:
            try:
                self.specialized_executors["wordpress_content"] = WordPressContentExecutor(
                    sheets_manager=self.sheets_manager, browser_controller=self.browser_controller
                )
                logger.info("✅ WordPress Content Executor 初期化成功")
            except Exception as e:
                logger.error(f"❌ WordPress Content Executor 初期化失敗: {e}")

        if MarketingAutomationExecutor:
            try:
                self.specialized_executors["marketing_automation"] = MarketingAutomationExecutor(
                    sheets_manager=self.sheets_manager, browser_controller=self.browser_controller
                )
                logger.info("✅ Marketing Automation Executor 初期化成功")
            except Exception as e:
                logger.error(f"❌ Marketing Automation Executor 初期化失敗: {e}")

    def determine_executor_type(self, task: Dict) -> str:
        task_type = task.get("type", "").lower()
        title = task.get("title", "").lower()

        if any(keyword in task_type for keyword in ["wordpress", "wp", "blog", "post"]):
            return "wordpress_content"
        if any(keyword in title for keyword in ["wordpress", "ブログ", "投稿", "記事"]):
            return "wordpress_content"
        if any(keyword in task_type for keyword in ["marketing", "ma", "email", "campaign"]):
            return "marketing_automation"
        if any(keyword in title for keyword in ["マーケティング", "メール", "キャンペーン"]):
            return "marketing_automation"

        return "general"

    async def execute_task_coordinated(self, task: Dict) -> Dict:
        self.stats["total"] += 1

        task_id = task.get("task_id", "unknown")
        task_title = task.get("title", "no title")

        logger.info(f"📋 タスク実行開始: {task_id} - {task_title}")

        executor_type = self.determine_executor_type(task)
        logger.info(f"   Executor種別: {executor_type}")

        if executor_type not in self.stats["by_type"]:
            self.stats["by_type"][executor_type] = {"total": 0, "success": 0, "failed": 0}

        self.stats["by_type"][executor_type]["total"] += 1

        result = None

        if executor_type in self.specialized_executors:
            executor = self.specialized_executors[executor_type]

            try:
                logger.info(f"   🎯 専用Executor使用: {executor_type}")

                if hasattr(executor, "execute"):
                    result = await executor.execute(task)
                elif hasattr(executor, "execute_task"):
                    result = await executor.execute_task(task)
                else:
                    logger.warning(f"   ⚠️  専用Executorにexecuteメソッドがありません")
                    result = None

            except AttributeError as e:
                logger.warning(f"   ⚠️  専用Executor実行エラー: {e}")
                result = None
            except Exception as e:
                logger.error(f"   ❌ 専用Executor実行エラー: {e}")
                result = None

        if result is None and self.general_executor:
            try:
                logger.info(f"   🔄 汎用Executor使用")
                result = await self.general_executor.execute_task(task)
            except Exception as e:
                logger.error(f"   ❌ 汎用Executor実行エラー: {e}")
                result = {"success": False, "error": str(e)}

        if result is None:
            result = {"success": False, "message": "Executorが見つかりませんでした"}

        if result.get("success") or result.get("status") == "success":
            self.stats["success"] += 1
            self.stats["by_type"][executor_type]["success"] += 1
            logger.info(f"✅ タスク完了: {task_id}")
        else:
            self.stats["failed"] += 1
            self.stats["by_type"][executor_type]["failed"] += 1
            logger.error(f"❌ タスク失敗: {task_id}")

        if self.completion_handler:
            try:
                await self.completion_handler.on_task_completed(task, result)
            except Exception as e:
                logger.warning(f"タスク完了処理エラー: {e}")

        try:
            self.log_execution(task, result, executor_type)
            if task_id:
                new_status = "completed" if result.get("status") == "success" else "failed"
                self.update_task_status(task_id, new_status, result)
        except Exception as log_error:
            logger.warning(f"ログ記録エラー: {log_error}")

        return result

    def get_stats(self) -> Dict:
        return self.stats.copy()

    def log_execution(self, task: dict, result: dict, executor_type: str):
        print(
            f"🔍 DEBUG: log_execution呼び出し - task_id={task.get('id')}, executor={executor_type}"
        )
        try:
            log_entry = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                task.get("task_id", ""),
                task.get("title", ""),
                executor_type,
                result.get("status", "unknown"),
                str(result.get("output", "")),
                str(result.get("error", "")),
                task.get("goal_id", ""),
            ]

            data = self.sheets_manager.read_range("task_execution_log!A:Z")
            next_row = len(data) + 1 if data else 1
            range_name = f"task_execution_log!A{next_row}:H{next_row}"
            self.sheets_manager.write_range(range_name, [log_entry])
            logger.info(f"✅ ログ記録: {task.get('task_id', 'unknown')}")
        except Exception as e:
            logger.error(f"❌ ログ記録エラー: {e}")

    def update_task_status(self, task_id: str, status: str, result: dict = None):
        print(f"🔍 DEBUG: update_task_status呼び出し - task_id={task_id}, status={status}")
        try:
            data = self.sheets_manager.read_range("pm_tasks!A:Z")
            if not data:
                logger.warning("pm_tasksシートが空です")
                return

            for i, row in enumerate(data):
                if len(row) > 0 and row[0] == task_id:
                    cell = f"pm_tasks!D{i+1}"
                    self.sheets_manager.write_range(cell, [[status]])

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cell_time = f"pm_tasks!F{i+1}"
                    self.sheets_manager.write_range(cell_time, [[timestamp]])

                    logger.info(f"✅ ステータス更新: {task_id} → {status}")
                    return

            logger.warning(f"⚠️  タスクID {task_id} が見つかりません")
        except Exception as e:
            logger.error(f"❌ ステータス更新エラー: {e}")
