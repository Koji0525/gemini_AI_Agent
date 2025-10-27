#!/bin/bash

echo "=========================================="
echo "🔄 フィードバックループ機能確認"
echo "=========================================="

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. task_execution_log の最新データ確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 << 'PYTHON_CHECK'
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

# task_execution_log 確認
log_sheet = spreadsheet.worksheet('task_execution_log')
all_data = log_sheet.get_all_values()
headers = all_data[0]

print("\ntask_execution_log 構造:")
print(f"  列: {headers}")
print(f"  データ行数: {len(all_data) - 1}")

# 最新3件を表示
print("\n最新3件のログ:")
for i, row in enumerate(all_data[-3:], 1):
    print(f"\n{i}. ログID: {row[0]}")
    for j, (header, value) in enumerate(zip(headers, row)):
        if value and j < 7:  # 最初の7列のみ
            print(f"   {header}: {value[:80]}")

# タスク間の依存関係を確認
print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("2. pm_tasks の dependencies 列確認")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

pm_tasks = spreadsheet.worksheet('pm_tasks')
pm_data = pm_tasks.get_all_values()
pm_headers = pm_data[0]

# dependencies列のインデックスを探す
dep_index = None
for i, h in enumerate(pm_headers):
    if 'dependencies' in h.lower():
        dep_index = i
        break

if dep_index:
    print(f"\ndependencies列が見つかりました（列{dep_index + 1}）")
    
    # 依存関係があるタスクを抽出
    tasks_with_deps = []
    for row in pm_data[1:]:
        if dep_index < len(row) and row[dep_index]:
            task_id = row[0] if len(row) > 0 else ''
            description = row[2] if len(row) > 2 else ''
            deps = row[dep_index]
            tasks_with_deps.append((task_id, description[:50], deps))
    
    if tasks_with_deps:
        print(f"\n依存関係があるタスク: {len(tasks_with_deps)}件")
        for task_id, desc, deps in tasks_with_deps[:5]:
            print(f"  タスク{task_id}: {desc}... → 依存: {deps}")
    else:
        print("\n依存関係が設定されているタスクはありません")
else:
    print("\n⚠️  dependencies列が見つかりません")

PYTHON_CHECK

echo ""
echo "=========================================="

