#!/usr/bin/env python3
"""1タスク実行（品質強化版 v4.0）"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from agents.task_execution.high_quality_executor_v4 import \
    HighQualityExecutorV4
from tools.base_data_accessor import BaseDataAccessor


def main():
    print("=" * 60)
    print("🚀 1タスク実行（品質強化版 v4.0）")
    print("=" * 60)

    try:
        accessor = BaseDataAccessor()

        # pendingタスク取得
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

        # 実行（v4）
        executor = HighQualityExecutorV4(model_name="gemini-2.0-flash-exp")
        result = executor.execute_task(
            task_id=task.get("task_id"),
            task_description=task.get("description", ""),
            required_role=task.get("required_role", "general"),
        )

        # 結果記録
        if result["status"] == "success":
            task_id = task.get("task_id")
            tasks_data = accessor.read_sheet_as_dicts("pm_tasks")

            for i, t in enumerate(tasks_data, start=2):
                if t.get("task_id") == task_id:
                    accessor.sheets.update_range(f"pm_tasks!E{i}", [["completed"]])
                    print(f"✅ ステータス更新: completed")
                    break

            print(f"\n{'='*60}")
            print(f"✅ タスク完了")
            print(f"{'='*60}")
            print(f"📦 成果物: {result.get('structured_output_dir', 'N/A')}")
            print(f"📄 ファイル数: {result.get('file_count', 0)}")
            print(f"📊 品質スコア: {result.get('quality_score', 0)}/100")
            print(f"📏 コード行数: {result.get('line_count', 0)}")
            print(f"{'='*60}")

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
