"""最終検証スクリプト"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🔍 最終検証")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# 1. ファイル存在確認
checks = {
    "SQLiteDB": project_root / "knowledge_system/database/knowledge.db",
    "FAISSインデックス": project_root / "knowledge_system/database/faiss_index/knowledge.index",
    "IntegratedOrchestrator v30": project_root / "scripts/integrated_orchestrator_v30_knowledge.py",
    "TaskExecutor v2": project_root / "task_executor/task_executor.py",
    "README": project_root / "knowledge_system/README.md",
}

print("\n📁 ファイル確認:")
for name, path in checks.items():
    status = "✅" if path.exists() else "❌"
    print(f"  {status} {name}")

# 2. システム動作確認
print("\n🧪 システム動作確認:")
try:
    import yaml

    from knowledge_system.core_agents.knowledge_manager_v2 import \
        KnowledgeManagerV2

    config_path = project_root / "knowledge_system/configuration/knowledge_config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    db_path = project_root / config["database"]["path"]
    index_path = project_root / config["vector_search"]["index_path"]
    km = KnowledgeManagerV2(str(db_path), str(index_path), config["vector_search"]["model_name"])

    print("  ✅ KnowledgeManager v2.0")

    stats = km.get_stats()
    print(f"  ✅ ナレッジ数: {stats['total_knowledge']}")
    print(f"  ✅ インデックス: {stats['vector_index_size']}")

    results = km.hybrid_search("テスト", top_k=1)
    print(f"  ✅ 検索機能: 動作OK")

except Exception as e:
    print(f"  ❌ エラー: {e}")

print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("✅ 最終検証完了")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
