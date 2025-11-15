#!/bin/bash

TASK_ID="$1"
LIMIT="${2:-1}"

if [ -z "$TASK_ID" ]; then
    echo "使用方法: $0 <タスクID> [実行数]"
    echo "例: $0 6_implementation_002 1"
    exit 1
fi

echo "🎯 特定タスク実行: $TASK_ID"

# タスクの存在確認と優先度設定
python3 -c "
from tools.sheets_manager import GoogleSheetsManager
from tools.safe_sheets_wrapper import SafeSheetsWrapper
sheets = GoogleSheetsManager()
safe_sheets = SafeSheetsWrapper(sheets)

tasks = safe_sheets.safe_read('pm_tasks!A2:Z1000', default=[])
target_task = None
for task in tasks:
    if task[0] == '$TASK_ID':
        target_task = task
        break

if target_task:
    print(f'✅ タスク発見: {target_task[0]} - {target_task[2]}')
    # 優先度を最高に設定
    for i, t in enumerate(tasks):
        if t[0] == '$TASK_ID':
            range_name = f'pm_tasks!E{i+2}'
            safe_sheets.safe_update(range_name, [['highest']])
            print(f'🎯 優先度を highest に設定')
            break
else:
    print(f'❌ タスク $TASK_ID が見つかりません')
    exit(1)
"

# タスク実行
echo "🚀 タスク実行開始..."
python3 run_3_cycles.py --limit $LIMIT

echo "✅ タスク実行完了: $TASK_ID"
