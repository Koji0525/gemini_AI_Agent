# knowledge_system/core_agents/knowledge_manager.py
import logging
from typing import List

from .data_models import KnowledgeEntry
from .sqlite_manager import SQLiteManager
from .embedding_engine import EmbeddingEngine
from .faiss_manager import FaissManager

# ロガーの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KnowledgeManager:
    """
    ナレッジの登録、更新、削除を管理し、データベースとベクトルインデックス間の
    一貫性を保証します。
    """
    def __init__(self, db_manager: SQLiteManager, embedding_engine: EmbeddingEngine, faiss_manager: FaissManager):
        self.db_manager = db_manager
        self.embedding_engine = embedding_engine
        self.faiss_manager = faiss_manager
        logging.info("KnowledgeManagerが正常に初期化されました。")

    def add_knowledge(self, entry: KnowledgeEntry) -> str:
        """
        新しいナレッジをデータベースとベクトルインデックスの両方に追加します。

        Args:
            entry (KnowledgeEntry): 追加するナレッジエントリー。

        Returns:
            str: 追加されたエントリーのID。
        """
        try:
            # 1. データベースにエントリーを保存
            self.db_manager.add_entry(entry)

            # 2. コンテンツのベクトル埋め込みを生成
            embedding = self.embedding_engine.get_embedding(entry.content)

            # 3. FAISSインデックスにベクトルを追加
            self.faiss_manager.add_vectors(
                vectors=embedding.reshape(1, -1), # (1, D)の形状にする
                ids=[entry.id]
            )

            logging.info(f"ナレッジが正常に追加されました: ID={entry.id}")
            return entry.id
        except Exception as e:
            logging.error(f"ナレッジの追加中にエラーが発生しました (ID={entry.id}): {e}")
            # トランザクションを考慮: エラーが発生した場合、DBからエントリーを削除するなどの
            # ロールバック処理を本番環境では検討すべき
            raise

    def get_knowledge(self, entry_id: str) -> KnowledgeEntry | None:
        """データベースからナレッジを取得します。"""
        return self.db_manager.get_entry(entry_id)

    def get_all_knowledge(self) -> List[KnowledgeEntry]:
        """データベースからすべてのナレッジを取得します。"""
        return self.db_manager.get_all_entries()

    def rebuild_faiss_index(self):
        """
        データベース内のすべてのナレッジからFAISSインデックスを再構築します。
        データベースとインデックスの間に不整合が生じた場合に使用します。
        """
        logging.info("FAISSインデックスの再構築を開始します...")
        all_entries = self.get_all_knowledge()

        if not all_entries:
            logging.warning("再構築するナレッジがデータベースにありません。")
            return

        contents = [entry.content for entry in all_entries]
        ids = [entry.id for entry in all_entries]

        # 1. すべてのコンテンツの埋め込みを一度に生成
        embeddings = self.embedding_engine.get_embeddings(contents)

        # 2. FAISSインデックスをリセット
        self.faiss_manager.reset()

        # 3. 新しい埋め込みをインデックスに追加
        self.faiss_manager.add_vectors(embeddings, ids)

        logging.info(f"{len(all_entries)}件のナレッジからインデックスを再構築しました。")

if __name__ == '__main__':
    # KnowledgeManagerの使用例 (テストセットアップ)
    from pathlib import Path

    # テスト用のパス
    DB_PATH = "database/test_knowledge_manager.db"
    INDEX_PATH = "database/faiss_index/test_km.index"

    # テスト前のクリーンアップ
    if Path(DB_PATH).exists(): Path(DB_PATH).unlink()
    if Path(INDEX_PATH).exists(): Path(INDEX_PATH).unlink()

    try:
        # 1. 依存コンポーネントの初期化
        db_manager = SQLiteManager(DB_PATH)
        embedding_engine = EmbeddingEngine()
        faiss_manager = FaissManager(INDEX_PATH, embedding_engine.dimension)

        # 2. KnowledgeManagerの初期化
        knowledge_manager = KnowledgeManager(db_manager, embedding_engine, faiss_manager)

        # 3. ナレッジの追加
        entry1 = KnowledgeEntry(content="最初のナレッジです。", tags=["first"])
        knowledge_manager.add_knowledge(entry1)

        entry2 = KnowledgeEntry(content="これは2番目のナレッジです。", tags=["second"])
        knowledge_manager.add_knowledge(entry2)

        # 4. 追加されたナレッジの確認
        retrieved = knowledge_manager.get_knowledge(entry1.id)
        assert retrieved.content == entry1.content
        assert faiss_manager.index.ntotal == 2

        print("ナレッジの追加テストが成功しました。")

        # 5. インデックスの再構築テスト
        knowledge_manager.rebuild_faiss_index()
        assert faiss_manager.index.ntotal == 2
        print("FAISSインデックスの再構築テストが成功しました。")

    except Exception as e:
        print(f"テスト中にエラーが発生しました: {e}")
    finally:
        # クリーンアップ
        db_manager.close()
        if Path(DB_PATH).exists(): Path(DB_PATH).unlink()
        if Path(INDEX_PATH).exists(): Path(INDEX_PATH).unlink()
