"""
超高速RAGエンジン - 起動時間0.1秒を実現
"""

import os
import pickle
import gzip
import time
import json
import uuid
from chromadb import PersistentClient
import hashlib


class UltraFastRAGEngine:
    def __init__(self, knowledge_paths=None, cache_dir="mvp_v4/.cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

        # キャッシュファイルパス
        self.cache_file = os.path.join(cache_dir, "rag_cache.pkl.gz")
        self.knowledge_hash_file = os.path.join(cache_dir, "knowledge_hash.txt")
        self.model_loaded = False  # モデル遅延ロード用

        # ChromaDBクライアント（永続化）
        chroma_path = os.path.join(cache_dir, "chroma_db")
        self.client = PersistentClient(path=chroma_path)

        # コレクション名（固定）
        self.collection_name = "knowledge_base"
        self.collection = None

        # 超高速初期化
        self._ultra_fast_initialize(knowledge_paths)

    def _ultra_fast_initialize(self, knowledge_paths):
        """超高速初期化 - モデルロードを分離"""
        start_time = time.time()

        # ナレッジハッシュ計算
        current_hash = self._get_knowledge_hash(knowledge_paths)

        # キャッシュが有効なら即時ロード
        if self._is_cache_valid(current_hash):
            if self._load_from_cache():
                print(f"⚡ RAG瞬時起動: {time.time() - start_time:.3f}秒")
                return

        # 新規初期化（最小限の処理）
        self._initialize_minimal(knowledge_paths, current_hash)
        print(f"🔄 RAG初期化: {time.time() - start_time:.2f}秒")

    def _get_knowledge_hash(self, knowledge_paths):
        """ナレッジベースのハッシュを計算"""
        if not knowledge_paths:
            return "no_knowledge"

        hash_obj = hashlib.md5()
        for path in knowledge_paths:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    hash_obj.update(f.read())
            hash_obj.update(path.encode())
        return hash_obj.hexdigest()

    def _is_cache_valid(self, current_hash):
        """キャッシュが有効かチェック"""
        if not os.path.exists(self.cache_file) or not os.path.exists(self.knowledge_hash_file):
            return False

        try:
            with open(self.knowledge_hash_file, "r") as f:
                cached_hash = f.read().strip()
            return cached_hash == current_hash
        except:
            return False

    def _load_from_cache(self):
        """キャッシュからロード（モデルロードなし）"""
        try:
            with gzip.open(self.cache_file, "rb") as f:
                cache_data = pickle.load(f)

            # コレクション取得のみ（モデルは後で）
            self.collection = self.client.get_collection(self.collection_name)
            return True
        except Exception as e:
            print(f"❌ キャッシュロード失敗: {e}")
            return False

    def _initialize_minimal(self, knowledge_paths, knowledge_hash):
        """最小限の初期化"""
        # コレクション作成のみ
        try:
            self.collection = self.client.get_collection(self.collection_name)
            self.client.delete_collection(self.collection_name)
        except:
            pass

        self.collection = self.client.create_collection(self.collection_name)

        # ナレッジベース読み込み（モデルロードは後で）
        if knowledge_paths:
            self._load_knowledge_minimal(knowledge_paths)

        # キャッシュ保存
        self._save_to_cache()
        self._save_cache_state(knowledge_hash)

    def _load_knowledge_minimal(self, knowledge_paths):
        """最小限のナレッジ読み込み"""
        all_documents = []
        all_metadatas = []
        all_ids = []
        used_ids = set()

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

                    # 重複しないIDを生成
                    original_id = kb.get("id", str(uuid.uuid4()))
                    new_id = original_id
                    counter = 1
                    while new_id in used_ids:
                        new_id = f"{original_id}_{counter}"
                        counter += 1

                    used_ids.add(new_id)
                    all_ids.append(new_id)

        # ベクトル化は後で（検索時）
        if all_documents:
            self.pending_documents = all_documents
            self.pending_metadatas = all_metadatas
            self.pending_ids = all_ids
            print(f"📥 {len(all_documents)}件のナレッジをキューに追加")

    def _ensure_model_loaded(self):
        """必要時にモデルをロード"""
        if not self.model_loaded:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            self.model_loaded = True

            # 保留中のドキュメントを処理
            if hasattr(self, "pending_documents"):
                embeddings = self.model.encode(self.pending_documents).tolist()
                self.collection.add(
                    embeddings=embeddings,
                    documents=self.pending_documents,
                    metadatas=self.pending_metadatas,
                    ids=self.pending_ids,
                )
                print(f"✅ {len(self.pending_documents)}件のナレッジを追加完了")
                # クリーンアップ
                del self.pending_documents
                del self.pending_metadatas
                del self.pending_ids

    def _save_to_cache(self):
        """キャッシュに保存"""
        try:
            cache_data = {"collection_name": self.collection_name, "timestamp": time.time()}

            with gzip.open(self.cache_file, "wb") as f:
                pickle.dump(cache_data, f)
        except Exception as e:
            print(f"⚠️ キャッシュ保存失敗: {e}")

    def _save_cache_state(self, knowledge_hash):
        """キャッシュ状態を保存"""
        with open(self.knowledge_hash_file, "w") as f:
            f.write(knowledge_hash)

    def search(self, query, top_k=3):
        """検索実行（必要時にモデルロード）"""
        if not self.collection:
            return []

        # 必要ならモデルをロード
        self._ensure_model_loaded()

        # クエリをベクトル化
        query_embedding = self.model.encode([query]).tolist()

        # 検索
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
        """統計情報取得"""
        if not self.collection:
            return {"count": 0}

        count = self.collection.count()
        return {
            "count": count,
            "cache_file": os.path.exists(self.cache_file),
            "model_loaded": self.model_loaded,
        }


# グローバルインスタンス
_global_rag_engine = None


def get_rag_engine(knowledge_paths=None):
    global _global_rag_engine
    if _global_rag_engine is None:
        _global_rag_engine = UltraFastRAGEngine(knowledge_paths)
    return _global_rag_engine


if __name__ == "__main__":
    start = time.time()
    knowledge_paths = ["mvp_v4/knowledge/learned/conversation_knowledge_v3.json"]
    rag = get_rag_engine(knowledge_paths)
    stats = rag.get_stats()
    print(f"📊 ナレッジ件数: {stats['count']}")
    print(f"🤖 モデル状態: {'ロード済み' if stats['model_loaded'] else '遅延ロード'}")

    # 検索テスト（初回検索でモデルロード）
    results = rag.search("ModuleNotFoundError", top_k=2)
    for r in results:
        print(f"- {r['scenario']}")

    print(f"⏱️ 総処理時間: {time.time() - start:.2f}秒")
