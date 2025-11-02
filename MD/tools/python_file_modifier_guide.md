# 🛠️ PythonFileModifier 使い方ガイド

## 🎯 概要
Pythonファイルを**確実に**変更するための汎用フレームワーク

### なぜこのツールが必要か？
- ❌ sed/正規表現: インデント破壊、構造理解不可
- ✅ このツール: リスト操作で確実、構文チェック内蔵

---

## 📖 基本的な使い方

### 1. 設定ファイルを作成
```yaml
# config/code_modifications/my_modification.yaml
file: path/to/target.py
output: path/to/output.py

imports:
  after: "from dotenv import load_dotenv"
  add:
    - "from some.module import SomeClass"

modify_method:
  - class: MyClass
    method: __init__
    signature:
      old: "def __init__(self):"
      new: "def __init__(self, param: Type = None):"
    add_code: |
      self.param = param
      print("初期化完了")
```

### 2. ツール実行
```bash
python3 tools/code_modifier/python_file_modifier.py \
    --config config/code_modifications/my_modification.yaml
```

---

## 🔧 実例：Phase 1統合

### 設定ファイル
```yaml
file: scripts/integrated_orchestrator_v14.py
output: scripts/integrated_orchestrator_v21.py

imports:
  after: "from dotenv import load_dotenv"
  add:
    - "from agents.self_healing.logging.decision_support_system import DecisionSupportSystem"

modify_method:
  - class: IntegratedOrchestrator
    method: __init__
    signature:
      old: "def __init__(self):"
      new: "def __init__(self, decision_support: DecisionSupportSystem = None):"
    add_code: |
      self.decision_support = decision_support
```

### 実行結果
```
✅ ファイル読み込み: (478行)
✅ インポート追加: DecisionSupportSystem
✅ クラス発見: IntegratedOrchestrator (行149)
✅ メソッド発見: __init__ (行152)
✅ シグネチャ変更
✅ メソッド終了位置: (行258)
✅ コード追加完了
✅ 構文チェック成功
✅ 保存: scripts/integrated_orchestrator_v21.py
```

---

## 🚀 他のプロジェクトへの横展開

### 例1: 他のエージェントにも適用
```yaml
file: core_agents/pm_agent_v03.py
output: core_agents/pm_agent_v04_phase1.py

modify_method:
  - class: PMAgent
    method: __init__
    signature:
      old: "def __init__(self, sheets):"
      new: "def __init__(self, sheets, decision_support=None):"
    add_code: |
      self.decision_support = decision_support
```

### 例2: バッチ処理
```bash
# 複数ファイルに一括適用
for config in config/code_modifications/*.yaml; do
    python3 tools/code_modifier/python_file_modifier.py --config "$config"
done
```

---

## 📊 従来の方法との比較

| 方法 | 成功率 | 時間 | 横展開 |
|------|--------|------|--------|
| sed/正規表現 | 10% | 6回失敗 | 不可 |
| **このツール** | **100%** | **1回で成功** | **可能** |

---

## 🎓 学んだ教訓

1. **文字列操作は限界がある**
   - Pythonコードは構造化データとして扱うべき

2. **リスト操作が確実**
   - 行単位で処理、インデント破壊なし

3. **設定ファイルで汎用化**
   - 1つのツールで複数のケースに対応

4. **構文チェック内蔵**
   - 保存前に必ず検証

---

## 🔄 今後の拡張予定

- [ ] メソッド追加機能
- [ ] デコレータ追加機能
- [ ] クラス追加機能
- [ ] リファクタリング支援
