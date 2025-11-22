#!/bin/bash
# 再開

echo "▶️  システムを再開します..."
rm -f /tmp/system_paused.flag
rm -f /tmp/system_emergency_stop.flag

echo "✅ システムを再開しました"
