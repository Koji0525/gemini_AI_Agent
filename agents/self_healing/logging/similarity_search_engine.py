#!/usr/bin/env python3
"""
SimilaritySearchEngine: 高度な類似ケース検索エンジン

TF-IDFと複数の類似度指標を組み合わせた、
意味的類似度を考慮した検索システム。
"""
from typing import Dict, Any, List, Tuple, Optional
import json
from collections import Counter
import math
from datetime import datetime


class SimilaritySearchEngine:
    """類似ケース検索エンジン"""

    def __init__(self, kb_manager):
        """
        初期化

        Args:
            kb_manager: KnowledgeBaseManagerインスタンス
        """
        self.kb_manager = kb_manager

        # TF-IDF用のドキュメント頻度キャッシュ
        self._document_frequencies = {}
        self._total_documents = 0

        print("✅ SimilaritySearchEngine初期化完了")

    def _tokenize(self, text: str) -> List[str]:
        """
        テキストをトークン化

        Args:
            text: 入力テキスト

        Returns:
            トークンのリスト
        """
        if not text:
            return []

        # 簡易的なトークン化（実際はMeCabなど使用可能）
        text = text.lower()

        # 記号を除去
        for char in ".,!?;:()[]{}「」、。！？":
            text = text.replace(char, " ")

        # 分割
        tokens = text.split()

        return [t for t in tokens if len(t) > 1]  # 1文字のトークンは除外

    def _calculate_tf(self, tokens: List[str]) -> Dict[str, float]:
        """
        TF (Term Frequency) を計算

        Args:
            tokens: トークンのリスト

        Returns:
            TFの辞書
        """
        if not tokens:
            return {}

        counter = Counter(tokens)
        total = len(tokens)

        return {term: count / total for term, count in counter.items()}

    def _calculate_idf(self, term: str) -> float:
        """
        IDF (Inverse Document Frequency) を計算

        Args:
            term: 単語

        Returns:
            IDF値
        """
        if self._total_documents == 0:
            return 0.0

        doc_freq = self._document_frequencies.get(term, 0)

        if doc_freq == 0:
            return 0.0

        return math.log(self._total_documents / doc_freq)

    def _build_tfidf_index(self, documents: List[Dict[str, Any]]):
        """
        TF-IDFインデックスを構築

        Args:
            documents: ドキュメントのリスト
        """
        self._total_documents = len(documents)
        self._document_frequencies = {}

        # 各ドキュメントからトークンを抽出
        for doc in documents:
            # 説明文からトークン抽出
            description = doc.get("pattern_description", "")
            tokens = set(self._tokenize(description))

            # ドキュメント頻度をカウント
            for token in tokens:
                self._document_frequencies[token] = self._document_frequencies.get(token, 0) + 1

    def _calculate_tfidf_vector(self, text: str) -> Dict[str, float]:
        """
        TF-IDFベクトルを計算

        Args:
            text: テキスト

        Returns:
            TF-IDFベクトル
        """
        tokens = self._tokenize(text)
        tf = self._calculate_tf(tokens)

        tfidf = {}
        for term, tf_value in tf.items():
            idf_value = self._calculate_idf(term)
            tfidf[term] = tf_value * idf_value

        return tfidf

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """
        コサイン類似度を計算

        Args:
            vec1: ベクトル1
            vec2: ベクトル2

        Returns:
            コサイン類似度 (0.0 ~ 1.0)
        """
        # 共通する単語
        common_terms = set(vec1.keys()) & set(vec2.keys())

        if not common_terms:
            return 0.0

        # 内積
        dot_product = sum(vec1[term] * vec2[term] for term in common_terms)

        # ノルム
        norm1 = math.sqrt(sum(v**2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v**2 for v in vec2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _calculate_metadata_similarity(self, query: Dict[str, Any], document: Dict[str, Any]) -> float:
        """
        メタデータベースの類似度を計算

        Args:
            query: クエリ
            document: ドキュメント

        Returns:
            類似度 (0.0 ~ 1.0)
        """
        score = 0.0
        factors = 0

        # 1. エラータイプの一致（重要度: 高）
        if query.get("error_type"):
            try:
                related_errors = json.loads(document.get("related_errors", "[]"))
                if query["error_type"] in related_errors:
                    score += 0.5
            except:
                pass
            factors += 1

        # 2. タスクタイプの一致（重要度: 中）
        if query.get("task_type"):
            try:
                context = json.loads(document.get("context", "{}"))
                if query["task_type"] == context.get("task_type"):
                    score += 0.3
            except:
                pass
            factors += 1

        # 3. ナレッジタイプの一致（重要度: 低）
        if query.get("knowledge_type"):
            if query["knowledge_type"] == document.get("knowledge_type"):
                score += 0.1
            factors += 1

        # 4. 学習タグの重複（重要度: 中）
        if query.get("tags"):
            query_tags = set(query["tags"])
            doc_tags = set(document.get("learning_tags", "").split(","))

            if query_tags and doc_tags:
                overlap = len(query_tags & doc_tags)
                union = len(query_tags | doc_tags)
                if union > 0:
                    score += (overlap / union) * 0.3
            factors += 1

        return score / factors if factors > 0 else 0.0

    def _calculate_effectiveness_score(self, document: Dict[str, Any]) -> float:
        """
        有効性スコアを正規化

        Args:
            document: ドキュメント

        Returns:
            正規化された有効性スコア (0.0 ~ 1.0)
        """
        try:
            effectiveness = float(document.get("effectiveness_score", 0))
            return effectiveness / 100.0  # 0-100 を 0.0-1.0 に正規化
        except (ValueError, TypeError):
            return 0.0

    def _calculate_recency_score(self, document: Dict[str, Any]) -> float:
        """
        新しさスコアを計算

        Args:
            document: ドキュメント

        Returns:
            新しさスコア (0.0 ~ 1.0)
        """
        try:
            timestamp_str = document.get("timestamp", "")
            if not timestamp_str:
                return 0.5  # 不明な場合は中立

            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()

            # 日数差を計算
            days_diff = (now - timestamp).days

            # 30日以内なら1.0、それ以降は徐々に減衰
            if days_diff <= 0:
                return 1.0
            elif days_diff <= 30:
                return 1.0 - (days_diff / 30) * 0.3  # 0.7 ~ 1.0
            elif days_diff <= 90:
                return 0.7 - ((days_diff - 30) / 60) * 0.3  # 0.4 ~ 0.7
            else:
                return 0.4 - min((days_diff - 90) / 365, 0.4)  # 0.0 ~ 0.4

        except:
            return 0.5

    def search(
        self, query: Dict[str, Any], limit: int = 5, min_score: float = 0.1
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        類似ケースを検索

        Args:
            query: 検索クエリ
                - text: 検索テキスト（description用）
                - error_type: エラータイプ
                - task_type: タスクタイプ
                - knowledge_type: ナレッジタイプ
                - tags: タグのリスト
            limit: 返す結果の最大数
            min_score: 最小スコア閾値

        Returns:
            (ドキュメント, スコア) のタプルリスト
        """
        print(f"\n🔍 類似ケース検索開始")
        print(f"   クエリ: {query}")

        # ナレッジベースから全ドキュメント取得
        try:
            sheet = self.kb_manager._get_sheet(self.kb_manager.KB_SHEET)
            if not sheet:
                print("   ⚠️ knowledge_baseシート取得失敗")
                return []

            documents = sheet.get_all_records()

            if not documents:
                print("   ⚠️ ナレッジが見つかりません")
                return []

            print(f"   📊 検索対象: {len(documents)}件")

        except Exception as e:
            print(f"   ❌ ドキュメント取得エラー: {e}")
            return []

        # TF-IDFインデックス構築
        self._build_tfidf_index(documents)

        # クエリのTF-IDFベクトル計算
        query_text = query.get("text", "")
        query_vector = self._calculate_tfidf_vector(query_text)

        # 各ドキュメントとの類似度を計算
        scored_docs = []

        for doc in documents:
            # 1. テキスト類似度（TF-IDF + コサイン類似度）
            doc_text = doc.get("pattern_description", "")
            doc_vector = self._calculate_tfidf_vector(doc_text)
            text_similarity = self._cosine_similarity(query_vector, doc_vector)

            # 2. メタデータ類似度
            metadata_similarity = self._calculate_metadata_similarity(query, doc)

            # 3. 有効性スコア
            effectiveness = self._calculate_effectiveness_score(doc)

            # 4. 新しさスコア
            recency = self._calculate_recency_score(doc)

            # 総合スコア計算（重み付け平均）
            total_score = (
                text_similarity * 0.3  # テキスト類似度: 30%
                + metadata_similarity * 0.4  # メタデータ: 40%
                + effectiveness * 0.2  # 有効性: 20%
                + recency * 0.1  # 新しさ: 10%
            )

            if total_score >= min_score:
                scored_docs.append((doc, total_score))

        # スコア順にソート
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # 上位N件を返す
        results = scored_docs[:limit]

        print(f"   ✅ {len(results)}件の類似ケースを発見")
        for i, (doc, score) in enumerate(results, 1):
            print(f"      {i}. {doc.get('pattern_description', 'N/A')[:50]}... (スコア: {score:.3f})")

        return results

    def explain_similarity(self, query: Dict[str, Any], document: Dict[str, Any]) -> Dict[str, Any]:
        """
        類似度の説明を生成

        Args:
            query: クエリ
            document: ドキュメント

        Returns:
            類似度の詳細説明
        """
        # 各要素のスコアを計算
        query_text = query.get("text", "")
        doc_text = document.get("pattern_description", "")

        self._build_tfidf_index([document])
        query_vector = self._calculate_tfidf_vector(query_text)
        doc_vector = self._calculate_tfidf_vector(doc_text)

        text_sim = self._cosine_similarity(query_vector, doc_vector)
        metadata_sim = self._calculate_metadata_similarity(query, document)
        effectiveness = self._calculate_effectiveness_score(document)
        recency = self._calculate_recency_score(document)

        total = text_sim * 0.3 + metadata_sim * 0.4 + effectiveness * 0.2 + recency * 0.1

        return {
            "total_score": total,
            "breakdown": {
                "text_similarity": {"score": text_sim, "weight": 0.3, "contribution": text_sim * 0.3},
                "metadata_similarity": {"score": metadata_sim, "weight": 0.4, "contribution": metadata_sim * 0.4},
                "effectiveness": {"score": effectiveness, "weight": 0.2, "contribution": effectiveness * 0.2},
                "recency": {"score": recency, "weight": 0.1, "contribution": recency * 0.1},
            },
        }
