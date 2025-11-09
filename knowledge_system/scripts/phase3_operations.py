"""Phase 3運用スクリプト"""

import sys
from pathlib import Path

import yaml

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from knowledge_system.core_agents.knowledge_manager_v2 import \
    KnowledgeManagerV2

config_path = project_root / "knowledge_system/configuration/knowledge_config.yaml"
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

db_path = project_root / config["database"]["path"]
index_path = project_root / config["vector_search"]["index_path"]
km = KnowledgeManagerV2(str(db_path), str(index_path), config["vector_search"]["model_name"])

print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🚀 Phase 3 運用テスト")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# テスト1: 検索パフォーマンス
print("\n📊 検索パフォーマンステスト:")
queries = ["エラー対処", "タスク完了", "スプレッドシート更新"]
for q in queries:
    results = km.hybrid_search(q, top_k=3)
    print(f"  {q}: {len(results)}件")

# テスト2: キャッシュ効果確認
print("\n🔄 キャッシュテスト（同じクエリ再実行）:")
km.hybrid_search("エラー対処", top_k=3)

stats = km.get_stats()
perf = stats["performance"]
print(f"  キャッシュヒット率: {perf['cache_hit_rate']*100:.1f}%")
print(f"  平均検索時間: {perf['avg_search_time']}秒")
print(f"  目標時間: {perf['target_time']}秒")

# テスト3: バックアップ作成
print("\n�� バックアップ作成:")
backup_path = km.create_backup()
print(f"  ✅ バックアップ: {backup_path.name}")

# テスト4: 重複検出
print("\n🔍 ナレッジ品質チェック:")
all_knowledge = km.sqlite_manager.search_by_keyword("", limit=100)
duplicates = km.quality_assessor.find_duplicates(all_knowledge)
print(f"  重複: {len(duplicates)}件")

print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("✅ Phase 3 運用テスト完了")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
