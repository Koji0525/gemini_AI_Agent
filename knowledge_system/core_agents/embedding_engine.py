# knowledge_system/core_agents/embedding_engine.py
from sentence_transformers import SentenceTransformer
import numpy as np
import logging
from typing import List

# ロガーの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EmbeddingEngine:
    """
    SentenceTransformerモデルを使用して、テキストの埋め込みベクトルを生成します。
    モデルのロードをシングルトンパターンで管理し、効率化を図ります。
    """
    _instance = None
    _model = None

    def __new__(cls, model_name: str = "all-MiniLM-L6-v2"):
        if cls._instance is None:
            cls._instance = super(EmbeddingEngine, cls).__new__(cls)
            try:
                logging.info(f"'{model_name}'モデルをロードしています...")
                cls._model = SentenceTransformer(model_name)
                logging.info("モデルのロードが完了しました。")
            except Exception as e:
                logging.error(f"モデルのロード中にエラーが発生しました: {e}")
                cls._instance = None # エラーが発生した場合はインスタンスを無効化
                raise
        return cls._instance

    def get_embedding(self, text: str) -> np.ndarray:
        """単一のテキストの埋め込みベクトルを取得します。"""
        if self._model is None:
            raise RuntimeError("モデルがロードされていません。")

        # S-BERTは通常、文のリストを入力として受け取るため、単一テキストでもリストで渡す
        embedding = self._model.encode([text], convert_to_numpy=True)
        return embedding[0]

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """複数のテキストの埋め込みベクトルを一度に取得します。"""
        if self._model is None:
            raise RuntimeError("モデルがロードされていません。")

        return self._model.encode(texts, convert_to_numpy=True)

    @property
    def dimension(self) -> int:
        """モデルの出力ベクトルの次元数を返します。"""
        if self._model is None:
            raise RuntimeError("モデルがロードされていません。")
        return self._model.get_sentence_embedding_dimension()

if __name__ == '__main__':
    # EmbeddingEngineの使用例
    try:
        engine = EmbeddingEngine()

        # 1. 単一テキストの埋め込み
        text1 = "こんにちは、世界！"
        embedding1 = engine.get_embedding(text1)
        print(f"テキスト: '{text1}'")
        print(f"埋め込みベクトルの次元数: {embedding1.shape}")
        assert embedding1.shape == (engine.dimension,)

        # 2. 複数テキストの埋め込み
        texts = ["これは最初の文です。", "これは2番目の文です。"]
        embeddings = engine.get_embeddings(texts)
        print(f"\nテキストリスト: {texts}")
        print(f"埋め込みベクトルの次元数: {embeddings.shape}")
        assert embeddings.shape == (len(texts), engine.dimension)

        # 3. シングルトンの確認
        engine2 = EmbeddingEngine()
        assert engine is engine2 # 同じインスタンスであることを確認
        print("\nシングルトンインスタンスが正常に機能していることを確認しました。")

    except Exception as e:
        print(f"テスト中にエラーが発生しました: {e}")
