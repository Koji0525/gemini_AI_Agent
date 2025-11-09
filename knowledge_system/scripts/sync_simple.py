#!/usr/bin/env python3
"""
データ同期スクリプト - 絶対確実版
"""
import os
import sys

import faiss
import numpy as np

# 絶対確実なパス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
utils_dir = os.path.join(current_dir, "..", "utils")
sys.path.insert(0, utils_dir)

print(f"🔧 カレントディレクトリ: {current_dir}")
print(f"🔧 ユーティリティディレクトリ: {utils_dir}")

try:
    from database import get_db_connection, get_stats
    from models import get_embedding, get_embedding_dimension

    print("✅ インポート成功")
except ImportError as e:
    print(f"❌ インポート失敗: {e}")
    sys.exit(1)


def sync_data():
    """データを確実に同期"""
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
        return True

    # FAISSインデックスの準備
    current_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(current_dir, "..", "database", "faiss_index", "knowledge.index")
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
    return True


def main():
    try:
        success = sync_data()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ 同期失敗: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
