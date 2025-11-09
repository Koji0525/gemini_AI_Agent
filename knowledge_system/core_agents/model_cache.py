"""
モデルキャッシュ管理 - パフォーマンス改善用
"""

import threading

from sentence_transformers import SentenceTransformer


class ModelCache:
    _instance = None
    _lock = threading.Lock()
    _model = None
    _model_name = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ModelCache, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_model(cls, model_name="paraphrase-multilingual-MiniLM-L12-v2"):
        with cls._lock:
            if cls._model is None or cls._model_name != model_name:
                print(f"📥 モデルをロード中: {model_name}")
                cls._model = SentenceTransformer(model_name)
                cls._model_name = model_name
                print("✅ モデルロード完了")
            return cls._model

    @classmethod
    def clear_cache(cls):
        with cls._lock:
            cls._model = None
            cls._model_name = None
