#!/bin/bash
# ====================================
# 環境変数設定スクリプト
# すべてのshスクリプトで使用
# ====================================

# プロジェクトルートに移動
cd /workspaces/gemini_AI_Agent || exit 1

# .envファイルから環境変数を読み込み
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
    echo "✅ .env 環境変数読み込み完了"
else
    echo "❌ .envファイルが見つかりません"
    echo "   場所: $(pwd)/.env"
    exit 1
fi

# サービスアカウントファイルの設定（必須）
if [ -z "$SERVICE_ACCOUNT_FILE" ]; then
    export SERVICE_ACCOUNT_FILE="configuration/service_account.json"
    echo "✅ SERVICE_ACCOUNT_FILE 設定: $SERVICE_ACCOUNT_FILE"
fi

if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    export GOOGLE_APPLICATION_CREDENTIALS="configuration/service_account.json"
    echo "✅ GOOGLE_APPLICATION_CREDENTIALS 設定: $GOOGLE_APPLICATION_CREDENTIALS"
fi

# 環境変数の確認
echo ""
echo "🔑 環境変数確認:"
echo "   PROJECT_ROOT: $(pwd)"
echo "   SPREADSHEET_ID: ${SPREADSHEET_ID:0:20}..."
echo "   SERVICE_ACCOUNT_FILE: $SERVICE_ACCOUNT_FILE"

# ファイル存在確認
if [ -f "$SERVICE_ACCOUNT_FILE" ]; then
    echo "   ✅ サービスアカウントファイル存在"
else
    echo "   ❌ サービスアカウントファイルが見つかりません"
    echo "   パス: $(pwd)/$SERVICE_ACCOUNT_FILE"
    exit 1
fi

echo ""
echo "✅ 環境変数設定完了"
echo ""

# この後、他のスクリプトで使用可能
# 使用例: source sh/setup_env.sh && bash sh/test_task_execution.sh
