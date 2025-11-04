"""
AutoRecoveryManager - 自動復旧マネージャー
Phase 3: エラー自動復旧システム
"""

import time
from enum import Enum
from typing import Dict, Any
from datetime import datetime

from tools.sheets_manager import GoogleSheetsManager


class RecoveryLevel(Enum):
    """復旧可能性のレベル"""

    IMMEDIATE = "immediate"  # 即座に復旧可能（再試行）
    FIXABLE = "fixable"  # 設定変更で復旧可能
    KNOWLEDGE = "knowledge"  # ナレッジベース活用で復旧
    HUMAN = "human"  # 人間の介入が必要


class AutoRecoveryManager:
    """エラー自動復旧マネージャー"""

    def __init__(self, sheets_manager: GoogleSheetsManager):
        """
        初期化

        Args:
            sheets_manager: GoogleSheetsManager インスタンス
        """
        self.sheets = sheets_manager

        # 復旧統計
        self.stats = {
            "total_errors": 0,
            "immediate_recoveries": 0,
            "fixable_recoveries": 0,
            "knowledge_recoveries": 0,
            "human_escalations": 0,
        }

    async def handle_error(
        self, task_id: str, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        エラーを分析して復旧を試みる

        Args:
            task_id: タスクID
            error: 発生したエラー
            context: エラーコンテキスト

        Returns:
            復旧結果の辞書
        """
        self.stats["total_errors"] += 1

        error_str = str(error).lower()
        error_type = type(error).__name__

        print(f"🔍 エラー分析中: {error_type}")

        # エラー分類と復旧レベルの決定
        recovery_level = self._classify_error(error_str, error_type)

        print(f"📊 復旧レベル: {recovery_level.value}")

        # 復旧レベルに応じた処理
        if recovery_level == RecoveryLevel.IMMEDIATE:
            self.stats["immediate_recoveries"] += 1
            return {
                "recovery_level": recovery_level,
                "action": "retry",
                "strategy": "exponential_backoff",
                "max_retries": 3,
            }

        elif recovery_level == RecoveryLevel.FIXABLE:
            self.stats["fixable_recoveries"] += 1
            fix_strategy = await self._generate_fix_strategy(error_str, error_type, context)
            return {
                "recovery_level": recovery_level,
                "action": "apply_fix",
                "fix_strategy": fix_strategy,
            }

        elif recovery_level == RecoveryLevel.KNOWLEDGE:
            self.stats["knowledge_recoveries"] += 1
            knowledge = await self._search_knowledge_base(error_str, error_type)
            return {
                "recovery_level": recovery_level,
                "action": "apply_knowledge",
                "knowledge": knowledge,
            }

        else:  # HUMAN
            self.stats["human_escalations"] += 1
            await self._escalate_to_human(task_id, error, context)
            return {
                "recovery_level": recovery_level,
                "action": "human_required",
                "escalation_id": f"escalation_{int(time.time())}",
            }

    def _classify_error(self, error_str: str, error_type: str) -> RecoveryLevel:
        """
        エラーを分類して復旧レベルを決定

        Args:
            error_str: エラーメッセージ（小文字）
            error_type: エラータイプ

        Returns:
            復旧レベル
        """
        # IMMEDIATE: ネットワーク系、一時的なエラー
        immediate_keywords = [
            "timeout",
            "timed out",
            "connection",
            "network",
            "rate limit",
            "too many requests",
            "retry",
        ]

        if any(kw in error_str for kw in immediate_keywords):
            return RecoveryLevel.IMMEDIATE

        # FIXABLE: 設定・認証系
        fixable_keywords = [
            "authentication",
            "auth",
            "credential",
            "permission",
            "not found",
            "404",
            "401",
            "403",
            "config",
        ]

        if any(kw in error_str for kw in fixable_keywords):
            return RecoveryLevel.FIXABLE

        # KNOWLEDGE: 既知のパターン
        knowledge_keywords = ["invalid", "unsupported", "deprecated", "format"]

        if any(kw in error_str for kw in knowledge_keywords):
            return RecoveryLevel.KNOWLEDGE

        # デフォルト: 人間介入
        return RecoveryLevel.HUMAN

    async def _generate_fix_strategy(
        self, error_str: str, error_type: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        修正戦略を生成

        Args:
            error_str: エラーメッセージ
            error_type: エラータイプ
            context: コンテキスト

        Returns:
            修正戦略
        """
        # 基本的な修正戦略
        strategy = {"type": "configuration_change", "changes": []}

        # 認証エラーの場合
        if "auth" in error_str or "credential" in error_str:
            strategy["changes"].append(
                {"action": "refresh_credentials", "target": "authentication"}
            )

        # Not Found エラーの場合
        if "not found" in error_str or "404" in error_str:
            strategy["changes"].append({"action": "verify_resource", "target": "resource_path"})

        return strategy

    async def _search_knowledge_base(self, error_str: str, error_type: str) -> Dict[str, Any]:
        """
        ナレッジベースから類似エラーの解決策を検索

        Args:
            error_str: エラーメッセージ
            error_type: エラータイプ

        Returns:
            ナレッジ情報
        """
        try:
            # knowledge_base シートから検索
            # 注: 実装は簡易版
            return {
                "found": False,
                "similar_cases": [],
                "recommended_action": "manual_investigation",
            }
        except Exception as e:
            print(f"⚠️ ナレッジベース検索エラー: {e}")
            return {"found": False, "error": str(e)}

    async def _escalate_to_human(self, task_id: str, error: Exception, context: Dict[str, Any]):
        """
        人間にエスカレーション

        Args:
            task_id: タスクID
            error: エラー
            context: コンテキスト
        """
        escalation_entry = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            task_id,
            "human_required",
            type(error).__name__,
            str(error)[:200],
            str(context)[:200],
        ]

        try:
            # human_escalations シートに記録
            self.sheets.append_rows("human_escalations", [escalation_entry])
            print(f"📮 人間へのエスカレーション記録完了: {task_id}")
        except Exception as e:
            print(f"⚠️ エスカレーション記録失敗: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        total = self.stats["total_errors"]
        if total == 0:
            return self.stats

        return {
            **self.stats,
            "immediate_rate": (self.stats["immediate_recoveries"] / total) * 100,
            "fixable_rate": (self.stats["fixable_recoveries"] / total) * 100,
            "knowledge_rate": (self.stats["knowledge_recoveries"] / total) * 100,
            "human_rate": (self.stats["human_escalations"] / total) * 100,
        }
