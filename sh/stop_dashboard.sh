#!/bin/bash
# ==
# Phase 5 ダッシュボードサーバー停止スクリプト
# ==

echo "🛑 ダッシュボードサーバー停止中..."

# ポート5000-5002のプロセスを停止
for PORT in 5000 5001 5002; do
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        PID=$(lsof -ti:$PORT)
        kill -9 $PID 2>/dev/null
        echo "✅ ポート $PORT のプロセス停止（PID: $PID）"
    fi
done

echo "✅ 停止完了"
