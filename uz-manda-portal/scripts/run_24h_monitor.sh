#!/bin/bash

# 24時間監視テストスクリプト
echo "🚀 24時間監視テストを開始します..."
echo "開始時刻: $(date)"

# 実行間隔（6時間）
INTERVAL_HOURS=6
TOTAL_CYCLES=4

for ((i=1; i<=TOTAL_CYCLES; i++)); do
    echo ""
    echo "=========================================="
    echo "🔄 実行 $i/$TOTAL_CYCLES ($(date))"
    echo "=========================================="
    
    # メイン実行
    cd /workspaces/gemini_AI_Agent/uz-manda-portal
    python3 scripts/run_day4_integrated.py
    
    # 最終実行でなければ待機
    if [ $i -lt $TOTAL_CYCLES ]; then
        echo ""
        echo "⏰ 次の実行まで ${INTERVAL_HOURS}時間待機..."
        echo "次回実行: $(date -d "+${INTERVAL_HOURS} hours")"
        sleep $(($INTERVAL_HOURS * 3600))
    fi
done

echo ""
echo "=========================================="
echo "🎉 24時間監視テスト完了！ ($(date))"
echo "=========================================="
echo "📊 最終レポートを生成..."
python3 scripts/generate_24h_report.py
