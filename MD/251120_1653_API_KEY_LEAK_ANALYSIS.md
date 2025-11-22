# APIキー漏洩問題 - なぜなぜ分析

## 🚨 問題
```
403 Your API key was reported as leaked. 
Please use another API key.
```

## 📊 なぜなぜ分析（10+原因候補）

### 1. GitHubリポジトリへの露出 ⭐⭐⭐
**可能性: 高**
- .envファイルが誤ってコミット/プッシュされた
- Codespacesが公開リポジトリの場合、.envが見えている可能性
- GitHubのSecret Scanningが自動検出 → Googleに通報

**確認方法**:
```bash
# Gitの履歴を確認
git log --all --full-history -- .env
git log --all --full-history -S "GEMINI_API_KEY"
```

### 2. ターミナル出力への平文表示 ⭐⭐⭐
**可能性: 高**
- 既存スクリプトでAPIキーを平文出力している
- TaskExecutorにも確認メッセージで一部表示している
- Codespacesのターミナルが共有されている可能性

**確認箇所**:
```python
# TaskExecutorEnhanced v2で追加した行
print(f"🔑 GEMINI_API_KEY: {self.gemini_api_key[:10]}...（読み込み成功）")
# ↑ これでも検出される可能性
```

### 3. 過去のチャット履歴への混入 ⭐⭐
**可能性: 中**
- Claudeとの会話で.envの内容を貼り付けた
- ログファイルを共有した際に含まれていた

### 4. ログファイルへの記録 ⭐⭐⭐
**可能性: 高**
- logs/配下にAPIキーが記録されている
- エラーメッセージに含まれている
- スタックトレースに含まれている

**確認方法**:
```bash
# ログファイルを検索
grep -r "AIza" logs/ 2>/dev/null
```

### 5. バックアップファイルの存在 ⭐⭐
**可能性: 中**
- .env.backup_* ファイルが残っている
- エディタの自動バックアップ（.env~など）

**確認方法**:
```bash
find . -name ".env*" -o -name "*backup*" | grep env
```

### 6. 既存システムでのハードコーディング ⭐⭐⭐
**可能性: 高**
- agents/配下のファイルに直接記述されている
- complete_engine_ultimate.pyなど

**確認方法**:
```bash
grep -r "AIza" agents/ tools/ --include="*.py" 2>/dev/null
```

### 7. Google Sheets経由での漏洩 ⭐
**可能性: 低**
- APIキーがシートに記録されている
- シートが公開設定になっている

### 8. 環境変数の設定ミス ⭐
**可能性: 低**
- Codespacesのシークレット設定が誤っている
- 環境変数が公開されている

### 9. 複数IPからの同時アクセス ⭐⭐
**可能性: 中**
- 同じAPIキーを複数の場所で使用
- 自動化スクリプトの並列実行

### 10. APIキー使用量の異常 ⭐⭐
**可能性: 中**
- 短時間に大量のリクエスト
- レート制限を超えた使用

### 11. .gitignoreの設定ミス ⭐⭐⭐
**可能性: 高**
- .envが.gitignoreに含まれていない
- .gitignoreの記述ミス

**確認方法**:
```bash
cat .gitignore | grep ".env"
```

### 12. スクリーンショット/ビデオへの映り込み ⭐
**可能性: 低**
- 画面共有時に表示された
- デモ動画に含まれた

## 🎯 最も可能性が高い原因（トップ3）

1. **GitHubへの露出**（可能性: 80%）
   - .envファイルが誤ってコミットされた
   - GitHubのSecret Scanningが検出

2. **ログファイルへの記録**（可能性: 70%）
   - エラーログにAPIキーが含まれている
   - logs/配下が公開されている

3. **ターミナル出力**（可能性: 60%）
   - デバッグ出力で平文表示
   - Codespacesのターミナルが記録されている

## 📋 既存システムの成功事例

既存のF1エージェント（agents/pm_agent/task_breakdown_gemini.py）は
正常に動作している → そちらのAPIキー管理方法を確認すべき
```python
# task_breakdown_gemini.pyでの使用例
self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
```

**F1が動作している理由**:
- 同じ.envを使用しているはず
- しかし、エラーが出ていない
- → 別のAPIキーを使用している可能性？
- → または、F1は漏洩前に実行済み？

