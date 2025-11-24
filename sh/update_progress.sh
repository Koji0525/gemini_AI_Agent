#!/bin/bash
# 進捗チェックリスト更新スクリプト

echo "📝 進捗チェックリスト更新"
echo ""

PHASE=$1
TASK=$2
STATUS=$3
VALUE=$4

if [ -z "$PHASE" ] || [ -z "$TASK" ] || [ -z "$STATUS" ]; then
    echo "使用方法: sh/update_progress.sh <Phase> <Task> <Status> [Value]"
    echo "例: sh/update_progress.sh Phase0 T0.1.1 SUCCESS 85.5"
    exit 1
fi

echo "Phase: $PHASE"
echo "Task: $TASK"
echo "Status: $STATUS"
echo "Value: $VALUE"
echo ""
echo "✅ MD/PROGRESS_CHECKLIST.md を手動で更新してください"
echo ""
