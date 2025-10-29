#!/bin/bash
# スケジューラー起動スクリプト

echo "🚀 自動スケジューラー起動"
echo "======================================"

# 仮想環境アクティベート（必要な場合）
# source venv/bin/activate

# スケジューラー実行
python3 agents/scheduler/auto_scheduler.py

echo "======================================"
echo "✅ スケジューラー終了"
