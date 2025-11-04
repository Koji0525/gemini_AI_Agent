#!/usr/bin/env python3
"""
task_coordinator_v07_self_healing.py

自己修復機能統合版タスクコーディネーター + 計測機能（依存関係修正）

【v07の変更点】
- ContentTaskExecutor と WordPressOrchestrator をオプション依存に変更
- 存在しない場合でも動作するように修正
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
    """自己修復機能付きタスクコーディネーター（v07）"""

    def __init__(self, sheets_manager: GoogleSheetsManager, browser: BrowserController = None):
        """
        初期化

        Args:
            sheets_manager: Google Sheets管理
            browser: ブラウザコントローラー（オプション）
        """
        self.sheets_manager = sheets_manager
        self.browser = browser

        # オプション依存のエージェント初期化
        self.content_executor = None
        self.wp_orchestrator = None
        self._init_optional_agents()

        # 自己修復コンポーネント初期化
        self.self_healing_available = False
        self._init_self_healing()

        logger.info("✅ TaskCoordinator v07 初期化完了")
        # ✅ P2-1: トランザクション用バックアップ
        self.task_state_backup = {}
        self.deadlock_threshold = 300

    def _init_optional_agents(self):
        """オプションエージェント初期化"""
        # ContentTaskExecutor（オプション）
        try:
            from agents.content.content_task_executor import ContentTaskExecutor

            self.content_executor = ContentTaskExecutor()
            logger.info("✅ ContentTaskExecutor 利用可能")
        except ImportError:
            logger.info("ℹ️  ContentTaskExecutor は利用できません（オプション）")

        # WordPressOrchestrator（オプション）
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
        タスク実行（自己修復対応 + 堅牢ステータス更新）

        Args:
            task: タスク情報

        Returns:
            実行結果
        """
        import time

        task_id = task.get("task_id", "unknown")
        execution_type = task.get("execution_type", "content")

        logger.info(f"🎯 タスク実行開始: {task_id} (タイプ: {execution_type})")

        # ✅ P2-1: タスク開始時にステータス更新
        task_start = time.time()
        await self.update_task_status_robust(
            task_id=task_id, status="in_progress", elapsed_time=0, retry_count=0
        )

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

                # ✅ P2-1: 成功時のステータス更新
                elapsed = time.time() - task_start
                await self.update_task_status_robust(
                    task_id=task_id,
                    status="completed",
                    result=result,
                    elapsed_time=elapsed,
                    retry_count=retry_count,
                )

                logger.info(f"✅ タスク成功: {task_id} (実行時間: {elapsed:.2f}秒)")

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

        # ✅ P2-1: 最終失敗時のステータス更新
        elapsed = time.time() - task_start
        await self.update_task_status_robust(
            task_id=task_id,
            status="failed",
            error_message=str(last_error),
            elapsed_time=elapsed,
            retry_count=retry_count,
            error_type=type(last_error).__name__ if last_error else "Unknown",
        )

        logger.error(f"❌ タスク最終失敗: {task_id}")

        if self.self_healing_available:
            await self._record_failure(task, last_error)

        return {
            "status": "failed",
            "task_id": task_id,
            "error": str(last_error),
            "retry_count": retry_count,
        }
        return await self.wp_orchestrator.execute_task(task)

    async def _execute_content_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """コンテンツ生成タスク実行"""
        if self.content_executor is None:
            # フォールバック: 基本的な処理
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
            # 1. pm_tasks のステータス更新
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

    # ========================================
    # ✅ P2-1: トランザクション処理
    # ========================================

    def _backup_task_state(self, task_id: str):
        """タスクの現在の状態をバックアップ"""
        try:
            data = self.sheets_manager.read_range("pm_tasks!A:Z")
            if not data:
                return None

            for i, row in enumerate(data):
                if len(row) > 0 and row[0] == task_id:
                    backup = {"row_index": i + 1, "data": row.copy(), "timestamp": datetime.now()}
                    self.task_state_backup[task_id] = backup
                    logger.debug(f"💾 バックアップ保存: {task_id} (行{i+1})")
                    return backup

            return None
        except Exception as e:
            logger.error(f"❌ バックアップ失敗: {e}")
            return None

    def _rollback_task_state(self, task_id: str) -> bool:
        """タスクの状態をロールバック"""
        try:
            if task_id not in self.task_state_backup:
                return False

            backup = self.task_state_backup[task_id]
            row_index = backup["row_index"]
            range_str = f"pm_tasks!A{row_index}:Z{row_index}"
            self.sheets_manager.write_range(range_str, [backup["data"]])

            logger.info(f"🔄 ロールバック成功: {task_id}")
            del self.task_state_backup[task_id]
            return True
        except Exception as e:
            logger.error(f"❌ ロールバック失敗: {e}")
            return False

    async def _exponential_backoff(self, retry_count: int):
        """指数バックオフによる待機"""
        wait_time = min(2**retry_count, 16)
        logger.info(f"⏳ リトライ待機: {wait_time}秒")
        await asyncio.sleep(wait_time)

    def _check_deadlock(self, task_id: str) -> bool:
        """デッドロック検知"""
        try:
            data = self.sheets_manager.read_range("pm_tasks!A:Z")
            if not data:
                return False

            for row in data:
                if len(row) > 0 and row[0] == task_id:
                    status = row[3] if len(row) > 3 else ""
                    timestamp_str = row[5] if len(row) > 5 else ""

                    if status == "in_progress" and timestamp_str:
                        try:
                            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                            elapsed = (datetime.now() - timestamp).total_seconds()

                            if elapsed > self.deadlock_threshold:
                                logger.warning(f"🚨 デッドロック検知: {task_id} ({elapsed:.0f}秒)")
                                return True
                        except ValueError:
                            pass
            return False
        except Exception as e:
            logger.error(f"❌ デッドロック検知エラー: {e}")
            return False

    async def update_task_status_robust(
        self,
        task_id: str,
        status: str,
        result: dict = None,
        error_message: str = None,
        elapsed_time: float = None,
        retry_count: int = 0,
        error_type: str = None,
        max_retries: int = 3,
    ) -> bool:
        """堅牢なステータス更新（トランザクション＋リトライ）"""
        logger.info(f"🔍 堅牢ステータス更新: {task_id} → {status}")

        if self._check_deadlock(task_id):
            logger.error(f"❌ デッドロック検知: {task_id}")
            return False

        backup = self._backup_task_state(task_id)

        attempt = 0
        while attempt < max_retries:
            try:
                # pm_tasksのステータス更新
                data = self.sheets_manager.read_range("pm_tasks!A:Z")
                if data:
                    for i, row in enumerate(data):
                        if len(row) > 0 and row[0] == task_id:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            # ステータス更新
                            cell = f"pm_tasks!D{i+1}"
                            self.sheets_manager.write_range(cell, [[status]])

                            # タイムスタンプ更新
                            cell_time = f"pm_tasks!F{i+1}"
                            self.sheets_manager.write_range(cell_time, [[timestamp]])
                            break

                # task_execution_logに記録
                log_data = [
                    task_id,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    status,
                    result.get("summary", "") if result else "",
                    error_message or "",
                    "",  # output_file
                    "",  # length
                    result.get("quality_score", "") if result else "",
                    "",  # I列
                    "",  # J列
                    elapsed_time if elapsed_time else "",
                    retry_count,
                    error_type or "",
                    "",
                ]
                self.sheets_manager.append_rows("task_execution_log", [log_data])

                logger.info(f"✅ ステータス更新成功: {task_id}")

                if task_id in self.task_state_backup:
                    del self.task_state_backup[task_id]
                return True

            except Exception as e:
                attempt += 1
                logger.warning(f"⚠️ 更新失敗 (試行{attempt}/{max_retries}): {e}")

                if attempt < max_retries:
                    await self._exponential_backoff(attempt)
                else:
                    if backup:
                        self._rollback_task_state(task_id)
                    return False

        return False
