# Git自動化エージェントシステム

## 📋 概要

Git操作（コミット、プッシュ、ブランチ切り替え）を自動化し、品質チェックを統合したシステム

---

## 🚀 使い方

### 基本的な使い方（コミットのみ）
```bash
python3 agents/git_agent/run_git_workflow.py -m "✨ 新機能追加"
```

### コミット＋プッシュ
```bash
python3 agents/git_agent/run_git_workflow.py -m "🐛 バグ修正" --push
```

### コミット＋プッシュ＋バージョンアップ
```bash
# patch (v1.2.3 → v1.2.4)
python3 agents/git_agent/run_git_workflow.py -m "🐛 バグ修正" --push --version-up patch

# minor (v1.2.3 → v1.3.0)
python3 agents/git_agent/run_git_workflow.py -m "✨ 新機能" --push --version-up minor --feature "pm_agent_enhance"

# major (v1.2.3 → v2.0.0)
python3 agents/git_agent/run_git_workflow.py -m "💥 破壊的変更" --push --version-up major
```

---

## 📦 個別エージェント

### 1. Commit Agent
```bash
python3 agents/git_agent/commit_agent.py "コミットメッセージ"
```

**実行される処理:**
- STEP 1: 一時ファイルを_WIPに移動
- STEP 2: コミット対象をリスト
- STEP 3: 構文チェック（py_compile）
- STEP 3: Linterチェック（flake8）
- STEP 4: コード整形（Black）
- STEP 6: 不要ファイル削除
- STEP 8: Git commit

### 2. Push Agent
```bash
python3 agents/git_agent/push_agent.py
```

**オプション:**
- `--force`: 強制プッシュ

### 3. Branch Agent
```bash
# ブランチ切り替え
python3 agents/git_agent/branch_agent.py switch v1.3.0-feature

# 新ブランチ作成
python3 agents/git_agent/branch_agent.py new v1.4.0-new-feature

# 自動バージョンアップ
python3 agents/git_agent/branch_agent.py auto patch feature-name
```

---

## ⚙️ 設定

`configs/git_workflows/commit_config.yaml` で設定をカスタマイズ可能
```yaml
quality_gates:
  compile_check: true
  linter: true
  formatter: true

auto_fix: true
```

---

## 🎯 エイリアス設定（推奨）

`.bashrc` または `.zshrc` に追加:
```bash
alias gcommit='python3 agents/git_agent/run_git_workflow.py'

# 使用例
gcommit -m "✨ 新機能" --push --version-up patch
```

---

## 🔧 必要なツール
```bash
pip install pyyaml flake8 black --break-system-packages
```

---

## ✅ フロー全体
```
1. 一時ファイル整理
2. コミット対象リスト
3. 構文チェック
4. Linterチェック
5. コード整形
6. 不要ファイル削除
7. コミット
8. プッシュ（オプション）
9. ブランチ作成（オプション）
```

