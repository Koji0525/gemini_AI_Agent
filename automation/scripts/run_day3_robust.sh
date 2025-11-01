#!/bin/bash

# Day 3: ロバスト版実行スクリプト

echo "🚀 Day 3 企業データ実登録開始 (ロバスト版 V13)"
echo "============================================"

# まず診断を実行
echo "🔍 BrowserControllerの診断を実行中..."
python3 automation/scripts/diagnose_browser.py

if [ $? -ne 0 ]; then
    echo "❌ BrowserControllerに問題があります"
    exit 1
fi

# 構文チェック
echo "🔧 構文チェック中..."
python3 -m py_compile automation/modules/wp_data_populator_v13_robust.py
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
echo "  • ページ初期化問題の根本解決"
echo "  • 3段階のリトライメカニズム"
echo "  • 詳細な状態診断機能"
echo "  • 代替ページオブジェクト探索"
echo ""

python3 automation/modules/wp_data_populator_v13_robust.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 Day 3 完了！"
    echo "📊 結果確認: automation/logs/day3/registration_results_v13.json"
else
    echo ""
    echo "❌ Day 3 実行中にエラーが発生しました"
    echo "📄 詳細ログ: automation/logs/day3/registration_results_v13.json"
fi

exit $EXIT_CODE
