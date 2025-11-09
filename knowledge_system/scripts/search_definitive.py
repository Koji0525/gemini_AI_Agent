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


def search_knowledge(query, top_k=5):
    """確実なナレッジ検索"""
    try:
        db_path = os.path.join(parent_dir, "database", "knowledge.db")
        index_dir = os.path.join(parent_dir, "database", "faiss_index")

        print(f"🔍 検索クエリ: {query}")

        db = DatabaseManager(db_path)
        model = EmbeddingModel()

        # 統計情報表示
        stats = db.get_sync_stats()
        print(
            f"📊 システム状態: {stats['total_entries']}エントリー, {stats['synced_entries']}同期済み ({stats['sync_percentage']:.1f}%)"
        )

        # キーワード検索
        print("🔍 キーワード検索実行中...")
        keyword_results = db.search_entries(query=query, limit=top_k)
        print(f"✅ キーワード検索: {len(keyword_results)}件")

        # ベクトル検索（同期済みエントリーがある場合）
        vector_results = []
        if stats["synced_entries"] > 0:
            print("🧠 ベクトル検索実行中...")
            query_embedding = model.get_embedding(query)
            if query_embedding is not None:
                vector_results = db.vector_search(query_embedding, top_k=top_k, index_dir=index_dir)
                print(f"✅ ベクトル検索: {len(vector_results)}件")

        # 結果の統合と表示
        all_results = keyword_results + vector_results

        # 重複排除（IDベース）
        seen_ids = set()
        unique_results = []
        for result in all_results:
            if result["id"] not in seen_ids:
                seen_ids.add(result["id"])
                unique_results.append(result)

        print(
            f"\n📊 検索結果: {len(unique_results)}件 (キーワード: {len(keyword_results)}, ベクトル: {len(vector_results)})"
        )

        if unique_results:
            for i, result in enumerate(unique_results[:top_k], 1):
                print(
                    f"\n  {i}. {result.get('title', 'No title')} ({result.get('category', 'No category')})"
                )
                print(f"     内容: {result.get('content', 'No content')[:100]}...")
                print(f"     タグ: {result.get('tags', '[]')}")
                if "similarity" in result:
                    print(f"     類似度: {result['similarity']:.3f}")
        else:
            print("❌ 該当するナレッジが見つかりませんでした")

        return unique_results[:top_k]

    except Exception as e:
        print(f"❌ 検索中にエラー: {e}")
        return []


def main():
    if len(sys.argv) < 2:
        print('使用方法: python search_definitive.py "検索クエリ" [結果数]')
        print('例: python search_definitive.py "根本問題" 5')
        sys.exit(1)

    query = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    search_knowledge(query, top_k)


if __name__ == "__main__":
    main()
