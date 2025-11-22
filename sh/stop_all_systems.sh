#!/bin/bash
# 全システムを停止

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⏹️  全システムを停止"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🔄 ダッシュボードを停止中..."
pkill -f dashboard_server.py 2>/dev/null
sleep 1

echo "🔄 24時間稼働システムを停止中..."
pkill -f run_autonomous_24h 2>/dev/null
sleep 1

echo "🔄 一時停止フラグを削除中..."
rm -f /tmp/system_paused.flag

echo ""
echo "✅ 全システムを停止しました"
echo ""

