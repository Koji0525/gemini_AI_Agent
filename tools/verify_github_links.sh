#!/bin/bash
# GitHubリンク検証ツール

echo "🔍 GitHubリンク検証"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. スプレッドシートからリンク取得
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

python3 << 'PYEOF'
import sys
import os
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from dotenv import load_dotenv
load_dotenv('.env')

from tools.sheets_manager import GoogleSheetsManager
import requests

sheets = GoogleSheetsManager(
    spreadsheet_id=os.getenv("SPREADSHEET_ID"),
    service_account_file="configuration/service_account.json"
)

spreadsheet = sheets.gc.open_by_key(os.getenv("SPREADSHEET_ID"))
rules_sheet = spreadsheet.worksheet('dev_rules')

all_data = rules_sheet.get_all_values()

print("検証中...")
print()

ok_count = 0
ng_count = 0

for row in all_data[1:]:
    rule_id = row[0]
    doc_link = row[4]
    
    if doc_link.startswith('https://github.com'):
        # アンカー部分を除去してファイル存在確認
        base_url = doc_link.split('#')[0]
        
        try:
            response = requests.head(base_url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {rule_id}: OK")
                ok_count += 1
            else:
                print(f"❌ {rule_id}: {response.status_code}")
                print(f"   {base_url}")
                ng_count += 1
        except Exception as e:
            print(f"⚠️  {rule_id}: 接続エラー")
            ng_count += 1

print()
print(f"結果: ✅ {ok_count}件 / ❌ {ng_count}件")

if ng_count > 0:
    print()
    print("💡 エラーの場合:")
    print("  1. ファイルがGitHubにプッシュされているか確認")
    print("  2. ブランチ名が正しいか確認")
    print("  3. リポジトリがpublicか確認")
PYEOF
