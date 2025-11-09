#!/usr/bin/env python3
"""
データ同期スクリプト - 確実に動作する版
"""
import os
import sys

import faiss
import numpy as np

# ユーティリティをインポート
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.database import get_db_connection, get_stats
from utils.models import get_embedding, get_embedding_dimension


def sync_data():
    """データを同期"""
    print("🔄 データ同期を開始...")

    conn = get_db_connection()
    cursor = conn.cursor()

    # 統計取得
    stats = get_stats()
    print(f"📊 現在: {stats['total_entries']}エントリー, {stats['total_mappings']}マッピング")

    # マッピングされていないエントリーを検出
    cursor.execute(
        """
        SELECT ke.id, ke.title, ke.cause 
        FROM knowledge_entries ke
        LEFT JOIN vector_mappings vm ON ke.id = vm.knowledge_id
        WHERE vm.knowledge_id IS NULL
    """
    )
    missing_entries = cursor.fetchall()

    print(f"🔍 未マッピングエントリー: {len(missing_entries)}件")

    if not missing_entries:
        print("✅ すべてのエントリーが同期済みです")
        conn.close()
        return

    # FAISSインデックスの準備
    index_path = os.path.join(
        os.path.dirname(__file__), "..", "database", "faiss_index", "knowledge.index"
    )
    embedding_dim = get_embedding_dimension()

    try:
        index = faiss.read_index(index_path)
        print(f"✅ 既存インデックスをロード: {index.ntotal}件")
    except:
        print("📝 新規インデックスを作成")
        index = faiss.IndexFlatIP(embedding_dim)

    # 未マッピングエントリーを処理
    success_count = 0
    for entry_id, title, content in missing_entries:
        try:
            if not content:
                continue

            # 埋め込み生成
            embedding = get_embedding(content)
            embedding_array = np.array([embedding], dtype="float32")

            # FAISSに追加
            index.add(embedding_array)
            faiss_index = index.ntotal - 1

            # マッピングテーブルに登録
            cursor.execute(
                """
                INSERT INTO vector_mappings (knowledge_id, vector_index)
                VALUES (?, ?)
            """,
                (entry_id, faiss_index),
            )

            success_count += 1
            if success_count % 50 == 0:
                print(f"  進行状況: {success_count}/{len(missing_entries)}")

        except Exception as e:
            print(f"❌ エラー (ID {entry_id}): {e}")

    # 変更を保存
    conn.commit()
    conn.close()

    # FAISSインデックスを保存
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    faiss.write_index(index, index_path)

    print(f"✅ 同期完了: {success_count}件を追加")

    # 最終統計
    stats = get_stats()
    print(
        f"📊 同期後: {stats['total_entries']}エントリー, {stats['total_mappings']}マッピング ({stats['sync_rate']:.1f}%)"
    )


def main():
    try:
        sync_data()
    except Exception as e:
        print(f"❌ 同期失敗: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
