#!/bin/bash

# Day 3: 企業データ実登録実行スクリプト - ブロックエディタ対応版

echo "🚀 Day 3 企業データ実登録開始 (ブロックエディタ対応 V5)"
echo "=========================================="

# まず構文エラーを修正
echo "�� 構文エラーを修正中..."
python3 -m py_compile configuration/config_loader.py
if [ $? -eq 0 ]; then
    echo "✅ configuration/config_loader.py 構文OK"
else
    echo "❌ configuration/config_loader.py に構文エラーがあります"
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
echo "  • ブロックエディタ完全対応"
echo "  • 複数のコンテンツ入力方法"
echo "  • コードエディタ経由HTML入力"
echo "  • 段階的なフォールバック戦略"
echo ""

python3 automation/modules/wp_data_populator_v5_block_editor.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 Day 3 完了！"
    echo "📊 結果確認: automation/logs/day3/registration_results_v5.json"
else
    echo ""
    echo "❌ Day 3 実行中にエラーが発生しました"
    echo "📄 詳細ログ: automation/logs/day3/registration_results_v5.json"
fi

echo ""
echo "📅 次のステップ: Day 4 - Task Executor統合"
echo "=========================================="

exit $EXIT_CODE
