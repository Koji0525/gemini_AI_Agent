#!/bin/bash

# Day 3: 企業データ実登録実行スクリプト

echo "🚀 Day 3 企業データ実登録開始"
echo "=========================================="

# テスト実行
echo "🧪 テスト実行中..."
python3 automation/tests/test_data_population.py

if [ $? -eq 0 ]; then
    echo "✅ テスト成功"
else
    echo "❌ テスト失敗"
    exit 1
fi

# 本番実行
echo ""
echo "🏢 本番実行開始..."
python3 automation/modules/wp_data_populator_v3.py

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
