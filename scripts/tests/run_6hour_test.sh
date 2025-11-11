#!/bin/bash
echo "⏱️  6時間稼働テスト開始"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# テスト開始時刻記録
START_TIME=$(date +%s)
START_DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "開始時刻: $START_DATE"
echo ""

# ログディレクトリ作成
mkdir -p logs

# ログファイル名
LOG_FILE="logs/6hour_test_$(date +%Y%m%d_%H%M%S).log"

# v31を6時間実行（引数で秒数指定: 21600秒 = 6時間）
echo "🚀 IntegratedOrchestrator v31起動中..."
echo "   実行時間: 6時間 (21600秒)"
echo "   ログファイル: $LOG_FILE"
echo ""

# バックグラウンド実行
python3 scripts/integrated/integrated_orchestrator_v31_core.py 21600 \
    > "$LOG_FILE" 2>&1 &

PID=$!
echo "✅ 起動完了 (PID: $PID)"
echo ""

# 監視ループ（5分ごとにチェック × 72回 = 360分 = 6時間）
echo "📊 5分ごとに状態チェック開始..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for i in {1..72}; do
    sleep 300  # 5分待機
    
    # プロセス生存確認
    if ! kill -0 $PID 2>/dev/null; then
        echo ""
        echo "❌ プロセス停止検出 ($(($i * 5))分経過)"
        echo "   ログを確認してください: $LOG_FILE"
        exit 1
    fi
    
    # 進捗表示
    ELAPSED=$(($i * 5))
    REMAINING=$((360 - $ELAPSED))
    echo "[$i/72] $(date '+%H:%M:%S') | 経過: ${ELAPSED}分 | 残り: ${REMAINING}分 | ✅ 正常動作中"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 6時間テスト完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 終了時刻記録
END_TIME=$(date +%s)
END_DATE=$(date '+%Y-%m-%d %H:%M:%S')
DURATION=$((END_TIME - START_TIME))
DURATION_MIN=$((DURATION / 60))

echo "終了時刻: $END_DATE"
echo "実行時間: ${DURATION_MIN}分"
echo "ログファイル: $LOG_FILE"
echo ""

# ログ内エラー確認
ERROR_COUNT=$(grep -i "error\|exception\|failed" "$LOG_FILE" | wc -l)
echo "📊 エラー検出数: $ERROR_COUNT"

if [ $ERROR_COUNT -eq 0 ]; then
    echo "✅ エラーなし - テスト成功"
else
    echo "⚠️  エラーあり - ログを確認してください"
fi
