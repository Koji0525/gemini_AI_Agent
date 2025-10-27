#!/bin/bash

echo "=========================================="
echo "✅ セットアップ最終確認"
echo "=========================================="

echo ""
echo "📁 [1/3] ファイル配置確認"
echo "=========================================="

if [ -f "configuration/service_account.json" ]; then
    echo "✅ configuration/service_account.json 存在"
    echo "   サイズ: $(stat -c%s configuration/service_account.json 2>/dev/null || stat -f%z configuration/service_account.json) bytes"
else
    echo "❌ configuration/service_account.json が見つかりません"
    echo "�� 上記の移動手順を実行してください"
fi

echo ""
echo "📝 [2/3] config_utils.py の設定確認"
echo "=========================================="

if grep -q "SERVICE_ACCOUNT" configuration/config_utils.py; then
    echo "✅ SERVICE_ACCOUNT 設定あり"
    grep "SERVICE_ACCOUNT" configuration/config_utils.py
else
    echo "⚠️  SERVICE_ACCOUNT 設定が見つかりません"
fi

echo ""
echo "🔗 [3/3] sheets_manager.py との連携確認"
echo "=========================================="

echo "sheets_manager.py のservice_account参照:"
grep -n "service_account_file\|SERVICE_ACCOUNT" tools/sheets_manager.py | head -5

echo ""
echo "=========================================="
echo "✅ 確認完了"
echo "=========================================="

