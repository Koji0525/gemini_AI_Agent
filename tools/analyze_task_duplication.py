#!/usr/bin/env python3
"""
タスク重複実行の問題分析
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.base_data_accessor import BaseDataAccessor

    class TaskDuplicationAnalyzer(BaseDataAccessor):
        def analyze_duplication(self):
            """タスク重複問題を分析"""
            print("🔍 タスク重複実行問題分析")
            print("=" * 60)

            # ゴール6のタスクを取得
            tasks = self.read_sheet_as_dicts("pm_tasks")
            goal_6_tasks = [t for t in tasks if str(t.get("parent_goal_id")) == "6"]

            print(f"ゴール6のタスク数: {len(goal_6_tasks)}")

            # ステータス別のタスク数
            status_count = {}
            for task in goal_6_tasks:
                status = task.get("status", "unknown")
                if status not in status_count:
                    status_count[status] = 0
                status_count[status] += 1

            print("\n📊 ステータス別タスク数:")
            for status, count in status_count.items():
                print(f"  {status}: {count}件")

            # 重複している可能性のあるタスクをチェック
            task_descriptions = {}
            duplicate_tasks = []

            for task in goal_6_tasks:
                desc = task.get("description", "")
                if desc in task_descriptions:
                    duplicate_tasks.append((task_descriptions[desc], task))
                else:
                    task_descriptions[desc] = task

            if duplicate_tasks:
                print(f"\n❌ 重複タスク発見: {len(duplicate_tasks)}組")
                for task1, task2 in duplicate_tasks:
                    print(f"  タスクA: {task1.get('task_id')} - {task1.get('description')[:50]}...")
                    print(f"  タスクB: {task2.get('task_id')} - {task2.get('description')[:50]}...")
            else:
                print("\n✅ 重複タスクはありません")

            # 6_test_004タスクの詳細を確認
            print(f"\n🔍 6_test_004タスクの詳細:")
            task_6_test_004 = [t for t in goal_6_tasks if t.get("task_id") == "6_test_004"]
            if task_6_test_004:
                task = task_6_test_004[0]
                print(f"  タスクID: {task.get('task_id')}")
                print(f"  ステータス: {task.get('status')}")
                print(f"  説明: {task.get('description')}")
                print(f"  親ゴールID: {task.get('parent_goal_id')}")
            else:
                print("  ❌ 6_test_004タスクが見つかりません")

            # 次の保留タスク候補
            pending_tasks = [t for t in goal_6_tasks if t.get("status") == "pending"]
            print(f"\n📋 保留中のタスク: {len(pending_tasks)}件")
            for task in pending_tasks[:5]:  # 最大5件表示
                print(f"  - {task.get('task_id')}: {task.get('description')[:50]}...")

    analyzer = TaskDuplicationAnalyzer()
    analyzer.analyze_duplication()

except Exception as e:
    print(f"❌ 分析エラー: {e}")
    import traceback

    traceback.print_exc()
