"""
FAISSベクトル検索エージェント
運用ルール7準拠: 検索に特化（単一責任）
"""

import json
from pathlib import Path
from typing import List, Tuple

import faiss
from sentence_transformers import SentenceTransformer


class HybridSearchAgent:
    """FAISSを使ったベクトル検索"""

    def __init__(self, index_path: str, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.index_path = Path(index_path)
        self.model_name = model_name
        self.model = None
        self.index = None
        self.index_to_id = {}  # vector_index -> knowledge_id
        self._initialize()

    def _initialize(self):
        """初期化"""
        # ディレクトリ作成
        self.index_path.parent.mkdir(parents=True, exist_ok=True)

        # モデルロード（初回は時間がかかる）
        print(f"📥 埋め込みモデルをロード中: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        print(f"✅ モデルロード完了（次元数: {self.model.get_sentence_embedding_dimension()}）")

        # インデックスのロードまたは作成
        self._load_or_create_index()

    def _load_or_create_index(self):
        """インデックスのロードまたは新規作成"""
        mapping_path = self.index_path.parent / "index_mapping.json"

        if self.index_path.exists() and mapping_path.exists():
            # 既存インデックスをロード
            self.index = faiss.read_index(str(self.index_path))
            with open(mapping_path, "r", encoding="utf-8") as f:
                self.index_to_id = json.load(f)
            print(f"✅ 既存インデックスをロード: {self.index.ntotal}件")
        else:
            # 新規作成
            embedding_dim = self.model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatIP(embedding_dim)  # 内積（コサイン類似度）
            self.index_to_id = {}
            print("✅ 新規インデックスを作成")

    def add_knowledge(self, knowledge_id: str, text: str) -> int:
        """ナレッジをインデックスに追加"""
        # テキストをベクトル化
        embedding = self.model.encode([text], convert_to_numpy=True)

        # 正規化（コサイン類似度のため）
        faiss.normalize_L2(embedding)

        # インデックスに追加
        vector_index = self.index.ntotal
        self.index.add(embedding)

        # マッピングを保存
        self.index_to_id[str(vector_index)] = knowledge_id

        return vector_index

    def search(
        self, query: str, top_k: int = 10, min_similarity: float = 0.3
    ) -> List[Tuple[str, float]]:
        """ベクトル検索を実行"""
        if self.index.ntotal == 0:
            return []

        # クエリをベクトル化
        query_vector = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_vector)

        # 検索実行
        similarities, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))

        # 結果を整形
        results = []
        for i, idx in enumerate(indices[0]):
            similarity = float(similarities[0][i])
            if similarity >= min_similarity:
                knowledge_id = self.index_to_id.get(str(idx))
                if knowledge_id:
                    results.append((knowledge_id, similarity))

        return results

    def save(self):
        """インデックスとマッピングを保存"""
        faiss.write_index(self.index, str(self.index_path))

        mapping_path = self.index_path.parent / "index_mapping.json"
        with open(mapping_path, "w", encoding="utf-8") as f:
            json.dump(self.index_to_id, f, ensure_ascii=False, indent=2)

        print(f"✅ インデックス保存完了: {self.index.ntotal}件")
