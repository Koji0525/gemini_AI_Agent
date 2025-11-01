#!/usr/bin/env python3
"""
M&Aポータル進捗確認スクリプト
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from tools.sheets_manager import GoogleSheetsManager


def check_progress():
    print("📊 M&Aポータル構築 進捗確認")
    print("=" * 60)

    sheets = GoogleSheetsManager()
    data = sheets.read_range("pm_tasks")

    if not data or len(data) <= 1:
        print("⚠️ pm_tasksが空です")
        return

    headers = data[0]
    ma_tasks = [row for row in data[1:] if len(row) > 0 and str(row[0]).startswith("MA_PORTAL")]

    if not ma_tasks:
        print("⚠️ M&Aポータルタスクが見つかりません")
        return

    print(f"\n総タスク数: {len(ma_tasks)}件\n")

    completed = 0
    pending = 0
    in_progress = 0

    for task in ma_tasks:
        task_id = task[0]
        desc = task[1] if len(task) > 1 else ""
        status = task[2] if len(task) > 2 else "pending"
        time = task[7] if len(task) > 7 else ""

        status_emoji = {
            "completed": "✅",
            "in_progress": "🔄",
            "pending": "⏳",
            "failed": "❌",
        }.get(status, "❓")

        print(f"{status_emoji} {task_id}: {desc}")
        print(f"   状態: {status} | 所要時間: {time}")
        print()

        if status == "completed":
            completed += 1
        elif status == "in_progress":
            in_progress += 1
        else:
            pending += 1

    progress = (completed / len(ma_tasks) * 100) if ma_tasks else 0

    print("=" * 60)
    print(f"📈 進捗: {progress:.0f}%")
    print(f"   完了: {completed}件")
    print(f"   進行中: {in_progress}件")
    print(f"   未着手: {pending}件")
    print("=" * 60)

    if completed == len(ma_tasks):
        print("\n�� 全タスク完了！デモ実施の準備が整いました")
    else:
        print(f"\n次のタスク: {ma_tasks[completed][1] if completed < len(ma_tasks) else 'なし'}")


if __name__ == "__main__":
    check_progress()
