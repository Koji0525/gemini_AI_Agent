#!/bin/bash

# Day 3: 企業データ実登録実行スクリプト - 最終版

echo "🚀 Day 3 企業データ実登録開始 (最終版)"
echo "=========================================="

# まずデータファイルの存在を確認
if [ ! -f "automation/data/company_dataset.json" ]; then
    echo "❌ 企業データファイルが存在しません: automation/data/company_dataset.json"
    echo "📁 現在のautomation/data/ の内容:"
    ls -la automation/data/ 2>/dev/null || echo "ディレクトリが存在しません"
    exit 1
fi

echo "✅ 企業データファイル確認完了"

# ログディレクトリ作成
mkdir -p automation/logs/day3

# 本番実行
echo ""
echo "🏢 本番実行開始..."
python3 automation/modules/wp_data_populator_v3_final.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 Day 3 完了！"
    echo "📊 結果確認: automation/logs/day3/registration_results.json"
else
    echo ""
    echo "❌ Day 3 実行中にエラーが発生しました"
    echo "📄 詳細ログ: automation/logs/day3/registration_results.json"
fi

echo ""
echo "📅 次のステップ: Day 4 - Task Executor統合"
echo "=========================================="

exit $EXIT_CODE
