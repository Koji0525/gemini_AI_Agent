import os
from pathlib import Path

# パス確認
service_account_path = Path("service_account.json")
print(f"ファイル存在: {service_account_path.exists()}")
print(f"絶対パス: {service_account_path.absolute()}")

# 環境変数設定
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(service_account_path.absolute())
print(f"環境変数設定: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")

# sheets_manager テスト
from sheets_manager import GoogleSheetsManager
sheets = GoogleSheetsManager(spreadsheet_id='1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s')
print("✅ GoogleSheetsManager 初期化成功")

# タスク読み込みテスト
import asyncio
async def test():
    tasks = await sheets.load_tasks_from_sheet()
    print(f"✅ タスク取得: {len(tasks)} 件")
    return tasks

asyncio.run(test())
