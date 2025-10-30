#!/bin/bash
# 週次ルールレビュー

echo "📊 週次ルールレビュー"
echo ""

# 1. 今週追加されたルール
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 今週の新規ルール"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')
from dotenv import load_dotenv
load_dotenv('.env')
from tools.sheets_manager import GoogleSheetsManager
from datetime import datetime, timedelta
import os

sheets = GoogleSheetsManager(
    spreadsheet_id=os.getenv("SPREADSHEET_ID"),
    service_account_file="configuration/service_account.json"
)

spreadsheet = sheets.gc.open_by_key(os.getenv("SPREADSHEET_ID"))
history_sheet = spreadsheet.worksheet('rule_history')

all_history = history_sheet.get_all_values()

# 今週の変更
week_ago = datetime.now() - timedelta(days=7)

for row in all_history[1:]:
    if len(row) > 0:
        timestamp = row[0]
        if timestamp >= week_ago.strftime('%Y-%m-%d'):
            print(f"  {timestamp}: {row[1]} - {row[2]}")

PYEOF

# 2. 使用頻度の高いツール
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "�� よく使われたツール TOP3"
# （ログ解析など）

# 3. 改善提案
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 改善提案"
echo "  - ツールXの自動化"
echo "  - ルールYの簡略化"
