#!/bin/bash
################################################################################
# 共有黒板システム健全性チェック
################################################################################

echo "========================================"
echo "📋 共有黒板システム健全性チェック"
echo "========================================"

# 黒板ファイル数
BLACKBOARD_COUNT=$(find shared_states/ -name "goal_*_state.json" | wc -l)
echo "黒板ファイル数: ${BLACKBOARD_COUNT}"

# 履歴ファイル数
HISTORY_COUNT=$(find shared_states/history/ -name "*.json" 2>/dev/null | wc -l)
echo "履歴ファイル数: ${HISTORY_COUNT}"

# 合計サイズ
TOTAL_SIZE=$(du -sh shared_states/ | awk '{print $1}')
echo "合計サイズ: ${TOTAL_SIZE}"

# 最近の更新
RECENT_UPDATES=$(find shared_states/ -name "goal_*_state.json" -mtime -1 | wc -l)
echo "最近24時間の更新: ${RECENT_UPDATES}件"

echo ""
echo "✅ 共有黒板健全性チェック完了"
