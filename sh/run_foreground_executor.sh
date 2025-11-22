#!/bin/bash
# フォアグラウンド実行スクリプト（ターミナル2用）

cd /workspaces/gemini_AI_Agent

clear

cat << 'BANNER'
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║         🚀 24時間自律開発システム - タスク実行ログ                  ║
║                                                                      ║
║   このターミナルでタスク実行のログをリアルタイム表示します          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
BANNER

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 システム状態を監視中..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

STATE_FILE="/tmp/system_control.state"
LOG_FILE="logs/autonomous_v6_$(TZ=Asia/Tokyo date +%y%m%d_%H%M).log"

echo "⏳ ダッシュボードから開始ボタンが押されるのを待機中..."
echo "   http://localhost:8000 で「▶️ 開始」ボタンをクリックしてください"
echo ""

# システム起動を待機
while true; do
    if [ -f "$STATE_FILE" ]; then
        STATE=$(cat $STATE_FILE)
        if [ "$STATE" = "running" ]; then
            echo "✅ システムが起動しました！"
            echo ""
            break
        fi
    fi
    sleep 2
done

# ログファイルが作成されるまで待機
echo "🔄 ログファイルの作成を待機中..."
while [ ! -f "$LOG_FILE" ] && [ ! -f "logs/autonomous_main.log" ]; do
    sleep 1
    # 最新のログファイルを検索
    LATEST_LOG=$(ls -t logs/autonomous_v6_*.log 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        LOG_FILE=$LATEST_LOG
        break
    fi
done

echo "📝 ログファイル: $LOG_FILE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 タスク実行ログをリアルタイム表示"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 既存のログがあれば最後の20行を表示
if [ -f "$LOG_FILE" ]; then
    tail -20 "$LOG_FILE"
fi

# ログをリアルタイム表示
tail -f "$LOG_FILE" logs/autonomous_main.log 2>/dev/null

