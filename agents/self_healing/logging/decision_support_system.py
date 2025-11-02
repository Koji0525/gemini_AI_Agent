"""
decision_support_system_v02.py

Phase 9: AI判断支援システム（改善版）

【変更理由】
初期化の依存関係を簡素化し、段階的な機能提供を可能に

【狙い】
- 信頼度スコアに基づく自動判断
- ナレッジベース検索結果から最適な修正戦略を決定
- fix/retry/escalate/ignoreの4つの戦略
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class DecisionSupportSystem:
    """
    AI判断支援システム

    ナレッジベース検索結果に基づき、最適な修正戦略を決定
    """

    def __init__(self, kb_manager=None, search_engine=None):
        """
        初期化

        Args:
            kb_manager: KnowledgeBaseManagerインスタンス（オプション）
            search_engine: SimilaritySearchEngineインスタンス（オプション）
        """
        self.kb_manager = kb_manager
        self.search_engine = search_engine

        # search_engineが未提供の場合は作成
        if not self.search_engine and kb_manager:
            try:
                from agents.self_healing.logging.similarity_search_engine_v02 import (
                    SimilaritySearchEngine,
                )

                self.search_engine = SimilaritySearchEngine(kb_manager)
                logger.info("✅ SimilaritySearchEngine自動作成")
            except Exception as e:
                logger.warning(f"⚠️ SimilaritySearchEngine作成失敗: {e}")

    def decide_fix_strategy(self, error_context: Dict) -> Dict:
        """
        修正戦略を決定

        Args:
            error_context: エラーコンテキスト
                - error_type: エラータイプ
                - error_message: エラーメッセージ
                - severity: 深刻度
                - retry_count: リトライ回数

        Returns:
            決定結果
                - strategy: 戦略（fix/retry/escalate/ignore）
                - confidence: 信頼度（0.0-1.0）
                - recommended_action: 推奨アクション
                - reasoning: 判断理由
                - auto_fix_code: 自動修正コード（オプション）
        """
        error_message = error_context.get("error_message", "")
        error_type = error_context.get("error_type", "Unknown")
        retry_count = error_context.get("retry_count", 0)
        severity = error_context.get("severity", "MEDIUM")

        logger.info(f"🤖 修正戦略決定: {error_type}")

        # デフォルト戦略
        decision = {
            "strategy": "retry",
            "confidence": 0.5,
            "recommended_action": "リトライを推奨",
            "reasoning": "デフォルト戦略",
            "auto_fix_code": None,
        }

        # ナレッジベース検索（利用可能な場合）
        if self.search_engine:
            try:
                similar_cases = self.search_engine.search_similar_knowledgees(
                    query=error_message, case_type="fix_recipe", limit=3
                )

                if similar_cases:
                    best_case = similar_cases[0]
                    confidence = best_case.get("confidence", 0.5)

                    logger.info(f"   📚 類似ケース発見: 信頼度 {confidence:.1%}")

                    # 高信頼度の場合は自動修正
                    if confidence > 0.7:
                        decision = {
                            "strategy": "fix",
                            "confidence": confidence,
                            "recommended_action": best_case.get(
                                "fix_description", "ナレッジベースから修正適用"
                            ),
                            "reasoning": f"ナレッジベースに高信頼度の修正レシピあり（{confidence:.1%}）",
                            "auto_fix_code": best_case.get("fix_code", None),
                        }
                    # 中程度の信頼度はリトライ
                    elif confidence > 0.4:
                        decision = {
                            "strategy": "retry",
                            "confidence": confidence,
                            "recommended_action": "リトライ後、修正適用を検討",
                            "reasoning": f"ナレッジベースに中信頼度のレシピあり（{confidence:.1%}）",
                            "auto_fix_code": None,
                        }
            except Exception as e:
                logger.warning(f"⚠️ ナレッジベース検索エラー: {e}")

        # リトライ回数による判断
        if retry_count >= 3:
            decision["strategy"] = "escalate"
            decision["recommended_action"] = "人間にエスカレーション"
            decision["reasoning"] = f"リトライ{retry_count}回失敗 - 人間の介入が必要"

        # 深刻度による判断
        if severity == "CRITICAL":
            decision["strategy"] = "escalate"
            decision["recommended_action"] = "即座に人間にエスカレーション"
            decision["reasoning"] = "クリティカルエラー - 即座対応必要"
        elif severity == "LOW":
            if retry_count > 1:
                decision["strategy"] = "ignore"
                decision["recommended_action"] = "エラーを無視して継続"
                decision["reasoning"] = "軽微なエラー - 影響小"

        logger.info(f"   戦略: {decision['strategy']}")
        logger.info(f"   信頼度: {decision['confidence']:.1%}")

        return decision
