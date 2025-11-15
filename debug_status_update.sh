#!/bin/bash

echo "=== タスクステータス更新デバッグ開始 ==="

# 1. 現在のタスク状態確認
echo -e "\n📊 現在のタスク状態:"
python3 -c "
from tools.sheets_manager import GoogleSheetsManager
from tools.safe_sheets_wrapper import SafeSheetsWrapper
sheets = GoogleSheetsManager()
safe_sheets = SafeSheetsWrapper(sheets)

# pm_tasksシートの全データ取得
tasks = safe_sheets.safe_read('pm_tasks!A2:Z1000', default=[])
print(f'総タスク数: {len(tasks)}')

# 6_implementation_002 タスクの状態
target_task = None
for i, task in enumerate(tasks):
    if task[0] == '6_implementation_002':
        target_task = task
        print(f'対象タスク発見: 行 {i+2}')
        print(f'  task_id: {task[0]}')
        print(f'  status: {task[4]}')  # E列
        print(f'  priority: {task[5]}') # F列
        break

if not target_task:
    print('❌ 6_implementation_002 タスクが見つかりません')
"

# 2. 実行ログの確認
echo -e "\n📝 最近の実行ログ:"
python3 -c "
from tools.sheets_manager import GoogleSheetsManager
from tools.safe_sheets_wrapper import SafeSheetsWrapper
sheets = GoogleSheetsManager()
safe_sheets = SafeSheetsWrapper(sheets)

# task_execution_log の確認
logs = safe_sheets.safe_read('task_execution_log!A2:Z100', default=[])
print(f'実行ログ数: {len(logs)}')

recent_logs = logs[-5:] if logs else []
for log in recent_logs:
    if '6_implementation_002' in str(log):
        print(f'関連ログ: {log[:3]}...')
"

# 3. ステータス更新コードの確認
echo -e "\n🔍 ステータス更新コードの確認:"
grep -n "ステータス更新" agents/complete_engine_ultimate.py
grep -n "status.*completed" agents/complete_engine_ultimate.py

# 4. 実際の更新処理をトレース
echo -e "\n🎯 ステータス更新処理のトレース:"
python3 -c "
import traceback
from tools.sheets_manager import GoogleSheetsManager
from tools.safe_sheets_wrapper import SafeSheetsWrapper

try:
    sheets = GoogleSheetsManager()
    safe_sheets = SafeSheetsWrapper(sheets)
    
    # 現在の状態を確認
    tasks = safe_sheets.safe_read('pm_tasks!A2:Z1000', default=[])
    
    # 6_implementation_002 の行を探す
    target_row = None
    for i, task in enumerate(tasks):
        if task[0] == '6_implementation_002':
            target_row = i + 2  # 0-indexed + ヘッダー行
            print(f'対象タスク: 行 {target_row}, 現在のstatus: {task[4]}')
            break
    
    if target_row:
        # ステータス更新を試みる
        update_range = f'pm_tasks!E{target_row}'
        print(f'更新範囲: {update_range}')
        
        # 更新実行
        result = safe_sheets.safe_update(update_range, [['completed']])
        print(f'更新結果: {result}')
        
        # 更新確認
        updated = safe_sheets.safe_read(f'pm_tasks!E{target_row}', default=[])
        print(f'更新後status: {updated}')
    else:
        print('❌ 対象タスクが見つかりません')

except Exception as e:
    print(f'❌ エラー発生: {e}')
    traceback.print_exc()
"

echo -e "\n=== デバッグ完了 ==="
