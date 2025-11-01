#!/bin/bash

# Day 3: 最終版実行スクリプト

echo "🚀 Day 3 企業データ実登録開始 (最終版 V12)"
echo "=========================================="

# まずBrowserControllerのメソッドシグネチャを確認
echo "🔍 BrowserControllerのsetup_browserメソッドを確認中..."
grep -n "def setup_browser" browser_control/browser_controller.py

# 構文チェック
echo "🔧 構文チェック中..."
python3 -m py_compile automation/modules/wp_data_populator_v12_fixed.py
if [ $? -ne 0 ]; then
    echo "❌ 構文エラーがあります"
    exit 1
fi

# データファイル確認
if [ ! -f "automation/data/company_dataset.json" ]; then
    echo "❌ 企業データファイルが存在しません"
    exit 1
fi

echo "✅ 準備完了"

# 本番実行
echo ""
echo "🏢 本番実行開始..."
echo "💡 修正内容:"
echo "  • BrowserControllerの互換性問題を解決"
echo "  • viewport引数をsetup_browser後に設定"
echo "  • 詳細なエラートレースバック追加"
echo ""

python3 automation/modules/wp_data_populator_v12_fixed.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 Day 3 完了！"
    echo "📊 結果確認: automation/logs/day3/registration_results_v12.json"
else
    echo ""
    echo "❌ Day 3 実行中にエラーが発生しました"
    echo "📄 詳細ログ: automation/logs/day3/registration_results_v12.json"
fi

exit $EXIT_CODE
