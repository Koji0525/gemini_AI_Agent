# 🚀 完全自律運用システム 起動ガイド

## 現状

✅ **準備完了項目:**
- WordPress自動投稿エージェント（品質スコア10.0/10）
- GitHub Actionsワークフローファイル
- Slack通知機能
- GitHub Issues自動生成機能
- ナレッジベース学習システム

❌ **未完了項目:**
- GitHub Actionsへの登録
- GitHub Secretsの設定
- 24時間自動実行の開始

---

## 🎯 完全自律運用を開始する手順

### Step 1: GitHub Actionsファイルをリポジトリに登録
```bash
cd /workspaces/gemini_AI_Agent

# uz-manda-portalのGitHub Actionsを親リポジトリに追加
cp uz-manda-portal/.github/workflows/wordpress_automation.yml .github/workflows/

# コミット
git add .github/workflows/wordpress_automation.yml
git commit -m "🤖 GitHub Actions自動実行設定追加"
git push
```

### Step 2: GitHub Secretsを設定

GitHubリポジトリ設定で以下のSecretsを追加:

**必須:**
- `WP_URL`: `https://uzbek-ma.com`
- `WP_USERNAME`: WordPress管理者ユーザー名
- `WP_PASSWORD`: WordPress管理者パスワード

**オプション（通知機能用）:**
- `SLACK_WEBHOOK_URL`: Slack Webhook URL
- `GITHUB_TOKEN`: GitHub Personal Access Token

**設定方法:**
1. GitHubリポジトリページを開く
2. Settings → Secrets and variables → Actions
3. 「New repository secret」で各項目を追加

### Step 3: GitHub Actionsを有効化

1. GitHubリポジトリの「Actions」タブを開く
2. ワークフロー「WordPress自動投稿 - 6時間ごと実行」を確認
3. 「Enable workflow」をクリック

### Step 4: 手動実行でテスト

1. Actionsタブでワークフローを選択
2. 「Run workflow」ボタンをクリック
3. 実行結果を確認

### Step 5: 自動実行の確認

- 6時間ごと（0:00, 6:00, 12:00, 18:00 UTC）に自動実行
- 実行結果はActionsタブで確認可能
- エラー時はSlack通知（設定している場合）

---

## 🔄 自動運用の流れ
```
6時間ごとに自動実行
    ↓
WordPress自動投稿（5社）
    ↓
品質スコア計算
    ↓
ナレッジベース記録
    ↓
成功 → Slack通知（成功）
失敗 → Slack通知（エラー） + GitHub Issue自動生成
    ↓
学習システムがパターンを分析
    ↓
次回実行時に改善を自動適用
```

---

## 📊 現在の開発状態

### 達成済み（ローカル実行）
- ✅ Day 3: 5社データ投稿完了
- ✅ Day 4: Task Executor統合
- ✅ Day 5: Self Learning Pipeline統合
- ✅ Day 6: 自律運用コード準備完了

### 次のステップ（本番稼働）
- 📌 GitHub Actionsに登録
- 📌 Secretsを設定
- 📌 自動実行開始
- 📌 24時間監視開始

---

## ⚠️ 重要な注意事項

1. **GitHub Actionsの実行時間**
   - 無料プランは月2,000分まで
   - 1回の実行: 約1分
   - 6時間ごと = 1日4回 = 月120回 ≈ 120分/月

2. **WordPress API負荷**
   - 6時間ごとに5社投稿
   - API呼び出し: 約15回/実行
   - 適切な間隔を保っている

3. **エラー処理**
   - 自動リトライ: 3回まで
   - 失敗時: GitHub Issue自動生成
   - 通知: Slack（設定時）

---

## 🎯 完全自律運用の定義

**完全自律運用 = 人間の介入なしで以下が自動実行:**

1. ✅ 6時間ごとに自動でWordPress投稿
2. ✅ 品質スコアを自動計算
3. ✅ ナレッジベースに自動記録
4. ✅ 失敗時に自動でIssue作成
5. ✅ 成功/失敗を自動通知
6. ✅ 学習システムが自動で改善

**現状**: コードは完成、GitHub Actionsへの登録が必要

