#!/usr/bin/env python3
"""1タスク実行（最終版 v6.0 - 機能完全性保証）"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from agents.task_execution.high_quality_executor_v6 import \
    HighQualityExecutorV6
from tools.base_data_accessor import BaseDataAccessor


def main():
    print("=" * 60)
    print("🚀 1タスク実行（最終版 v6.0 - 機能完全性保証）")
    print("=" * 60)

    try:
        accessor = BaseDataAccessor()

        tasks = accessor.read_sheet_as_dicts(
            "pm_tasks", filter_func=lambda t: t.get("status") == "pending"
        )

        if not tasks:
            print("✅ pendingタスクなし")
            return

        task = tasks[0]

        print(f"\n📋 実行タスク:")
        print(f"  ID: {task.get('task_id')}")
        print(f"  説明: {task.get('description', '')[:100]}...")

        executor = HighQualityExecutorV6()
        result = executor.execute_task(
            task_id=task.get("task_id"),
            task_description=task.get("description", ""),
            required_role=task.get("required_role", "general"),
        )

        if result["status"] == "success":
            task_id = task.get("task_id")
            tasks_data = accessor.read_sheet_as_dicts("pm_tasks")

            for i, t in enumerate(tasks_data, start=2):
                if t.get("task_id") == task_id:
                    accessor.sheets.update_range(f"pm_tasks!E{i}", [["completed"]])
                    break

            print(f"\n{'='*60}")
            print(f"✅ タスク完了")
            print(f"{'='*60}")
            print(f"📦 ファイル数: {result.get('file_count', 0)}")
            print(f"📊 品質: {result.get('final_quality_score', 0)}/100")

            if "completeness" in result:
                comp = result["completeness"]
                print(f"\n機能完全性: {comp['quality_score']}/100")
                print(f"  問題点: {len(comp['issues'])}件")

            print(f"{'='*60}")

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
