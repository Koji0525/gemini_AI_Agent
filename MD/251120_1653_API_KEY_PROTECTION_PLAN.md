# APIキー保護計画

## 🚨 即座に実施すべきこと

### 1. 新しいAPIキーを発行 ⭐⭐⭐
**最優先**
1. Google AI Studioにアクセス
2. 漏洩したAPIキーを削除
3. 新しいAPIキーを発行
4. .envファイルを更新

### 2. .gitignoreの強化 ⭐⭐⭐
```bash
# .gitignoreに追加
.env
.env.*
*.env
.env.backup*
configuration/service_account.json
```

### 3. Git履歴からの削除 ⭐⭐⭐
もし.envがコミットされていた場合：
```bash
# Git履歴から完全削除
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 強制プッシュ（注意！）
git push origin --force --all
```

### 4. ログファイルのクリーンアップ ⭐⭐
```bash
# logs/配下のAPIキー含むファイルを削除
find logs/ -type f -exec grep -l "AIza" {} \; -delete
```

### 5. デバッグ出力の削除 ⭐⭐⭐
すべてのprint文でAPIキーを表示しない：
```python
# ❌ 危険
print(f"API Key: {api_key}")

# ❌ これも危険
print(f"API Key: {api_key[:10]}...")

# ✅ 安全
# 何も出力しない、またはマスク
print("API Key: ********")
```

## 🛡️ 長期的な対策

### 1. Codespacesシークレットの活用
.envファイルを使わず、Codespacesの環境変数機能を使用

### 2. APIキーのローテーション
定期的に（月1回）APIキーを変更

### 3. APIキー使用のモニタリング
Google Cloud Consoleで使用状況を監視

### 4. 最小権限の原則
必要最小限のスコープでAPIキーを発行

### 5. 複数APIキーの使用
開発用・本番用でAPIキーを分ける

## 📝 既存システムとの整合性

### F1エージェントの確認
```bash
# F1が使用しているAPIキー管理方法を確認
cat agents/pm_agent/task_breakdown_gemini.py | grep -A 10 "api_key"
```

もしF1が正常動作しているなら：
- 別のAPIキーを使用している可能性
- または、環境変数の読み込み方が異なる

### 統一的なAPIキー管理
すべてのエージェントで同じ方法を使用：
```python
import os
from dotenv import load_dotenv

# プロジェクトルートの.envを読み込み
load_dotenv('/workspaces/gemini_AI_Agent/.env')

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEYが設定されていません")
```

## 🔒 セキュリティチェックリスト

- [ ] 新しいAPIキーを発行
- [ ] .envを.gitignoreに追加
- [ ] Git履歴をクリーンアップ
- [ ] ログファイルをクリーンアップ
- [ ] すべてのprint文からAPIキーを削除
- [ ] Codespacesシークレットに移行
- [ ] APIキー使用状況をモニタリング
- [ ] ドキュメントを更新

