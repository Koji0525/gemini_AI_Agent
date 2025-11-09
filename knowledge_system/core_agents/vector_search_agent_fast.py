"""高速ベクトル検索エージェント（ローカルモデル版）"""

import json
from pathlib import Path
from typing import Any, Dict, List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class FastVectorSearchAgent:
    """ローカルモデルを使用した高速ベクトル検索"""

    def __init__(self, index_path: str, dimension: int = 384):
        """
        Args:
            index_path: FAISSインデックスのパス
            dimension: ベクトル次元数（all-MiniLM-L6-v2は384次元）
        """
        self.index_path = Path(index_path)
        self.dimension = dimension
        self.mapping_path = self.index_path.parent / "index_mapping.json"

        # 軽量モデル（約90MB、高速）
        print("⏳ ローカルモデル読み込み中...")
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        print("✅ モデル読み込み完了")

        # FAISSインデックス
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
        else:
            self.index = faiss.IndexFlatL2(dimension)

        # ID マッピング
        self.id_mapping = self._load_mapping()

    def _load_mapping(self) -> Dict[int, str]:
        """ID マッピング読み込み"""
        if self.mapping_path.exists():
            with open(self.mapping_path, "r") as f:
                return json.load(f)
        return {}

    def _save_mapping(self):
        """ID マッピング保存"""
        self.mapping_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.mapping_path, "w") as f:
            json.dump(self.id_mapping, f, indent=2)

    def create_embedding(self, text: str) -> np.ndarray:
        """
        テキストをベクトル化（高速・ローカル処理）

        Args:
            text: ベクトル化するテキスト

        Returns:
            384次元のベクトル
        """
        # 0.01秒程度で完了
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype("float32")

    def add_vector(self, knowledge_id: str, text: str):
        """
        ベクトルをインデックスに追加

        Args:
            knowledge_id: ナレッジID
            text: ベクトル化するテキスト
        """
        vector = self.create_embedding(text)
        vector = vector.reshape(1, -1)

        # インデックスに追加
        faiss_id = self.index.ntotal
        self.index.add(vector)

        # マッピング保存
        self.id_mapping[str(faiss_id)] = knowledge_id

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        類似ベクトル検索

        Args:
            query: 検索クエリ
            top_k: 取得件数

        Returns:
            検索結果（knowledge_id と similarity のリスト）
        """
        if self.index.ntotal == 0:
            return []

        # クエリをベクトル化
        query_vector = self.create_embedding(query)
        query_vector = query_vector.reshape(1, -1)

        # 検索実行
        distances, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))

        # 結果整形
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and str(idx) in self.id_mapping:
                # L2距離を類似度に変換（0-1の範囲）
                similarity = 1 / (1 + dist)
                results.append(
                    {"knowledge_id": self.id_mapping[str(idx)], "similarity": float(similarity)}
                )

        return results

    def save_index(self):
        """インデックスを保存"""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        self._save_mapping()

    def get_stats(self) -> Dict[str, Any]:
        """統計情報"""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "model": "all-MiniLM-L6-v2 (local)",
            "index_size_mb": (
                self.index_path.stat().st_size / (1024 * 1024) if self.index_path.exists() else 0
            ),
        }
