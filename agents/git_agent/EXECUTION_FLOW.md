# 🚀 Git自動化ワークフロー 完全実行フロー

## 📋 実行される全ステップ

### STEP 1: CLEANUP - 一時ファイル整理
**目的**: テストコードを_WIPに移動
**対象パターン**:
- `test_*.py`
- `tmp_*.py`
- `debug_*.py`
- `*_test.py`

**実行内容**:
```python
for pattern in ['test_*.py', 'tmp_*.py', ...]:
    move to _WIP/
```

---

### STEP 2: LIST - コミット対象の列挙
**目的**: 変更されたファイルを列挙
**除外対象**: `_WIP/`, `_BACKUP/`, `_ARCHIVE/`

**実行内容**:
```bash
git status --porcelain
# 除外ディレクトリ以外の.pyファイルをリスト
```

---

### STEP 3: SECURITY CHECK - 認証ファイル検出
**目的**: 認証情報の漏洩防止
**検出パターン**:
- `service_account.json`
- `**/*_key.json`
- `**/*.pem`
- `**/credentials.json`
- `**/.env`

**実行内容**:
```python
# Gitの追跡対象のみチェック
tracked_files = git ls-files
for pattern in secret_patterns:
    if pattern in tracked_files:
        ERROR and STOP
```

---

### STEP 3: DUPLICATE CHECK - 重複メソッド検出
**目的**: 重複メソッドによるバグ防止

**検出対象**:
- 同じクラス内の同名メソッド
- executeメソッドの重複

**実行内容**:
```python
for each .py file:
    parse classes and methods
    detect duplicates
    if found: ERROR and STOP
```

---

### STEP 3: COMPILE CHECK - 構文チェック
**目的**: 構文エラーの検出

**実行内容**:
```bash
for each file in staged_files:
    python3 -m py_compile file
    if error: STOP
```

**結果**: ✅ 274ファイル構文OK（前回実績）

---

### STEP 3: LINTER CHECK - flake8品質チェック
**目的**: コーディング規約違反の検出

**設定**:
```yaml
max_line_length: 120
ignore_codes: [E203, W503]
warning_only: false  # エラーはブロック
```

**実行内容**:
```bash
for each file in staged_files:
    flake8 --max-line-length=120 \
           --extend-ignore=E203,W503 \
           file
```

**検出内容**:
- 未定義変数
- 未使用インポート
- 命名規則違反
- インデントエラー

**動作**:
- ⚠️  警告: 表示のみ
- ❌ エラー: ワークフロー中断

---

### STEP 4: FORMATTER - Black自動整形
**目的**: コードスタイルの統一

**設定**:
```yaml
line_length: 120
auto_fix: true
```

**実行内容**:
```bash
for each file in staged_files:
    black --line-length=120 file
```

**効果**:
- インデント統一
- スペース調整
- クォート統一
- 行の長さ調整

---

### STEP 5: TEST - 開発プログラムのテスト
**目的**: 実装が正しく動作するか確認

**実行方法**: 対話式
```
📝 開発したプログラムのテストコマンドを入力してください
   例: DISPLAY=:1 python3 agents/pm_agent/automation.py
   スキップする場合は Enter

テストコマンド: _
```

**動作**:
- テスト成功: 続行
- テスト失敗: 「無視してコミット？」確認

---

### STEP 6: FINAL CLEANUP - 不要ファイル削除
**目的**: ビルド生成物の削除

**削除対象**:
- `**/__pycache__/`
- `**/*.pyc`
- `**/*.log`
- `**/*.tmp`

**実行内容**:
```bash
find and delete:
  - __pycache__ directories
  - .pyc files
  - .log files
  - .tmp files
```

**結果**: ✅ 42個削除（前回実績）

---

### STEP 8: UPDATE .gitignore
**目的**: 必要な除外ルールを追加

**追加パターン**:
```gitignore
# 認証情報
service_account.json
**/*.pem

# 実行時生成
__pycache__/
*.pyc
*.log
logs/
agent_outputs/
```

