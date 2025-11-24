#!/usr/bin/env python3
"""1タスク実行（安定版 v7.0）"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from agents.task_execution.high_quality_executor_v7 import \
    HighQualityExecutorV7
from tools.base_data_accessor import BaseDataAccessor


def main():
    print("=" * 60)
    print("🚀 1タスク実行（安定版 v7.0）")
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

        executor = HighQualityExecutorV7()
        result = executor.execute_task(
            task_id=task.get("task_id"),
            task_description=task.get("description", ""),
            required_role=task.get("required_role", "general"),
        )

        if result.get("completeness", {}).get("is_complete", False):
            task_id = task.get("task_id")
            tasks_data = accessor.read_sheet_as_dicts("pm_tasks")

            for i, t in enumerate(tasks_data, start=2):
                if t.get("task_id") == task_id:
                    accessor.sheets.update_range(f"pm_tasks!E{i}", [["completed"]])
                    break

            print(f"\n{'='*60}")
            print(f"✅ 完了（高品質）")
            print(f"{'='*60}")
            print(f"📦 ファイル数: {result.get('file_count', 0)}")
            comp = result.get("completeness", {})
            print(f"📊 品質: {comp.get('quality_score', 0)}/100")
            print(f"{'='*60}")
        else:
            print(f"\n⚠️  品質改善の余地あり")

    except Exception as e:
        print(f"\n❌ エラー: {e}")


if __name__ == "__main__":
    main()
