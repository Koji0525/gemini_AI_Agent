#!/bin/bash

# Day 3: 企業データ実登録実行スクリプト - 信頼性向上版

echo "🚀 Day 3 企業データ実登録開始 (信頼性向上版 V8)"
echo "=========================================="

# 構文チェック
echo "🔧 構文チェック中..."
python3 -m py_compile automation/modules/wp_data_populator_v8_reliable.py
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
echo "  • コードエディタを使用しない確実な方法"
echo "  • 直接段落ブロック入力とキーボード操作"
echo "  • シンプルなクラシックブロック使用"
echo "  • 複数の公開ボタンセレクタ対応"
echo ""

python3 automation/modules/wp_data_populator_v8_reliable.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 Day 3 完了！"
    echo "📊 結果確認: automation/logs/day3/registration_results_v8.json"
else
    echo ""
    echo "❌ Day 3 実行中にエラーが発生しました"
    echo "📄 詳細ログ: automation/logs/day3/registration_results_v8.json"
fi

echo ""
echo "📅 次のステップ: Day 4 - Task Executor統合"
echo "=========================================="

exit $EXIT_CODE
