"""
FAISS Manager: ベクトル検索インデックス管理
"""

import faiss
import numpy as np
from pathlib import Path
from typing import List, Tuple


class FAISSManager:
    """FAISS ベクトルインデックス管理"""

    def __init__(self, index_path: str = "database/faiss_index/knowledge.index"):
        self.index_path = Path(index_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.index = None
        self.dimension = 384  # all-MiniLM-L6-v2 の次元数

        self._initialize_index()

    def _initialize_index(self):
        """インデックス初期化"""
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            print(f"✅ FAISS インデックス読み込み: {self.index.ntotal}件")
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            print("✅ FAISS 新規インデックス作成")

    def add_vectors(self, vectors: np.ndarray, ids: List[int]):
        """ベクトル追加"""
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"ベクトル次元不一致: {vectors.shape[1]} != {self.dimension}")

        self.index.add(vectors)
        print(f"📥 ベクトル追加: {len(ids)}件")

    def search_similar(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[int, float]]:
        """類似ベクトル検索"""
        if query_vector.shape[0] != self.dimension:
            raise ValueError(f"クエリ次元不一致: {query_vector.shape[0]} != {self.dimension}")

        query_vector = query_vector.reshape(1, -1)
        distances, indices = self.index.search(query_vector, top_k)

        results = [(int(idx), float(dist)) for idx, dist in zip(indices[0], distances[0])]
        return results

    def save_index(self):
        """インデックス保存"""
        faiss.write_index(self.index, str(self.index_path))
        print(f"💾 FAISS インデックス保存: {self.index.ntotal}件")

    def load_index(self):
        """インデックス読み込み"""
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            print(f"📂 FAISS インデックス読み込み: {self.index.ntotal}件")
        else:
            print("⚠️ インデックスファイル未発見")
