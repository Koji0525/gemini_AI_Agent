#!/bin/bash
# 一時停止

echo "⏸️  システムを一時停止します..."
touch /tmp/system_paused.flag

echo "✅ 一時停止フラグを設定しました"
echo ""
echo "再開するには:"
echo "  bash sh/resume_system.sh"
