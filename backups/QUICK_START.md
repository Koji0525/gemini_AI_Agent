# 🚀 WordPress完全自動デプロイ - クイックスタート

## 初回セットアップ（3分）
```bash
# たった1コマンド
./wp-setup
```

**このコマンドが自動的に：**
1. ✅ WordPressにプラグインをアップロード
2. ✅ プラグインを有効化
3. ✅ アプリケーションパスワードの取得方法を表示
4. ✅ 自動デプロイ設定
5. ✅ 初回デプロイ実行

**あなたがやること：**
- WordPressのURL、ユーザー名、FTP情報を入力（初回のみ）
- アプリケーションパスワードをコピペ（1回だけ）

---

## 2回目以降（10秒）
```bash
# デプロイだけ
./wp-deploy
```

これだけ！完全自動でWordPressが更新されます。

---

## 何が起こるか

### セットアップ時
1. プラグインファイルをZIP圧縮
2. FTP経由でWordPressにアップロード
3. REST API経由で自動有効化
4. アプリケーションパスワード設定
5. functions.phpを自動生成してデプロイ

### デプロイ時
1. 最新のfunctions.phpを自動生成
2. WordPressに自動デプロイ
3. パーマリンク設定を自動更新
4. エラーチェック

---

## トラブルシューティング

### プラグインアップロード失敗
```bash
# 手動でアップロード
cd deploy_system/wp_auto_deploy_plugin
# このフォルダを /wp-content/plugins/ にアップロード
```

### FTP接続エラー
```bash
# 設定ファイルを削除して再設定
rm tools/wp_config.json
./wp-setup
```

### アプリケーションパスワードがわからない
```bash
# WordPressにログイン
# ユーザー → プロフィール → 「アプリケーションパスワード」
# 「新しいアプリケーションパスワード名」に「AutoDeploy」
# 生成されたパスワードをコピー（スペースは削除）
```

---

## 上級者向け

### GitHub Actions連携
```bash
# .github/workflows/auto-deploy.yml が既に生成されています
# GitHubのSecretsに以下を設定:
# - WP_URL
# - WP_USER  
# - WP_PASSWORD (アプリケーションパスワード)
```

### カスタマイズ
```bash
# 設定ファイル
cat deploy_system/config.json

# ログ確認
cat deploy_system/logs/deploy_*.log
```

---

## よくある質問

**Q: セットアップは何回必要？**
A: 1回だけ。その後は `./wp-deploy` だけでOK

**Q: 複数のWordPressサイトに対応？**
A: 設定ファイルを複数作成可能

**Q: エラーが出たら？**
A: `deploy_system/logs/` のログファイルを確認

**Q: 安全性は？**
A: バックアップを自動作成。元に戻せます

---

## サポート

問題が解決しない場合:
1. ログファイルを確認
2. WordPress管理画面でエラーをチェック
3. FTP/SSH接続を確認

