#!/usr/bin/env python3
"""TaskExecutor実行"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
os.environ['DISPLAY'] = ':1'

from configuration.config_loader import get_spreadsheet_id, get_service_account_file
from browser_control.browser_controller import BrowserController
from tools.sheets_manager import GoogleSheetsManager
from scripts.task_executor_simple import TaskExecutor

async def main():
    print("="*70)
    print("🎯 TaskExecutor 統合実行")
    print("="*70)
    
    # 初期化
    sheets = GoogleSheetsManager(
        spreadsheet_id=get_spreadsheet_id(),
        service_account_file=get_service_account_file()
    )
    
    async with BrowserController(download_folder="./downloads") as browser:
        executor = TaskExecutor(sheets, browser)
        results = await executor.execute_all_pending()
    
    print(f"\n最終結果: {results}")

if __name__ == "__main__":
    asyncio.run(main())

