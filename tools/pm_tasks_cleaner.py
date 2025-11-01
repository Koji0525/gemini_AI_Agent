#!/usr/bin/env python3
"""
pm_tasks 自動クリーンアップツール
変更理由: 重複タスクの自動検出・削除で品質向上
"""

import sys
from pathlib import Path
from collections import defaultdict

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager


class PMTasksCleaner:
    """pm_tasksの自動クリーンアップ"""

    def __init__(self):
        self.sheets = GoogleSheetsManager()

    def clean_duplicates(self, dry_run=True):
        """重複タスクを検出・削除"""
        print("🧹 pm_tasks クリーンアップ開始")
        print("=" * 70)

        data = self.sheets.read_range("pm_tasks")

        if not data or len(data) <= 1:
            print("⚠️ pm_tasksが空です")
            return

        headers = data[0]
        rows = data[1:]

        # タスクIDでグループ化
        task_groups = defaultdict(list)

        for i, row in enumerate(rows):
            if len(row) > 0:
                task_id = str(row[0])
                task_groups[task_id].append((i, row))

        # 重複検出
        duplicates = {tid: tasks for tid, tasks in task_groups.items() if len(tasks) > 1}

        if duplicates:
            print(f"\n⚠️ {len(duplicates)}個の重複タスクIDを検出:")

            for task_id, tasks in duplicates.items():
                print(f"\n📋 {task_id}: {len(tasks)}件の重複")

                # 最も情報が多い行を選択
                best_task = max(tasks, key=lambda x: sum(1 for cell in x[1] if cell))

                print(f"   保持: {best_task[1][1][:50] if len(best_task[1]) > 1 else ''}...")
                print(f"   削除: {len(tasks) - 1}件")

        # クリーンアップ実行
        if not dry_run and duplicates:
            # 最良の行のみを保持
            cleaned_rows = []
            seen_ids = set()

            for task_id, tasks in task_groups.items():
                if task_id in duplicates:
                    # 最良の行を1つだけ追加
                    best_task = max(tasks, key=lambda x: sum(1 for cell in x[1] if cell))
                    if task_id not in seen_ids:
                        cleaned_rows.append(best_task[1])
                        seen_ids.add(task_id)
                else:
                    # 重複なしはそのまま追加
                    cleaned_rows.append(tasks[0][1])

            # 更新
            cleaned_data = [headers] + cleaned_rows
            self.sheets.write_range("pm_tasks", cleaned_data)

            print(f"\n✅ クリーンアップ完了")
            print(f"   削除: {len(rows) - len(cleaned_rows)}件")
            print(f"   保持: {len(cleaned_rows)}件")
        else:
            print(f"\n🔍 ドライランモード（変更なし）")
            print(f"   実行するには dry_run=False で呼び出してください")

        return len(duplicates)


def main():
    cleaner = PMTasksCleaner()

    # まずドライランで確認
    print("🔍 ドライラン: 重複チェックのみ")
    duplicate_count = cleaner.clean_duplicates(dry_run=True)

    if duplicate_count > 0:
        print("\n" + "=" * 70)
        response = input("重複を削除しますか？ (y/n): ")

        if response.lower() == "y":
            cleaner.clean_duplicates(dry_run=False)
        else:
            print("キャンセルしました")


if __name__ == "__main__":
    main()
