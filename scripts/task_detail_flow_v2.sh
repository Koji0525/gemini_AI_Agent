#!/bin/bash
# ==============================================================================
# タスク詳細化フロー v2（使いやすい版）
# 使用方法: 
#   Option 1 (Sheets): bash scripts/task_detail_flow_v2.sh sheets <task_id>
#   Option 2 (JSON):   bash scripts/task_detail_flow_v2.sh json <task_id>
# ==============================================================================

METHOD=$1
TASK_ID=$2

if [ -z "$METHOD" ] || [ -z "$TASK_ID" ]; then
    echo "使用方法:"
    echo "  Option 1 (推奨): bash scripts/task_detail_flow_v2.sh sheets <task_id>"
    echo "  Option 2:        bash scripts/task_detail_flow_v2.sh json <task_id>"
    echo ""
    echo "Option 1: Google Sheetsで入力（推奨）"
    echo "  - task_interviews シートに直接入力"
    echo "  - 修正・コピペが簡単"
    echo ""
    echo "Option 2: JSONテンプレートで入力"
    echo "  - VSCodeで編集"
    echo "  - Gitで管理可能"
    exit 1
fi

echo "=============================================="
echo "タスク詳細化フロー v2: $TASK_ID"
echo "方法: $METHOD"
echo "=============================================="

if [ "$METHOD" == "sheets" ]; then
    # Google Sheets方式
    echo ""
    echo "【Step 1/3】Google Sheetsからインタビュー読み込み"
    echo ""
    echo "📝 準備:"
    echo "  1. Google Sheetsを開く"
    echo "  2. task_interviews シートに移動"
    echo "  3. タスク $TASK_ID の行を編集"
    echo "  4. 保存"
    echo ""
    read -p "準備完了？ (y/N): " confirm
    
    if [[ $confirm != "y" && $confirm != "Y" ]]; then
        echo "キャンセルしました"
        exit 0
    fi
    
    python3 agents/task_requirements/task_interview_sheets.py $TASK_ID
    
elif [ "$METHOD" == "json" ]; then
    # JSONテンプレート方式
    echo ""
    echo "【Step 1/3】JSONテンプレート生成"
    python3 agents/task_requirements/task_interview_template.py $TASK_ID
    
    echo ""
    echo "📝 VSCodeで編集してください"
    read -p "編集完了？ (y/N): " confirm
    
    if [[ $confirm != "y" && $confirm != "Y" ]]; then
        echo "キャンセルしました"
        exit 0
    fi
    
    python3 agents/task_requirements/task_interview_from_json.py $TASK_ID
    
else
    echo "❌ 不明な方法: $METHOD"
    echo "sheets または json を指定してください"
    exit 1
fi

if [ $? -ne 0 ]; then
    echo "❌ インタビュー処理失敗"
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

# Step 3: 表示
echo ""
echo "【Step 3/3】要件定義書確認"
echo "=============================================="
cat agent_outputs/tasks/task_$TASK_ID/task_${TASK_ID}_requirements.md
echo "=============================================="

echo ""
echo "✅ タスク詳細化完了！"
echo ""
echo "次のステップ:"
echo "  python3 scripts/run_with_practical_tools.py $TASK_ID"
echo ""
