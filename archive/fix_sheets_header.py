#!/usr/bin/env python3
"""
Google Sheetsヘッダー修正
pm_tasksシートの空白列を削除
"""
import gspread
from google.oauth2.service_account import Credentials

# 認証
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file('service_account.json', scopes=SCOPES)
client = gspread.authorize(creds)

# スプレッドシート取得
spreadsheet_id = '1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s'
spreadsheet = client.open_by_key(spreadsheet_id)

# pm_tasksシート取得
worksheet = spreadsheet.worksheet('pm_tasks')

# ヘッダー行を取得（1行目）
headers = worksheet.row_values(1)

print("現在のヘッダー:")
for i, header in enumerate(headers, 1):
    print(f"  {i}: '{header}'")

# 空白のヘッダーを見つける
empty_indices = [i for i, h in enumerate(headers, 1) if not h.strip()]

if empty_indices:
    print(f"\n⚠️ 空白ヘッダーが {len(empty_indices)} 個見つかりました:")
    print(f"   列: {empty_indices}")
    print("\n💡 解決方法:")
    print("   1. Google Sheetsを開く")
    print(f"   2. {empty_indices} 列目のヘッダーに名前を付ける")
    print("   3. または、その列を削除する")
else:
    print("\n✅ ヘッダーに問題ありません")

# 予想されるヘッダーを表示
expected_headers = [
    'task_id', 'parent', 'description', 'required_role',
    'status', 'priority', 'estimated_time', 'dependencies', 'created_at'
]

print("\n📋 推奨ヘッダー:")
for i, header in enumerate(expected_headers, 1):
    actual = headers[i-1] if i <= len(headers) else '(なし)'
    match = "✅" if i <= len(headers) and headers[i-1] == header else "❌"
    print(f"  {match} {i}: {header} (実際: '{actual}')")
