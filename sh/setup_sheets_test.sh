#!/bin/bash
set -e

echo "=========================================="
echo "📊 Google Sheets テスト準備"
echo "=========================================="

echo ""
echo "必要な設定:"
echo "1. Google Sheets ID"
echo "2. service_account.json の確認"
echo ""

# service_account.json の確認
if [ ! -f "configuration/service_account.json" ]; then
    echo "❌ service_account.json が見つかりません"
    echo "   configuration/service_account.json を配置してください"
    exit 1
fi

echo "✅ service_account.json 確認完了"

# スプレッドシートIDの入力
echo ""
echo "Google Sheets の設定:"
echo ""
read -p "スプレッドシートID を入力してください: " SHEET_ID

if [ -z "$SHEET_ID" ]; then
    echo "❌ スプレッドシートIDが入力されていません"
    exit 1
fi

# 設定ファイルに保存
cat > config/sheets_config.json << CONFIG
{
    "spreadsheet_id": "$SHEET_ID",
    "service_account_file": "configuration/service_account.json"
}
CONFIG

echo ""
echo "✅ 設定保存完了: config/sheets_config.json"

echo ""
echo "=========================================="
echo "📋 次のステップ"
echo "=========================================="
echo ""
echo "Google Sheets に以下の形式でテストデータを作成してください:"
echo ""
echo "シート名: tasks"
echo ""
echo "列:"
echo "  A列: id"
echo "  B列: title"
echo "  C列: prompt"
echo "  D列: status"
echo "  E列: timestamp"
echo "  F列: result"
echo "  G列: error"
echo "  H列: output_file"
echo ""
echo "テストデータ（1行目）:"
echo "  A2: TEST001"
echo "  B2: テストタスク"
echo "  C2: Please write a short summary about AI."
echo "  D2: pending"
echo ""
echo "準備ができたら:"
echo "  ./test_sheets_integration.sh"
echo ""

