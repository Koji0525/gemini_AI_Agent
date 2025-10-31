#!/bin/bash

# Day 3: 企業データ実登録実行スクリプト - 修正版

echo "🚀 Day 3 企業データ実登録開始 (修正版)"
echo "=========================================="

# まずデータファイルの存在を確認
if [ ! -f "automation/data/company_dataset.json" ]; then
    echo "❌ 企業データファイルが存在しません: automation/data/company_dataset.json"
    echo "📁 現在のautomation/data/ の内容:"
    ls -la automation/data/ 2>/dev/null || echo "ディレクトリが存在しません"
    exit 1
fi

echo "✅ 企業データファイル確認完了"

# テスト実行
echo "🧪 テスト実行中..."
python3 automation/tests/test_data_population_fixed.py

if [ $? -eq 0 ]; then
    echo "✅ テスト成功"
else
    echo "❌ テスト失敗"
    exit 1
fi

# 本番実行
echo ""
echo "🏢 本番実行開始..."
python3 automation/modules/wp_data_populator_v3_fixed.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Day 3 完了！"
    echo "📊 結果確認: automation/logs/day3/registration_results.json"
else
    echo ""
    echo "❌ Day 3 実行中にエラーが発生しました"
    exit 1
fi

echo ""
echo "📅 次のステップ: Day 4 - Task Executor統合"
echo "=========================================="
