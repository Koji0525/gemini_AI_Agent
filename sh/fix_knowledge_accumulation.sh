#!/bin/bash
# ナレッジ蓄積エラーの診断と修正
# 既存システムを壊さない安全な修正

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 ナレッジ蓄積エラー診断"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【エラー内容】"
echo "  AttributeError: 'SQLiteKnowledgeManager' object has no attribute 'add_knowledge_entry'"
echo ""
echo "【原因推測】"
echo "  knowledge_manager.py が呼び出すメソッド名と"
echo "  SQLiteKnowledgeManager の実装メソッド名が不一致"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: SQLiteKnowledgeManagerの診断
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: SQLiteKnowledgeManager診断"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << 'PYTHON'
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

print("🔍 SQLiteKnowledgeManager メソッド確認")
print("━" * 60)

try:
    # SQLiteKnowledgeManagerをインポート
    from knowledge_system.database.sqlite_knowledge_manager import SQLiteKnowledgeManager
    
    print("\n【SQLiteKnowledgeManagerのメソッド一覧】")
    
    # インスタンス作成
    db_manager = SQLiteKnowledgeManager()
    
    # すべてのメソッドを取得
    methods = [m for m in dir(db_manager) if not m.startswith('_') and callable(getattr(db_manager, m))]
    
    print(f"  メソッド数: {len(methods)}")
    
    # 特に関連するメソッドをチェック
    important_methods = [
        'add_knowledge',
        'add_knowledge_entry', 
        'register_knowledge',
        'insert_knowledge',
        'save_knowledge',
        'add_entry'
    ]
    
    print("\n【重要メソッドの存在確認】")
    found_methods = []
    for method in important_methods:
        if hasattr(db_manager, method):
            print(f"  ✅ {method}() 存在")
            found_methods.append(method)
        else:
            print(f"  ❌ {method}() なし")
    
    # すべてのメソッドを表示
    print("\n【全メソッド一覧】")
    for method in methods[:15]:
        print(f"  - {method}()")
    
    if len(methods) > 15:
        print(f"  ... 他 {len(methods) - 15} 個")
    
    # 問題の特定
    print("\n【問題の特定】")
    if 'add_knowledge_entry' not in found_methods:
        print("  ❌ add_knowledge_entry メソッドが存在しない")
        
        if found_methods:
            print(f"\n  💡 代替メソッド候補: {', '.join(found_methods)}")
        else:
            print("\n  ⚠️  ナレッジ追加メソッドが一切存在しない")
            print("  🔧 メソッドの新規作成が必要")
    else:
        print("  ✅ add_knowledge_entry メソッドは存在する")
        print("  ⚠️  他の問題の可能性")

except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    print("\n【ファイル検索】")
    import subprocess
    result = subprocess.run(['find', '.', '-name', '*sqlite*knowledge*.py', '-type', 'f'], 
                          capture_output=True, text=True)
    print(result.stdout)

except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()

PYTHON

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: knowledge_manager.pyの確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: knowledge_manager.py の呼び出し確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "【add_knowledge メソッドの実装確認】"
grep -n "def add_knowledge" knowledge_system/core_agents/knowledge_manager.py

echo ""
echo "【add_knowledge_entry 呼び出し箇所】"
grep -n "add_knowledge_entry" knowledge_system/core_agents/knowledge_manager.py

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: 修正方針の決定
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: 修正方針"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > "MD/${NOW_JST}_KNOWLEDGE_FIX_PROPOSAL.md" << 'PROPOSAL'
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

PROPOSAL

echo "✅ 修正提案書作成: MD/${NOW_JST}_KNOWLEDGE_FIX_PROPOSAL.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "�� 診断結果"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【問題】"
echo "  SQLiteKnowledgeManager.add_knowledge_entry() が存在しない"
echo ""
echo "【修正方針】"
echo "  方法1（推奨）: knowledge_manager.py の呼び出しを修正"
echo "  方法2: SQLiteKnowledgeManager にエイリアスメソッド追加"
echo ""
echo "【次のアクション】"
echo "  1. 診断スクリプト実行で正しいメソッド名を確認"
echo "  2. バックアップ取得"
echo "  3. 1行修正"
echo "  4. 動作確認"
echo ""

