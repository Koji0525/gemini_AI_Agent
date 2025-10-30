#!/bin/bash
# ==================================================
# データ分析統合スイート - ワンコマンド実行
# ==================================================

echo "🚀 データ分析統合スイート起動"
echo "=" 60

# 環境チェック
echo ""
echo "📋 環境チェック..."
python3 tools/env_checker.py
if [ $? -ne 0 ]; then
    echo "❌ 環境設定に問題があります"
    exit 1
fi

echo ""
echo "="*60
echo "実行するツールを選択してください："
echo "="*60
echo "1. 📊 インタラクティブダッシュボード（対話式）"
echo "2. 🤖 パターンベース最適化エンジン"
echo "3. 📈 効果測定レポート生成"
echo "4. 🎯 全ツール順次実行"
echo "0. 終了"
echo "="*60

read -p "選択 (0-4): " choice

case $choice in
    1)
        echo "📊 インタラクティブダッシュボードを起動..."
        python3 tools/interactive_dashboard.py
        ;;
    2)
        echo "🤖 パターンベース最適化を実行..."
        python3 tools/pattern_based_optimizer.py
        ;;
    3)
        echo "📈 効果測定レポートを生成..."
        python3 tools/impact_measurement.py
        ;;
    4)
        echo "🎯 全ツールを順次実行..."
        echo ""
        echo "--- パターンベース最適化 ---"
        python3 tools/pattern_based_optimizer.py
        echo ""
        echo "--- 効果測定レポート ---"
        python3 tools/impact_measurement.py
        echo ""
        echo "✅ 全ツール実行完了"
        ;;
    0)
        echo "終了します"
        exit 0
        ;;
    *)
        echo "❌ 無効な選択です"
        exit 1
        ;;
esac

echo ""
echo "🎉 実行完了"
