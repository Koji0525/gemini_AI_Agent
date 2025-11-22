#!/bin/bash
# Webダッシュボード起動スクリプト v2（ポート競合対応）

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

echo "🌐 Webダッシュボードを起動します..."
echo "   ポート: $PORT"
echo ""

# ポートが使用中かチェック
if lsof -ti:$PORT >/dev/null 2>&1; then
    echo "⚠️  ポート $PORT は既に使用されています"
    echo ""
    
    # 使用中のプロセスを表示
    echo "【使用中のプロセス】"
    lsof -i:$PORT 2>/dev/null
    echo ""
    
    read -p "このプロセスを停止して再起動しますか？ [y/N] " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        PID=$(lsof -ti:$PORT)
        echo "🔄 プロセス($PID)を停止中..."
        kill -9 $PID 2>/dev/null
        sleep 2
    else
        echo "❌ キャンセルしました"
        echo "   別のポートで起動: bash start_dashboard_v2.sh --port 8080"
        exit 0
    fi
fi

# FastAPIとuvicornのチェック
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  FastAPIがインストールされていません"
    echo "📦 インストール中..."
    pip install fastapi uvicorn --break-system-packages
fi

# サーバー起動
echo ""
echo "🚀 サーバーを起動中..."
python3 -c "
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')
from agents.web_dashboard.dashboard_server import start_server
start_server(port=$PORT)
"

