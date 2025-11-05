#!/bin/bash
echo "🔍 ナレッジ検索: $1"
python3 << CODE
from mvp_v4.scripts.rag_engine_local import FrugalRAGEngine
import json

# ナレッジファイルのリスト
knowledge_files = [
    'mvp_v4/knowledge/learned/conversation_knowledge_v3.json',
    'mvp_v4/knowledge/learned/conversation_knowledge_v4.json'
]

rag = FrugalRAGEngine()
rag.load_knowledge([f for f in knowledge_files if os.path.exists(f)])

results = rag.search("$1", top_k=3)

if results:
    print(f"✅ {len(results)}件見つかりました:")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['scenario']} (類似度: {r['similarity']:.2f})")
else:
    print("❌ 該当するナレッジが見つかりません")
CODE
