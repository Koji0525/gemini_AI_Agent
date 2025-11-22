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

