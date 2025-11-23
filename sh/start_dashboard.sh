#!/bin/bash
# 依存関係可視化ダッシュボード起動スクリプト

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 依存関係可視化ダッシュボード起動"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 既存プロセス確認
echo "🔍 既存プロセス確認..."
if ps aux | grep -v grep | grep api_server.py > /dev/null; then
    echo "⚠️  既存プロセスを停止中..."
    pkill -f "api_server.py"
    sleep 2
fi

# 依存関係データ確認
echo "📊 依存関係データ確認..."
if [ ! -f "docs/dependency_map.json" ]; then
    echo "📈 依存関係データ生成中（初回のみ）..."
    python3 scripts/analysis/dependency_mapper.py
fi

# APIサーバー起動
echo "🚀 APIサーバー起動中..."
python3 agents/observer_enhanced/api_server.py > /tmp/api_server.log 2>&1 &
PID=$!
echo "   PID: $PID"

sleep 3

# ヘルスチェック
echo ""
echo "🔍 ヘルスチェック..."
if curl -s http://localhost:5001/api/health > /dev/null; then
    echo "✅ APIサーバー正常稼働"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🌐 アクセス方法"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  📊 ダッシュボード: http://localhost:5001"
    echo "  📖 API仕様書: http://localhost:5001/docs"
    echo "  🔍 診断ページ: http://localhost:5001/diagnostic"
    echo ""
    echo "📋 ログ確認: tail -f /tmp/api_server.log"
    echo "⏹️  停止方法: pkill -f api_server.py"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo "❌ APIサーバー起動失敗"
    echo "📋 ログ確認: tail /tmp/api_server.log"
    exit 1
fi
