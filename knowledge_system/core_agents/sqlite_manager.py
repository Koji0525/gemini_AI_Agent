# knowledge_system/core_agents/sqlite_manager.py
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import logging

from .data_models import KnowledgeEntry

# ロガーの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SQLiteManager:
    """
    SQLiteデータベースを管理し、ナレッジエントリーの永続化を処理します。
    """
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()
        self._create_table()

    def _connect(self):
        """データベースへの接続を確立します。"""
        try:
            self.conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            self.conn.row_factory = sqlite3.Row
            logging.info(f"データベースに正常に接続しました: {self.db_path}")
        except sqlite3.Error as e:
            logging.error(f"データベース接続エラー: {e}")
            raise

    def _create_table(self):
        """'knowledge'テーブルが存在しない場合に作成します。"""
        if not self.conn:
            raise ConnectionError("データベースに接続されていません。")
        try:
            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS knowledge (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        category TEXT,
                        tags TEXT, -- JSON-encoded list of strings
                        metadata TEXT, -- JSON-encoded dictionary
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP
                    )
                """)
                logging.info("'knowledge'テーブルが正常に作成または確認されました。")
        except sqlite3.Error as e:
            logging.error(f"テーブル作成エラー: {e}")
            raise

    def add_entry(self, entry: KnowledgeEntry) -> None:
        """新しいナレッジエントリーをデータベースに追加します。"""
        if not self.conn:
            raise ConnectionError("データベースに接続されていません。")
        try:
            with self.conn:
                self.conn.execute(
                    """
                    INSERT INTO knowledge (id, content, category, tags, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entry.id,
                        entry.content,
                        entry.category,
                        json.dumps(entry.tags),
                        json.dumps(entry.metadata),
                        entry.created_at,
                        entry.updated_at,
                    ),
                )
            logging.info(f"ナレッジエントリーを追加しました: ID={entry.id}")
        except sqlite3.IntegrityError:
            logging.warning(f"IDが{entry.id}のエントリーは既に存在します。")
            raise
        except sqlite3.Error as e:
            logging.error(f"エントリー追加エラー: {e}")
            raise

    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """IDでナレッジエントリーを取得します。"""
        if not self.conn:
            raise ConnectionError("データベースに接続されていません。")
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM knowledge WHERE id = ?", (entry_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_entry(row)
            return None
        except sqlite3.Error as e:
            logging.error(f"エントリー取得エラー: {e}")
            return None

    def get_all_entries(self) -> List[KnowledgeEntry]:
        """すべてのナレッジエントリーを取得します。"""
        if not self.conn:
            raise ConnectionError("データベースに接続されていません。")
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM knowledge ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [self._row_to_entry(row) for row in rows]
        except sqlite3.Error as e:
            logging.error(f"全エントリー取得エラー: {e}")
            return []

    def update_entry(self, entry: KnowledgeEntry) -> None:
        """既存のナレッジエントリーを更新します。"""
        if not self.conn:
            raise ConnectionError("データベースに接続されていません。")
        try:
            entry.updated_at = datetime.utcnow()
            with self.conn:
                self.conn.execute(
                    """
                    UPDATE knowledge
                    SET content = ?, category = ?, tags = ?, metadata = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        entry.content,
                        entry.category,
                        json.dumps(entry.tags),
                        json.dumps(entry.metadata),
                        entry.updated_at,
                        entry.id,
                    ),
                )
            logging.info(f"ナレッジエントリーを更新しました: ID={entry.id}")
        except sqlite3.Error as e:
            logging.error(f"エントリー更新エラー: {e}")
            raise

    def delete_entry(self, entry_id: str) -> None:
        """IDでナレッジエントリーを削除します。"""
        if not self.conn:
            raise ConnectionError("データベースに接続されていません。")
        try:
            with self.conn:
                self.conn.execute("DELETE FROM knowledge WHERE id = ?", (entry_id,))
            logging.info(f"ナレッジエントリーを削除しました: ID={entry_id}")
        except sqlite3.Error as e:
            logging.error(f"エントリー削除エラー: {e}")
            raise

    def close(self):
        """データベース接続を閉じます。"""
        if self.conn:
            self.conn.close()
            logging.info("データベース接続を閉じました。")

    def _row_to_entry(self, row: sqlite3.Row) -> KnowledgeEntry:
        """データベースの行をKnowledgeEntryオブジェクトに変換します。"""
        return KnowledgeEntry(
            id=row["id"],
            content=row["content"],
            category=row["category"],
            tags=json.loads(row["tags"]),
            metadata=json.loads(row["metadata"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

if __name__ == '__main__':
    # SQLiteManagerの使用例
    DB_PATH = "database/knowledge_test.db"

    # テスト用データベースファイルをクリーンアップ
    if Path(DB_PATH).exists():
        Path(DB_PATH).unlink()

    db_manager = SQLiteManager(DB_PATH)

    # 1. エントリーの追加
    entry1 = KnowledgeEntry(content="最初のナレッジ。")
    db_manager.add_entry(entry1)

    # 2. エントリーの取得
    retrieved_entry = db_manager.get_entry(entry1.id)
    print(f"取得したエントリー: {retrieved_entry.content}")
    assert retrieved_entry.id == entry1.id

    # 3. エントリーの更新
    retrieved_entry.content = "更新された最初のナレッジ。"
    retrieved_entry.tags = ["updated"]
    db_manager.update_entry(retrieved_entry)

    updated_entry = db_manager.get_entry(entry1.id)
    print(f"更新されたエントリー: {updated_entry.content}")
    assert updated_entry.content == "更新された最初のナレッジ。"
    assert updated_entry.tags == ["updated"]

    # 4. 全エントリーの取得
    entry2 = KnowledgeEntry(content="2番目のナレッジ。")
    db_manager.add_entry(entry2)
    all_entries = db_manager.get_all_entries()
    print(f"すべてのエントリー数: {len(all_entries)}")
    assert len(all_entries) == 2

    # 5. エントリーの削除
    db_manager.delete_entry(entry1.id)
    deleted_entry = db_manager.get_entry(entry1.id)
    assert deleted_entry is None

    db_manager.close()
    print("SQLiteManagerのテストが正常に完了しました。")
