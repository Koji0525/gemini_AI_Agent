# Phase 6: Google Sheets API 認証設定ガイド

## 📋 概要

Phase 6の本番耐久テスト（P6-005、P6-006）を実施するには、
Google Sheets APIの認証情報が必要です。

## 🔑 認証情報の取得方法

### STEP 1: Google Cloud Consoleでプロジェクト作成

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成（または既存を選択）
3. プロジェクト名: `gemini-ai-agent`（任意）

### STEP 2: Google Sheets APIを有効化

1. 「APIとサービス」→「ライブラリ」
2. "Google Sheets API" を検索
3. 「有効にする」をクリック

### STEP 3: サービスアカウント作成

1. 「APIとサービス」→「認証情報」
2. 「認証情報を作成」→「サービスアカウント」
3. サービスアカウント名: `gemini-agent`（任意）
4. ロール: 「編集者」を選択
5. 「完了」をクリック

### STEP 4: サービスアカウントキー生成

1. 作成したサービスアカウントをクリック
2. 「キー」タブ→「鍵を追加」→「新しい鍵を作成」
3. キーのタイプ: JSON
4. 「作成」→ JSONファイルがダウンロードされる

### STEP 5: 認証ファイル配置
```bash
# ダウンロードしたJSONファイルを配置
cp ~/Downloads/gemini-agent-xxxxx.json configuration/service_account.json

# パーミッション設定
chmod 600 configuration/service_account.json
```

### STEP 6: スプレッドシートの共有設定

1. Google Sheetsを開く
2. 「共有」をクリック
3. サービスアカウントのメールアドレスを追加
   - 形式: `gemini-agent@project-id.iam.gserviceaccount.com`
4. 権限: 「編集者」
5. 「送信」をクリック

### STEP 7: 環境変数設定
```bash
# .envファイル作成（なければ）
cat > .env << 'EOF'
# Google Sheets API
SPREADSHEET_ID=your_spreadsheet_id_here
GOOGLE_APPLICATION_CREDENTIALS=configuration/service_account.json

# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
EOF

# スプレッドシートIDの取得方法
# URLから取得: https://docs.google.com/spreadsheets/d/[THIS_IS_THE_ID]/edit
```

### STEP 8: 接続テスト
```bash
# 接続テスト実行
python3 scripts/test_google_sheets_connection.py

# 期待される出力:
# ✅ 初期化成功
# ✅ 読み取り成功: X件のゴール取得
# ✅ 読み取り成功: Y件のタスク取得
```

## ✅ 設定完了確認
```bash
# 認証ファイル確認
ls -l configuration/service_account.json

# 環境変数確認
cat .env | grep SPREADSHEET_ID
cat .env | grep GOOGLE_APPLICATION_CREDENTIALS
```

---

## 🚀 本番耐久テスト実行

認証設定完了後、以下のコマンドで耐久テストを実行：
```bash
# P6-005: 6時間テスト（カスタム）
for i in {1..24}; do
    echo "サイクル $i/24"
    python3 agents/complete_engine_ultimate.py --count 1
    sleep 900  # 15分待機
done

# P6-006: 24時間テスト
bash sh/run_autonomous_24h_v2.sh
```

---

## ⚠️ トラブルシューティング

### エラー: 認証情報が見つかりません

**原因**: service_account.jsonが正しく配置されていない

**対処**:
```bash
# ファイルパス確認
ls -l configuration/service_account.json

# 再配置
cp path/to/downloaded.json configuration/service_account.json
```

### エラー: 権限がありません

**原因**: スプレッドシートがサービスアカウントと共有されていない

**対処**:
1. Google Sheetsを開く
2. サービスアカウントのメールを共有設定に追加
3. 権限を「編集者」に設定

### エラー: API制限

**原因**: Google Sheets APIのクォータ超過

**対処**:
- 実行間隔を長くする（15分→30分）
- 複数のサービスアカウントで負荷分散

---

**最終更新**: 2025年11月26日
