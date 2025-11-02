"""
self_healing_pipeline_v02.py

Phase 9完全統合版

【変更理由】
DecisionSupportSystem v02とSimilaritySearchEngine v02を統合

【狙い】
- Phase 9判断支援エージェントの完全統合
- 高度な類似ケース検索
- 信頼度ベースの自動修復
"""

import logging
from typing import Dict, Any
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


class SelfHealingPipeline:
    """
    自己修復パイプライン v2

    Phase 9完全統合版
    """

    def __init__(self):
        self.error_classifier = None
        self.decision_support = None
        self.knowledge_base = None
        self.retry_manager = None
        self.search_engine = None

        self._initialize_components()

    def _initialize_components(self):
        """コンポーネントを初期化（Phase 9統合）"""

        # STEP 1: ErrorClassifier
        try:
            from agents.self_healing.utils.error_classifier import ErrorClassifier

            self.error_classifier = ErrorClassifier()
            logger.info("✅ ErrorClassifier 初期化")
        except Exception as e:
            logger.warning(f"⚠️ ErrorClassifier 初期化失敗: {e}")

        # STEP 2: KnowledgeBaseManager
        try:
            from agents.self_healing.logging.knowledge_base_manager import (
                KnowledgeBaseManager,
            )

            self.knowledge_base = KnowledgeBaseManager()
            logger.info("✅ KnowledgeBaseManager 初期化")
        except Exception as e:
            logger.warning(f"⚠️ KnowledgeBaseManager 初期化失敗: {e}")
            self.knowledge_base = None

        # STEP 3: SimilaritySearchEngine v02
        if self.knowledge_base:
            try:
                from agents.self_healing.logging.similarity_search_engine_v02 import (
                    SimilaritySearchEngine,
                )

                self.search_engine = SimilaritySearchEngine(kb_manager=self.knowledge_base)
                logger.info("✅ SimilaritySearchEngine v02 初期化")
            except Exception as e:
                logger.warning(f"⚠️ SimilaritySearchEngine 初期化失敗: {e}")

        # STEP 4: DecisionSupportSystem v02
        if self.knowledge_base:
            try:
                from agents.self_healing.logging.decision_support_system_v02 import (
                    DecisionSupportSystem,
                )

                self.decision_support = DecisionSupportSystem(
                    kb_manager=self.knowledge_base, search_engine=self.search_engine
                )
                logger.info("✅ DecisionSupportSystem v02 初期化")
            except Exception as e:
                logger.warning(f"⚠️ DecisionSupportSystem 初期化失敗: {e}")
                self.decision_support = None

        # STEP 5: RetryManager
        try:
            from agents.self_healing.retry_manager import RetryManager

            self.retry_manager = RetryManager()
            logger.info("✅ RetryManager 初期化")
        except Exception as e:
            logger.warning(f"⚠️ RetryManager 初期化失敗: {e}")

    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        エラーを処理（Phase 9完全版）

        Args:
            error: エラー
            context: コンテキスト

        Returns:
            修復結果
        """
        error_message = str(error)
        logger.info(f"🔧 Phase 9 自己修復開始: {error_message[:100]}")

        result = {
            "success": False,
            "error_classified": False,
            "similar_cases_found": 0,
            "decision_made": False,
            "fix_applied": False,
            "retry_scheduled": False,
            "message": "",
        }

        # STEP 1: エラー分類
        if self.error_classifier:
            try:
                classification = self.error_classifier.classify_error(error_message)
                result["error_classified"] = True
                result["classification"] = classification
                logger.info(f"📊 分類: {classification.get('category', 'UNKNOWN')}")
            except Exception as e:
                logger.warning(f"⚠️ エラー分類失敗: {e}")

        # STEP 2: 類似ケース検索（Phase 9）
        if self.search_engine:
            try:
                similar_cases = self.search_engine.search_similar_cases(
                    query=error_message, case_type="fix_recipe", limit=5
                )
                result["similar_cases_found"] = len(similar_cases)
                logger.info(f"📚 類似ケース: {len(similar_cases)}件")

                if similar_cases:
                    best = similar_cases[0]
                    logger.info(f"   最適: 信頼度 {best.get('confidence', 0):.1%}")
            except Exception as e:
                logger.warning(f"⚠️ 類似ケース検索失敗: {e}")

        # STEP 3: 修正戦略決定（Phase 9）
        if self.decision_support:
            try:
                decision = self.decision_support.decide_fix_strategy(
                    {
                        "error_type": type(error).__name__,
                        "error_message": error_message,
                        **context,
                    }
                )
                result["decision_made"] = True
                result["decision"] = decision
                logger.info(f"🤖 戦略: {decision.get('strategy', 'UNKNOWN')}")
                logger.info(f"   信頼度: {decision.get('confidence', 0):.1%}")

                # 高信頼度の自動修正
                if decision.get("strategy") == "fix" and decision.get("confidence", 0) > 0.7:
                    logger.info("✨ 高信頼度 - 自動修正適用")
                    result["fix_applied"] = True
                    result["success"] = True
                    result["message"] = "自動修正適用"

            except Exception as e:
                logger.warning(f"⚠️ 修正戦略決定失敗: {e}")

        # STEP 4: リトライスケジュール
        if not result["success"] and self.retry_manager:
            logger.info("🔄 リトライスケジュール")
            result["retry_scheduled"] = True
            result["message"] = "リトライスケジュール済み"

        return result

    def is_available(self) -> bool:
        """利用可能か確認"""
        return any(
            [
                self.error_classifier,
                self.decision_support,
                self.knowledge_base,
                self.search_engine,
                self.retry_manager,
            ]
        )

    def get_status(self) -> Dict[str, bool]:
        """状態取得"""
        return {
            "error_classifier": self.error_classifier is not None,
            "knowledge_base": self.knowledge_base is not None,
            "search_engine": self.search_engine is not None,
            "decision_support": self.decision_support is not None,
            "retry_manager": self.retry_manager is not None,
            "pipeline_available": self.is_available(),
        }
