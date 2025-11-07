"""
Frugal RAGエンジン v4.0 (完全ローカル版)
ChromaDB + LlamaIndexによる軽量RAGシステム

【変更履歴】
- v1: 初版（OpenAI依存）
- v2: LlamaIndex v0.10+対応
- v3 (local): 完全ローカル動作（OpenAI不要）

【Frugal AI戦略】
- コスト: $0（完全無料）
- 依存: なし（外部API不要）
- 速度: 高速（ネットワーク遅延なし）
"""

import json
import os
from typing import List, Dict
import chromadb

from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


class FrugalRAGEngine:
    """完全ローカル動作のRAGエンジン"""

    def __init__(self, persist_dir: str = "mvp_v4/models/chroma_db"):
        """
        初期化

        【変更理由】
        何が起きた: 完全ローカル動作のRAGシステム
        原因: 外部API依存を排除する必要
        狙い: $0コストでの運用を実現
        """
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        print("🔧 完全ローカル版RAGエンジン初期化中...")
        print("   - コスト: $0")
        print("   - API依存: なし")
        print("   - 動作: 完全ローカル")

        # ChromaDBクライアント初期化
        self.chroma_client = chromadb.PersistentClient(path=persist_dir)

        # コレクション作成（または取得）
        try:
            self.collection = self.chroma_client.get_collection("knowledge_base")
            print("✅ 既存のコレクションを読み込みました")
        except:
            self.collection = self.chroma_client.create_collection("knowledge_base")
            print("✅ 新規コレクションを作成しました")

        # Embedding設定（完全ローカル）
        self.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        print("✅ ローカル埋め込みモデル読み込み完了")

        # Vector Store設定
        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        # インデックス
        self.index = None

    def load_knowledge(self, knowledge_files: List[str]):
        """
        ナレッジファイルを読み込んでインデックス化

        【変更理由】
        何が起きた: JSONからベクトルDBへの変換
        原因: 構造化データを検索可能にする必要
        狙い: 類似度ベースの高速検索を実現
        """
        documents = []

        for file_path in knowledge_files:
            print(f"📂 読み込み中: {file_path}")

            if not os.path.exists(file_path):
                print(f"⚠️ ファイルが見つかりません: {file_path}")
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for kb in data.get("knowledge_base", []):
                # ドキュメント化
                text = f"""
                タスクタイプ: {kb.get('task_type', '')}
                シナリオ: {kb.get('scenario', '')}
                ベストプラクティス: {kb.get('best_practice', '')}
                コード例: {kb.get('code_example', '')}
                成功率: {kb.get('success_rate', 0)}
                平均実行時間: {kb.get('avg_execution_time', 0)}秒
                前提条件: {', '.join(kb.get('conditions', []))}
                避けるべきパターン: {', '.join(kb.get('avoid_patterns', []))}
                """

                doc = Document(
                    text=text.strip(),
                    metadata={
                        "knowledge_id": kb.get("id"),
                        "task_type": kb.get("task_type"),
                        "success_rate": kb.get("success_rate", 0),
                        "scenario": kb.get("scenario", ""),
                    },
                )
                documents.append(doc)

        if not documents:
            print("⚠️ ナレッジが読み込めませんでした")
            return

        print(f"📊 ナレッジ件数: {len(documents)}件")

        # インデックス作成
        print("🔨 インデックス構築中...")
        self.index = VectorStoreIndex.from_documents(
            documents, storage_context=self.storage_context, embed_model=self.embed_model
        )

        print("✅ RAGシステム構築完了（完全ローカル動作）")

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        ナレッジ検索（完全ローカル）

        【変更理由】
        何が起きた: as_query_engine()からas_retriever()に変更
        原因: query_engineはLLM（OpenAI）を必要とする
        狙い: ベクトル検索のみで完全ローカル動作
              → $0コスト、API不要
        """
        if not self.index:
            print("⚠️ インデックスが構築されていません")
            return []

        # ✅ 修正: query_engineではなくretrieverを使用
        # これによりLLM不要、完全ローカルで動作
        retriever = self.index.as_retriever(similarity_top_k=top_k)
        nodes = retriever.retrieve(query)

        # 結果整形
        results = []
        for node in nodes:
            results.append(
                {
                    "knowledge_id": node.metadata.get("knowledge_id"),
                    "task_type": node.metadata.get("task_type"),
                    "scenario": node.metadata.get("scenario"),
                    "success_rate": node.metadata.get("success_rate"),
                    "similarity_score": node.score,
                    "text": node.text[:200],  # 最初の200文字
                }
            )

        return results


if __name__ == "__main__":
    # テスト実行
    print("\n" + "=" * 60)
    print("🧪 RAGエンジンテスト (完全ローカル版)")
    print("=" * 60 + "\n")

    # RAGエンジン初期化
    rag = FrugalRAGEngine()

    # ナレッジ読み込み
    knowledge_files = [
        "mvp_v4/knowledge/learned/unified_knowledge_base.json",
        "mvp_v4/knowledge/learned/conversation_knowledge_v4.json",
        "mvp_v4/knowledge/learned/conversation_knowledge_v3.json",
    ]
    rag.load_knowledge(knowledge_files)

    # 検索テスト
    test_queries = [
        "WordPressに記事を投稿したい",
        "画像をアップロードする方法",
        "ワイヤーフレームを作成",
    ]

    for query in test_queries:
        print(f"\n📝 クエリ: {query}")
        print("-" * 60)

        results = rag.search(query, top_k=2)

        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['scenario']} (成功率: {result['success_rate']*100:.0f}%)")
            print(f"   類似度: {result['similarity_score']:.3f}")
            print(f"   ID: {result['knowledge_id']}")

    print("\n" + "=" * 60)
    print("✅ テスト完了（完全ローカル動作）")
    print("   - OpenAI APIキー: 不要")
    print("   - コスト: $0")
    print("=" * 60)
