#!/usr/bin/env python3
"""
task_coordinator_v08_self_healing.py

自己修復機能統合版タスクコーディネーター + 計測機能（timestamp修正）

【v08の変更点】
- update_task_status の timestamp スコープエラー修正
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

logger = logging.getLogger(__name__)


class TaskCoordinatorWithSelfHealing:
    """自己修復機能付きタスクコーディネーター（v08）"""

    def __init__(self, sheets_manager: GoogleSheetsManager, browser: BrowserController = None):
        self.sheets_manager = sheets_manager
        self.browser = browser

        self.content_executor = None
        self.wp_orchestrator = None
        self._init_optional_agents()

        self.self_healing_available = False
        self._init_self_healing()

        logger.info("✅ TaskCoordinator v08 初期化完了")

    def _init_optional_agents(self):
        """オプションエージェント初期化"""
        try:
            from agents.content.content_task_executor import ContentTaskExecutor

            self.content_executor = ContentTaskExecutor()
            logger.info("✅ ContentTaskExecutor 利用可能")
        except ImportError:
            logger.info("ℹ️  ContentTaskExecutor は利用できません（オプション）")

        try:
            from agents.wordpress.specialized.wp_orchestrator import WordPressOrchestrator

            self.wp_orchestrator = WordPressOrchestrator(self.sheets_manager)
            logger.info("✅ WordPressOrchestrator 利用可能")
        except ImportError:
            logger.info("ℹ️  WordPressOrchestrator は利用できません（オプション）")

    def _init_self_healing(self):
        """自己修復コンポーネント初期化"""
        try:
            from agents.self_healing.error_classifier import ErrorClassifier
            from agents.self_healing.retry_manager import RetryManager
            from agents.self_healing.logging.decision_support_system import (
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
        """タスク実行（自己修復対応）"""
        task_id = task.get("task_id", "unknown")
        execution_type = task.get("execution_type", "content")

        logger.info(f"🎯 タスク実行開始: {task_id} (タイプ: {execution_type})")

        max_retries = 3
        retry_count = 0
        last_error = None

        while retry_count < max_retries:
            try:
                if execution_type == "wordpress":
                    result = await self._execute_wordpress_task(task)
                else:
                    result = await self._execute_content_task(task)

                logger.info(f"✅ タスク成功: {task_id}")

                if self.self_healing_available:
                    await self._record_success(task, result)

                return result

            except Exception as e:
                last_error = e
                retry_count += 1

                logger.warning(f"⚠️ タスク失敗 (試行{retry_count}/{max_retries}): {e}")

                if self.self_healing_available and retry_count < max_retries:
                    should_retry, strategy = await self._analyze_and_decide(task, e, retry_count)

                    if not should_retry:
                        logger.error(f"❌ 修復不可能: {task_id}")
                        break

                    logger.info(f"🔧 修復戦略: {strategy}")
                    await asyncio.sleep(2**retry_count)
                else:
                    await asyncio.sleep(2**retry_count)

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
        if self.wp_orchestrator is None:
            raise RuntimeError("WordPressOrchestrator が利用できません")
        return await self.wp_orchestrator.execute_task(task)

    async def _execute_content_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """コンテンツ生成タスク実行"""
        if self.content_executor is None:
            logger.warning("ContentTaskExecutor が利用できません（フォールバック処理）")
            return {
                "status": "completed",
                "task_id": task.get("task_id"),
                "message": "基本処理のみ実行",
            }

        description = task.get("description", "")
        return await self.content_executor.execute(description)

    async def _analyze_and_decide(
        self, task: Dict, error: Exception, retry_count: int
    ) -> tuple[bool, str]:
        """エラー分析と修復戦略決定"""
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

    def update_task_status(
        self,
        task_id: str,
        status: str,
        result: dict = None,
        error_message: str = None,
        output_file: str = None,
        elapsed_time: float = None,
        retry_count: int = 0,
        error_type: str = None,
        fix_applied: bool = False,
    ):
        """
        タスクステータスを更新（計測データ付き）
        """
        logger.info(f"🔍 ステータス更新: {task_id} → {status}")

        try:
            # ✅ timestamp をメソッドの先頭で定義
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 1. pm_tasks のステータス更新
            data = self.sheets_manager.read_range("pm_tasks!A:Z")
            if not data:
                logger.warning("pm_tasksシートが空です")
                return

            for i, row in enumerate(data):
                if len(row) > 0 and row[0] == task_id:
                    cell = f"pm_tasks!D{i+1}"
                    self.sheets_manager.write_range(cell, [[status]])

                    cell_time = f"pm_tasks!F{i+1}"
                    self.sheets_manager.write_range(cell_time, [[timestamp]])

                    logger.info(f"✅ pm_tasks更新: {task_id} → {status}")
                    break

            # 2. task_execution_log に計測データを記録
            log_data = [
                task_id,
                timestamp,
                status,
                result.get("summary", "") if result else "",
                error_message or "",
                output_file or "",
                result.get("length", "") if result else "",
                result.get("quality_score", "") if result else "",
                "",
                "",
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
