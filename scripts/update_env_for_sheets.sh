#!/bin/bash

# ================================================
# .env設定アシスタント (Google Sheets認証)
# ================================================

echo "================================================"
echo "🔧 Google Sheets認証設定アシスタント"
echo "================================================"
echo ""

# JSONファイルを検索
JSON_FILES=(*.json)

if [ ${#JSON_FILES[@]} -eq 0 ] || [ ! -f "${JSON_FILES[0]}" ]; then
    echo "❌ サービスアカウントJSONファイルが見つかりません"
    echo ""
    echo "📝 次の手順でファイルを取得してください:"
    echo "   1. Google Cloud Console でサービスアカウントを作成"
    echo "   2. JSONキーをダウンロード"
    echo "   3. このプロジェクトのルートディレクトリに配置"
    echo "   4. このスクリプトを再実行"
    exit 1
fi

echo "✅ 見つかったJSONファイル:"
for i in "${!JSON_FILES[@]}"; do
    echo "   $((i+1)). ${JSON_FILES[$i]}"
done
echo ""

# デフォルトで最初のファイルを使用
JSON_FILE="${JSON_FILES[0]}"
echo "使用するファイル: $JSON_FILE"
echo ""

# 現在の.env設定を確認
echo "【現在の.env設定】"
grep -E "SERVICE_ACCOUNT|GOOGLE_APPLICATION_CREDENTIALS|SPREADSHEET_ID" .env 2>/dev/null || echo "  (設定なし)"
echo ""

# .envに設定を追加/更新
echo "【.env更新中】"

# SERVICE_ACCOUNT_FILE
if grep -q "^SERVICE_ACCOUNT_FILE=" .env 2>/dev/null; then
    sed -i "s|^SERVICE_ACCOUNT_FILE=.*|SERVICE_ACCOUNT_FILE=$JSON_FILE|" .env
    echo "✅ SERVICE_ACCOUNT_FILE を更新"
else
    echo "SERVICE_ACCOUNT_FILE=$JSON_FILE" >> .env
    echo "✅ SERVICE_ACCOUNT_FILE を追加"
fi

# GOOGLE_APPLICATION_CREDENTIALS
if grep -q "^GOOGLE_APPLICATION_CREDENTIALS=" .env 2>/dev/null; then
    sed -i "s|^GOOGLE_APPLICATION_CREDENTIALS=.*|GOOGLE_APPLICATION_CREDENTIALS=$JSON_FILE|" .env
    echo "✅ GOOGLE_APPLICATION_CREDENTIALS を更新"
else
    echo "GOOGLE_APPLICATION_CREDENTIALS=$JSON_FILE" >> .env
    echo "✅ GOOGLE_APPLICATION_CREDENTIALS を追加"
fi

echo ""
echo "【更新後の設定】"
grep -E "SERVICE_ACCOUNT|GOOGLE_APPLICATION_CREDENTIALS|SPREADSHEET_ID" .env
echo ""

echo "================================================"
echo "✅ 認証設定完了"
echo "================================================"
echo ""
echo "次のステップ:"
echo "  python3 scripts/setup_sheets_auth.py  # 設定確認"
echo "  python3 scripts/create_retry_history_sheet.py  # シート作成"
echo ""
