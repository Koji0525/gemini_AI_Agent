#!/bin/bash

echo "================================================"
echo "🔧 手動.env設定ツール"
echo "================================================"
echo ""

# 現在の.env内容を表示（APIキーは隠す）
echo "【現在の.env設定（抜粋）】"
grep -E "SERVICE|GOOGLE|SPREADSHEET" .env 2>/dev/null || echo "  (該当設定なし)"
echo ""

# JSONファイル一覧表示
echo "【利用可能なJSONファイル】"
ls -lh *.json 2>/dev/null | awk '{print "  " NR ". " $9 " (" $5 ")"}'
echo ""

# ユーザーに確認
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "質問: どのファイルがGoogle Cloudサービスアカウントですか？"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "特徴:"
echo "  - Google Cloud Consoleからダウンロードした"
echo "  - ファイル名に日付やproject名が含まれることが多い"
echo "  - 2-4KB程度のサイズ"
echo "  - 中に 'private_key' と 'client_email' が含まれる"
echo ""
echo "該当するファイルがない場合:"
echo "  → Google Cloud Consoleから新規作成が必要です"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "ファイル名を入力してください（例: my-service-account.json）: " SA_FILE

if [ -z "$SA_FILE" ]; then
    echo "❌ ファイル名が入力されませんでした"
    exit 1
fi

if [ ! -f "$SA_FILE" ]; then
    echo "❌ ファイルが見つかりません: $SA_FILE"
    echo ""
    echo "現在のディレクトリ内のJSONファイル:"
    ls -1 *.json 2>/dev/null || echo "  (なし)"
    exit 1
fi

# JSONの内容を検証
echo ""
echo "🔍 ファイル内容を検証中..."

if grep -q "private_key" "$SA_FILE" && grep -q "client_email" "$SA_FILE"; then
    echo "✅ サービスアカウントファイルとして有効です"
    
    # プロジェクトID抽出
    PROJECT_ID=$(grep -o '"project_id": "[^"]*"' "$SA_FILE" | cut -d'"' -f4)
    CLIENT_EMAIL=$(grep -o '"client_email": "[^"]*"' "$SA_FILE" | cut -d'"' -f4)
    
    echo "  プロジェクトID: $PROJECT_ID"
    echo "  クライアントメール: $CLIENT_EMAIL"
else
    echo "⚠️  警告: このファイルはサービスアカウントではない可能性があります"
    read -p "それでも続行しますか？ (y/N): " CONFIRM
    if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
        echo "キャンセルしました"
        exit 1
    fi
fi

# .envを更新
echo ""
echo "📝 .envファイルを更新中..."

# SERVICE_ACCOUNT_FILE
if grep -q "^SERVICE_ACCOUNT_FILE=" .env 2>/dev/null; then
    sed -i "s|^SERVICE_ACCOUNT_FILE=.*|SERVICE_ACCOUNT_FILE=$SA_FILE|" .env
    echo "✅ SERVICE_ACCOUNT_FILE を更新"
else
    echo "" >> .env
    echo "# Google Sheets認証" >> .env
    echo "SERVICE_ACCOUNT_FILE=$SA_FILE" >> .env
    echo "✅ SERVICE_ACCOUNT_FILE を追加"
fi

# GOOGLE_APPLICATION_CREDENTIALS
if grep -q "^GOOGLE_APPLICATION_CREDENTIALS=" .env 2>/dev/null; then
    sed -i "s|^GOOGLE_APPLICATION_CREDENTIALS=.*|GOOGLE_APPLICATION_CREDENTIALS=$SA_FILE|" .env
    echo "✅ GOOGLE_APPLICATION_CREDENTIALS を更新"
else
    echo "GOOGLE_APPLICATION_CREDENTIALS=$SA_FILE" >> .env
    echo "✅ GOOGLE_APPLICATION_CREDENTIALS を追加"
fi

# 古い設定を削除
if grep -q "^GOOGLE_SERVICE_ACCOUNT_FILE=" .env 2>/dev/null; then
    sed -i '/^GOOGLE_SERVICE_ACCOUNT_FILE=/d' .env
    echo "🗑️  GOOGLE_SERVICE_ACCOUNT_FILE を削除（不要な設定）"
fi

echo ""
echo "【更新後の設定】"
grep -E "SERVICE_ACCOUNT_FILE|GOOGLE_APPLICATION_CREDENTIALS|SPREADSHEET_ID" .env
echo ""

echo "================================================"
echo "✅ 設定完了"
echo "================================================"
echo ""
echo "🚀 次のステップ:"
echo "  python3 scripts/create_retry_history_sheet.py"
echo ""
