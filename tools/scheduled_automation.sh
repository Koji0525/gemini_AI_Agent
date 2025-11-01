#!/bin/bash
# ==================================================
# 定期自動化スクリプト
# 変更理由: 1日1回自動でパターン学習→タスク自動化を実行
# ==================================================

echo "🕐 $(date '+%Y-%m-%d %H:%M:%S') - 定期自動化開始"

cd /workspaces/gemini_AI_Agent

# パターン学習
echo "🔄 パターン学習実行..."
python3 tools/real_pattern_learner.py > /dev/null 2>&1

# タスク自動化
echo "🤖 タスク自動化実行..."
python3 tools/task_automation_engine.py > /dev/null 2>&1

echo "✅ 定期自動化完了"
