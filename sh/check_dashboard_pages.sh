#!/bin/bash
# ダッシュボードページ確認スクリプト

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 ダッシュボードページ確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "1. 利用可能なHTMLページ:"
ls -la agents/observer_enhanced/templates/

echo ""
echo "2. Flaskルート確認:"
grep -E "@app.route\(" agents/observer_enhanced/web_server.py | head -20

echo ""
echo "3. アクセス方法:"
echo "   メインダッシュボード: http://localhost:5000/"
echo "   依存関係グラフ: http://localhost:5000/dependencies"
echo "   問題検出: http://localhost:5000/analysis"

echo ""
echo "4. APIエンドポイント:"
echo "   GET /api/health"
echo "   GET /api/metrics"
echo "   GET /api/status"
echo "   GET /api/dependencies/scan"
echo "   GET /api/analysis/report"
echo "   GET /api/analysis/duplicates"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
