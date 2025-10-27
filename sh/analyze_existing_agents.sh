#!/bin/bash

echo "=========================================="
echo "🔍 既存システム完全分析"
echo "=========================================="

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 既存のエージェントファイル"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "メインエージェント:"
ls -la agents/*agent*.py 2>/dev/null | grep -v "__pycache__" || echo "  (なし)"

echo ""
echo "WordPressエージェント:"
ls -la wordpress/*.py 2>/dev/null | grep -v "__pycache__" || echo "  (なし)"
ls -la wordpress/wp_dev/*.py 2>/dev/null | grep -v "__pycache__" || echo "  (なし)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. config_utils.py の確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "config_utils.py" ]; then
    echo ""
    echo "エージェント設定部分:"
    grep -A 20 "AGENT\|agent" config_utils.py | head -30
else
    echo "⚠️  config_utils.py が見つかりません"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. sheets_manager.py のログ機能"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "task_execution_log 関連メソッド:"
grep -n "task_execution_log\|save_task_output\|log_task" tools/sheets_manager.py | head -20

echo ""
echo "save_task_output のシグネチャ:"
grep -A 15 "def save_task_output\|async def save_task_output" tools/sheets_manager.py | head -20

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. 実行ログの分析"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 << 'CHECK_LOG'
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

print("\nスプレッドシート内のシート一覧:")
for ws in spreadsheet.worksheets():
    print(f"  - {ws.title}")

# task_execution_log シートの確認
try:
    log_sheet = spreadsheet.worksheet('task_execution_log')
    headers = log_sheet.row_values(1)
    all_data = log_sheet.get_all_values()
    
    print(f"\ntask_execution_log シート:")
    print(f"  列: {headers}")
    print(f"  データ行数: {len(all_data) - 1}")
    
    if len(all_data) > 1:
        print(f"\n  最新のログ（最後の行）:")
        last_row = all_data[-1]
        for header, value in zip(headers, last_row):
            if value:
                print(f"    {header}: {value[:50]}")
                
except Exception as e:
    print(f"\n⚠️  task_execution_log シートが見つかりません: {e}")

CHECK_LOG

echo ""
echo "=========================================="
echo "✅ 分析完了"
echo "=========================================="

