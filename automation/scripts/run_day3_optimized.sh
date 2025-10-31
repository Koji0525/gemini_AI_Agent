#!/bin/bash

# Day 3: 企業データ実登録実行スクリプト - 最適化版

echo "🚀 Day 3 企業データ実登録開始 (最適化版 V7)"
echo "=========================================="

# 構文チェック
echo "🔧 構文チェック中..."
python3 -m py_compile automation/modules/wp_data_populator_v7_optimized.py
if [ $? -ne 0 ]; then
    echo "❌ 構文エラーがあります"
    exit 1
fi

# データファイル確認
if [ ! -f "automation/data/company_dataset.json" ]; then
    echo "❌ 企業データファイルが存在しません"
    exit 1
fi

echo "✅ 企業データファイル確認完了"

# ログディレクトリ作成
mkdir -p automation/logs/day3

# 本番実行
echo ""
echo "🏢 本番実行開始..."
echo "💡 改善点:"
echo "  • タイムアウト時間延長と待機条件最適化"
echo "  • ブロックエディタ完全対応"
echo "  • 複数の入力方法によるフォールバック"
echo "  • シンプルなテキストコンテンツで確実性向上"
echo ""

python3 automation/modules/wp_data_populator_v7_optimized.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 Day 3 完了！"
    echo "📊 結果確認: automation/logs/day3/registration_results_v7.json"
else
    echo ""
    echo "❌ Day 3 実行中にエラーが発生しました"
    echo "📄 詳細ログ: automation/logs/day3/registration_results_v7.json"
fi

echo ""
echo "📅 次のステップ: Day 4 - Task Executor統合"
echo "=========================================="

exit $EXIT_CODE
