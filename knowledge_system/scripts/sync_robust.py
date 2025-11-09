#!/usr/bin/env python3
import os
import sys

# パス設定を確実化
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, "utils"))

try:
    from utils.database import DatabaseManager
    from utils.models import EmbeddingModel

    print("✅ インポート成功")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    sys.exit(1)


def robust_sync():
    """確実に動作する同期関数"""
    try:
        print("🔄 堅牢なデータ同期を開始...")

        # パス設定
        db_path = os.path.join(parent_dir, "database", "knowledge.db")
        index_dir = os.path.join(parent_dir, "database", "faiss_index")
        os.path.join(index_dir, "index_mapping.json")

        # ディレクトリ作成
        os.makedirs(index_dir, exist_ok=True)

        # データベースマネージャー初期化
        db_manager = DatabaseManager(db_path)

        # 統計情報取得
        stats = db_manager.get_sync_stats()
        print(
            f"📊 現在の状態: {stats['total_entries']}エントリー, {stats['synced_entries']}同期済み ({stats['sync_percentage']:.1f}%)"
        )

        # モデル初期化
        print("📥 モデルをロード中...")
        model = EmbeddingModel()
        print("✅ モデルロード成功")

        # 未同期エントリーを取得
        unsynced_entries = db_manager.get_unsynced_entries()
        print(f"🔍 未同期エントリー: {len(unsynced_entries)}件")

        if not unsynced_entries:
            print("✅ すべてのエントリーが同期済みです")
            return True

        # バッチ処理で同期（メモリ効率化）
        batch_size = 50
        successful_syncs = 0

        for i in range(0, len(unsynced_entries), batch_size):
            batch = unsynced_entries[i : i + batch_size]
            print(
                f"🔄 バッチ処理: {i+1}-{min(i+batch_size, len(unsynced_entries))}/{len(unsynced_entries)}"
            )

            for entry in batch:
                try:
                    # 埋め込み生成
                    combined_text = f"{entry['title']} {entry['content']} {entry.get('tags', '')}"
                    embedding = model.get_embedding(combined_text)

                    if embedding is not None:
                        # ベクトルインデックスに追加
                        success = db_manager.add_to_vector_index(entry["id"], embedding, index_dir)
                        if success:
                            successful_syncs += 1
                        else:
                            print(f"⚠️  インデックス追加失敗: ID {entry['id']}")
                    else:
                        print(f"⚠️  埋め込み生成失敗: ID {entry['id']}")

                except Exception as e:
                    print(f"⚠️  エントリー処理中エラー (ID {entry['id']}): {e}")
                    continue

            # 進捗表示
            progress = min(i + batch_size, len(unsynced_entries))
            print(f"  進行状況: {progress}/{len(unsynced_entries)}")

        # 最終統計
        final_stats = db_manager.get_sync_stats()
        print(f"📊 同期完了: {successful_syncs}件を追加")
        print(
            f"📊 最終状態: {final_stats['total_entries']}エントリー, {final_stats['synced_entries']}同期済み ({final_stats['sync_percentage']:.1f}%)"
        )

        return successful_syncs > 0

    except Exception as e:
        print(f"❌ 同期中にエラー: {e}")
        return False


def main():
    print("🚀 堅牢な同期処理を開始")
    success = robust_sync()

    if success:
        print("🎉 同期処理完了")
    else:
        print("💥 同期処理失敗")
        sys.exit(1)


if __name__ == "__main__":
    main()
