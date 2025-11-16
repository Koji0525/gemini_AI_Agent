#!/bin/bash
# ==============================================================================
# タスク詳細化フロー
# 使用方法: bash scripts/task_detail_flow.sh <task_id>
# ==============================================================================

TASK_ID=$1

if [ -z "$TASK_ID" ]; then
    echo "使用方法: bash scripts/task_detail_flow.sh <task_id>"
    exit 1
fi

echo "=============================================="
echo "タスク詳細化フロー開始: タスクID $TASK_ID"
echo "=============================================="

# Step 1: インタビュー
echo ""
echo "【Step 1/3】インタビュー実施"
python3 agents/task_requirements/task_interview.py $TASK_ID

if [ $? -ne 0 ]; then
    echo "❌ インタビュー失敗"
    exit 1
fi

# Step 2: 要件定義書生成
echo ""
echo "【Step 2/3】要件定義書生成"
python3 agents/task_requirements/task_requirements_generator.py $TASK_ID

if [ $? -ne 0 ]; then
    echo "❌ 要件定義書生成失敗"
    exit 1
fi

# Step 3: 要件定義書を表示
echo ""
echo "【Step 3/3】要件定義書を確認"
echo "=============================================="
cat agent_outputs/tasks/task_$TASK_ID/task_${TASK_ID}_requirements.md
echo "=============================================="

echo ""
echo "✅ タスク詳細化完了！"
echo ""
echo "次のステップ:"
echo "  python3 scripts/run_with_practical_tools.py $TASK_ID"
echo ""
