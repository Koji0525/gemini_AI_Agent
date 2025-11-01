#!/bin/bash

# Day 3: 企業データ実登録実行スクリプト - 総合対策版

echo "🚀 Day 3 企業データ実登録開始 (総合対策版 V11)"
echo "=========================================="

# 構文チェック
echo "🔧 構文チェック中..."
python3 -m py_compile automation/modules/wp_data_populator_v11_comprehensive.py
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
echo "💡 総合対策の内容:"
echo "  • 10個以上の原因分析と対策"
echo "  • 詳細なデバッグ機能"
echo "  • 5段階のコンテンツ入力方法"
echo "  • スクリーンショットによる状態確認"
echo "  • Base64エンコードによる安全なデータ転送"
echo ""

python3 automation/modules/wp_data_populator_v11_comprehensive.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 Day 3 完了！"
    echo "📊 結果確認: automation/logs/day3/registration_results_v11.json"
    echo ""
    echo "🔍 デバッグ情報:"
    echo "   • スクリーンショット: automation/logs/day3/debug_*.png"
    echo "   • 詳細ログ: automation/logs/day3/registration_results_v11.json"
else
    echo ""
    echo "❌ Day 3 実行中にエラーが発生しました"
    echo "📄 詳細ログ: automation/logs/day3/registration_results_v11.json"
fi

echo ""
echo "📅 次のステップ: Day 4 - Task Executor統合"
echo "=========================================="

exit $EXIT_CODE
