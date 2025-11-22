# ナレッジ蓄積エラー修正提案

**日時**: $(TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M:%S JST")  
**エラー**: AttributeError: 'SQLiteKnowledgeManager' object has no attribute 'add_knowledge_entry'

---

## 問題の詳細

### エラー発生箇所
```python
# knowledge_system/core_agents/knowledge_manager.py (行40付近)
def add_knowledge(self, title, content, category='general', tags=None):
    return self.db_manager.add_knowledge_entry(title, content, category, tags)
    #                      ^^^^^^^^^^^^^^^^^^^
    #                      このメソッドが存在しない
```

### 原因
`SQLiteKnowledgeManager`クラスに`add_knowledge_entry`メソッドが存在しない

---

## 修正方法（3つの選択肢）

### 【方法1】メソッド名を修正（推奨）
**概要**: knowledge_manager.pyの呼び出しを、実際に存在するメソッド名に変更

**実装**:
```python
# knowledge_system/core_agents/knowledge_manager.py

def add_knowledge(self, title, content, category='general', tags=None):
    # 修正前
    # return self.db_manager.add_knowledge_entry(title, content, category, tags)
    
    # 修正後（実際に存在するメソッド名に変更）
    return self.db_manager.add_knowledge(title, content, category, tags)
    # または
    return self.db_manager.register_knowledge(title, content, category, tags)
```

**メリット**:
- ✅ 既存のSQLiteKnowledgeManagerを変更しない
- ✅ 安全性が高い
- ✅ 修正箇所が1箇所のみ

**デメリット**:
- ⚠️  実際に存在するメソッド名を確認する必要がある

---

### 【方法2】メソッドを追加（中リスク）
**概要**: SQLiteKnowledgeManagerに`add_knowledge_entry`メソッドを追加

**実装**:
```python
# knowledge_system/database/sqlite_knowledge_manager.py

class SQLiteKnowledgeManager:
    # 既存のメソッド...
    
    def add_knowledge_entry(self, title, content, category='general', tags=None):
        """エイリアスメソッド: 既存メソッドへの転送"""
        # 既存の正しいメソッドを呼び出す
        return self.add_knowledge(title, content, category, tags)
```

**メリット**:
- ✅ knowledge_manager.pyを変更しない
- ✅ 後方互換性を保つ

**デメリット**:
- ⚠️  SQLiteKnowledgeManagerに変更を加える
- ⚠️  既存の正しいメソッド名を知る必要がある

---

### 【方法3】完全な新規実装（高リスク）
**概要**: add_knowledge_entryメソッドを完全に新規実装

**メリット**:
- ✅ 完全に制御可能

**デメリット**:
- ❌ 既存システムへのリスク大
- ❌ テストが必要
- ❌ 推奨しない

---

## 推奨修正手順

### STEP 1: バックアップ
```bash
cp knowledge_system/core_agents/knowledge_manager.py \
   knowledge_system/core_agents/knowledge_manager.py.backup_$(date +%Y%m%d_%H%M%S)
```

### STEP 2: 実際のメソッド名を確認
診断スクリプトの結果から、実際に存在するメソッド名を特定

### STEP 3: 修正（方法1を採用）
```python
# knowledge_system/core_agents/knowledge_manager.py

def add_knowledge(self, title, content, category='general', tags=None):
    # 実際に存在するメソッド名に変更
    return self.db_manager.<正しいメソッド名>(title, content, category, tags)
```

### STEP 4: 検証
```bash
python3 -c "
from agents.complete_engine_ultimate import CompleteEngineUltimate
engine = CompleteEngineUltimate()
# ナレッジ追加テスト
result = engine.knowledge_wrapper.add_knowledge('test', 'テスト内容', 'test')
print('✅ 成功' if result else '❌ 失敗')
"
```

---

## 安全性確認

- ✅ 既存のSQLiteKnowledgeManagerは変更しない
- ✅ 修正箇所は1行のみ
- ✅ バックアップ取得済み
- ✅ 動作確認方法が明確

