#!/usr/bin/env python3
"""
ベクトルマッピング同期ツール - 直接実行版
"""
import os
import sys

# スクリプトのディレクトリを基準にパスを設定
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

print(f"🔧 パス設定: {project_root}")

try:
    from knowledge_system.core_agents.model_cache import ModelCache

    print("✅ モデルキャッシュインポート成功")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    sys.path.insert(0, os.path.join(project_root, "knowledge_system"))
    from core_agents.model_cache import ModelCache

    print("✅ 代替インポート成功")

import sqlite3
from datetime import datetime

import faiss
import numpy as np


def check_sync_status():
    """同期状態をチェック"""
    db_path = "knowledge_system/database/knowledge.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM knowledge_entries")
    entries_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM vector_mappings")
    mappings_count = cursor.fetchone()[0]

    # FAISSインデックスの件数確認
    index_path = "knowledge_system/database/faiss_index/knowledge.index"
    index = faiss.read_index(index_path)
    faiss_count = index.ntotal

    conn.close()

    print("🔄 同期状態チェック:")
    print(f"  📊 ナレッジエントリー: {entries_count}件")
    print(f"  🗂️  ベクトルマッピング: {mappings_count}件")
    print(f"  🔍 FAISSインデックス: {faiss_count}件")

    status = "✅ 同期済み" if entries_count == mappings_count == faiss_count else "❌ 非同期"
    print(f"  ステータス: {status}")

    return {
        "entries_count": entries_count,
        "mappings_count": mappings_count,
        "faiss_count": faiss_count,
        "is_synced": entries_count == mappings_count == faiss_count,
    }


def sync_vector_mappings():
    """ベクトルマッピングを同期"""
    print("🔄 ベクトルマッピング同期を開始...")

    status = check_sync_status()
    if status["is_synced"]:
        print("✅ 既に同期済みです")
        return

    db_path = "knowledge_system/database/knowledge.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # マッピングが不足しているエントリーを検出
    cursor.execute(
        """
        SELECT ke.id, ke.title, ke.content 
        FROM knowledge_entries ke
        LEFT JOIN vector_mappings vm ON ke.id = vm.entry_id
        WHERE vm.entry_id IS NULL
    """
    )
    missing_entries = cursor.fetchall()

    print(f"🔍 マッピング不足エントリー: {len(missing_entries)}件")

    if not missing_entries:
        print("✅ 不足エントリーはありません")
        conn.close()
        return

    # モデルとFAISSインデックスを準備
    model = ModelCache.get_model()
    index_path = "knowledge_system/database/faiss_index/knowledge.index"
    index = faiss.read_index(index_path)

    # 不足分の埋め込みを生成して登録
    for entry_id, title, content in missing_entries:
        try:
            # 埋め込み生成
            embedding = model.encode(content)
            embedding_array = np.array([embedding], dtype="float32")

            # FAISSインデックスに追加
            index.add(embedding_array)
            faiss_id = index.ntotal - 1  # 追加されたインデックス

            # ベクトルマッピングテーブルに登録
            cursor.execute(
                """
                INSERT INTO vector_mappings (entry_id, faiss_index, created_at)
                VALUES (?, ?, ?)
            """,
                (entry_id, faiss_id, datetime.now()),
            )

            print(f"✅ 同期: {title} (ID: {entry_id} → FAISS: {faiss_id})")

        except Exception as e:
            print(f"❌ 同期失敗 {entry_id}: {e}")

    # 変更を保存
    conn.commit()
    conn.close()

    # FAISSインデックスを保存
    faiss.write_index(index, index_path)

    print("✅ ベクトルマッピング同期完了")
    check_sync_status()


if __name__ == "__main__":
    sync_vector_mappings()
