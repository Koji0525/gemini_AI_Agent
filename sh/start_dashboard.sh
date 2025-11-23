#!/bin/bash
# ==
# Phase 5 ダッシュボードサーバー起動スクリプト
# ==

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Observer Enhanced Dashboard 起動"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ポート使用状況確認
PORT=5000
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️ ポート $PORT は既に使用中です"
    echo "   既存プロセスを停止しますか？ (y/n)"
    read -r response
    if [[ "$response" == "y" ]]; then
        PID=$(lsof -ti:$PORT)
        kill -9 $PID 2>/dev/null
        echo "✅ プロセス停止完了（PID: $PID）"
        sleep 1
    else
        PORT=5001
        echo "📝 代替ポート $PORT を使用します"
    fi
fi

# サーバー起動
echo ""
echo "🚀 Flaskサーバー起動中..."
echo "   ポート: $PORT"
echo "   ホスト: 0.0.0.0 (全インターフェース)"
echo ""

# バックグラウンド起動
nohup python3 -c "
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')
from agents.observer_enhanced.web_server import run_server
run_server(host='0.0.0.0', port=$PORT, debug=False)
" > logs/dashboard.log 2>&1 &

SERVER_PID=$!

echo "✅ サーバー起動完了（PID: $SERVER_PID）"
echo ""

# 起動待機
sleep 3

# ヘルスチェック
echo "🔍 ヘルスチェック実行中..."
if curl -s http://localhost:$PORT/api/health > /dev/null; then
    echo "✅ サーバー正常動作"
else
    echo "❌ サーバーが応答しません"
    echo "   ログを確認: cat logs/dashboard.log"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ダッシュボード起動成功"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 アクセス方法:"
echo ""
echo "【GitHub Codespaces環境】"
echo "1. VSCodeの「ポート」タブを開く"
echo "2. ポート $PORT が表示されているか確認"
echo "3. 「地球儀」アイコンをクリック → ブラウザで開く"
echo ""
echo "【ローカル環境】"
echo "   http://localhost:$PORT"
echo ""
echo "📡 APIエンドポイント:"
echo "   GET  /api/health   - システム健全性"
echo "   GET  /api/metrics  - メトリクス取得"
echo "   GET  /api/alerts   - アラート一覧"
echo "   GET  /api/status   - 統合ステータス"
echo ""
echo "🛑 サーバー停止:"
echo "   kill $SERVER_PID"
echo "   または: bash sh/stop_dashboard.sh"
echo ""
echo "📝 ログ確認:"
echo "   tail -f logs/dashboard.log"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
