#!/bin/bash

# Day 3: 企業データ実登録実行スクリプト - 直接入力版（構文修正）

echo "🚀 Day 3 企業データ実登録開始 (直接入力版 V9 - 構文修正)"
echo "=========================================="

# 構文チェック
echo "🔧 構文チェック中..."
python3 -m py_compile automation/modules/wp_data_populator_v9_direct_fixed.py
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
echo "  • 構文エラー修正（JavaScriptテンプレートリテラル問題解決）"
echo "  • JavaScript直接実行でコンテンツ設定"
echo "  • 複数の入力方法で確実性向上"
echo "  • 詳細なコンテンツ生成（500文字以上）"
echo ""

python3 automation/modules/wp_data_populator_v9_direct_fixed.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 Day 3 完了！"
    echo "📊 結果確認: automation/logs/day3/registration_results_v9_fixed.json"
    echo ""
    echo "🔍 WordPress管理画面で以下の点を確認してください:"
    echo "   • 本文の文字数が500文字以上になっているか"
    echo "   • 企業データの内容が正しく表示されているか"
    echo "   • すべての企業が公開状態になっているか"
else
    echo ""
    echo "❌ Day 3 実行中にエラーが発生しました"
    echo "📄 詳細ログ: automation/logs/day3/registration_results_v9_fixed.json"
fi

echo ""
echo "📅 次のステップ: Day 4 - Task Executor統合"
echo "=========================================="

exit $EXIT_CODE
