#!/usr/bin/env python3
"""
pm_tasks タスクステータス更新スクリプト
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager


def update_task_status(task_id, new_status):
    """タスクのステータスを更新"""
    sheets = GoogleSheetsManager()

    try:
        data = sheets.read_range("pm_tasks")

        if not data or len(data) <= 1:
            print("❌ pm_tasksが空です")
            return False

        headers = data[0]
        task_id_idx = headers.index("task_id") if "task_id" in headers else 0
        status_idx = headers.index("status") if "status" in headers else 2

        updated = False
        for i, row in enumerate(data[1:], start=1):
            if len(row) > task_id_idx and row[task_id_idx] == task_id:
                # ステータスを更新
                while len(row) <= status_idx:
                    row.append("")
                row[status_idx] = new_status
                data[i] = row
                updated = True
                print(f"✅ {task_id} のステータスを '{new_status}' に更新")

        if updated:
            sheets.write_range("pm_tasks", data)
            return True
        else:
            print(f"⚠️ タスクID '{task_id}' が見つかりません")
            return False

    except Exception as e:
        print(f"❌ エラー: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使い方: python3 update_task_status.py <task_id> <status>")
        print("例: python3 update_task_status.py MA_PORTAL_1 completed")
        sys.exit(1)

    task_id = sys.argv[1]
    status = sys.argv[2]

    update_task_status(task_id, status)
