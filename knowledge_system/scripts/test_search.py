"""
ナレッジ検索のテスト
"""

import sys
from pathlib import Path

import yaml

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from knowledge_system.core_agents.knowledge_manager import KnowledgeManager


def test_search():
    """検索テスト"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("�� ナレッジ検索テスト")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # 設定読み込み
    config_path = project_root / "knowledge_system" / "configuration" / "knowledge_config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # ナレッジマネージャー初期化
    db_path = project_root / config["database"]["path"]
    index_path = project_root / config["vector_search"]["index_path"]
    model_name = config["vector_search"]["model_name"]

    knowledge_manager = KnowledgeManager(str(db_path), str(index_path), model_name)

    # 統計表示
    stats = knowledge_manager.get_stats()
    print(f"\n📊 システム状態:")
    print(f"  総ナレッジ数: {stats['total_knowledge']}")
    print(f"  ベクトルインデックス: {stats['vector_index_size']}件")

    # テストクエリ
    test_queries = [
        "エラーが発生した時の対処法",
        "タスクが完了しない",
        "スプレッドシートの更新",
        "非同期処理",
    ]

    for query in test_queries:
        print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🔍 クエリ: {query}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        results = knowledge_manager.hybrid_search(query, top_k=3)

        if results:
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['scenario'][:50]}...")
                print(f"   類似度: {result.get('similarity', 0):.3f}")
                print(f"   信頼度: {result.get('confidence', 0):.2f}")
                print(f"   検索タイプ: {result.get('search_type', 'unknown')}")
        else:
            print("❌ 該当するナレッジが見つかりませんでした")


if __name__ == "__main__":
    test_search()
