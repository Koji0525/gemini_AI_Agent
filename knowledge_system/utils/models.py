#!/usr/bin/env python3
"""
モデル管理ユーティリティ - 確実動作版
"""
from sentence_transformers import SentenceTransformer
import numpy as np

# シンプルなグローバルキャッシュ
_model = None

def get_model():
    """モデルを確実に取得"""
    global _model
    if _model is None:
        try:
            print("📥 モデルをロード中...")
            _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print(f"✅ モデルロード成功: {_model.get_sentence_embedding_dimension()}次元")
        except Exception as e:
            print(f"❌ モデルロード失敗: {e}")
            raise
    return _model

def get_embedding(text):
    """テキストの埋め込みを確実に取得"""
    try:
        model = get_model()
        embedding = model.encode(text)
        print(f"✅ 埋め込み生成成功: {len(embedding)}次元")
        return embedding
    except Exception as e:
        print(f"❌ 埋め込み生成失敗: {e}")
        raise

def get_embedding_dimension():
    """埋め込み次元数を確実に取得"""
    model = get_model()
    return model.get_sentence_embedding_dimension()
