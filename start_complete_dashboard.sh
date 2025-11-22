#!/bin/bash

# Enhanced Observer 統合ダッシュボード起動スクリプト

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Enhanced Observer 起動中..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ログディレクトリ作成
mkdir -p logs

# サーバー起動（バックグラウンド）
nohup python3 agents/observer_enhanced/web/integrated_server.py > logs/integrated_dashboard.log 2>&1 &
SERVER_PID=$!

echo "サーバー起動完了 (PID: $SERVER_PID)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 アクセス情報"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  🌐 Dashboard: http://localhost:5003/"
echo "  🔌 API Base:  http://localhost:5003/api/"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 利用可能なAPIエンドポイント"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  GET  /api/health"
echo "  POST /api/dependencies/scan"
echo "  POST /api/search/code"
echo "  POST /api/impact/analyze"
echo "  POST /api/breaking/detect"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 起動確認（5秒待機）
echo "起動確認中..."
sleep 5

if curl -s http://localhost:5003/api/health > /dev/null 2>&1; then
    echo "✅ サーバー正常起動"
    echo ""
    echo "ログ確認: tail -f logs/integrated_dashboard.log"
    echo "停止方法: kill $SERVER_PID"
else
    echo "⚠️ サーバー起動失敗"
    echo "ログ確認: cat logs/integrated_dashboard.log"
fi

echo ""
