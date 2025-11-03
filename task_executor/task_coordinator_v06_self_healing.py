#!/usr/bin/env python3
"""
task_coordinator_v06_self_healing.py

自己修復機能統合版タスクコーディネーター + 計測機能

【v06の変更点】
- P0-1: update_task_status に計測パラメータ追加
  - elapsed_time: タスク実行時間（秒）
  - retry_count: リトライ回数
  - error_type: エラー分類
  - fix_applied: 自動修復フラグ
- task_execution_log への書き込み機能追加
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager
from browser_control.browser_controller import BrowserController
from agents.content.content_task_executor import ContentTaskExecutor
from agents.wordpress.specialized.wp_orchestrator import WordPressOrchestrator

logger = logging.getLogger(__name__)


class TaskCoordinatorWithSelfHealing:
    """自己修復機能付きタスクコーディネーター（v06）"""

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

        logger.info("✅ TaskCoordinator v06 初期化完了")

    def _init_self_healing(self):
        """自己修復コンポーネント初期化"""
        try:
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
                    await asyncio.sleep(2**retry_count)
                else:
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
        return await self.wp_orchestrator.execute_task(task)

    async def _execute_content_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """コンテンツ生成タスク実行"""
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
            error_type = self.error_classifier.classify(error)
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
            logger.debug(f"📝 成功パターン記録: {task.get('task_id')}")
        except Exception as e:
            logger.warning(f"⚠️ 成功記録エラー: {e}")

    async def _record_failure(self, task: Dict, error: Exception):
        """失敗パターンを記録"""
        try:
            error_data = [[task.get("task_id", "unknown"), str(error)[:200], "unresolved", ""]]
            self.sheets_manager.append_rows("error_log", error_data)
            logger.info(f"📝 失敗パターン記録: {task.get('task_id')}")
        except Exception as e:
            logger.warning(f"⚠️ 失敗記録エラー: {e}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ✅ P0-1: update_task_status（計測パラメータ追加）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def update_task_status(
        self,
        task_id: str,
        status: str,
        result: dict = None,
        error_message: str = None,
        output_file: str = None,
        # ✅ P0-1: 計測パラメータ
        elapsed_time: float = None,
        retry_count: int = 0,
        error_type: str = None,
        fix_applied: bool = False,
    ):
        """
        タスクステータスを更新（計測データ付き）

        Args:
            task_id: タスクID
            status: ステータス（completed, failed, in_progress）
            result: 実行結果
            error_message: エラーメッセージ
            output_file: 出力ファイルパス
            elapsed_time: 実行時間（秒）
            retry_count: リトライ回数
            error_type: エラー分類
            fix_applied: 自動修復フラグ
        """
        logger.info(f"🔍 ステータス更新: {task_id} → {status}")

        try:
            # 1. pm_tasks のステータス更新
            data = self.sheets_manager.read_range("pm_tasks!A:Z")
            if not data:
                logger.warning("pm_tasksシートが空です")
                return

            for i, row in enumerate(data):
                if len(row) > 0 and row[0] == task_id:
                    # ステータス更新
                    cell = f"pm_tasks!D{i+1}"
                    self.sheets_manager.write_range(cell, [[status]])

                    # タイムスタンプ更新
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cell_time = f"pm_tasks!F{i+1}"
                    self.sheets_manager.write_range(cell_time, [[timestamp]])

                    logger.info(f"✅ pm_tasks更新: {task_id} → {status}")
                    break

            # 2. ✅ P0-1: task_execution_log に計測データを記録
            log_data = [
                task_id,
                timestamp,
                status,
                result.get("summary", "") if result else "",
                error_message or "",
                output_file or "",
                result.get("length", "") if result else "",
                result.get("quality_score", "") if result else "",
                "",  # I列（予約）
                "",  # J列（予約）
                # ✅ K-N列: 計測データ
                elapsed_time if elapsed_time is not None else "",
                retry_count,
                error_type or "",
                "Yes" if fix_applied else "No",
            ]

            self.sheets_manager.append_rows("task_execution_log", [log_data])
            logger.info(f"✅ task_execution_log記録完了（計測データ含む）")

        except Exception as e:
            logger.error(f"❌ ステータス更新エラー: {e}")

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
    print("🛡️ TaskCoordinator v06 テスト")
    print("=" * 60)

    try:
        sheets_manager = GoogleSheetsManager()
        coordinator = TaskCoordinatorWithSelfHealing(sheets_manager)

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
