# knowledge_system/core_agents/faiss_manager.py
import faiss
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
import logging

# ロガーの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FaissManager:
    """
    FAISSインデックスを管理し、ベクトル検索機能を提供します。
    """
    def __init__(self, index_path: str, dimension: int):
        self.index_path = Path(index_path)
        self.dimension = dimension
        self.index: Optional[faiss.IndexIDMap] = None
        self.id_map: List[str] = [] # FAISSの内部IDとナレッジIDをマッピング

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_index()

    def _load_index(self):
        """ディスクからインデックスを読み込みます。存在しない場合は新規作成します。"""
        try:
            if self.index_path.exists():
                logging.info(f"既存のFAISSインデックスを読み込んでいます: {self.index_path}")
                self.index = faiss.read_index(str(self.index_path))
                # IDマップも同様に読み込む必要がある (ここでは簡略化のため、再構築を想定)
                # 本番実装では、IDマップも永続化するのが望ましい
                logging.info("インデックスの読み込みが完了しました。")
            else:
                self._create_index()
        except Exception as e:
            logging.error(f"インデックスの読み込みに失敗しました: {e}。新しいインデックスを作成します。")
            self._create_index()

    def _create_index(self):
        """新しいFAISSインデックスを作成します。"""
        logging.info("新しいFAISSインデックスを作成しています...")
        # L2距離（ユークリッド距離）を使用するフラットなインデックス
        index = faiss.IndexFlatL2(self.dimension)
        # 内部IDを外部のカスタムID（ここでは連番）にマッピングするIndexIDMapラッパーを使用
        self.index = faiss.IndexIDMap(index)
        logging.info("新しいインデックスの作成が完了しました。")

    def add_vectors(self, vectors: np.ndarray, ids: List[str]):
        """
        ベクトルとそれに対応するIDをインデックスに追加します。
        FAISSのIDMapは64ビット整数IDしかサポートしないため、連番を内部IDとして使用し、
        実際の文字列IDは別のリストで管理します。
        """
        if self.index is None:
            raise RuntimeError("インデックスが初期化されていません。")
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"ベクトルの次元が一致しません (期待値: {self.dimension}, 実際: {vectors.shape[1]})")

        # 文字列IDをFAISSが扱える整数IDに変換
        start_id = len(self.id_map)
        internal_ids = np.arange(start_id, start_id + len(ids)).astype('int64')

        self.index.add_with_ids(vectors.astype('float32'), internal_ids)
        self.id_map.extend(ids)
        logging.info(f"{len(ids)}個のベクトルをインデックスに追加しました。")

    def search(self, query_vector: np.ndarray, k: int) -> List[Tuple[str, float]]:
        """
        クエリベクトルに最も類似したk個のベクトルを検索します。
        返り値: (ID, 距離) のタプルのリスト
        """
        if self.index is None or self.index.ntotal == 0:
            return [] # インデックスが空の場合は空リストを返す

        # クエリベクトルを2D配列に変換
        query_vector = np.array([query_vector]).astype('float32')

        distances, internal_ids = self.index.search(query_vector, k)

        results = []
        for i, internal_id in enumerate(internal_ids[0]):
            if internal_id != -1: # FAISSは見つからない場合に-1を返すことがある
                # 内部IDを元の文字列IDに変換
                original_id = self.id_map[internal_id]
                distance = distances[0][i]
                results.append((original_id, float(distance)))

        return results

    def save_index(self):
        """現在のインデックスをディスクに保存します。"""
        if self.index is None:
            raise RuntimeError("保存するインデックスが存在しません。")

        logging.info(f"FAISSインデックスをディスクに保存しています: {self.index_path}")
        faiss.write_index(self.index, str(self.index_path))
        # IDマップも保存する必要がある
        logging.info("インデックスの保存が完了しました。")

    def reset(self):
        """インデックスをリセットし、ディスク上のファイルも削除します。"""
        self._create_index()
        self.id_map = []
        if self.index_path.exists():
            self.index_path.unlink()
        logging.info("FAISSインデックスはリセットされました。")

if __name__ == '__main__':
    # FaissManagerの使用例
    INDEX_PATH = "database/faiss_index/test.index"
    DIMENSION = 384 # all-MiniLM-L6-v2の次元数

    # 0. テスト前のクリーンアップ
    if Path(INDEX_PATH).exists():
        Path(INDEX_PATH).unlink()

    # 1. FaissManagerの初期化
    faiss_manager = FaissManager(INDEX_PATH, DIMENSION)

    # 2. ダミーベクトルの追加
    vectors_to_add = np.random.rand(5, DIMENSION).astype('float32')
    ids_to_add = [f"id_{i}" for i in range(5)]
    faiss_manager.add_vectors(vectors_to_add, ids_to_add)

    assert faiss_manager.index.ntotal == 5

    # 3. 検索の実行
    query = vectors_to_add[2] # 3番目のベクトルで検索
    results = faiss_manager.search(query, k=3)

    print("検索結果 (ID, 距離):", results)
    assert len(results) == 3
    assert results[0][0] == "id_2" # 最も近いのは自分自身
    assert results[0][1] == 0.0 # 距離は0

    # 4. インデックスの保存と再読み込み
    faiss_manager.save_index()

    # 新しいマネージャーでインデックスを読み込む
    new_faiss_manager = FaissManager(INDEX_PATH, DIMENSION)
    # 注意: 現在の実装ではIDマップは永続化されないため、再読み込み後はIDが失われる
    # ここではインデックスのntotalが復元されることだけを確認
    assert new_faiss_manager.index.ntotal == 5

    print("\nFAISSインデックスの保存と読み込みテストが完了しました。")

    # 5. クリーンアップ
    faiss_manager.reset()
    assert not Path(INDEX_PATH).exists()
