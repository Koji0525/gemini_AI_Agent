#!/usr/bin/env python3
import os
import sqlite3
import sys


def recreate_database():
    # 絶対パスを使用
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(current_dir, "..", "database")
    db_path = os.path.join(db_dir, "knowledge.db")

    print(f"🔧 データベースパス: {db_path}")

    # ディレクトリ作成
    os.makedirs(db_dir, exist_ok=True)

    # 既存ファイルのバックアップ
    if os.path.exists(db_path):
        backup_path = db_path + ".backup"
        os.rename(db_path, backup_path)
        print(f"✅ 既存データベースをバックアップ: {backup_path}")

    try:
        # データベース接続とテーブル作成
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 知識エントリー用テーブル（シンプル版）
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                tags TEXT DEFAULT '',
                scenario TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                embedding BLOB,
                vector_synced BOOLEAN DEFAULT FALSE
            )
        """
        )

        # ベクトルマッピング用テーブル
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS vector_mappings (
                entry_id INTEGER,
                vector_index INTEGER,
                FOREIGN KEY (entry_id) REFERENCES knowledge_entries (id)
            )
        """
        )

        # インデックス作成
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON knowledge_entries(title)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON knowledge_entries(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created ON knowledge_entries(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_synced ON knowledge_entries(vector_synced)")

        conn.commit()

        # テストデータの挿入
        test_data = [
            ("テストナレッジ1", "これはテスト用のナレッジデータです", "test", "テスト,サンプル"),
            ("AI開発", "AI開発におけるベストプラクティス", "technology", "AI,開発"),
            ("問題解決", "なぜなぜ分析による根本原因の追求", "analysis", "問題解決,分析"),
        ]

        for title, content, category, tags in test_data:
            cursor.execute(
                """
                INSERT INTO knowledge_entries (title, content, category, tags)
                VALUES (?, ?, ?, ?)
            """,
                (title, content, category, tags),
            )

        conn.commit()

        # テーブル確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("📋 作成されたテーブル:")
        for table in tables:
            print(f"  - {table[0]}")

        cursor.execute("SELECT COUNT(*) FROM knowledge_entries")
        count = cursor.fetchone()[0]
        print(f"📊 テストデータ数: {count}件")

        conn.close()
        print("✅ データベース再構築完了")
        return True

    except Exception as e:
        print(f"❌ データベース作成失敗: {e}")
        return False


if __name__ == "__main__":
    success = recreate_database()
    sys.exit(0 if success else 1)
