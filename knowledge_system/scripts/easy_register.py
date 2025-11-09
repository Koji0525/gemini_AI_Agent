"""簡易ナレッジ登録ツール"""

import sys
from pathlib import Path

import yaml

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from knowledge_system.core_agents.knowledge_manager_v2 import \
    KnowledgeManagerV2

# 初期化
config_path = project_root / "knowledge_system/configuration/knowledge_config.yaml"
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

db_path = project_root / config["database"]["path"]
index_path = project_root / config["vector_search"]["index_path"]
km = KnowledgeManagerV2(str(db_path), str(index_path))

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("📝 簡易ナレッジ登録")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# 入力
scenario = input("\n問題・シナリオ: ")
solution = input("解決策: ")
cause = input("原因（省略可・Enterでスキップ）: ") or None
category = input("カテゴリ（省略可・Enterでスキップ）: ") or "一般"

knowledge = {
    "scenario": scenario,
    "solution": solution,
    "cause": cause,
    "category": category,
    "confidence": 0.7,
    "success_rate": 0.8,
    "source_system": "manual_entry",
    "task_type": "general",
}

# 登録
print("\n⏳ 登録中...")
kid = km.register_knowledge(knowledge)
km.save_vector_index()

print(f"\n✅ 登録完了: {kid}")

# 統計表示
stats = km.get_stats()
print(f"📊 総ナレッジ数: {stats['total_knowledge']}")
print(f"📊 ベクトルインデックス: {stats['vector_index_size']}")

# 登録されたナレッジを確認
print("\n🔍 登録内容の確認:")
results = km.hybrid_search(scenario, top_k=1)
if results:
    r = results[0]
    print(f"  シナリオ: {r['scenario']}")
    print(f"  解決策: {r['solution']}")
    print(f"  信頼度: {r['confidence']}")
    print(f"  類似度: {r.get('similarity', 'N/A')}")

print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("✨ 登録が完了しました！")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
