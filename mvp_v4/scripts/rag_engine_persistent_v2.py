"""
永続化RAGエンジン v2 - 超高速安定版
"""

import os
import time
import json
import uuid
from chromadb import PersistentClient
import hashlib


class PersistentRAGEngineV2:
    def __init__(self, knowledge_paths=None, cache_dir="mvp_v4/.cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

        # 高速起動のための軽量初期化
        self._fast_initialize(knowledge_paths)

    def _fast_initialize(self, knowledge_paths):
        """超高速初期化 - モデルロードを完全分離"""
        start_time = time.time()

        # ChromaDBクライアント（永続化）
        chroma_path = os.path.join(self.cache_dir, "chroma_db_v2")
        self.client = PersistentClient(path=chroma_path)

        # コレクション名
        self.collection_name = "knowledge_base_v2"

        # コレクション取得（既存なら即時利用）
        try:
            self.collection = self.client.get_collection(self.collection_name)
            print(f"⚡ RAG v2瞬時起動: {time.time() - start_time:.3f}秒")
        except:
            # 新規コレクション作成
            self.collection = self.client.create_collection(self.collection_name)
            if knowledge_paths:
                self._load_knowledge_batch(knowledge_paths)
            print(f"🔄 RAG v2新規初期化: {time.time() - start_time:.2f}秒")

        # モデルは検索時までロードしない
        self.model = None

    def _load_knowledge_batch(self, knowledge_paths):
        """バッチ処理でナレッジ読み込み"""
        from sentence_transformers import SentenceTransformer

        all_documents = []
        all_metadatas = []
        all_ids = []
        used_ids = set()

        print("�� ナレッジバッチ処理開始...")

        for path in knowledge_paths:
            if not os.path.exists(path):
                continue

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for kb in data.get("knowledge_base", []):
                text_parts = []
                if kb.get("scenario"):
                    text_parts.append(f"シナリオ: {kb['scenario']}")
                if kb.get("best_practice"):
                    text_parts.append(f"解決策: {kb['best_practice']}")

                if text_parts:
                    document = " ".join(text_parts)
                    all_documents.append(document)
                    all_metadatas.append(
                        {
                            "scenario": kb.get("scenario", ""),
                            "success_rate": kb.get("success_rate", 0),
                            "source": os.path.basename(path),
                        }
                    )

                    # 重複しないID生成
                    original_id = kb.get("id", str(uuid.uuid4()))
                    new_id = original_id
                    counter = 1
                    while new_id in used_ids:
                        new_id = f"{original_id}_{counter}"
                        counter += 1
                    used_ids.add(new_id)
                    all_ids.append(new_id)

        if all_documents:
            # モデルロードとベクトル化
            model = SentenceTransformer("all-MiniLM-L6-v2")
            embeddings = model.encode(all_documents).tolist()

            # バッチ追加
            self.collection.add(
                embeddings=embeddings, documents=all_documents, metadatas=all_metadatas, ids=all_ids
            )
            print(f"✅ {len(all_documents)}件のナレッジを追加完了")

    def search(self, query, top_k=3):
        """検索実行（必要時にモデルロード）"""
        if not self.collection:
            return []

        # 必要ならモデルをロード
        if self.model is None:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # 検索実行
        query_embedding = self.model.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            include=["metadatas", "documents", "distances"],
        )

        # 結果整形
        formatted_results = []
        if results["metadatas"]:
            for i, (metadata, document, distance) in enumerate(
                zip(results["metadatas"][0], results["documents"][0], results["distances"][0])
            ):
                formatted_results.append(
                    {
                        "scenario": metadata.get("scenario", ""),
                        "best_practice": document,
                        "success_rate": metadata.get("success_rate", 0),
                        "distance": distance,
                        "rank": i + 1,
                    }
                )

        return formatted_results

    def get_stats(self):
        """統計情報"""
        if not self.collection:
            return {"count": 0}

        count = self.collection.count()
        return {"count": count, "model_loaded": self.model is not None}


# グローバルインスタンス
_global_rag_engine_v2 = None


def get_rag_engine_v2(knowledge_paths=None):
    global _global_rag_engine_v2
    if _global_rag_engine_v2 is None:
        _global_rag_engine_v2 = PersistentRAGEngineV2(knowledge_paths)
    return _global_rag_engine_v2


if __name__ == "__main__":
    start = time.time()
    rag = get_rag_engine_v2(["mvp_v4/knowledge/learned/conversation_knowledge_v3.json"])
    stats = rag.get_stats()
    print(f"📊 ナレッジ件数: {stats['count']}")

    # 検索テスト
    results = rag.search("ModuleNotFoundError", top_k=2)
    for r in results:
        print(f"- {r['scenario']}")

    print(f"⏱️ 総処理時間: {time.time() - start:.2f}秒")
