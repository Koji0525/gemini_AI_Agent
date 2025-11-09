# ⚡ クイックリファレンス

## 📝 ナレッジ登録

### 自動抽出（推奨）
```bash
python3 knowledge_system/scripts/auto_extract_knowledge.py
```

### 簡易登録
```bash
python3 knowledge_system/scripts/easy_register.py
```

## 🔍 検索
```bash
python3 knowledge_system/scripts/test_search.py
```

## 📊 確認
```bash
python3 knowledge_system/scripts/final_verification.py
```

## 💾 バックアップ
```python
from knowledge_system.core_agents.knowledge_manager_v2 import KnowledgeManagerV2
km = KnowledgeManagerV2(...)
km.create_backup()
```

## 📂 データ保存場所

- **メイン**: `knowledge_system/database/knowledge.db`
- **検索用**: `knowledge_system/database/faiss_index/`
- **バックアップ**: `knowledge_system/database/backups/`
