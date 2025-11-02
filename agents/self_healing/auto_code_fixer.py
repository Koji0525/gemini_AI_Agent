#!/usr/bin/env python3
"""
自動コード修正エージェント
エラーを検出し、修正コードを生成・適用
"""
import logging
from typing import Dict, Optional
import sys

sys.path.insert(0, ".")

from agents.self_healing.logging.knowledge_base_manager import KnowledgeBaseManager
from agents.self_healing.logging.decision_support_system import DecisionSupportSystem

logger = logging.getLogger(__name__)


class AutoCodeFixer:
    """エラーを検出し、修正コードを生成・適用"""

    def __init__(
        self, knowledge_base: KnowledgeBaseManager, decision_support: DecisionSupportSystem
    ):
        self.kb = knowledge_base
        self.dss = decision_support
        self.logger = logger

    async def fix_error(self, error: Exception, context: Dict) -> Dict:
        """
        エラー修正のメインフロー

        Args:
            error: 発生したエラー
            context: エラーコンテキスト

        Returns:
            修正結果
        """
        try:
            self.logger.info(f"🔧 自動修正開始: {type(error).__name__}")

            # 1. エラー分類
            error_type = type(error).__name__
            error_message = str(error)

            # 2. KnowledgeBaseから類似事例検索
            similar = self.kb.search_similar_knowledge(
                {"error_type": error_type, "error_message": error_message, "context": context},
                limit=3,
            )

            self.logger.info(f"📚 類似事例: {len(similar)}件発見")

            # 3. 修正戦略決定
            strategy = self.dss.decide_fix_strategy(
                {
                    "error_type": error_type,
                    "error_message": error_message,
                    "similar_cases": similar,
                    "context": context,
                }
            )

            self.logger.info(f"🎯 修正戦略: {strategy.get('strategy', 'unknown')}")

            # 4. 修正コード生成
            fix_code = await self.generate_fix_code(error, similar, strategy)

            if not fix_code:
                self.logger.warning("修正コード生成失敗")
                return {"success": False, "reason": "no_fix_generated"}

            # 5. 修正適用（現段階では提案のみ）
            result = await self.propose_fix(fix_code, context)

            # 6. 成功したらKnowledgeBaseに登録
            if result.get("success"):
                await self.save_fix_pattern(error, fix_code, context)

            return result

        except Exception as e:
            self.logger.error(f"❌ 自動修正エラー: {e}")
            return {"success": False, "error": str(e)}

    async def generate_fix_code(
        self, error: Exception, similar_cases: list, strategy: Dict
    ) -> Optional[str]:
        """
        修正コードを生成

        Returns:
            修正コード（文字列）またはNone
        """
        # 類似事例から修正コードを抽出
        for case in similar_cases:
            if case.get("knowledge_type") == "fix_recipe":
                fix_code = case.get("code_snippet")
                if fix_code:
                    self.logger.info("✅ 類似事例から修正コード取得")
                    return fix_code

        # 類似事例がない場合は、基本的な修正パターンを生成
        error_type = type(error).__name__

        if error_type == "ImportError":
            return "# インポートエラーの修正\n# pip install <missing_package>"

        elif error_type == "AttributeError":
            return "# 属性エラーの修正\n# オブジェクトの属性を確認"

        else:
            return f"# {error_type}の修正が必要\n# エラー詳細: {str(error)}"

    async def propose_fix(self, fix_code: str, context: Dict) -> Dict:
        """
        修正を提案（実際の適用は将来実装）

        Args:
            fix_code: 修正コード
            context: コンテキスト

        Returns:
            提案結果
        """
        self.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.logger.info("🔧 修正コード提案")
        self.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.logger.info(fix_code)
        self.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # TODO: 実際の修正適用ロジック
        # - ファイルの特定
        # - バックアップ作成
        # - 修正適用
        # - テスト実行

        return {
            "success": True,
            "fix_code": fix_code,
            "applied": False,  # 現段階では提案のみ
            "message": "修正コードを提案しました（自動適用は未実装）",
        }

    async def save_fix_pattern(self, error: Exception, fix_code: str, context: Dict) -> None:
        """
        修正パターンをKnowledgeBaseに保存
        """
        try:
            from agents.self_healing.logging.knowledge_base_manager import KnowledgePattern

            pattern = KnowledgePattern(
                knowledge_type="fix_recipe",
                pattern_description=f"{type(error).__name__}の修正",
                success_rate=1.0,
                related_errors=str(error),
                code_snippet=fix_code,
                context_summary=str(context),
            )

            await self.kb.save_pattern(pattern)
            self.logger.info("✅ 修正パターンをKnowledgeBaseに保存")

        except Exception as e:
            self.logger.error(f"修正パターン保存エラー: {e}")
