#!/bin/bash
# Webダッシュボードをバックグラウンドで起動 v2

cd /workspaces/gemini_AI_Agent

# デフォルトポート
PORT=8000

# ポート指定オプション
while [[ $# -gt 0 ]]; do
    case $1 in
        --port|-p)
            PORT="$2"
            shift 2
            ;;
        *)
            echo "不明なオプション: $1"
            exit 1
            ;;
    esac
done

echo "🌐 Webダッシュボードをバックグラウンドで起動..."
echo "   ポート: $PORT"
echo ""

# 既存のプロセスを停止
echo "🔄 既存のダッシュボードプロセスを停止中..."
pkill -f "dashboard_server.py" 2>/dev/null
sleep 2

# ポートが使用中かチェック
if lsof -ti:$PORT >/dev/null 2>&1; then
    echo "⚠️  ポート $PORT は依然として使用されています"
    PID=$(lsof -ti:$PORT)
    echo "   PID: $PID を強制停止中..."
    kill -9 $PID 2>/dev/null
    sleep 2
fi

# FastAPIとuvicornのチェック
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 FastAPIをインストール中..."
    pip install fastapi uvicorn --break-system-packages
fi

# バックグラウンドで起動
mkdir -p logs

nohup python3 -c "
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')
from agents.web_dashboard.dashboard_server import start_server
start_server(port=$PORT)
" > logs/dashboard_${PORT}.log 2>&1 &

PID=$!
sleep 3

# 起動確認
if ps -p $PID > /dev/null; then
    echo "✅ 起動完了 (PID: $PID)"
    echo ""
    echo "📍 アクセス:"
    echo "   http://localhost:$PORT"
    echo "   http://0.0.0.0:$PORT"
    echo ""
    echo "📝 ログ確認:"
    echo "   tail -f logs/dashboard_${PORT}.log"
    echo ""
    echo "⏹️  停止方法:"
    echo "   pkill -f dashboard_server.py"
    echo "   または"
    echo "   kill $PID"
else
    echo "❌ 起動に失敗しました"
    echo "   ログを確認: cat logs/dashboard_${PORT}.log"
    exit 1
fi

