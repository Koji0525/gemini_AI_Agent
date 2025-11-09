#!/usr/bin/env python3
"""
根本問題解決スクリプト
データベーススキーマとメソッドの不一致を一気に解決
"""
import os
import sqlite3
import sys

# プロジェクトルートをパスに追加
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)


def fix_database_schema():
    """データベーススキーマの問題を解決"""
    print("🔧 データベーススキーマを修正...")

    db_path = "knowledge_system/database/knowledge.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. vector_mappings テーブルに entry_id カラムを追加（既存の knowledge_id と互換性を保つ）
    try:
        cursor.execute("ALTER TABLE vector_mappings ADD COLUMN entry_id TEXT")
        print("✅ vector_mappings に entry_id カラムを追加")
    except sqlite3.OperationalError:
        print("ℹ️  entry_id カラムは既に存在します")

    # 2. knowledge_entries に content カラムを追加（既存の cause カラムからデータを移行）
    try:
        cursor.execute("ALTER TABLE knowledge_entries ADD COLUMN content TEXT")
        print("✅ knowledge_entries に content カラムを追加")

        # cause カラムのデータを content にコピー
        cursor.execute("UPDATE knowledge_entries SET content = cause WHERE content IS NULL")
        print("✅ cause カラムのデータを content にコピー")
    except sqlite3.OperationalError:
        print("ℹ️  content カラムは既に存在します")

    conn.commit()
    conn.close()
    print("✅ データベーススキーマ修正完了")


def fix_sqlite_manager_methods():
    """SQLiteManagerのメソッド名を修正"""
    print("🔧 SQLiteManagerのメソッドを修正...")

    sqlite_manager_path = "knowledge_system/core_agents/sqlite_manager.py"

    with open(sqlite_manager_path, "r") as f:
        content = f.read()

    # add_knowledge_entry メソッドを add_knowledge にエイリアス
    if "def add_knowledge(" in content and "def add_knowledge_entry(" not in content:
        # add_knowledge_entry メソッドを追加
        new_method = '''
    def add_knowledge_entry(self, title, content, category="general", tags=""):
        """add_knowledge_entry - add_knowledge のエイリアス"""
        return self.add_knowledge(title, content, category, tags)
'''
        # クラスの最後にメソッドを追加
        if "class SQLiteKnowledgeManager" in content:
            # 最後の } の前にメソッドを挿入
            last_brace = content.rfind("}")
            if last_brace != -1:
                content = content[:last_brace] + new_method + "\\n" + content[last_brace:]
                print("✅ add_knowledge_entry メソッドを追加")

    with open(sqlite_manager_path, "w") as f:
        f.write(content)

    print("✅ SQLiteManagerメソッド修正完了")


def fix_knowledge_manager_initialization():
    """KnowledgeManagerの初期化問題を修正"""
    print("🔧 KnowledgeManagerの初期化を修正...")

    km_path = "knowledge_system/core_agents/knowledge_manager.py"

    with open(km_path, "r") as f:
        content = f.read()

    # db_path が None の場合のデフォルト値を設定
    if "def __init__(self, db_path: str = None):" in content:
        # 初期化コードを修正
        old_init = """    def __init__(self, db_path: str = None):
        self.db_manager = SQLiteKnowledgeManager(db_path)
        self.vector_agent = HybridSearchAgent(
            "knowledge_system/database/faiss_index/knowledge.index"
        )"""

        new_init = """    def __init__(self, db_path: str = None):
        # db_path が None の場合のデフォルト値を設定
        if db_path is None:
            db_path = "knowledge_system/database/knowledge.db"
        self.db_manager = SQLiteKnowledgeManager(db_path)
        self.vector_agent = HybridSearchAgent(
            "knowledge_system/database/faiss_index/knowledge.index"
        )"""

        content = content.replace(old_init, new_init)
        print("✅ KnowledgeManager初期化を修正")

    with open(km_path, "w") as f:
        f.write(content)

    print("✅ KnowledgeManager初期化修正完了")


def create_unified_import_solution():
    """統合インポート解決策を作成"""
    print("🔧 統合インポート解決策を作成...")

    # プロジェクトルートに setup.py を作成
    setup_content = """
from setuptools import setup, find_packages

setup(
    name="knowledge_system",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "faiss-cpu",
        "sentence-transformers",
        "sqlite3",
    ],
)
"""
    with open("knowledge_system/setup.py", "w") as f:
        f.write(setup_content)

    print("✅ 統合インポート解決策を作成完了")


if __name__ == "__main__":
    print("🚀 根本問題解決スクリプトを開始")

    fix_database_schema()
    fix_sqlite_manager_methods()
    fix_knowledge_manager_initialization()
    create_unified_import_solution()

    print("🎉 根本問題解決完了！")
