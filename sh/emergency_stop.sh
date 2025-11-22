#!/bin/bash
# 緊急停止

echo "🚨 システムを緊急停止します..."
touch /tmp/system_emergency_stop.flag
touch /tmp/system_paused.flag

echo "✅ 緊急停止フラグを設定しました"
echo ""
echo "再開するには:"
echo "  bash sh/resume_system.sh"
