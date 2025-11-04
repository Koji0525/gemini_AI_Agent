# 🚀 ナレッジベース運用ガイド

## 📋 目次
1. [クイックスタート](#クイックスタート)
2. [日常の使い方](#日常の使い方)
3. [ナレッジ登録](#ナレッジ登録)
4. [検索方法](#検索方法)
5. [トラブルシューティング](#トラブルシューティング)

---

## 🚀 クイックスタート

### 初回セットアップ（1回だけ）
````bash
# 1. 最新ナレッジ取得
git pull origin main

# 2. ChromaDB初期化（自動実行済み）
# ターミナル起動時に自動で実行されます
````

---

## 💼 日常の使い方

### 1️⃣ エラー発生時
````bash
# STEP 1: まず検索
python3 << 'EOF'
from mvp_v4.scripts.rag_engine_local import FrugalRAGEngine
rag = FrugalRAGEngine()
rag.load_knowledge(['mvp_v4/knowledge/learned/conversation_knowledge_v3.json'])
results = rag.search("エラーメッセージをここに", top_k=3)
for i, r in enumerate(results, 1):
    print(f"{i}. {r['scenario']}")
