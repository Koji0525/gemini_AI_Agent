#!/bin/bash
# F7-F9エージェントの連携修正
# 既存システムを壊さず、インスタンス変数として保持

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 F7-F9エージェント連携修正"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: 現状確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: 現状の詳細確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << 'PYTHON'
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

print("🔍 CompleteEngineUltimate詳細診断")
print("━" * 60)

try:
    from agents.complete_engine_ultimate import CompleteEngineUltimate
    
    # インスタンス作成
    engine = CompleteEngineUltimate()
    
    # すべての属性を確認
    print("\n【CompleteEngineの全属性】")
    attrs = [attr for attr in dir(engine) if not attr.startswith('_')]
    
    # エージェント関連の属性を探す
    agent_attrs = [attr for attr in attrs if 'agent' in attr.lower() or 'healing' in attr.lower() or 'evolution' in attr.lower() or 'collaboration' in attr.lower()]
    
    print(f"  全属性数: {len(attrs)}")
    print(f"  エージェント関連: {len(agent_attrs)}")
    
    if agent_attrs:
        print("\n【エージェント関連属性】")
        for attr in agent_attrs:
            value = getattr(engine, attr, None)
            print(f"  ✅ {attr}: {type(value).__name__}")
    else:
        print("\n  ⚠️  エージェント関連属性が見つかりません")
    
    # 特定の属性名を直接確認
    print("\n【特定属性の存在確認】")
    check_attrs = [
        'self_healing_agent', 'healing_agent', 
        'self_evolution_agent', 'evolution_agent',
        'human_collaboration_agent', 'collaboration_agent',
        'quality_evaluator', 'health_check_agent'
    ]
    
    found_attrs = {}
    for attr in check_attrs:
        if hasattr(engine, attr):
            value = getattr(engine, attr)
            found_attrs[attr] = value
            print(f"  ✅ {attr}: {type(value).__name__}")
        else:
            print(f"  ❌ {attr}: 存在しない")
    
    # 問題の特定
    print("\n【問題の特定】")
    if not found_attrs:
        print("  ❌ エージェントインスタンスが一切保持されていない")
        print("  📋 原因: 初期化されているが、self.xxx として保持していない")
        print("  🔧 修正: CompleteEngineUltimate.__init__ でインスタンス変数として保持")
    else:
        print(f"  ✅ {len(found_attrs)}個のエージェントが保持されている")
        print(f"  ⚠️  F7-F9の属性名が予想と異なる可能性")

except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()

PYTHON

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: CompleteEngineのソースコード確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: CompleteEngine.__init__の確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "【__init__メソッドの該当部分】"
grep -n "SelfHealingAgent\|SelfEvolutionAgent\|HumanCollaborationAgent" agents/complete_engine_ultimate.py | head -20

echo ""
echo "【self.への代入を確認】"
grep -n "self\\..*_agent.*=" agents/complete_engine_ultimate.py | head -20

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: 修正の提案
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: 修正提案"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > "MD/${NOW_JST}_FIX_PROPOSAL.md" << 'PROPOSAL'
# F7-F9エージェント連携修正提案

**日時**: $(TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M:%S JST")  
**問題**: エージェントは初期化されるが、インスタンス変数として保持されていない

---

## 問題の詳細

### 現状
```python
# agents/complete_engine_ultimate.py の __init__ 内
# エージェントは初期化されている
SelfHealingAgent()  # ← 初期化される
SelfEvolutionAgent()  # ← 初期化される
HumanCollaborationAgent()  # ← 初期化される

# しかし、インスタンス変数として保持していない可能性
# self.xxx_agent = ... の形になっていない
```

### 影響
- エージェントは初期化されるので、ログには「✅ 初期化完了」と表示される
- しかし、後から呼び出せない（self.xxx_agent が存在しない）
- 24時間稼働時に、エラー時の自己修復が動作しない

---

## 修正方法（既存システムを壊さない）

### 修正箇所
`agents/complete_engine_ultimate.py` の `__init__` メソッド

### 修正内容
```python
# 修正前（推定）
try:
    from agents.self_evolution.self_healing_agent import SelfHealingAgent
    SelfHealingAgent()  # ← 初期化するだけ
    print("✅ SelfHealingAgent 初期化完了")
except Exception as e:
    print(f"⚠️ SelfHealingAgent初期化失敗: {e}")

# 修正後
try:
    from agents.self_evolution.self_healing_agent import SelfHealingAgent
    self.self_healing_agent = SelfHealingAgent()  # ← self.に代入
    print("✅ SelfHealingAgent 初期化完了")
except Exception as e:
    self.self_healing_agent = None
    print(f"⚠️ SelfHealingAgent初期化失敗: {e}")
```

同様に、F8, F9も修正：
```python
# F8
self.self_evolution_agent = SelfEvolutionAgent()

# F9
self.human_collaboration_agent = HumanCollaborationAgent()
```

### 安全性
- ✅ 既存のコードは一切削除しない
- ✅ 既存の処理フローは変更しない
- ✅ エラー時のフォールバックも維持
- ✅ 単に `self.xxx =` を追加するだけ

---

## 検証方法

修正後、以下のコマンドで確認：
```bash
python3 -c "
from agents.complete_engine_ultimate import CompleteEngineUltimate
engine = CompleteEngineUltimate()
print('F7:', hasattr(engine, 'self_healing_agent'))
print('F8:', hasattr(engine, 'self_evolution_agent'))
print('F9:', hasattr(engine, 'human_collaboration_agent'))
"
```

期待結果：
```
F7: True
F8: True
F9: True
```

---

## 次のステップ

1. CompleteEngineUltimateのバックアップ
2. __init__メソッドの修正
3. 動作確認
4. 24時間稼働テスト

PROPOSAL

echo "✅ 修正提案書作成: MD/${NOW_JST}_FIX_PROPOSAL.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 診断結果サマリー"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【問題】"
echo "  エージェントは初期化されるが、self.xxx として保持されていない"
echo ""
echo "【影響】"
echo "  - ログには「初期化完了」と表示される（誤解を招く）"
echo "  - しかし、実際には後から呼び出せない"
echo "  - 24時間稼働時にエージェントが使えない"
echo ""
echo "【修正方法】"
echo "  CompleteEngineUltimate.__init__ で"
echo "  self.self_healing_agent = SelfHealingAgent() に変更"
echo ""
echo "【安全性】"
echo "  ✅ 既存コード削除なし"
echo "  ✅ 単に self.xxx = を追加するだけ"
echo ""

