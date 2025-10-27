#!/bin/bash

echo "=========================================="
echo "🔍 既存コード完全分析"
echo "=========================================="

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. SheetsManagerの既存メソッド"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "メソッド一覧:"
grep -n "^\s*def \|^\s*async def " tools/sheets_manager.py | grep -v "__"

echo ""
echo "update_task_status のシグネチャ:"
grep -A 20 "def update_task_status\|async def update_task_status" tools/sheets_manager.py | head -25

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. pm_tasksシートの実際の構造"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 << 'CHECK_SHEET'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from configuration.config_loader import get_spreadsheet_id, get_service_account_file
from tools.sheets_manager import GoogleSheetsManager

sheets = GoogleSheetsManager(
    spreadsheet_id=get_spreadsheet_id(),
    service_account_file=get_service_account_file()
)

import gspread
spreadsheet = sheets.gc.open_by_key(get_spreadsheet_id())
pm_tasks = spreadsheet.worksheet('pm_tasks')

print("\npm_tasksシートの構造:")
print("="*70)

# ヘッダー行
headers = pm_tasks.row_values(1)
print(f"\n列数: {len(headers)}")
print(f"ヘッダー: {headers}")

# 最初のデータ行
if len(pm_tasks.get_all_values()) > 1:
    first_row = pm_tasks.row_values(2)
    print(f"\n最初のデータ行:")
    for i, (header, value) in enumerate(zip(headers, first_row), 1):
        print(f"  {i}. {header}: {value[:50] if value else '(空)'}")

# pending タスク数
all_values = pm_tasks.get_all_values()
status_col_index = None
if 'status' in [h.lower() for h in headers]:
    status_col_index = [h.lower() for h in headers].index('status')
    
    pending_count = 0
    for row in all_values[1:]:
        if status_col_index < len(row):
            if row[status_col_index].lower() in ['pending', '']:
                pending_count += 1
    
    print(f"\npendingタスク数: {pending_count}")

CHECK_SHEET

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. 既存のTaskExecutor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "scripts/task_executor.py" ]; then
    echo ""
    echo "TaskExecutorのクラス定義:"
    grep -A 30 "^class TaskExecutor" scripts/task_executor.py | head -35
    
    echo ""
    echo "エージェント登録部分:"
    grep -A 5 "self.agents\|register_agent" scripts/task_executor.py | head -20
else
    echo "⚠️  scripts/task_executor.py が見つかりません"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. 既存のエージェント"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "エージェントファイル:"
ls -la agents/*.py 2>/dev/null || echo "⚠️  agentsディレクトリが見つかりません"

echo ""
echo "=========================================="
echo "✅ 分析完了"
echo "=========================================="

