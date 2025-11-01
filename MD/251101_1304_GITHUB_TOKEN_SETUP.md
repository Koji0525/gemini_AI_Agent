# 🔑 GitHub Personal Access Token 設定手順

## 📋 目的
Human Interaction Agent v2.0がGitHub Issuesを監視・操作するために必要

## 🔧 トークン作成手順

### STEP 1: GitHubの設定ページにアクセス
1. GitHubにログイン
2. 右上のアイコン → **Settings**
3. 左サイドバー → **Developer settings**（一番下）
4. **Personal access tokens** → **Tokens (classic)**
5. **Generate new token** → **Generate new token (classic)**

### STEP 2: トークンの設定
- **Note**: `Human Interaction Agent v2.0`
- **Expiration**: `90 days`（推奨）

### STEP 3: 権限の選択
以下の権限を有効化：
- ✅ **repo** - フルコントロール
  - repo:status
  - repo_deployment
  - public_repo
  - repo:invite
  - security_events
- ✅ **workflow** - GitHub Actions管理
- ✅ **write:packages** - パッケージ管理（オプション）

### STEP 4: トークン生成
1. ページ下部の **Generate token** をクリック
2. 表示されたトークンを**必ずコピー**
   - 形式: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - ⚠️ 再表示不可能なので必ず保存

## 🔐 GitHub Secretsへの登録

### STEP 1: リポジトリの設定ページ
1. リポジトリページにアクセス
2. **Settings** タブ
3. 左サイドバー → **Secrets and variables** → **Actions**

### STEP 2: Secret追加
1. **New repository secret** をクリック
2. 以下を入力：
   - **Name**: `GITHUB_TOKEN`
   - **Secret**: コピーしたトークン（`ghp_...`）
3. **Add secret** をクリック

## ✅ 設定確認

### ローカルでテスト
```bash
# トークンを環境変数に設定
export GITHUB_TOKEN=ghp_your_token_here

# Human Interaction Agentをテスト実行
python3 core_agents/human_interaction_agent_v02_github_api.py \
    --repo Koji0525/gemini_AI_Agent \
    --interval 10 \
    --test-duration 1
```

成功すると：
```
✅ GitHub API接続成功: Koji0525/gemini_AI_Agent
🔍 GitHub Issues監視開始
```

## 🚨 セキュリティ注意事項

### トークンの取り扱い
- ❌ Git にコミットしない
- ❌ ログに出力しない
- ❌ 他人に共有しない
- ✅ GitHub Secrets に保存
- ✅ 定期的に更新（90日ごと推奨）

### 漏洩時の対応
1. 即座にGitHubでトークンを削除
2. 新しいトークンを生成
3. GitHub Secretsを更新

## 📊 トークン状態の確認

定期的にチェック：
1. GitHub → Settings → Developer settings
2. Personal access tokens
3. トークンの有効期限を確認

---

**作成日**: 2025-11-01
**対象**: Human Interaction Agent v2.0
**有効期限**: 要確認（推奨90日）
