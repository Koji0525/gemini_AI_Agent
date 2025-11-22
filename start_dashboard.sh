#!/bin/bash
# Webダッシュボードを起動

cd /workspaces/gemini_AI_Agent

echo "🌐 Webダッシュボードを起動します..."
echo ""

# FastAPIとuvicornのチェック
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  FastAPIがインストールされていません"
    echo "📦 インストール中..."
    pip install fastapi uvicorn --break-system-packages
fi

# サーバー起動
python3 agents/web_dashboard/dashboard_server.py

