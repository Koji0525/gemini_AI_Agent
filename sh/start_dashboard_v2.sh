#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 オブザーバーダッシュボード v2 起動"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 既存プロセス停止
pkill -f "api_server" 2>/dev/null

# 重複検知実行
echo "🔍 重複コード検知実行中..."
python3 scripts/quality/duplicate_detector.py

# 依存関係マップ生成（必要な場合）
if [ ! -f "dependency_map.json" ]; then
    echo "📊 依存関係マップ生成中..."
    python3 scripts/analysis/dependency_mapper.py
fi

# API Server v2起動
echo "🚀 API Server v2 起動中..."
python3 agents/observer_enhanced/web/api_server_v2.py > /tmp/api_server_v2.log 2>&1 &
API_PID=$!

echo "   PID: $API_PID"

# ヘルスチェック
sleep 3

if curl -s http://localhost:5001/health > /dev/null; then
    echo "✅ API Server正常稼働"
else
    echo "⚠️  API Server起動確認中..."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 アクセス方法"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📊 ダッシュボード: http://localhost:5001"
echo "  📖 API仕様書: http://localhost:5001/docs"
echo ""
echo "📋 ログ確認: tail -f /tmp/api_server_v2.log"
echo "⏹️  停止方法: pkill -f api_server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
