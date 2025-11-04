"""
高速起動版RAGエンジン（重複ID対応版）
"""

import chromadb
import json
import os
from sentence_transformers import SentenceTransformer


class FastRAGEngine:
    """高速起動版RAGエンジン（修正版）"""

    def __init__(self, persist_dir="mvp_v4/chroma_persist"):
        print("🔧 高速版RAGエンジン初期化中...")

        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        # ChromaDBクライアント（永続化）
        self.client = chromadb.PersistentClient(path=persist_dir)

        # コレクション取得または作成
        try:
            self.collection = self.client.get_collection("knowledge_base")
            print("✅ 既存データベースを読み込みました（高速起動）")
        except:
            self.collection = self.client.create_collection(
                name="knowledge_base", metadata={"hnsw:space": "cosine"}
            )
            print("📊 新規データベース作成")

        # 埋め込みモデル（キャッシュから読み込み）
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        print("✅ 埋め込みモデル読み込み完了")

    def load_knowledge(self, json_file="mvp_v4/knowledge/learned/conversation_knowledge_v3.json"):
        """ナレッジ読み込み（重複対応版）"""

        with open(json_file, "r") as f:
            data = json.load(f)

        kb_list = data["knowledge_base"]

        # 既存IDを取得
        existing_ids = set()
        try:
            existing = self.collection.get()
            existing_ids = set(existing["ids"])
        except:
            pass

        # ユニークIDのみ抽出（重複を除外）
        seen_ids = set()
        unique_kb = []
        for kb in kb_list:
            kb_id = kb.get("id")
            if kb_id not in existing_ids and kb_id not in seen_ids:
                unique_kb.append(kb)
                seen_ids.add(kb_id)

        if unique_kb:
            print(f"📂 新規ナレッジ: {len(unique_kb)}件を追加中...")

            # バッチ処理で追加
            batch_size = 10
            for i in range(0, len(unique_kb), batch_size):
                batch = unique_kb[i : i + batch_size]

                ids = []
                embeddings = []
                metadatas = []
                documents = []

                for kb in batch:
                    text = f"{kb.get('scenario', '')} {kb.get('best_practice', '')}"
                    vector = self.model.encode(text).tolist()

                    ids.append(kb["id"])
                    embeddings.append(vector)
                    metadatas.append(kb)
                    documents.append(text)

                self.collection.add(
                    ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents
                )

            print(f"✅ {len(unique_kb)}件追加完了")
        else:
            total = len(existing_ids)
            print(f"✅ 全{total}件（更新なし）")

        print("✅ RAGシステム準備完了")

    def search(self, query, top_k=3):
        """検索"""
        query_vector = self.model.encode(query).tolist()

        results = self.collection.query(query_embeddings=[query_vector], n_results=top_k)

        output = []
        for i in range(len(results["ids"][0])):
            output.append(
                {
                    "knowledge_id": results["ids"][0][i],
                    "scenario": results["metadatas"][0][i].get("scenario", ""),
                    "similarity_score": 1 - results["distances"][0][i],
                    "metadata": results["metadatas"][0][i],
                }
            )

        return output


if __name__ == "__main__":
    import time

    print("\n" + "=" * 70)
    print("⏱️ 高速版起動テスト（修正版）")
    print("=" * 70)

    start = time.time()

    rag = FastRAGEngine()
    rag.load_knowledge()

    elapsed = time.time() - start

    print("\n" + "=" * 70)
    print(f"⏱️ 起動時間: {elapsed:.2f}秒")
    print("=" * 70)

    # 検索テスト
    print("\n🔍 検索テスト:")
    results = rag.search("heredoc", top_k=1)
    if results:
        print(f"  ✅ {results[0]['scenario']}")
