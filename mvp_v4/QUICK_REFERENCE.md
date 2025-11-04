# 🚀 ナレッジベース クイックリファレンス

## 🔍 検索（コピペ用）
````bash
python3 << 'SEARCH'
from mvp_v4.scripts.rag_engine_local import FrugalRAGEngine
rag = FrugalRAGEngine()
rag.load_knowledge(['mvp_v4/knowledge/learned/conversation_knowledge_v3.json'])
results = rag.search("キーワード", top_k=3)
for r in results: print(f"- {r['scenario']}")
SEARCH
````

## 📝 登録（コピペ用）
````bash
python3 << 'REGISTER'
from mvp_v4.scripts.conversation_to_knowledge_v3 import ConversationKnowledgeExtractorV3
text = '''
何が起きた: 
原因: 
狙い: 
成功率: 80%
'''
extractor = ConversationKnowledgeExtractorV3()
kb = extractor.extract_from_simple_format(text)
if kb: extractor.save_knowledge(kb)
REGISTER
````

## 🔄 同期（コピペ用）
````bash
# 最新取得
git pull origin main

# チーム共有
git add mvp_v4/knowledge/learned/conversation_knowledge_v3.json
git commit -m "Add knowledge"
git push origin main
````

## 🎯 Claudeへの依頼テンプレート

### 検索時
````
「このエラーをナレッジ検索してください:
（エラーメッセージ）」
````

### 登録時
````
「このエラー解決をナレッジ登録用に整形してください」
````

