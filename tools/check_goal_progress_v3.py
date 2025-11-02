#!/usr/bin/env python3
"""
目標進捗確認ツール v3.0（範囲自動検出版）
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.smart_sheets_manager import SmartSheetsManager

manager = SmartSheetsManager()

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("📊 アクティブな目標一覧 v3.0（範囲自動検出）")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# 🆕 実データ範囲を自動検出
last_row = manager.detect_actual_data_range("project_goal")
print(f"\n📍 検出されたデータ範囲: {last_row}行")

# 🆕 全データを読み込む（範囲を動的に）
all_data = manager.read_range(f"project_goal!A2:D{last_row}")
print(f"📋 読み込んだデータ: {len(all_data)}行")

# activeな目標を抽出
active_goals = []
for row in all_data:
    if len(row) >= 3:
        status = row[2] if len(row) > 2 else ""
        if status.lower() == "active":
            active_goals.append(row)

if active_goals:
    print(f"\n🎯 アクティブな目標: {len(active_goals)}件\n")

    for goal in active_goals:
        goal_id = goal[0] if len(goal) > 0 else ""
        description = goal[1] if len(goal) > 1 else ""
        status = goal[2] if len(goal) > 2 else ""
        created = goal[3] if len(goal) > 3 else ""

        print(f"目標ID: {goal_id}")
        print(f"  内容: {description[:80]}...")
        print(f"  status: {status}")
        print(f"  作成日: {created}")

        # 関連タスクを確認
        tasks = manager.read_range("pm_tasks!A2:K200")
        related_tasks = [t for t in tasks if len(t) > 1 and goal_id in str(t[1])]

        if related_tasks:
            total = len(related_tasks)
            completed = sum(1 for t in related_tasks if len(t) > 3 and t[3] == "completed")
            print(f"  📋 タスク: {completed}/{total} 完了")
        else:
            print(f"  ⚠️ まだタスクに分解されていません")

        print()
else:
    print("\n⚠️ アクティブな目標はありません")

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
