# knowledge_system/tests/test_database.py
import pytest
from pathlib import Path
import os
import sys

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core_agents.sqlite_manager import SQLiteManager
from core_agents.data_models import KnowledgeEntry

# テスト用のデータベースパス
TEST_DB_PATH = project_root / "tests" / "test_knowledge.db"

@pytest.fixture(scope="function")
def db_manager():
    """
    各テスト関数のために、クリーンなデータベースでSQLiteManagerインスタンスをセットアップします。
    テスト終了後にデータベースファイルをクリーンアップします。
    """
    # テスト前に古いデータベースファイルが存在すれば削除
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    manager = SQLiteManager(str(TEST_DB_PATH))
    yield manager

    # テスト後に接続を閉じてファイルを削除
    manager.close()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

def test_add_and_get_entry(db_manager: SQLiteManager):
    """ナレッジエントリーの追加と取得が正しく機能するかをテストします。"""
    entry = KnowledgeEntry(
        content="これはテストコンテンツです。",
        category="Test",
        tags=["pytest", "sqlite"],
        metadata={"author": "Jules"}
    )

    # 1. エントリーを追加
    db_manager.add_entry(entry)

    # 2. エントリーを取得して検証
    retrieved_entry = db_manager.get_entry(entry.id)

    assert retrieved_entry is not None
    assert retrieved_entry.id == entry.id
    assert retrieved_entry.content == "これはテストコンテンツです。"
    assert retrieved_entry.category == "Test"
    assert retrieved_entry.tags == ["pytest", "sqlite"]
    assert retrieved_entry.metadata == {"author": "Jules"}
    assert retrieved_entry.created_at.date() == entry.created_at.date()

def test_get_nonexistent_entry(db_manager: SQLiteManager):
    """存在しないエントリーを取得しようとするとNoneが返されることをテストします。"""
    retrieved_entry = db_manager.get_entry("nonexistent-id")
    assert retrieved_entry is None

def test_update_entry(db_manager: SQLiteManager):
    """既存のエントリーを更新する機能をテストします。"""
    entry = KnowledgeEntry(content="オリジナルのコンテンツ。")
    db_manager.add_entry(entry)

    # 取得したエントリーを更新
    entry_to_update = db_manager.get_entry(entry.id)
    entry_to_update.content = "更新されたコンテンツ。"
    entry_to_update.category = "Updated"
    entry_to_update.tags.append("edited")

    db_manager.update_entry(entry_to_update)

    # 再度取得して更新が反映されているか検証
    updated_entry = db_manager.get_entry(entry.id)
    assert updated_entry.content == "更新されたコンテンツ。"
    assert updated_entry.category == "Updated"
    assert "edited" in updated_entry.tags
    assert updated_entry.updated_at > updated_entry.created_at

def test_delete_entry(db_manager: SQLiteManager):
    """エントリーを削除する機能をテストします。"""
    entry = KnowledgeEntry(content="削除される予定のコンテンツ。")
    db_manager.add_entry(entry)

    # エントリーが存在することを確認
    assert db_manager.get_entry(entry.id) is not None

    # エントリーを削除
    db_manager.delete_entry(entry.id)

    # 削除後にエントリーが存在しないことを確認
    assert db_manager.get_entry(entry.id) is None

def test_get_all_entries(db_manager: SQLiteManager):
    """すべてのエントリーを取得する機能をテストします。"""
    # 最初にエントリーがないことを確認
    assert len(db_manager.get_all_entries()) == 0

    # 複数のエントリーを追加
    entry1 = KnowledgeEntry(content="エントリー1")
    entry2 = KnowledgeEntry(content="エントリー2")
    db_manager.add_entry(entry1)
    db_manager.add_entry(entry2)

    # すべてのエントリーを取得し、数が正しいことを確認
    all_entries = db_manager.get_all_entries()
    assert len(all_entries) == 2

    # IDが一致することを確認 (順序は作成日時の降順)
    entry_ids = {e.id for e in all_entries}
    assert {entry1.id, entry2.id} == entry_ids

def test_add_duplicate_id_raises_error(db_manager: SQLiteManager):
    """同じIDのエントリーを追加しようとするとエラーが発生することをテストします。"""
    entry = KnowledgeEntry(content="重複IDテスト")
    db_manager.add_entry(entry)

    # 同じIDを持つ新しいインスタンスで再度追加
    duplicate_entry = KnowledgeEntry(id=entry.id, content="重複コンテンツ")

    with pytest.raises(Exception): # sqlite3.IntegrityErrorをキャッチ
        db_manager.add_entry(duplicate_entry)
