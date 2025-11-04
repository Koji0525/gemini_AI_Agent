#!/usr/bin/env python3
"""
シンプルなタスク実行スクリプト

PMTasksLoaderの正しいメソッドを使用して、
pendingタスクを順次実行します。
"""

import asyncio
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.pm_tasks_loader import PMTasksLoader
from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import ConfigLoader
from scripts.task_executor import TaskExecutor


async def main():
    """メイン実行関数"""
    print("=" * 70)
    print("🚀 シンプルタスク実行システム")
    print("=" * 70)
    print()

    # 設定読み込み
    config = ConfigLoader()
    spreadsheet_id = config.get("SPREADSHEET_ID")
    service_account_file = config.get("GOOGLE_SERVICE_ACCOUNT_FILE")

    # 初期化
    sheets_manager = GoogleSheetsManager(spreadsheet_id, service_account_file)
    tasks_loader = PMTasksLoader(spreadsheet_id, service_account_file)
    executor = TaskExecutor(sheets_manager, None)  # BrowserControllerは後で初期化

    # pendingタスクを取得
    print("📋 pendingタスクを取得中...")
    tasks = tasks_loader.load_tasks(status_filter="pending", max_tasks=5)

    if not tasks:
        print("⚠️ 実行可能なタスクがありません")
        return

    print(f"✅ {len(tasks)}個のタスクを取得しました")
    print()

    # タスクを順次実行
    success_count = 0
    fail_count = 0

    for i, task in enumerate(tasks, 1):
        task_id = task.get("task_id", "Unknown")
        task_name = task.get("task_name", "Unknown")

        print(f"[{i}/{len(tasks)}] タスク#{task_id}: {task_name}")

        try:
            # タスク実行
            result = await executor.execute_single_task(task)

            if result.get("success"):
                print(f"  ✅ 成功")
                success_count += 1
            else:
                print(f"  ❌ 失敗: {result.get('error', 'Unknown')}")
                fail_count += 1

        except Exception as e:
            print(f"  ❌ エラー: {e}")
            fail_count += 1

        print()

    # サマリー
    print("=" * 70)
    print("📊 実行結果")
    print("=" * 70)
    print(f"成功: {success_count}件")
    print(f"失敗: {fail_count}件")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
