# knowledge_system/tests/test_vector_search.py
import pytest
import numpy as np
from pathlib import Path
import sys

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core_agents.embedding_engine import EmbeddingEngine
from core_agents.faiss_manager import FaissManager

# テスト用のFAISSインデックスパス
TEST_INDEX_PATH = project_root / "tests" / "test.index"

@pytest.fixture(scope="module")
def embedding_engine():
    """
    テストモジュール全体でEmbeddingEngineの単一インスタンスを提供します。
    モデルのロードは一度だけ行われます。
    """
    try:
        engine = EmbeddingEngine(model_name="all-MiniLM-L6-v2")
        return engine
    except Exception as e:
        pytest.fail(f"EmbeddingEngineの初期化に失敗しました: {e}")

@pytest.fixture(scope="function")
def faiss_manager(embedding_engine: EmbeddingEngine):
    """
    各テスト関数用に、クリーンなFAISSインデックスでFaissManagerをセットアップします。
    """
    # テスト前にインデックスファイルが存在すれば削除
    if TEST_INDEX_PATH.exists():
        TEST_INDEX_PATH.unlink()

    dimension = embedding_engine.dimension
    manager = FaissManager(str(TEST_INDEX_PATH), dimension)
    yield manager

    # テスト後にファイルをクリーンアップ
    manager.reset()

def test_embedding_engine_initialization(embedding_engine: EmbeddingEngine):
    """EmbeddingEngineが正常に初期化され、正しい次元数を持つことをテストします。"""
    assert embedding_engine is not None
    assert embedding_engine.dimension > 0

    # シングルトンのテスト
    engine2 = EmbeddingEngine()
    assert embedding_engine is engine2

def test_text_to_embedding_conversion(embedding_engine: EmbeddingEngine):
    """テキストからベクトルへの変換をテストします。"""
    text = "これはテスト文です。"
    embedding = embedding_engine.get_embedding(text)

    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (embedding_engine.dimension,)

    # 複数テキストのテスト
    texts = ["文1", "文2"]
    embeddings = embedding_engine.get_embeddings(texts)
    assert embeddings.shape == (2, embedding_engine.dimension)

def test_add_vectors_and_search(embedding_engine: EmbeddingEngine, faiss_manager: FaissManager):
    """
    テキストをベクトル化し、FAISSインデックスに追加、そして検索する一連の流れをテストします。
    """
    # 1. テキストとIDを準備
    texts = [
        "今日の天気は晴れです。",
        "猫は可愛い動物です。",
        "プログラミングは楽しい。",
        "美味しいリンゴの選び方。",
        "A sunny day is perfect for a walk." # 英語の文
    ]
    ids = [f"doc_{i}" for i in range(len(texts))]

    # 2. テキストをベクトルに変換
    embeddings = embedding_engine.get_embeddings(texts)

    # 3. FAISSインデックスにベクトルを追加
    faiss_manager.add_vectors(embeddings, ids)

    # 4. 検索クエリを準備
    query_text = "What is a cute animal?"
    query_vector = embedding_engine.get_embedding(query_text)

    # 5. 検索を実行
    results = faiss_manager.search(query_vector, k=3)

    # 6. 結果を検証
    assert len(results) > 0
    # 最も類似しているのは「猫は可愛い動物です。」のはず
    top_result_id = results[0][0]
    assert top_result_id == "doc_1"

    # 別のクエリでテスト
    query_text_2 = "How to code?"
    query_vector_2 = embedding_engine.get_embedding(query_text_2)
    results_2 = faiss_manager.search(query_vector_2, k=3)

    # 検索結果の上位3つに期待されるIDが含まれていることを確認
    result_ids_2 = {res[0] for res in results_2}
    expected_ids = {"doc_2", "doc_3"} # 「プログラミング」と「選び方」が類似と判断される可能性がある

    # 少なくとも期待されるIDのいずれかが結果に含まれていることを確認
    assert any(eid in result_ids_2 for eid in expected_ids)
    # モデルの判断に基づき、最も類似しているのは'doc_3'（選び方）であると期待
    assert results_2[0][0] == "doc_3"

def test_save_and_load_index(embedding_engine: EmbeddingEngine, faiss_manager: FaissManager):
    """FAISSインデックスの保存と読み込みをテストします。"""
    texts = ["サンプルテキスト1", "サンプルテキスト2"]
    ids = ["sample_1", "sample_2"]
    embeddings = embedding_engine.get_embeddings(texts)

    faiss_manager.add_vectors(embeddings, ids)
    assert faiss_manager.index.ntotal == 2

    # インデックスを保存
    faiss_manager.save_index()
    assert TEST_INDEX_PATH.exists()

    # 新しいFaissManagerでインデックスを読み込む
    new_manager = FaissManager(str(TEST_INDEX_PATH), embedding_engine.dimension)

    # 読み込んだインデックスが元のものと同じ数のベクトルを持っているか確認
    assert new_manager.index.ntotal == 2

def test_search_in_empty_index(faiss_manager: FaissManager):
    """空のインデックスで検索してもエラーが発生せず、空の結果が返ることをテストします。"""
    query_vector = np.random.rand(faiss_manager.dimension).astype('float32')
    results = faiss_manager.search(query_vector, k=5)
    assert results == []
