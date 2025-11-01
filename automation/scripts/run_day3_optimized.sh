#!/bin/bash

# Day 3: 最適化版実行スクリプト

echo "🚀 Day 3 企業データ実登録開始 (最適化版 V14)"
echo "============================================"

# ネットワーク診断
echo "🔍 ネットワーク接続性を診断中..."
python3 automation/scripts/network_diagnosis.py

if [ $? -ne 0 ]; then
    echo "⚠️ ネットワークに問題がありますが、続行します..."
fi

# 構文チェック
echo "🔧 構文チェック中..."
python3 -m py_compile automation/modules/wp_data_populator_v14_optimized.py
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
echo "💡 最適化内容:"
echo "  • ネットワークタイムアウトの短縮 (90秒→45秒)"
echo "  • ページ読み込み条件の最適化 (networkidle→domcontentloaded)"
echo "  • 段階的なエディタ読み込み確認"
echo "  • リトライメカニズムの強化"
echo ""

python3 automation/modules/wp_data_populator_v14_optimized.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 Day 3 完了！"
    echo "📊 結果確認: automation/logs/day3/registration_results_v14.json"
    echo "📸 デバッグ画像: automation/logs/day3/debug_*.png"
else
    echo ""
    echo "❌ Day 3 実行中にエラーが発生しました"
    echo "📄 詳細ログ: automation/logs/day3/registration_results_v14.json"
fi

exit $EXIT_CODE
