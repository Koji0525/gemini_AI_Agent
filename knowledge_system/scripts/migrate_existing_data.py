#!/usr/bin/env python3
import os
import sqlite3
from datetime import datetime

# 絶対パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)


def get_backup_db_paths():
    """バックアップDBのパスを取得"""
    backup_paths = [
        os.path.join(parent_dir, "database", "backups", "backup_20251109_021909", "knowledge.db"),
        os.path.join(parent_dir, "knowledge_system", "database", "knowledge.db"),
        os.path.join(parent_dir, "database", "knowledge.db.backup"),
    ]

    existing_backups = []
    for path in backup_paths:
        if os.path.exists(path):
            existing_backups.append(path)

    return existing_backups


def analyze_backup_database(backup_path):
    """バックアップデータベースの分析"""
    print(f"🔍 バックアップ分析: {backup_path}")

    try:
        conn = sqlite3.connect(backup_path)
        cursor = conn.cursor()

        # テーブル一覧を取得
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 テーブル一覧: {tables}")

        if "knowledge_entries" in tables:
            # ナレッジエントリーの統計
            cursor.execute("SELECT COUNT(*) FROM knowledge_entries")
            total_entries = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT category) FROM knowledge_entries")
            category_count = cursor.fetchone()[0]

            cursor.execute(
                "SELECT category, COUNT(*) FROM knowledge_entries GROUP BY category ORDER BY COUNT(*) DESC LIMIT 10"
            )
            top_categories = cursor.fetchall()

            print(f"📊 ナレッジエントリー: {total_entries}件")
            print(f"�� カテゴリ数: {category_count}件")
            print("🏷️  主要カテゴリ:")
            for category, count in top_categories:
                print(f"    - {category}: {count}件")

            # サンプルデータの表示
            cursor.execute(
                "SELECT title, category, created_at FROM knowledge_entries ORDER BY created_at DESC LIMIT 3"
            )
            sample_entries = cursor.fetchall()
            print("📝 最新エントリーサンプル:")
            for title, category, created_at in sample_entries:
                print(f"    - {title} ({category}) - {created_at}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ バックアップ分析失敗: {e}")
        return False


def migrate_data(source_db_path, target_db_path):
    """データの移行"""
    print(f"🔄 データ移行開始: {source_db_path} → {target_db_path}")

    try:
        # ソースDB接続
        source_conn = sqlite3.connect(source_db_path)
        source_cursor = source_conn.cursor()

        # ターゲットDB接続
        target_conn = sqlite3.connect(target_db_path)
        target_cursor = target_conn.cursor()

        # ソースのテーブル構造を確認
        source_cursor.execute("PRAGMA table_info(knowledge_entries)")
        source_columns = {row[1]: row[2] for row in source_cursor.fetchall()}

        # ターゲットのテーブル構造を確認
        target_cursor.execute("PRAGMA table_info(knowledge_entries)")
        target_columns = {row[1]: row[2] for row in target_cursor.fetchall()}

        print("📋 カラムマッピング:")
        common_columns = set(source_columns.keys()) & set(target_columns.keys())
        for col in common_columns:
            print(f"    ✅ {col}: {source_columns[col]} → {target_columns[col]}")

        # データ移行
        source_cursor.execute("SELECT * FROM knowledge_entries")
        source_data = source_cursor.fetchall()

        migrated_count = 0
        for row in source_data:
            try:
                # カラム名と値のマッピングを作成
                column_names = [desc[0] for desc in source_cursor.description]
                row_dict = dict(zip(column_names, row))

                # 新しいテーブル構造に合わせてデータを変換
                insert_data = {
                    "title": row_dict.get("title", ""),
                    "content": row_dict.get("content", "") or row_dict.get("solution", ""),
                    "category": row_dict.get("category", "general"),
                    "tags": row_dict.get("tags", ""),
                    "scenario": row_dict.get("scenario", "general"),
                    "created_at": row_dict.get("created_at", datetime.now().isoformat()),
                }

                # 新しいDBに挿入
                target_cursor.execute(
                    """
                    INSERT INTO knowledge_entries 
                    (title, content, category, tags, scenario, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        insert_data["title"],
                        insert_data["content"],
                        insert_data["category"],
                        insert_data["tags"],
                        insert_data["scenario"],
                        insert_data["created_at"],
                    ),
                )

                migrated_count += 1

                if migrated_count % 100 == 0:
                    print(f"  進行状況: {migrated_count}/{len(source_data)} 件移行")

            except Exception as e:
                print(f"  ⚠️  エントリー移行失敗: {e}")
                continue

        target_conn.commit()

        source_conn.close()
        target_conn.close()

        print(f"✅ 移行完了: {migrated_count}/{len(source_data)} 件成功")
        return migrated_count

    except Exception as e:
        print(f"❌ 移行失敗: {e}")
        return 0


def main():
    print("�� 既存データ移行ツール")
    print("=" * 50)

    # バックアップパスの確認
    backup_paths = get_backup_db_paths()

    if not backup_paths:
        print("❌ バックアップデータベースが見つかりません")
        return

    print("📦 見つかったバックアップ:")
    for i, path in enumerate(backup_paths, 1):
        print(f"  {i}. {path}")

    # バックアップの分析
    for backup_path in backup_paths:
        analyze_backup_database(backup_path)
        print()

    # メインデータベースのパス
    target_db_path = os.path.join(parent_dir, "database", "knowledge.db")

    print(f"🎯 移行先: {target_db_path}")

    # 移行の確認
    response = input("移行を実行しますか？ (y/N): ").strip().lower()
    if response not in ["y", "yes"]:
        print("移行をキャンセルしました")
        return

    # 各バックアップから順次移行
    total_migrated = 0
    for backup_path in backup_paths:
        print(f"\n🔄 {backup_path} から移行開始...")
        migrated = migrate_data(backup_path, target_db_path)
        total_migrated += migrated

    print(f"\n🎉 移行完了: 合計 {total_migrated} 件のナレッジを移行しました")

    # 最終確認
    if os.path.exists(target_db_path):
        conn = sqlite3.connect(target_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM knowledge_entries")
        final_count = cursor.fetchone()[0]
        conn.close()
        print(f"📊 現在の総ナレッジ数: {final_count}件")


if __name__ == "__main__":
    main()
