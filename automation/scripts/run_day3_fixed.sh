#!/bin/bash

# Day 3: 修正版実行スクリプト

echo "🚀 Day 3 企業データ実登録開始 (修正版)"
echo "======================================"

# 構文チェック
echo "🔧 構文チェック中..."
python3 automation/scripts/check_syntax.py
if [ $? -ne 0 ]; then
    echo "❌ 構文エラーがあります - 修正してください"
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
python3 automation/modules/wp_data_populator_v10_final.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 Day 3 完了！"
    echo "📊 結果確認: automation/logs/day3/registration_results_v11.json"
else
    echo ""
    echo "❌ Day 3 実行中にエラーが発生しました"
fi

exit $EXIT_CODE
