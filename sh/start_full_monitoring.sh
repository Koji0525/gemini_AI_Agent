#!/bin/bash

echo "============================================================"
echo "🔍 完全監視システム起動"
echo "============================================================"
echo ""

# STEP 1: パス修正
echo "[STEP 1] パス修正"
bash << 'PATHFIX'
if [ -f "docs/dependency_map.json" ]; then
    cp docs/dependency_map.json dependency_map.json
    echo "✅ dependency_map.jsonコピー"
fi
PATHFIX

# STEP 2: 依存関係マップ生成
echo ""
echo "[STEP 2] 依存関係マップ生成"
python3 scripts/analysis/dependency_mapper.py

# STEP 3: 変更検知（ハイブリッド）
echo ""
echo "[STEP 3] 変更検知"
python3 scripts/analysis/hybrid_change_detector.py

# STEP 4: 契約監視
echo ""
echo "[STEP 4] 契約監視"
python3 scripts/monitoring/contract_monitor.py

# STEP 5: テスト実行 & 分析
echo ""
echo "[STEP 5] テスト実行"
python3 scripts/monitoring/test_integration_monitor.py || true

# STEP 6: 重複検知
echo ""
echo "[STEP 6] 重複コード検知"
python3 scripts/quality/duplicate_detector.py

# STEP 7: ダッシュボード起動
echo ""
echo "[STEP 7] ダッシュボード起動"
pkill -f "api_server" 2>/dev/null

python3 agents/observer_enhanced/web/api_server_v3.py > /tmp/api_server_v3.log 2>&1 &
API_PID=$!

sleep 3

if curl -s http://localhost:5001/api/health_check > /dev/null; then
    echo "✅ ダッシュボード起動成功"
else
    echo "⚠️  起動確認中..."
fi

echo ""
echo "============================================================"
echo "🌐 アクセス"
echo "============================================================"
echo "  📊 ダッシュボード: http://localhost:5001"
echo "  📖 API: http://localhost:5001/docs"
echo ""
echo "📋 ログ: tail -f /tmp/api_server_v3.log"
echo "============================================================"
