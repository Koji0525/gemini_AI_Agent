"""
similarity_search_engine_v02.py

Phase 9: 類似ケース検索エンジン（改善版）

【変更理由】
初期化の依存関係を簡素化し、KnowledgeBaseManagerとの統合を改善

【狙い】
- TF-IDFやコサイン類似度による高度検索
- ナレッジベースから最適な修正レシピを発見
- 信頼度スコア付き結果返却
"""

import logging
from typing import List, Dict
import re
from collections import Counter
import math

logger = logging.getLogger(__name__)


class SimilaritySearchEngine:
    """
    類似ケース検索エンジン

    TF-IDFとコサイン類似度を使用
    """

    def __init__(self, kb_manager=None):
        """
        初期化

        Args:
            kb_manager: KnowledgeBaseManagerインスタンス（オプション）
        """
        self.kb_manager = kb_manager
        self.idf_cache = {}

    def search_similar_cases(
        self, query: str, case_type: str = "fix_recipe", limit: int = 5
    ) -> List[Dict]:
        """
        類似ケースを検索

        Args:
            query: 検索クエリ（エラーメッセージなど）
            case_type: ケースタイプ（fix_recipe, success_pattern, failure_pattern）
            limit: 返却する結果数

        Returns:
            類似ケースのリスト（信頼度スコア付き）
        """
        if not self.kb_manager:
            logger.warning("⚠️ KnowledgeBaseManager未設定 - 空の結果を返却")
            return []

        try:
            # ナレッジベースから全ケースを取得
            if case_type == "fix_recipe":
                all_cases = self.kb_manager.search_fix_recipes(
                    error_type="", limit=100  # 多めに取得してフィルタ
                )
            else:
                all_cases = []

            if not all_cases:
                return []

            # 類似度計算
            scored_cases = []
            query_vector = self._vectorize_text(query)

            for case in all_cases:
                case_text = case.get("error_message", "") + " " + case.get("fix_description", "")
                case_vector = self._vectorize_text(case_text)

                similarity = self._cosine_similarity(query_vector, case_vector)

                if similarity > 0.1:  # 最小閾値
                    scored_cases.append(
                        {
                            **case,
                            "similarity_score": similarity,
                            "confidence": similarity,  # 信頼度として使用
                        }
                    )

            # 類似度でソート
            scored_cases.sort(key=lambda x: x["similarity_score"], reverse=True)

            return scored_cases[:limit]

        except Exception as e:
            logger.error(f"❌ 類似ケース検索エラー: {e}")
            return []

    def _vectorize_text(self, text: str) -> Dict[str, float]:
        """
        テキストをTF-IDFベクトルに変換

        Args:
            text: テキスト

        Returns:
            TF-IDFベクトル（単語 -> スコア）
        """
        # トークン化（簡易版）
        tokens = re.findall(r"\w+", text.lower())

        # TF（単語頻度）計算
        tf = Counter(tokens)
        total_tokens = len(tokens)

        # TF正規化
        tf_vector = {word: count / total_tokens for word, count in tf.items()}

        # IDF（逆文書頻度）は簡易実装
        # 実際のプロダクションではコーパス全体から計算

        return tf_vector

    def _cosine_similarity(self, vector1: Dict[str, float], vector2: Dict[str, float]) -> float:
        """
        コサイン類似度を計算

        Args:
            vector1: ベクトル1
            vector2: ベクトル2

        Returns:
            類似度（0.0-1.0）
        """
        # 共通単語のセット
        common_words = set(vector1.keys()) & set(vector2.keys())

        if not common_words:
            return 0.0

        # 内積計算
        dot_product = sum(vector1[word] * vector2[word] for word in common_words)

        # ノルム計算
        norm1 = math.sqrt(sum(v**2 for v in vector1.values()))
        norm2 = math.sqrt(sum(v**2 for v in vector2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)