---

### STEP 9: UPDATE README
**目的**: 変更内容のドキュメント化

**実行方法**: 対話式
```
📝 READMEに追加する内容を入力してください
   例: - ✅ PM Agent自動化完了
   スキップする場合は Enter

README更新内容: _
```

**更新場所**: `## 📝 変更履歴` セクション

---

### STEP 10: COMMIT & PUSH
**目的**: 変更をリモートに反映

**実行内容**:
```bash
git add -A
git commit -m "message"
git push origin branch
```

**Push Protection対応**:
- 認証情報検出時: 自動ガイド表示

---

## 🎯 完全実行例
```bash
$ gauto "✨ 新機能追加"

======================================================================
🤖 完全自動化Git統合ワークフロー
======================================================================

======================================================================
STEP 1: CLEANUP
======================================================================
✅ 5個のファイルを_WIPに移動

======================================================================
STEP 2: LIST
======================================================================
📋 コミット対象: 15ファイル

======================================================================
STEP 3: SECURITY CHECK
======================================================================
✅ 認証ファイルなし

======================================================================
STEP 3: DUPLICATE CHECK
======================================================================
✅ 重複メソッドなし

======================================================================
STEP 3: COMPILE CHECK
======================================================================
✅ 15個のファイルが構文OK

======================================================================
STEP 3: LINTER CHECK
======================================================================
   agents/example.py:42:1: E302 expected 2 blank lines, found 1
   agents/example.py:56:80: E501 line too long (121 > 120 characters)
⚠️  2個の警告

======================================================================
STEP 4: FORMATTER
======================================================================
   🔧 agents/example.py: 整形完了
✅ コード整形完了

======================================================================
STEP 5: TEST
======================================================================
テストコマンド: DISPLAY=:1 python3 agents/pm_agent/automation.py
✅ テスト成功

======================================================================
STEP 6: FINAL CLEANUP
======================================================================
✅ 42個の不要ファイルを削除

======================================================================
STEP 8: UPDATE .gitignore
======================================================================
✅ .gitignoreは最新

======================================================================
STEP 9: UPDATE README
======================================================================
README更新内容: - ✅ PM Agent自動化完了
✅ READMEを更新

======================================================================
STEP 10: COMMIT & PUSH
======================================================================
✅ コミット成功
✅ プッシュ成功

======================================================================
🎉 完全自動化ワークフロー完了！
======================================================================
```

---

## ⚙️ 設定ファイル

### 場所
`configs/git_workflows/auto_workflow_config.yaml`

### 各ステップの有効/無効
```yaml
quality_gates:
  cleanup: true              # STEP 1
  list: true                 # STEP 2
  security_check: true       # STEP 3
  duplicate_check: true      # STEP 3
  compile: true              # STEP 3
  linter: true               # STEP 3 ← flake8
  formatter: true            # STEP 4 ← Black
  test: true                 # STEP 5
  final_cleanup: true        # STEP 6
  update_gitignore: true     # STEP 8
  update_readme: true        # STEP 9
```

---

## 🚀 次回以降の実行方法

### 1回目のセットアップ
```bash
# エイリアス設定
echo "alias gauto='python3 agents/git_agent/auto_commit_push.py'" >> ~/.bashrc
source ~/.bashrc

# 必要なツールインストール
pip install flake8 black pyyaml --break-system-packages
```

### 毎回の実行
```bash
# 基本
gauto "コミットメッセージ"

# プッシュしない
gauto "メッセージ" --no-push

# カスタム設定
gauto "メッセージ" --config custom_config.yaml
```

---

## ✅ チェックリスト

実行前の確認:
- [ ] 開発完了
- [ ] ローカルテスト済み
- [ ] 認証ファイル除外確認
- [ ] コミットメッセージ準備

実行中の対話:
- [ ] STEP 5: テストコマンド入力
- [ ] STEP 9: README更新内容入力

実行後の確認:
- [ ] GitHub上で確認
- [ ] CIパス確認（将来）

