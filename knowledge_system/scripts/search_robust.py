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


def robust_search(query, top_k=5):
    """確実に動作する検索関数"""
    try:
        print(f"🔍 検索クエリ: {query}")

        # パス設定
        db_path = os.path.join(parent_dir, "database", "knowledge.db")
        index_dir = os.path.join(parent_dir, "database", "faiss_index")

        # データベースマネージャー初期化
        db_manager = DatabaseManager(db_path)

        # 統計情報表示
        stats = db_manager.get_sync_stats()
        print(
            f"📊 システム状態: {stats['total_entries']}エントリー, {stats['synced_entries']}同期済み ({stats['sync_percentage']:.1f}%)"
        )

        if stats["synced_entries"] == 0:
            print("⚠️  同期済みエントリーがありません。まず同期を実行してください。")
            return []

        # モデル初期化
        print("📥 モデルをロード中...")
        model = EmbeddingModel()
        print("✅ モデルロード成功")

        # クエリの埋め込み生成
        query_embedding = model.get_embedding(query)
        if query_embedding is None:
            print("❌ クエリの埋め込み生成失敗")
            return []

        # ベクトル検索実行
        print("🔍 ベクトル検索実行中...")
        results = db_manager.vector_search(query_embedding, top_k=top_k, index_dir=index_dir)

        print(f"✅ 検索成功: {len(results)}件")
        return results

    except Exception as e:
        print(f"❌ 検索中にエラー: {e}")
        return []


def main():
    if len(sys.argv) < 2:
        print('使用方法: python search_robust.py "検索クエリ" [結果数]')
        print('例: python search_robust.py "機械学習" 5')
        sys.exit(1)

    query = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    results = robust_search(query, top_k)

    if results:
        print(f"✅ {len(results)}件見つかりました:")
        for i, result in enumerate(results, 1):
            print(
                f"  {i}. {result.get('title', 'No title')} ({result.get('category', 'No category')})"
            )
            print(f"     内容: {result.get('content', 'No content')[:100]}...")
            print(f"     タグ: {result.get('tags', '[]')}")
            print()
    else:
        print("❌ 該当するナレッジが見つかりませんでした")


if __name__ == "__main__":
    main()
