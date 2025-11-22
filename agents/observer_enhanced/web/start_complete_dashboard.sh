#!/bin/bash

# 完全版ダッシュボード起動スクリプト

echo "🚀 Enhanced Observer - 完全版ダッシュボード起動"
echo ""
echo "起動中のサービス:"
echo "  1. メインAPI (ポート 5001) - 既存機能"
echo "  2. 拡張API (ポート 5002) - 新機能"
echo "  3. 完全版UI (ポート 5003) - 統合ダッシュボード"
echo ""

# 既存のプロセスを停止
pkill -f "api_endpoints.py" 2>/dev/null
pkill -f "api_extensions.py" 2>/dev/null
pkill -f "python -m http.server 5003" 2>/dev/null

sleep 2

# メインAPIサーバー起動（既存）
echo "📡 メインAPIサーバー起動中（ポート 5001）..."
cd /workspaces/gemini_AI_Agent
nohup python3 agents/observer_enhanced/web/api_endpoints.py > logs/main_api.log 2>&1 &
sleep 3

# 拡張APIサーバー起動（新規）
echo "📡 拡張APIサーバー起動中（ポート 5002）..."
nohup python3 agents/observer_enhanced/web/api_extensions.py > logs/extended_api.log 2>&1 &
sleep 3

# 完全版ダッシュボード配信（静的ファイルサーバー）
echo "🌐 完全版ダッシュボード起動中（ポート 5003）..."
cd agents/observer_enhanced/web
nohup python3 -m http.server 5003 > /workspaces/gemini_AI_Agent/logs/dashboard.log 2>&1 &
sleep 2

echo ""
echo "✅ 全サービス起動完了！"
echo ""
echo "📊 アクセス方法:"
echo "  完全版ダッシュボード: http://localhost:5003/complete_dashboard.html"
echo "  メインAPI: http://localhost:5001/api/health"
echo "  拡張API: http://localhost:5002/api/health-extended"
echo ""
echo "📝 ログ確認:"
echo "  tail -f /workspaces/gemini_AI_Agent/logs/main_api.log"
echo "  tail -f /workspaces/gemini_AI_Agent/logs/extended_api.log"
echo "  tail -f /workspaces/gemini_AI_Agent/logs/dashboard.log"
echo ""
echo "🛑 停止方法:"
echo "  pkill -f 'api_endpoints.py'"
echo "  pkill -f 'api_extensions.py'"
echo "  pkill -f 'python -m http.server 5003'"
