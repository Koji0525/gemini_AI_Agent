#!/bin/bash
# ==============================================================
# 🔍 オブザーバーシステム起動スクリプト
# ==============================================================

set -e

cd /workspaces/gemini_AI_Agent || exit 1

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 依存関係可視化システム起動"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ステップ1: 既存プロセス停止
echo "[1/5] 既存プロセス確認..."
if pgrep -f "api_server.py" > /dev/null; then
    echo "   ⚠️  既存プロセスを停止します"
    pkill -9 -f "api_server.py" || true
    sleep 2
else
    echo "   ✅ 既存プロセスなし"
fi

# ステップ2: ファイル確認
echo ""
echo "[2/5] ファイル確認..."
if [ -f "docs/dependency_map.json" ]; then
    echo "   ✅ dependency_map.json 存在"
else
    echo "   ❌ dependency_map.json が見つかりません"
    exit 1
fi

if [ -f "agents/observer_enhanced/web/api_server.py" ]; then
    echo "   ✅ api_server.py 存在"
else
    echo "   ❌ api_server.py が見つかりません"
    exit 1
fi

# ステップ3: APIサーバー起動
echo ""
echo "[3/5] APIサーバー起動..."
cd agents/observer_enhanced/web
nohup python3 api_server.py > /tmp/api_server.log 2>&1 &
API_PID=$!
cd ../../..

echo "   🚀 APIサーバー起動中..."
echo "   PID: $API_PID"
sleep 8

# ステップ4: 起動確認
echo ""
echo "[4/5] 起動確認..."

if lsof -i:8001 > /dev/null 2>&1; then
    echo "   ✅ ポート8001 開放"
else
    echo "   ❌ ポート8001 が開いていません"
    echo ""
    echo "📋 エラーログ:"
    tail -20 /tmp/api_server.log
    exit 1
fi

sleep 2

HEALTH=$(curl -s http://localhost:8001/health 2>&1)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ ヘルスチェック成功"
else
    echo "   ⚠️  ヘルスチェック失敗"
fi

# ステップ5: 情報表示
echo ""
echo "[5/5] 起動情報"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ オブザーバーシステム起動完了！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 アクセスURL:"
echo "   http://localhost:8001/          → ダッシュボード"
echo "   http://localhost:8001/docs      → Swagger UI"
echo "   http://localhost:8001/redoc     → ReDoc"
echo ""
echo "📊 APIエンドポイント:"
echo "   GET  /api/dependencies  → 依存関係データ"
echo "   GET  /api/signals       → 信号機データ"
echo "   GET  /api/snapshots     → スナップショット一覧"
echo "   GET  /api/changes       → 変更履歴"
echo "   POST /api/snapshot      → スナップショット作成"
echo ""
echo "📝 ログファイル:"
echo "   /tmp/api_server.log"
echo ""
echo "🛑 停止方法:"
echo "   pkill -f 'api_server.py'"
echo ""
