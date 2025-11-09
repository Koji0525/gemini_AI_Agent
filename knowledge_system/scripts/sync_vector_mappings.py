#!/usr/bin/env python3
"""
ベクトルマッピング同期ツール
データベースとFAISSインデックスの整合性を確保
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from datetime import datetime

import faiss
import numpy as np

from knowledge_system.core_agents.model_cache import ModelCache


def check_sync_status():
    """同期状態をチェック"""
    conn = sqlite3.connect("knowledge_system/database/knowledge.db")
    cursor = conn.cursor()

    # エントリー数とマッピング数を比較
    cursor.execute("SELECT COUNT(*) FROM knowledge_entries")
    entries_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM vector_mappings")
    mappings_count = cursor.fetchone()[0]

    # FAISSインデックスの件数確認
    index = faiss.read_index("knowledge_system/database/faiss_index/knowledge.index")
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
    print("�� ベクトルマッピング同期を開始...")

    status = check_sync_status()
    if status["is_synced"]:
        print("✅ 既に同期済みです")
        return

    conn = sqlite3.connect("knowledge_system/database/knowledge.db")
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
    index = faiss.read_index("knowledge_system/database/faiss_index/knowledge.index")

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
    faiss.write_index(index, "knowledge_system/database/faiss_index/knowledge.index")

    print("✅ ベクトルマッピング同期完了")
    check_sync_status()


def rebuild_vector_index():
    """ベクトルインデックスを完全再構築"""
    print("🔄 ベクトルインデックス再構築を開始...")

    conn = sqlite3.connect("knowledge_system/database/knowledge.db")
    cursor = conn.cursor()

    # すべてのエントリーを取得
    cursor.execute("SELECT id, content FROM knowledge_entries")
    all_entries = cursor.fetchall()

    print(f"📊 再構築対象: {len(all_entries)}件")

    if not all_entries:
        print("❌ 再構築対象がありません")
        return

    # モデル準備
    model = ModelCache.get_model()
    embedding_dim = model.get_sentence_embedding_dimension()

    # 新しいFAISSインデックスを作成
    index = faiss.IndexFlatIP(embedding_dim)

    # ベクトルマッピングテーブルをクリア
    cursor.execute("DELETE FROM vector_mappings")

    # すべてのエントリーを再処理
    embeddings = []
    mapping_data = []

    for entry_id, content in all_entries:
        embedding = model.encode(content)
        embeddings.append(embedding)
        mapping_data.append((entry_id, len(embeddings) - 1, datetime.now()))

    # FAISSインデックスに一括追加
    if embeddings:
        embedding_array = np.array(embeddings, dtype="float32")
        index.add(embedding_array)

    # ベクトルマッピングを一括登録
    cursor.executemany(
        """
        INSERT INTO vector_mappings (entry_id, faiss_index, created_at)
        VALUES (?, ?, ?)
    """,
        mapping_data,
    )

    # 変更を保存
    conn.commit()
    conn.close()

    # 新しいインデックスを保存
    faiss.write_index(index, "knowledge_system/database/faiss_index/knowledge.index")

    print("✅ ベクトルインデックス再構築完了")
    check_sync_status()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rebuild":
        rebuild_vector_index()
    else:
        sync_vector_mappings()
