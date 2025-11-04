"""
TaskExecutor with AutoRecoveryManager Integration
Phase 3: 自動復旧機能付きタスク実行エンジン
"""

import asyncio
import time
from typing import Dict, Any
from datetime import datetime

from tools.sheets_manager import GoogleSheetsManager
from agents.self_healing.auto_recovery_manager import AutoRecoveryManager, RecoveryLevel


class TaskExecutorWithRecovery:
    """自動復旧機能を持つタスク実行エンジン"""

    def __init__(
        self,
        sheets_manager: GoogleSheetsManager,
        browser_controller=None,
        gemini_agent=None,
        wordpress_agent=None,
    ):
        """
        初期化

        Args:
            sheets_manager: GoogleSheetsManager インスタンス
            browser_controller: ブラウザ制御（オプション）
            gemini_agent: Geminiエージェント（オプション）
            wordpress_agent: WordPressエージェント（オプション）
        """
        self.sheets = sheets_manager
        self.browser = browser_controller
        self.gemini = gemini_agent
        self.wordpress = wordpress_agent

        # AutoRecoveryManager を初期化
        self.recovery_manager = AutoRecoveryManager(sheets_manager)

        # 統計情報
        self.stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "recovered_tasks": 0,
            "recovery_attempts": 0,
        }

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスクを実行（自動復旧機能付き）

        Args:
            task: タスク情報の辞書

        Returns:
            実行結果の辞書
        """
        task_start = time.time()
        self.stats["total_tasks"] += 1

        task_id = task.get("task_id", f"task_{int(time.time())}")
        task_name = task.get("task_name", "Unknown Task")

        print(f"🚀 タスク実行開始: {task_name} (ID: {task_id})")

        # 初回実行
        result = await self._execute_single_attempt(task)

        # 成功した場合
        if result["status"] == "success":
            elapsed = time.time() - task_start
            self.stats["successful_tasks"] += 1

            await self._log_execution(task, result, elapsed, retry_count=0)
            print(f"✅ タスク成功: {task_name} ({elapsed:.2f}秒)")
            return result

        # エラーが発生した場合 → AutoRecoveryManager に委譲
        print(f"⚠️ エラー発生: {result.get('error', 'Unknown error')}")
        print(f"🔧 自動復旧を試みます...")

        recovery_result = await self._attempt_recovery(task, result, task_start)

        elapsed = time.time() - task_start

        # 復旧成功
        if recovery_result["status"] == "success":
            self.stats["recovered_tasks"] += 1
            await self._log_execution(
                task,
                recovery_result,
                elapsed,
                retry_count=recovery_result.get("retry_count", 1),
                recovery_applied=True,
            )
            print(f"✅ 復旧成功: {task_name} ({elapsed:.2f}秒)")
            return recovery_result

        # 復旧失敗
        self.stats["failed_tasks"] += 1
        await self._log_execution(
            task,
            recovery_result,
            elapsed,
            retry_count=recovery_result.get("retry_count", 0),
            recovery_applied=False,
        )
        print(f"❌ タスク失敗: {task_name} ({elapsed:.2f}秒)")
        return recovery_result

    async def _execute_single_attempt(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスクの1回の実行試行

        Args:
            task: タスク情報

        Returns:
            実行結果
        """
        try:
            agent_name = task.get("agent", "unknown")

            # エージェント別の実行ロジック
            if agent_name == "gemini":
                result = await self._execute_gemini_task(task)
            elif agent_name == "wordpress":
                result = await self._execute_wordpress_task(task)
            elif agent_name == "browser":
                result = await self._execute_browser_task(task)
            else:
                result = {
                    "status": "error",
                    "error": f"Unknown agent: {agent_name}",
                    "error_type": "ConfigurationError",
                }

            return result

        except Exception as e:
            return {"status": "error", "error": str(e), "error_type": type(e).__name__}

    async def _attempt_recovery(
        self, task: Dict[str, Any], error_result: Dict[str, Any], task_start_time: float
    ) -> Dict[str, Any]:
        """
        AutoRecoveryManager を使ってタスクの復旧を試みる

        Args:
            task: タスク情報
            error_result: エラー結果
            task_start_time: タスク開始時刻

        Returns:
            復旧結果
        """
        self.stats["recovery_attempts"] += 1

        # AutoRecoveryManager にエラーを渡して復旧を試みる
        recovery_result = await self.recovery_manager.handle_error(
            task_id=task.get("task_id", "unknown"),
            error=Exception(error_result.get("error", "Unknown error")),
            context={
                "task_name": task.get("task_name"),
                "agent": task.get("agent"),
                "original_error": error_result,
            },
        )

        # 復旧レベルに応じた処理
        recovery_level = recovery_result.get("recovery_level")

        if recovery_level == RecoveryLevel.IMMEDIATE:
            # 即座復旧: 指数バックオフで再試行
            return await self._retry_with_backoff(task, max_retries=3)

        elif recovery_level == RecoveryLevel.FIXABLE:
            # 設定変更: 修正案を適用して再試行
            fix_strategy = recovery_result.get("fix_strategy", {})
            modified_task = self._apply_fix_strategy(task, fix_strategy)
            return await self._execute_single_attempt(modified_task)

        elif recovery_level == RecoveryLevel.KNOWLEDGE:
            # ナレッジベース活用: 類似解決策を検索して適用
            knowledge = recovery_result.get("knowledge", {})
            enhanced_task = self._apply_knowledge(task, knowledge)
            return await self._execute_single_attempt(enhanced_task)

        else:  # RecoveryLevel.HUMAN
            # 人間介入が必要
            return {
                "status": "error",
                "error": error_result.get("error"),
                "error_type": error_result.get("error_type"),
                "recovery_level": "human_required",
                "recovery_action": recovery_result.get("action"),
                "retry_count": 0,
            }

    async def _retry_with_backoff(
        self, task: Dict[str, Any], max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        指数バックオフで再試行

        Args:
            task: タスク情報
            max_retries: 最大再試行回数

        Returns:
            実行結果
        """
        for retry in range(1, max_retries + 1):
            wait_time = 2 ** (retry - 1)  # 1秒, 2秒, 4秒
            print(f"🔄 再試行 {retry}/{max_retries} ({wait_time}秒待機後)...")

            await asyncio.sleep(wait_time)

            result = await self._execute_single_attempt(task)

            if result["status"] == "success":
                result["retry_count"] = retry
                return result

        # 全ての再試行が失敗
        return {
            "status": "error",
            "error": "Max retries exceeded",
            "error_type": "RetryExhausted",
            "retry_count": max_retries,
        }

    def _apply_fix_strategy(
        self, task: Dict[str, Any], fix_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        修正戦略をタスクに適用

        Args:
            task: 元のタスク
            fix_strategy: 修正戦略

        Returns:
            修正されたタスク
        """
        modified_task = task.copy()

        # 修正戦略の適用
        if "config_changes" in fix_strategy:
            modified_task.update(fix_strategy["config_changes"])

        if "retry_config" in fix_strategy:
            modified_task["retry_config"] = fix_strategy["retry_config"]

        return modified_task

    def _apply_knowledge(self, task: Dict[str, Any], knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        ナレッジベースの知見をタスクに適用

        Args:
            task: 元のタスク
            knowledge: ナレッジ情報

        Returns:
            強化されたタスク
        """
        enhanced_task = task.copy()

        # ナレッジからのヒントを適用
        if "best_practice" in knowledge:
            enhanced_task["hints"] = knowledge["best_practice"]

        if "success_rate" in knowledge:
            enhanced_task["expected_success_rate"] = knowledge["success_rate"]

        return enhanced_task

    async def _log_execution(
        self,
        task: Dict[str, Any],
        result: Dict[str, Any],
        elapsed_time: float,
        retry_count: int = 0,
        recovery_applied: bool = False,
    ):
        """
        実行結果をログに記録

        Args:
            task: タスク情報
            result: 実行結果
            elapsed_time: 実行時間（秒）
            retry_count: 再試行回数
            recovery_applied: 復旧が適用されたか
        """
        log_entry = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # timestamp
            task.get("task_id", "unknown"),  # task_id
            task.get("task_name", "Unknown"),  # task_name
            task.get("agent", "unknown"),  # agent
            result.get("status", "unknown"),  # status
            result.get("output", result.get("error", "")),  # result
            "",  # quality_score (後で追加)
            "",  # reviewer_notes
            round(elapsed_time, 2),  # elapsed_time
            retry_count,  # retry_count
            result.get("error_type", ""),  # error_type
            "Yes" if recovery_applied else "No",  # fix_applied
        ]

        try:
            self.sheets.append_rows("task_execution_log", [log_entry])
        except Exception as e:
            print(f"⚠️ ログ記録失敗: {e}")

    # ===== エージェント別実行メソッド =====

    async def _execute_gemini_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Geminiタスクの実行"""
        if not self.gemini:
            return {
                "status": "error",
                "error": "Gemini agent not configured",
                "error_type": "ConfigurationError",
            }

        try:
            # Gemini API呼び出し
            response = await self.gemini.generate_content(task.get("prompt", ""))
            return {"status": "success", "output": response}
        except Exception as e:
            return {"status": "error", "error": str(e), "error_type": type(e).__name__}

    async def _execute_wordpress_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """WordPressタスクの実行"""
        if not self.wordpress:
            return {
                "status": "error",
                "error": "WordPress agent not configured",
                "error_type": "ConfigurationError",
            }

        try:
            # WordPress操作
            result = await self.wordpress.execute(task)
            return {"status": "success", "output": result}
        except Exception as e:
            return {"status": "error", "error": str(e), "error_type": type(e).__name__}

    async def _execute_browser_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """ブラウザタスクの実行"""
        if not self.browser:
            return {
                "status": "error",
                "error": "Browser controller not configured",
                "error_type": "ConfigurationError",
            }

        try:
            # ブラウザ操作
            result = await self.browser.execute(task)
            return {"status": "success", "output": result}
        except Exception as e:
            return {"status": "error", "error": str(e), "error_type": type(e).__name__}

    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        total = self.stats["total_tasks"]
        if total == 0:
            return self.stats

        return {
            **self.stats,
            "success_rate": (self.stats["successful_tasks"] / total) * 100,
            "recovery_rate": (self.stats["recovered_tasks"] / total) * 100 if total > 0 else 0,
            "failure_rate": (self.stats["failed_tasks"] / total) * 100,
        }
