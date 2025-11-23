#!/bin/bash
# pendingタスク実行（修正版）
# 列インデックスで直接アクセス

cd /workspaces/gemini_AI_Agent

LIMIT=${1:-1}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 pendingタスク実行（修正版）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << PYTHON
import sys

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.complete_engine_ultimate import CompleteEngineUltimate
from agents.robust_task_selector import RobustTaskSelector
from tools.sheets_manager import GoogleSheetsManager

sheets = GoogleSheetsManager()
selector = RobustTaskSelector(sheets)
engine = CompleteEngineUltimate()

# タスク選択
selected_tasks = selector.select_executable_task(limit=${LIMIT})

if not selected_tasks:
    print("\n⚠️  実行可能なタスクがありません")
    sys.exit(1)

# タスク実行
success_count = 0
for task in selected_tasks:
    print(f"\n{'=' * 80}")
    print(f"�� タスク実行: {task['task_id']}")
    print('=' * 80)
    
    try:
        result = engine.execute_task(task)
        
        if result.get('status') == 'completed':
            # ステータス更新
            row_index = task['row_index']
            update_range = f"pm_tasks!E{row_index}"
            
            sheets.service.spreadsheets().values().update(
                spreadsheetId=sheets.spreadsheet_id,
                range=update_range,
                valueInputOption="RAW",
                body={"values": [["completed"]]}
            ).execute()
            
            print(f"✅ 完了: {task['task_id']}")
            success_count += 1
    
    except Exception as e:
        print(f"❌ エラー: {e}")

print(f"\n✅ 実行完了: {success_count}/{len(selected_tasks)}件成功")

PYTHON

# Test marker 1763858018
