#!/usr/bin/env python3
"""PM Agent自動化のモニタリング"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
os.environ["DISPLAY"] = ":1"

from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import get_config
from agents.pm_agent.progress_monitor import ProgressMonitorAgent


async def show_monitoring_dashboard():
    """モニタリングダッシュボードを表示"""
    print("=" * 70)
    print("📊 PM Agent自動化 - モニタリングダッシュボード")
    print("=" * 70)
    print(f"更新日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    config = get_config()
    sheets = GoogleSheetsManager(
        spreadsheet_id=config.get("SPREADSHEET_ID"), service_account_file=config.get("SERVICE_ACCOUNT_FILE")
    )

    monitor = ProgressMonitorAgent(sheets)

    # 進捗レポートを生成
    report = await monitor.generate_progress_report()
    print(report)

    # 今日生成されたタスクの詳細
    print("\n【今日生成されたタスクの詳細】")
    print("-" * 70)

    all_tasks = sheets.get_tasks()
    today = datetime.now().strftime("%Y-%m-%d")

    today_tasks = [task for task in all_tasks if task.get("created_at", "").startswith(today)]

    if not today_tasks:
        print("⚠️  今日生成されたタスクはありません")
    else:
        print(f"✅ 今日生成されたタスク: {len(today_tasks)}件\n")

        for i, task in enumerate(today_tasks, 1):
            print(f"{i}. [ID:{task.get('task_id', 'N/A')}] {task.get('description', 'N/A')}")
            print(
                f"   状態: {task.get('status', 'N/A')} | 担当: {task.get('required_role', 'N/A')} | 優先度: {task.get('priority', 'N/A')}"
            )
            print(f"   親目標: {task.get('parent_goal_id', 'N/A')} | 推定時間: {task.get('estimated_time', 'N/A')}h")
            print()

    # 最近のタスク生成履歴
    print("【最近のタスク生成履歴（直近7日）】")
    print("-" * 70)

    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    recent_tasks = [task for task in all_tasks if task.get("created_at", "") >= week_ago]

    by_date = {}
    for task in recent_tasks:
        date = task.get("created_at", "N/A")[:10]
        by_date[date] = by_date.get(date, 0) + 1

    for date in sorted(by_date.keys(), reverse=True):
        print(f"  {date}: {by_date[date]}件")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(show_monitoring_dashboard())
