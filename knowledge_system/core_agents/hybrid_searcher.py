# knowledge_system/core_agents/hybrid_searcher.py
import logging
from typing import List, Dict

from .data_models import KnowledgeEntry
from .sqlite_manager import SQLiteManager
from .embedding_engine import EmbeddingEngine
from .faiss_manager import FaissManager

# ロガーの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HybridSearcher:
    """
    ベクトル検索とキーワード検索を組み合わせたハイブリッド検索を提供します。
    """
    def __init__(self, db_manager: SQLiteManager, embedding_engine: EmbeddingEngine, faiss_manager: FaissManager):
        self.db_manager = db_manager
        self.embedding_engine = embedding_engine
        self.faiss_manager = faiss_manager
        logging.info("HybridSearcherが正常に初期化されました。")

    def search(self, query_text: str, k: int = 10, keyword: str = None) -> List[Dict]:
        """
        指定されたクエリテキストでハイブリッド検索を実行します。

        Args:
            query_text (str): 検索クエリ。
            k (int): 取得する結果の最大数。
            keyword (str, optional): 結果をフィルタリングするためのキーワード。

        Returns:
            List[Dict]: 検索結果のリスト。各要素はナレッジエントリーと類似度スコアを含む辞書。
        """
        try:
            # 1. クエリテキストをベクトル化
            query_vector = self.embedding_engine.get_embedding(query_text)

            # 2. FAISSで類似ベクトルを検索
            # キーワードフィルタリングを後で行うため、多めに候補を取得
            search_k = k * 2 if keyword else k
            vector_search_results = self.faiss_manager.search(query_vector, k=search_k)

            if not vector_search_results:
                return []

            # 3. 取得したIDを基にデータベースから完全なナレッジエントリーを取得
            result_ids = [res[0] for res in vector_search_results]

            # データベースから一括で取得 (効率化のため)
            # 注: 現在のSQLiteManagerにはIDリストで一括取得する機能がないため、ループで取得
            # 本番実装では `WHERE id IN (...)` を使うのが望ましい
            entries = [self.db_manager.get_entry(id) for id in result_ids]

            # 辞書に変換して距離も保持
            entry_map = {entry.id: entry for entry in entries if entry}

            # 4. キーワードフィルタリング (指定されている場合)
            final_results = []
            for entry_id, distance in vector_search_results:
                if entry_id in entry_map:
                    entry = entry_map[entry_id]

                    passes_keyword_filter = True
                    if keyword:
                        # コンテンツまたはタグにキーワードが含まれているかチェック
                        passes_keyword_filter = keyword.lower() in entry.content.lower() or \
                                                any(keyword.lower() in tag.lower() for tag in entry.tags)

                    if passes_keyword_filter:
                        final_results.append({
                            "entry": entry,
                            "distance_score": distance
                        })

            # k個の結果に絞る
            return final_results[:k]

        except Exception as e:
            logging.error(f"ハイブリッド検索中にエラーが発生しました: {e}")
            return []

if __name__ == '__main__':
    # HybridSearcherの使用例 (テストセットアップ)
    from pathlib import Path
    from .knowledge_manager import KnowledgeManager

    # テスト用のパス
    DB_PATH = "database/test_hybrid_searcher.db"
    INDEX_PATH = "database/faiss_index/test_hs.index"

    # テスト前のクリーンアップ
    if Path(DB_PATH).exists(): Path(DB_PATH).unlink()
    if Path(INDEX_PATH).exists(): Path(INDEX_PATH).unlink()

    try:
        # 1. 依存コンポーネントの初期化
        db_manager = SQLiteManager(DB_PATH)
        embedding_engine = EmbeddingEngine()
        faiss_manager = FaissManager(INDEX_PATH, embedding_engine.dimension)
        knowledge_manager = KnowledgeManager(db_manager, embedding_engine, faiss_manager)

        # 2. テスト用ナレッジの追加
        knowledge_manager.add_knowledge(KnowledgeEntry(content="猫はとても愛らしい生き物です。", tags=["animal", "pet"]))
        knowledge_manager.add_knowledge(KnowledgeEntry(content="Pythonは汎用的なプログラミング言語です。", tags=["tech", "code"]))
        knowledge_manager.add_knowledge(KnowledgeEntry(content="犬もまた、素晴らしいペットです。", tags=["animal", "pet"]))
        knowledge_manager.add_knowledge(KnowledgeEntry(content="FastAPIはPythonのWebフレームワークです。", tags=["tech", "python"]))

        # 3. HybridSearcherの初期化
        searcher = HybridSearcher(db_manager, embedding_engine, faiss_manager)

        # 4. 検索の実行
        print("--- ベクトル検索 (キーワードなし) ---")
        query1 = "What is a cute animal?"
        results1 = searcher.search(query1, k=2)
        print(f"クエリ: '{query1}'")
        for res in results1:
            print(f"  - Content: {res['entry'].content}, Score: {res['distance_score']:.4f}")
        assert results1[0]['entry'].content.startswith("猫は")

        print("\n--- ハイブリッド検索 (キーワードあり) ---")
        query2 = "Tell me about a lovely companion."
        results2 = searcher.search(query2, k=2, keyword="犬")
        print(f"クエリ: '{query2}', キーワード: '犬'")
        for res in results2:
            print(f"  - Content: {res['entry'].content}, Score: {res['distance_score']:.4f}")
        assert len(results2) == 1
        assert results2[0]['entry'].content.startswith("犬もまた")

        print("\nHybridSearcherのテストが正常に完了しました。")

    except Exception as e:
        print(f"テスト中にエラーが発生しました: {e}")
    finally:
        # クリーンアップ
        db_manager.close()
        if Path(DB_PATH).exists(): Path(DB_PATH).unlink()
        if Path(INDEX_PATH).exists(): Path(INDEX_PATH).unlink()
