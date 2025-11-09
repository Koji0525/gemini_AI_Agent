# 📚 ナレッジシステム運用ガイド

## 🔄 日常運用

### 毎日のタスク
```bash
# 1. 新規ナレッジの自動抽出
python3 knowledge_system/scripts/auto_extract_knowledge.py

# 2. 検索テスト
python3 knowledge_system/scripts/test_search.py
```

### 週次タスク
```python
from knowledge_system.core_agents.knowledge_manager_v2 import KnowledgeManagerV2

km = KnowledgeManagerV2(...)

# 1. バックアップ作成
km.create_backup()

# 2. 重複チェック
all_knowledge = km.sqlite_manager.search_by_keyword("", limit=100)
duplicates = km.quality_assessor.find_duplicates(all_knowledge)
print(f"重複: {len(duplicates)}件")

# 3. パフォーマンス確認
stats = km.get_stats()
print(stats['performance'])
```

## 🐛 トラブルシューティング

### Q1: 検索結果が0件
```python
# 原因: ナレッジが未登録
stats = km.get_stats()
print(f"総ナレッジ数: {stats['total_knowledge']}")

# 対処: 自動抽出を実行
# python3 knowledge_system/scripts/auto_extract_knowledge.py
```

### Q2: 検索が遅い
```python
# 確認
stats = km.get_stats()
print(stats['performance'])

# キャッシュクリアして再テスト
km.optimizer.query_cache.clear()
```

## 📈 パフォーマンスチューニング

### キャッシュサイズ調整
```python
# advanced_features.py
self.query_cache = {}  # デフォルト100件
# → 必要に応じて増減
```

### ベクトルインデックス最適化
```python
# 定期的に保存
km.save_vector_index()
```
