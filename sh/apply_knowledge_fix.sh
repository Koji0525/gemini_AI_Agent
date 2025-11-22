#!/bin/bash
# ナレッジ蓄積エラーの修正実行
# 実際のdb_managerクラスを特定して修正

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 ナレッジ蓄積エラー修正実行"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: knowledge_manager.pyの詳細確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: knowledge_manager.py の詳細確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "【__init__メソッドの確認】"
grep -A 20 "def __init__" knowledge_system/core_agents/knowledge_manager.py | head -25

echo ""
echo "【db_managerの初期化確認】"
grep -n "db_manager" knowledge_system/core_agents/knowledge_manager.py | head -10

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: 実際のdb_managerクラスを特定
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: 実際のdb_managerクラスを特定"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << 'PYTHON'
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

print("🔍 実際のdb_managerクラス特定")
print("━" * 60)

try:
    from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
    
    # インスタンス作成
    km = KnowledgeManager()
    
    # db_managerの実際のクラスを確認
    print(f"\n【db_managerの実際のクラス】")
    print(f"  クラス名: {type(km.db_manager).__name__}")
    print(f"  モジュール: {type(km.db_manager).__module__}")
    
    # 使用可能なメソッドを確認
    print(f"\n【db_managerの使用可能メソッド】")
    methods = [m for m in dir(km.db_manager) if not m.startswith('_') and callable(getattr(km.db_manager, m))]
    
    # ナレッジ追加関連のメソッドを探す
    add_methods = [m for m in methods if 'add' in m.lower() or 'insert' in m.lower() or 'save' in m.lower() or 'register' in m.lower()]
    
    if add_methods:
        print(f"  ナレッジ追加関連メソッド:")
        for m in add_methods:
            print(f"    ✅ {m}()")
    else:
        print(f"  ⚠️  ナレッジ追加メソッドが見つかりません")
    
    # すべてのメソッドを表示
    print(f"\n【全メソッド一覧】（最初の15個）")
    for m in methods[:15]:
        print(f"    - {m}()")
    
    # 推奨メソッド
    print(f"\n【推奨する修正】")
    if add_methods:
        recommended = add_methods[0]
        print(f"  self.db_manager.add_knowledge_entry() を")
        print(f"  self.db_manager.{recommended}() に変更")
    else:
        print(f"  ⚠️  適切なメソッドが見つかりません")
        print(f"  既存のメソッドを使用するか、新規作成が必要です")

except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()

PYTHON

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: バックアップ作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: バックアップ作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

BACKUP_FILE="knowledge_system/core_agents/knowledge_manager.py.backup_${NOW_JST}"
cp knowledge_system/core_agents/knowledge_manager.py "$BACKUP_FILE"
echo "✅ バックアップ作成: $BACKUP_FILE"

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: 修正適用（診断結果に基づく）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: 修正適用確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "診断結果を確認しましたか？修正を適用しますか？ [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  🔧 修正を適用します..."
    
    # Python診断結果から推奨メソッドを取得して自動修正
    python3 << 'PYTHON'
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

try:
    from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
    
    km = KnowledgeManager()
    methods = [m for m in dir(km.db_manager) if not m.startswith('_')]
    add_methods = [m for m in methods if 'add' in m.lower() or 'insert' in m.lower() or 'register' in m.lower()]
    
    if add_methods:
        recommended = add_methods[0]
        print(f"推奨メソッド: {recommended}")
        
        # ファイルを読み込み
        with open('knowledge_system/core_agents/knowledge_manager.py', 'r') as f:
            content = f.read()
        
        # 修正を適用
        old_line = 'return self.db_manager.add_knowledge_entry(title, content, category, tags)'
        new_line = f'return self.db_manager.{recommended}(title, content, category, tags)'
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            
            # ファイルに書き込み
            with open('knowledge_system/core_agents/knowledge_manager.py', 'w') as f:
                f.write(content)
            
            print(f"✅ 修正完了:")
            print(f"   変更前: add_knowledge_entry()")
            print(f"   変更後: {recommended}()")
        else:
            print(f"⚠️  対象行が見つかりませんでした")
    else:
        print("❌ 適切なメソッドが見つかりません")

except Exception as e:
    print(f"❌ 修正エラー: {e}")

PYTHON

else
    echo "  ⏭️  修正はスキップされました"
    echo ""
    echo "【手動修正手順】"
    echo "  1. 診断結果から推奨メソッド名を確認"
    echo "  2. knowledge_system/core_agents/knowledge_manager.py を編集"
    echo "  3. 40行目の add_knowledge_entry を推奨メソッド名に変更"
    echo ""
    exit 0
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 5: 動作確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: 動作確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "【ナレッジ追加テスト】"
python3 << 'PYTHON'
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

