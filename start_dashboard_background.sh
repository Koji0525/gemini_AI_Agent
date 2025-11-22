#!/bin/bash
# Webダッシュボードをバックグラウンドで起動

cd /workspaces/gemini_AI_Agent

echo "🌐 Webダッシュボードをバックグラウンドで起動..."

# 既存のプロセスを停止
pkill -f "dashboard_server.py" 2>/dev/null

# バックグラウンドで起動
nohup python3 agents/web_dashboard/dashboard_server.py > logs/dashboard.log 2>&1 &

PID=$!
echo "✅ 起動完了 (PID: $PID)"
echo "📍 アクセス: http://localhost:8000"
echo "📝 ログ: tail -f logs/dashboard.log"
echo "⏹️  停止: pkill -f dashboard_server.py"

