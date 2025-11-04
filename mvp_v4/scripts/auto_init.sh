#!/bin/bash
# Codespaces起動時に自動実行されるスクリプト

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 ナレッジベース自動初期化"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ChromaDB再構築
python3 << 'PYTHON'
from mvp_v4.scripts.rag_engine_local import FrugalRAGEngine
import json

print("📊 ナレッジベース読み込み中...")
rag = FrugalRAGEngine()
rag.load_knowledge(['mvp_v4/knowledge/learned/conversation_knowledge_v3.json'])

# 統計表示
with open('mvp_v4/knowledge/learned/conversation_knowledge_v3.json', 'r') as f:
    data = json.load(f)
    
print(f"✅ {len(data['knowledge_base'])}件のナレッジを読み込みました")
print("✅ 検索システム準備完了")
PYTHON

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 初期化完了！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
