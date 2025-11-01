#!/bin/bash
# automation_reliable_fixed.py 実行用ラッパー

echo "🚀 automation_reliable_fixed.py を実行中..."
echo "📺 DISPLAY=:1 を設定"
echo ""

export DISPLAY=:1
python3 agents/pm_agent/automation_reliable_fixed.py "$@"
