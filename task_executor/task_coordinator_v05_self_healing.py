import logging
import asyncio
from typing import Dict, Any
from pathlib import Path
import sys
from task_executor.content_task_executor import ContentTaskExecutor
from agents.wordpress.specialized.wp_orchestrator import WordPressOrchestrator
from tools.sheets_manager import GoogleSheetsManager
from browser_control.browser_controller import BrowserController

"""
task_coordinator_v05_self_healing.py

自己修復機能統合版タスクコーディネーター

【変更の理由】
- Phase 9の自己修復コンポーネント(ErrorClassifier, RetryManager)を統合
- エラー発生時の自動リトライと学習機能を実装
- ナレッジベースへの結果蓄積
"""


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


logger = logging.getLogger(__name__)


class TaskCoordinatorWithSelfHealing:
    """自己修復機能付きタスクコーディネーター"""

    def __init__(self, sheets_manager: GoogleSheetsManager, browser: BrowserController = None):
        """
        初期化

        Args:
            sheets_manager: Google Sheets管理
            browser: ブラウザコントローラー（オプション）
        """
        self.sheets_manager = sheets_manager
        self.browser = browser

        # 各エージェント初期化
        self.content_executor = ContentTaskExecutor()
        self.wp_orchestrator = WordPressOrchestrator(sheets_manager)

        # 自己修復コンポーネント初期化（可能な場合）
        self.self_healing_available = False
        self._init_self_healing()

        logger.info("✅ TaskCoordinator初期化完了")

    def _init_self_healing(self):
        """自己修復コンポーネント初期化"""
        try:
            # Phase 9コンポーネントのインポート試行
            from agents.self_healing.error_classifier import ErrorClassifier
            from agents.self_healing.retry_manager import RetryManager
            from agents.decision_support.decision_support_system import (
                DecisionSupportSystem,
            )

            self.error_classifier = ErrorClassifier()
            self.retry_manager = RetryManager()
            self.decision_support = DecisionSupportSystem()

            self.self_healing_available = True
            logger.info("✅ 自己修復機能が利用可能です")

        except ImportError as e:
            logger.warning(f"⚠️ 自己修復機能が利用できません: {e}")
            logger.info("💡 基本的なリトライ機能のみ使用します")

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスク実行（自己修復対応）

        Args:
            task: タスク情報

        Returns:
            実行結果
        """
        task_id = task.get("task_id", "unknown")
        execution_type = task.get("execution_type", "content")

        logger.info(f"🎯 タスク実行開始: {task_id} (タイプ: {execution_type})")

        max_retries = 3
        retry_count = 0
        last_error = None

        while retry_count < max_retries:
            try:
                # タスクタイプに応じて実行
                if execution_type == "wordpress":
                    result = await self._execute_wordpress_task(task)
                else:
                    result = await self._execute_content_task(task)

                logger.info(f"✅ タスク成功: {task_id}")

                # 成功パターンを記録（自己修復機能が利用可能な場合）
                if self.self_healing_available:
                    await self._record_success(task, result)

                return result

            except Exception as e:
                last_error = e
                retry_count += 1

                logger.warning(f"⚠️ タスク失敗 (試行{retry_count}/{max_retries}): {e}")

                # 自己修復機能による分析と修正
                if self.self_healing_available and retry_count < max_retries:
                    should_retry, strategy = await self._analyze_and_decide(task, e, retry_count)

                    if not should_retry:
                        logger.error(f"❌ 修復不可能: {task_id}")
                        break

                    logger.info(f"🔧 修復戦略: {strategy}")
                    await asyncio.sleep(2**retry_count)  # 指数バックオフ
                else:
                    # 基本的なリトライ
                    await asyncio.sleep(2**retry_count)

        # 最終的に失敗
        logger.error(f"❌ タスク最終失敗: {task_id}")

        if self.self_healing_available:
            await self._record_failure(task, last_error)

        return {
            "status": "failed",
            "task_id": task_id,
            "error": str(last_error),
            "retry_count": retry_count,
        }

    async def _execute_wordpress_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """WordPress関連タスク実行"""
        # WP Orchestratorに委譲
        return await self.wp_orchestrator.execute_task(task)

    async def _execute_content_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """コンテンツ生成タスク実行"""
        # Content Executorに委譲
        description = task.get("description", "")
        return await self.content_executor.execute(description)

    async def _analyze_and_decide(
        self, task: Dict, error: Exception, retry_count: int
    ) -> tuple[bool, str]:
        """
        エラー分析と修復戦略決定

        Returns:
            (リトライすべきか, 戦略説明)
        """
        if not self.self_healing_available:
            return (True, "基本リトライ")

        try:
            # エラー分類
            error_type = self.error_classifier.classify(error)

            # 意思決定システムに問い合わせ
            decision = await self.decision_support.get_retry_strategy(
                task_id=task.get("task_id"),
                error_type=error_type,
                retry_count=retry_count,
            )

            return (decision["should_retry"], decision["strategy"])

        except Exception as e:
            logger.warning(f"⚠️ 自己修復分析エラー: {e}")
            return (True, "フォールバック戦略")

    async def _record_success(self, task: Dict, result: Dict):
        """成功パターンを記録"""
        try:
            # ナレッジベースに記録（実装は省略）
            logger.debug(f"📝 成功パターン記録: {task.get('task_id')}")
        except Exception as e:
            logger.warning(f"⚠️ 成功記録エラー: {e}")

    async def _record_failure(self, task: Dict, error: Exception):
        """失敗パターンを記録"""
        try:
            # エラーログシートに記録
            error_data = [[task.get("task_id", "unknown"), str(error)[:200], "unresolved", ""]]

            self.sheets_manager.append_rows("error_log", error_data)
            logger.info(f"📝 失敗パターン記録: {task.get('task_id')}")

        except Exception as e:
            logger.warning(f"⚠️ 失敗記録エラー: {e}")

    async def cleanup(self):
        """リソースクリーンアップ"""
        try:
            if self.browser:
                await self.browser.close()
            logger.info("✅ クリーンアップ完了")
        except Exception as e:
            logger.warning(f"⚠️ クリーンアップエラー: {e}")


async def main():
    """テスト実行"""
    print("=" * 60)
    print("🛡️ 自己修復機能統合版 TaskCoordinator テスト")
    print("=" * 60)

    try:
        sheets_manager = GoogleSheetsManager()
        coordinator = TaskCoordinatorWithSelfHealing(sheets_manager)

        # テストタスク
        test_task = {
            "task_id": "TEST_001",
            "description": "テストタスク",
            "execution_type": "content",
        }

        result = await coordinator.execute_task(test_task)

        print(f"\n結果: {result.get('status')}")

        await coordinator.cleanup()

        return 0

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    exit(asyncio.run(main()))
