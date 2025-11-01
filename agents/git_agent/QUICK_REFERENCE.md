# ⚡ クイックリファレンス

## 🎯 ワンコマンド実行
```bash
gauto "コミットメッセージ"
```

これだけで以下が全て実行されます：

✅ STEP 1: 一時ファイル整理  
✅ STEP 2: コミット対象列挙  
✅ STEP 3: セキュリティチェック（認証ファイル検出）  
✅ STEP 3: 重複メソッド検出  
✅ STEP 3: 構文チェック（py_compile）  
✅ STEP 3: **Linterチェック（flake8）** ← 運用ルール必須  
✅ STEP 4: **自動整形（Black）** ← 運用ルール必須  
✅ STEP 5: テスト実行（対話式）  
✅ STEP 6: 不要ファイル削除  
✅ STEP 8: .gitignore更新  
✅ STEP 9: README更新（対話式）  
✅ STEP 10: コミット＋プッシュ  

---

## 📝 対話式入力

### STEP 5: テスト
```
テストコマンド: DISPLAY=:1 python3 agents/pm_agent/automation.py
```

### STEP 9: README
```
README更新内容: - ✅ PM Agent自動化完了
```

---

## ⚙️ オプション
```bash
# プッシュしない
gauto "メッセージ" --no-push

# カスタム設定
gauto "メッセージ" --config my_config.yaml
```

---

## 🔧 初回セットアップ（1回のみ）
```bash
# エイリアス設定
echo "alias gauto='python3 agents/git_agent/auto_commit_push.py'" >> ~/.bashrc
source ~/.bashrc

# ツールインストール
pip install flake8 black pyyaml --break-system-packages
```

---

## 📊 実行される品質チェック

| チェック | ツール | 動作 |
|---------|--------|------|
| 構文エラー | py_compile | エラーで中断 |
| コーディング規約 | flake8 | エラーで中断 |
| コードスタイル | Black | 自動修正 |
| 重複メソッド | 独自 | エラーで中断 |
| 認証ファイル | 独自 | エラーで中断 |

