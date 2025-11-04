#!/usr/bin/env python3
"""
AutoRecoveryManager
自動復旧機能の中核クラス

Phase 3: システム堅牢化
作成日: 2025-11-04
"""
import asyncio
import time
from typing import Dict, Optional, Any
from enum import Enum


class RecoveryLevel(Enum):
    """復旧レベル"""

    IMMEDIATE = 1  # 即座に復旧可能（再試行）
    FIXABLE = 2  # 設定変更で復旧可能
    KNOWLEDGE = 3  # ナレッジベースから解決策を検索
    HUMAN = 4  # 人間の介入が必要


class AutoRecoveryManager:
    """
    自動復旧管理クラス

    エラーを検知し、適切な復旧戦略を選択・実行する
    """

    def __init__(self, kb_manager=None, sheets_manager=None):
        """
        Args:
            kb_manager: KnowledgeBaseManager（ナレッジ検索用）
            sheets_manager: GoogleSheetsManager（ログ記録用）
        """
        self.kb_manager = kb_manager
        self.sheets = sheets_manager

        # 復旧統計
        self.recovery_stats = {
            "total_attempts": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
            "recovery_by_level": {level: 0 for level in RecoveryLevel},
        }

    async def detect_and_recover(self, error: Exception, context: Dict = None) -> Optional[Any]:
        """
        エラーを検知して自動復旧を試行

        Args:
            error: 発生したエラー
            context: エラー発生時のコンテキスト情報

        Returns:
            復旧結果（成功時）or None（失敗時）
        """
        self.recovery_stats["total_attempts"] += 1

        print(f"🔧 AutoRecovery: エラー検知 - {type(error).__name__}")

        # エラーを分類
        recovery_level = self._classify_error(error)
        self.recovery_stats["recovery_by_level"][recovery_level] += 1

        print(f"   復旧レベル: {recovery_level.name}")

        # レベルに応じた復旧を試行
        try:
            if recovery_level == RecoveryLevel.IMMEDIATE:
                result = await self._immediate_recovery(error, context)
            elif recovery_level == RecoveryLevel.FIXABLE:
                result = await self._configuration_recovery(error, context)
            elif recovery_level == RecoveryLevel.KNOWLEDGE:
                result = await self._knowledge_based_recovery(error, context)
            else:  # HUMAN
                result = await self._escalate_to_human(error, context)

            if result is not None:
                self.recovery_stats["successful_recoveries"] += 1
                print(f"   ✅ 復旧成功")
            else:
                self.recovery_stats["failed_recoveries"] += 1
                print(f"   ❌ 復旧失敗")

            # ログ記録
            await self._log_recovery_attempt(error, recovery_level, result is not None)

            return result

        except Exception as e:
            print(f"   ❌ 復旧処理中にエラー: {e}")
            self.recovery_stats["failed_recoveries"] += 1
            return None

    def _classify_error(self, error: Exception) -> RecoveryLevel:
        """
        エラーを分類して復旧レベルを決定

        Args:
            error: 発生したエラー

        Returns:
            復旧レベル
        """
        error_msg = str(error).lower()
        type(error).__name__

        # LEVEL 1: 即座に復旧可能
        if any(
            keyword in error_msg
            for keyword in [
                "timeout",
                "timed out",
                "rate limit",
                "too many requests",
                "connection reset",
                "connection refused",
                "temporary",
                "try again",
            ]
        ):
            return RecoveryLevel.IMMEDIATE

        # LEVEL 2: 設定変更で復旧可能
        if any(
            keyword in error_msg
            for keyword in [
                "authentication",
                "unauthorized",
                "401",
                "forbidden",
                "403",
                "not found",
                "404",
                "config",
                "environment variable",
            ]
        ):
            return RecoveryLevel.FIXABLE

        # LEVEL 3: ナレッジベースで解決可能（既知パターン）
        if self.kb_manager and any(
            keyword in error_msg
            for keyword in ["attribute", "import", "module", "key error", "value error"]
        ):
            return RecoveryLevel.KNOWLEDGE

        # LEVEL 4: 人間の介入が必要
        return RecoveryLevel.HUMAN

    async def _immediate_recovery(self, error: Exception, context: Dict) -> Optional[Any]:
        """
        LEVEL 1: 即座に復旧（指数バックオフで再試行）

        Args:
            error: エラー
            context: コンテキスト

        Returns:
            復旧結果 or None
        """
        print(f"   🔄 再試行戦略: 指数バックオフ")

        max_retries = 3
        base_delay = 2  # 秒

        for attempt in range(1, max_retries + 1):
            delay = base_delay**attempt
            print(f"      試行 {attempt}/{max_retries} （{delay}秒待機）")

            await asyncio.sleep(delay)

            # コンテキストに復旧関数があれば実行
            if context and "retry_func" in context:
                try:
                    result = await context["retry_func"]()
                    return result
                except Exception as e:
                    if attempt == max_retries:
                        print(f"      最終試行も失敗: {e}")
                        return None
                    print(f"      失敗、次回を試行: {e}")

        return None

    async def _configuration_recovery(self, error: Exception, context: Dict) -> Optional[Any]:
        """
        LEVEL 2: 設定変更で復旧

        Args:
            error: エラー
            context: コンテキスト

        Returns:
            復旧結果 or None
        """
        print(f"   🔧 設定修正戦略")

        # 環境変数の再読み込み
        if "authentication" in str(error).lower() or "401" in str(error):
            print(f"      環境変数を再読み込み")
            # TODO: 環境変数の再読み込み処理
            return None

        # TODO: その他の設定修正処理
        return None

    async def _knowledge_based_recovery(self, error: Exception, context: Dict) -> Optional[Any]:
        """
        LEVEL 3: ナレッジベースから解決策を検索

        Args:
            error: エラー
            context: コンテキスト

        Returns:
            復旧結果 or None
        """
        print(f"   📚 ナレッジベース検索")

        if not self.kb_manager:
            print(f"      ナレッジベースが利用不可")
            return None

        # TODO: ナレッジベースから解決策を検索
        # solution = await self.kb_manager.search_solution(str(error))
        # if solution:
        #     return await self._apply_solution(solution)

        return None

    async def _escalate_to_human(self, error: Exception, context: Dict) -> Optional[Any]:
        """
        LEVEL 4: 人間にエスカレーション

        Args:
            error: エラー
            context: コンテキスト

        Returns:
            None（人間の対応待ち）
        """
        print(f"   🚨 人間にエスカレーション")

        # TODO: 通知処理（Slack, GitHub Issue等）

        return None

    async def _log_recovery_attempt(self, error: Exception, level: RecoveryLevel, success: bool):
        """
        復旧試行をログに記録

        Args:
            error: エラー
            level: 復旧レベル
            success: 成功/失敗
        """
        if not self.sheets:
            return

        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "error_type": type(error).__name__,
            "error_message": str(error)[:200],
            "recovery_level": level.name,
            "success": success,
        }

        try:
            await self.sheets.append_row("recovery_log", list(log_entry.values()))
        except:
            pass  # ログ記録失敗は無視

    def get_stats(self) -> Dict:
        """
        復旧統計を取得

        Returns:
            統計情報
        """
        total = self.recovery_stats["total_attempts"]
        success = self.recovery_stats["successful_recoveries"]

        return {
            **self.recovery_stats,
            "success_rate": (success / total * 100) if total > 0 else 0,
        }


# ====================
# テスト用コード
# ====================
if __name__ == "__main__":

    async def test_recovery():
        """簡易テスト"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🧪 AutoRecoveryManager テスト")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        manager = AutoRecoveryManager()

        # テスト1: タイムアウトエラー
        print("\n🧪 テスト1: Timeout Error")
        error1 = TimeoutError("Connection timed out")
        await manager.detect_and_recover(error1)

        # テスト2: 認証エラー
        print("\n🧪 テスト2: Authentication Error")
        error2 = Exception("401 Unauthorized")
        await manager.detect_and_recover(error2)

        # テスト3: 未知のエラー
        print("\n🧪 テスト3: Unknown Error")
        error3 = ValueError("Something went wrong")
        await manager.detect_and_recover(error3)

        # 統計表示
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📊 復旧統計")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        stats = manager.get_stats()
        print(f"  総試行回数: {stats['total_attempts']}")
        print(f"  成功回数: {stats['successful_recoveries']}")
        print(f"  失敗回数: {stats['failed_recoveries']}")
        print(f"  成功率: {stats['success_rate']:.1f}%")

    asyncio.run(test_recovery())
