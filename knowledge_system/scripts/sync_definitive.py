#!/usr/bin/env python3
import os
import sys

# 絶対パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
utils_dir = os.path.join(parent_dir, "utils")

print(f"🔧 カレントディレクトリ: {current_dir}")
print(f"🔧 ユーティリティディレクトリ: {utils_dir}")

# 確実なインポート方法
try:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "models_fixed", os.path.join(utils_dir, "models_fixed.py")
    )
    models_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models_module)
    EmbeddingModel = models_module.EmbeddingModel

    spec = importlib.util.spec_from_file_location(
        "database_fixed", os.path.join(utils_dir, "database_fixed.py")
    )
    database_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(database_module)
    DatabaseManager = database_module.DatabaseManager

    print("✅ 直接インポート成功")

except Exception as e:
    print(f"❌ 直接インポート失敗: {e}")
    sys.exit(1)


def sync_all_entries():
    """すべてのエントリーを確実に同期"""
    try:
        db_path = os.path.join(parent_dir, "database", "knowledge.db")
        index_dir = os.path.join(parent_dir, "database", "faiss_index")

        print(f"🔧 データベースパス: {db_path}")
        print(f"🔧 インデックスディレクトリ: {index_dir}")

        db = DatabaseManager(db_path)
        model = EmbeddingModel()

        # 同期統計の取得
        stats = db.get_sync_stats()
        print(
            f"📊 同期前状態: {stats['total_entries']}エントリー, {stats['synced_entries']}同期済み ({stats['sync_percentage']:.1f}%)"
        )

        # 未同期エントリーの取得
        unsynced_entries = db.get_unsynced_entries()
        print(f"🔍 未同期エントリー: {len(unsynced_entries)}件")

        if not unsynced_entries:
            print("✅ すべてのエントリーが同期済みです")
            return True

        # バッチ処理で同期
        successful_syncs = 0
        total_entries = len(unsynced_entries)

        for i, entry in enumerate(unsynced_entries, 1):
            try:
                print(f"🔄 同期中 ({i}/{total_entries}): {entry['title'][:50]}...")

                # 埋め込み生成
                combined_text = f"{entry['title']} {entry['content']} {entry.get('tags', '')}"
                embedding = model.get_embedding(combined_text)

                if embedding is not None:
                    # ベクトルインデックスに追加
                    success = db.add_to_vector_index(entry["id"], embedding, index_dir)
                    if success:
                        successful_syncs += 1
                        print(f"  ✅ 同期成功: ID {entry['id']}")
                    else:
                        print(f"  ⚠️  同期失敗: ID {entry['id']}")
                else:
                    print(f"  ⚠️  埋め込み生成失敗: ID {entry['id']}")

            except Exception as e:
                print(f"  ❌ エントリー同期エラー (ID {entry['id']}): {e}")
                continue

        # 最終統計
        final_stats = db.get_sync_stats()
        print(f"\n�� 同期完了: {successful_syncs}/{total_entries} 件成功")
        print(
            f"📊 同期後状態: {final_stats['total_entries']}エントリー, {final_stats['synced_entries']}同期済み ({final_stats['sync_percentage']:.1f}%)"
        )

        return successful_syncs > 0

    except Exception as e:
        print(f"❌ 同期処理中にエラー: {e}")
        return False


def main():
    print("🚀 確実な同期処理を開始")
    success = sync_all_entries()

    if success:
        print("🎉 同期処理完了")
    else:
        print("💥 同期処理失敗")
        sys.exit(1)


if __name__ == "__main__":
    main()
