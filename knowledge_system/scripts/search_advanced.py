#!/usr/bin/env python3
import argparse
import os
import sys
from typing import Any, Dict, List

# 絶対パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
utils_dir = os.path.join(parent_dir, "utils")

sys.path.insert(0, parent_dir)
sys.path.insert(0, utils_dir)

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

except Exception as e:
    print(f"❌ インポート失敗: {e}")
    sys.exit(1)


class AdvancedSearchEngine:
    """高度な検索エンジン - 複数戦略とフィルタリング対応"""

    def __init__(self):
        self.db_path = os.path.join(parent_dir, "database", "knowledge.db")
        self.index_dir = os.path.join(parent_dir, "database", "faiss_index")
        self.db = DatabaseManager(self.db_path)
        self.model = EmbeddingModel()

    def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        search_types: List[str] = None,
        filters: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """ハイブリッド検索 - 複数検索手法を組み合わせ"""

        if search_types is None:
            search_types = ["keyword", "vector"]

        if filters is None:
            filters = {}

        all_results = []

        # 各種検索を実行
        for search_type in search_types:
            if search_type == "keyword":
                results = self._keyword_search(query, top_k, filters)
                all_results.extend(results)
            elif search_type == "vector":
                results = self._vector_search(query, top_k, filters)
                all_results.extend(results)
            elif search_type == "semantic":
                results = self._semantic_search(query, top_k, filters)
                all_results.extend(results)

        # 結果の統合とスコアリング
        merged_results = self._merge_results(all_results, top_k)

        return merged_results

    def _keyword_search(self, query: str, top_k: int, filters: Dict) -> List[Dict]:
        """キーワード検索"""
        print("🔍 キーワード検索実行中...")

        # フィルタ条件を適用
        category_filter = filters.get("category")

        results = self.db.search_entries(query=query, category=category_filter, limit=top_k)

        # スコア付与（キーワード一致度）
        for result in results:
            result["score"] = self._calculate_keyword_score(result, query)
            result["search_type"] = "keyword"

        print(f"✅ キーワード検索: {len(results)}件")
        return results

    def _vector_search(self, query: str, top_k: int, filters: Dict) -> List[Dict]:
        """ベクトル検索"""
        print("🧠 ベクトル検索実行中...")

        stats = self.db.get_sync_stats()
        if stats["synced_entries"] == 0:
            print("⚠️  同期済みエントリーがありません")
            return []

        query_embedding = self.model.get_embedding(query)
        if query_embedding is None:
            print("❌ クエリの埋め込み生成失敗")
            return []

        results = self.db.vector_search(query_embedding, top_k=top_k, index_dir=self.index_dir)

        # 検索タイプを設定
        for result in results:
            result["search_type"] = "vector"

        print(f"✅ ベクトル検索: {len(results)}件")
        return results

    def _semantic_search(self, query: str, top_k: int, filters: Dict) -> List[Dict]:
        """セマンティック検索 - 拡張クエリを使用"""
        print("🌟 セマンティック検索実行中...")

        # クエリ拡張（同義語や関連語を追加）
        expanded_queries = self._expand_query(query)

        all_results = []
        for expanded_query in expanded_queries:
            results = self._vector_search(expanded_query, top_k, filters)
            all_results.extend(results)

        # 重複排除
        seen_ids = set()
        unique_results = []
        for result in all_results:
            if result["id"] not in seen_ids:
                seen_ids.add(result["id"])
                unique_results.append(result)

        print(f"✅ セマンティック検索: {len(unique_results)}件")
        return unique_results

    def _expand_query(self, query: str) -> List[str]:
        """クエリの拡張（簡易版）"""
        # 実際の実装では同義語辞書やLLMを使用
        expansions = [query]

        # 簡単なクエリ拡張の例
        if "問題" in query:
            expansions.append(query.replace("問題", "課題"))
        if "解決" in query:
            expansions.append(query.replace("解決", "対応"))

        return expansions

    def _calculate_keyword_score(self, result: Dict, query: str) -> float:
        """キーワードスコアの計算"""
        score = 0.0

        # タイトルでの一致
        if "title" in result and query.lower() in result["title"].lower():
            score += 0.5

        # 内容での一致
        if "content" in result and query.lower() in result["content"].lower():
            score += 0.3

        # タグでの一致
        if "tags" in result and query.lower() in result["tags"].lower():
            score += 0.2

        return min(score, 1.0)

    def _merge_results(self, results: List[Dict], top_k: int) -> List[Dict]:
        """検索結果の統合とランキング"""

        # 結果をIDでグループ化
        results_by_id = {}
        for result in results:
            result_id = result["id"]
            if result_id not in results_by_id:
                results_by_id[result_id] = result
            else:
                # 既存の結果とマージ（スコアを加算）
                existing = results_by_id[result_id]
                existing["score"] = existing.get("score", 0) + result.get("score", 0)
                # 検索タイプを統合
                if "search_types" not in existing:
                    existing["search_types"] = []
                existing["search_types"].append(result.get("search_type", "unknown"))

        # スコアでソート
        sorted_results = sorted(
            results_by_id.values(), key=lambda x: x.get("score", 0), reverse=True
        )

        return sorted_results[:top_k]


def main():
    parser = argparse.ArgumentParser(description="高度なナレッジ検索システム")
    parser.add_argument("query", help="検索クエリ")
    parser.add_argument("--top-k", "-k", type=int, default=10, help="返却する結果数 (default: 10)")
    parser.add_argument(
        "--search-types",
        "-t",
        nargs="+",
        choices=["keyword", "vector", "semantic"],
        default=["keyword", "vector"],
        help="使用する検索タイプ (default: keyword vector)",
    )
    parser.add_argument("--category", "-c", help="カテゴリでフィルタ")

    args = parser.parse_args()

    print("🚀 高度な検索システムを起動")

    # 検索エンジン初期化
    search_engine = AdvancedSearchEngine()

    # フィルタ設定
    filters = {}
    if args.category:
        filters["category"] = args.category

    # 検索実行
    results = search_engine.hybrid_search(
        query=args.query, top_k=args.top_k, search_types=args.search_types, filters=filters
    )

    # 結果表示
    print(f"\n📊 検索結果: {len(results)}件")
    print("=" * 80)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.get('title', 'No title')}")
        print(f"   カテゴリ: {result.get('category', 'No category')}")
        print(f"   スコア: {result.get('score', 0):.3f}")
        print(f"   検索タイプ: {', '.join(result.get('search_types', ['unknown']))}")
        print(f"   内容: {result.get('content', 'No content')[:100]}...")

        if "similarity" in result:
            print(f"   類似度: {result['similarity']:.3f}")

        if "tags" in result and result["tags"]:
            print(f"   タグ: {result['tags']}")

    if not results:
        print("❌ 該当するナレッジが見つかりませんでした")


if __name__ == "__main__":
    main()