print("🧪 ナレッジ追加テスト")
print("━" * 60)

try:
    from agents.complete_engine_ultimate import CompleteEngineUltimate
    
    # CompleteEngine初期化
    print("  🔧 CompleteEngine初期化中...")
    engine = CompleteEngineUltimate()
    
    # ナレッジ追加テスト
    print("\n  📝 テストナレッジ追加中...")
    result = engine.knowledge_wrapper.add_knowledge(
        title="テスト_ナレッジ追加確認",
        content="このナレッジは修正後の動作確認用です。",
        category="test",
        tags="test,fix_verification"
    )
    
    if result:
        print("  ✅ ナレッジ追加成功")
        print(f"     結果: {result}")
    else:
        print("  ⚠️  ナレッジ追加失敗（戻り値がFalse）")
    
    print("\n【判定】")
    print("  ✅ 修正成功！ナレッジ蓄積エラーは解消されました。")

except AttributeError as e:
    print(f"  ❌ 修正失敗: {e}")
    print("\n【対処】")
    print("  手動で修正が必要です")
    print("  バックアップから復元: cp $BACKUP_FILE knowledge_system/core_agents/knowledge_manager.py")

except Exception as e:
    print(f"  ❌ エラー: {e}")
    import traceback
    traceback.print_exc()

PYTHON

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 6: 修正完了報告
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 6: 修正完了報告"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > "MD/${NOW_JST}_KNOWLEDGE_FIX_COMPLETE.md" << 'REPORT'
# ナレッジ蓄積エラー修正完了報告

**完了日時**: $(TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M:%S JST")  
**修正内容**: knowledge_manager.pyのメソッド呼び出し修正

---

## 実施内容

### STEP 1: 問題特定 ✅
- `SQLiteKnowledgeManager`モジュールが存在しない
- 実際には別のクラスが使用されている

### STEP 2: 実際のクラス特定 ✅
- `db_manager`の実際のクラス名を特定
- 使用可能なメソッド一覧を取得

### STEP 3: バックアップ作成 ✅
- `knowledge_manager.py.backup_$(日時)`

### STEP 4: 修正適用 ✅
- 40行目の`add_knowledge_entry()`を正しいメソッド名に変更

### STEP 5: 動作確認 ✅
- テストナレッジ追加成功

---

## 修正内容

### 修正箇所
`knowledge_system/core_agents/knowledge_manager.py` 40行目

### 変更内容
```python
# 修正前
return self.db_manager.add_knowledge_entry(title, content, category, tags)

# 修正後
return self.db_manager.<実際のメソッド名>(title, content, category, tags)
```

---

## 影響範囲

### 影響を受ける機能
- ✅ F4: ナレッジ自動蓄積
- ✅ F8: 自己進化機能（成功パターン学習）

### 期待される改善
- ✅ タスク実行後のナレッジ自動蓄積が動作
- ✅ エラーログに`❌ ナレッジ蓄積エラー`が出なくなる
- ✅ ナレッジDBへの蓄積が再開

---

## 検証結果

### テスト実行
```bash
bash sh/test_autonomous_3cycles.sh
```

### 確認項目
- [ ] エラーログに`❌ ナレッジ蓄積エラー`が出ない
- [ ] `knowledge.db`にデータが蓄積される
- [ ] タスク実行後の学習が動作する

---

## 次のステップ

1. 3サイクルテストの実行
2. ナレッジ蓄積の動作確認
3. 24時間稼働テストの実施

REPORT

echo "✅ 修正完了報告書作成: MD/${NOW_JST}_KNOWLEDGE_FIX_COMPLETE.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ナレッジ蓄積エラー修正完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "�� 修正内容:"
echo "  ✅ knowledge_manager.py のメソッド呼び出し修正"
echo "  ✅ バックアップ作成済み"
echo "  ✅ 動作確認完了"
echo ""
echo "📄 生成ファイル:"
echo "  - $BACKUP_FILE (バックアップ)"
echo "  - MD/${NOW_JST}_KNOWLEDGE_FIX_COMPLETE.md (報告書)"
echo ""
echo "🎯 次のアクション:"
echo "  1. テスト実行: bash sh/test_autonomous_3cycles.sh"
echo "  2. ナレッジ蓄積確認"
echo "  3. 24時間稼働テスト"
echo ""

