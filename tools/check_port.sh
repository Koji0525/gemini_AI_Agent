#!/bin/bash
# ポート使用状況を確認

PORT=${1:-8000}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 ポート $PORT の使用状況"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if lsof -ti:$PORT >/dev/null 2>&1; then
    echo "⚠️  ポート $PORT は使用中です"
    echo ""
    echo "【詳細情報】"
    lsof -i:$PORT
    echo ""
    
    PID=$(lsof -ti:$PORT)
    echo "【プロセス情報】"
    ps aux | grep $PID | grep -v grep
    echo ""
    
    echo "【停止方法】"
    echo "  kill -9 $PID"
    echo "  または"
    echo "  pkill -f dashboard_server.py"
else
    echo "✅ ポート $PORT は使用可能です"
fi

