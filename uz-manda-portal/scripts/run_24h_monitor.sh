#!/bin/bash

# 24時間監視テストスクリプト
echo "🚀 24時間監視テストを開始します..."
echo "開始時刻: $(date)"

# 環境変数を設定
export WP_URL="https://uzbek-ma.com"
export WP_USERNAME="uzbek" 
export WP_PASSWORD="RkLU07FkrNpeiENdFx3swseJ"

# 実行間隔（分単位でテスト - 本番は6時間）
INTERVAL_MINUTES=1  # テスト用1分間隔
TOTAL_CYCLES=3      # テスト用3回実行

for ((i=1; i<=TOTAL_CYCLES; i++)); do
    echo ""
    echo "=========================================="
    echo "🔄 実行 $i/$TOTAL_CYCLES ($(date))"
    echo "=========================================="
    
    # 環境変数確認
    echo "🔧 環境変数確認:"
    echo "WP_URL: $WP_URL"
    echo "WP_USERNAME: $WP_USERNAME"
    echo "WP_PASSWORD: ${WP_PASSWORD:0:6}..."
    
    # メイン実行
    cd /workspaces/gemini_AI_Agent/uz-manda-portal
    python3 scripts/run_day4_integrated.py
    
    # 最終実行でなければ待機
    if [ $i -lt $TOTAL_CYCLES ]; then
        echo ""
        echo "⏰ 次の実行まで ${INTERVAL_MINUTES}分待機..."
        echo "次回実行: $(date -d "+${INTERVAL_MINUTES} minutes")"
        sleep $(($INTERVAL_MINUTES * 60))
    fi
done

echo ""
echo "=========================================="
echo "🎉 24時間監視テスト完了！ ($(date))"
echo "=========================================="
