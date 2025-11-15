#!/bin/bash

# ===================================================================
# pendingタスク実行（簡易版）
# ===================================================================

echo "="*80
echo "📋 pendingタスク確認"
echo "="*80

# 引数処理
GOAL_ID=""
LIMIT=""
DRY_RUN=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --goal-id)
            GOAL_ID="--goal-id $2"
            shift 2
            ;;
        --limit)
            LIMIT="--limit $2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        *)
            echo "不明なオプション: $1"
            exit 1
            ;;
    esac
done

# Python実行
python3 /workspaces/gemini_AI_Agent/run_pending_tasks.py $GOAL_ID $LIMIT $DRY_RUN

echo ""
echo "="*80
echo "✅ 完了"
echo "="*80
