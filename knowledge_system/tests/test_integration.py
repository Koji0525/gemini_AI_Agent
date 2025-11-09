# knowledge_system/tests/test_integration.py
import pytest
from pathlib import Path
import sys

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core_agents.data_models import KnowledgeEntry
from core_agents.sqlite_manager import SQLiteManager
from core_agents.embedding_engine import EmbeddingEngine
from core_agents.faiss_manager import FaissManager
from core_agents.knowledge_manager import KnowledgeManager
from core_agents.hybrid_searcher import HybridSearcher

# テスト用のパス
TEST_DB_PATH = project_root / "tests" / "integration_test.db"
TEST_INDEX_PATH = project_root / "tests" / "integration_test.index"

@pytest.fixture(scope="module")
def embedding_engine():
    """モジュールスコープでEmbeddingEngineをセットアップ"""
    return EmbeddingEngine(model_name="all-MiniLM-L6-v2")

@pytest.fixture(scope="function")
def setup_managers(embedding_engine: EmbeddingEngine):
    """
    各テスト関数用に、すべてのマネージャーをクリーンな状態でセットアップします。
    """
    if TEST_DB_PATH.exists(): TEST_DB_PATH.unlink()
    if TEST_INDEX_PATH.exists(): TEST_INDEX_PATH.unlink()

    db_manager = SQLiteManager(str(TEST_DB_PATH))
    faiss_manager = FaissManager(str(TEST_INDEX_PATH), embedding_engine.dimension)
    knowledge_manager = KnowledgeManager(db_manager, embedding_engine, faiss_manager)
    searcher = HybridSearcher(db_manager, embedding_engine, faiss_manager)

    yield db_manager, faiss_manager, knowledge_manager, searcher

    db_manager.close()
    if TEST_DB_PATH.exists(): TEST_DB_PATH.unlink()
    if TEST_INDEX_PATH.exists(): TEST_INDEX_PATH.unlink()

def test_add_knowledge_and_search_flow(setup_managers):
    """ナレッジの追加から検索までの一連のフローをテストします。"""
    _, _, knowledge_manager, searcher = setup_managers

    # 1. テストデータの準備とナレッジの追加
    knowledge_data = [
        KnowledgeEntry(content="AIは人工知能の略です。", tags=["tech", "ai"]),
        KnowledgeEntry(content="太陽系で最も大きい惑星は木星です。", tags=["science", "space"]),
        KnowledgeEntry(content="SQLiteは軽量なデータベースエンジンです。", tags=["tech", "database"])
    ]

    for entry in knowledge_data:
        knowledge_manager.add_knowledge(entry)

    # 2. 追加されたことを確認 (DBとFAISSの両方)
    assert len(knowledge_manager.get_all_knowledge()) == 3
    assert knowledge_manager.faiss_manager.index.ntotal == 3

    # 3. ベクトル検索を実行
    query1 = "What is the largest planet?"
    results1 = searcher.search(query1)

    assert len(results1) > 0
    assert "木星" in results1[0]['entry'].content

    # 4. ハイブリッド検索 (キーワードフィルタリング)
    query2 = "Tell me about technology."
    results2_all = searcher.search(query2, k=2)
    results2_filtered = searcher.search(query2, k=2, keyword="database")

    assert len(results2_all) == 2
    # モデルの判断に基づき、"technology"に最も近いのは"SQLite"と判定されることを期待
    assert "SQLite" in results2_all[0]['entry'].content

    assert len(results2_filtered) == 1
    assert "SQLite" in results2_filtered[0]['entry'].content

def test_rebuild_index_functionality(setup_managers):
    """インデックスの再構築機能が正しく動作するかをテストします。"""
    db_manager, faiss_manager, knowledge_manager, _ = setup_managers

    # 1. ナレッジを追加
    entry1 = KnowledgeEntry(content="最初のドキュメント。")
    knowledge_manager.add_knowledge(entry1)

    # 2. 手動でFAISSインデックスをリセットして不整合な状態を作る
    faiss_manager.reset()
    assert faiss_manager.index.ntotal == 0

    # DBにはデータが残っている
    assert len(db_manager.get_all_entries()) == 1

    # 3. インデックスを再構築
    knowledge_manager.rebuild_faiss_index()

    # 4. FAISSインデックスがDBの状態と一致することを確認
    assert faiss_manager.index.ntotal == 1

def test_empty_search_returns_nothing(setup_managers):
    """ナレッジが何もない状態で検索しても結果が返らないことをテストします。"""
    _, _, _, searcher = setup_managers

    results = searcher.search("any query")
    assert results == []
