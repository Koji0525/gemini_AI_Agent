#!/usr/bin/env python3
"""
目標進捗確認ツール v2.0

既存のproject_goalシート構造に対応:
  A列: goal_id
  B列: goal_description
  C列: status
  D列: created_at
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.sheets_manager import GoogleSheetsManager

sheets_manager = GoogleSheetsManager()

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("📊 アクティブな目標一覧 v2.0")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# project_goalシートから取得
all_data = sheets_manager.read_range("project_goal!A2:D200")

print(f"\n📋 全データ行数: {len(all_data)}")

# activeな目標を抽出（C列 = status）
active_goals = []
for row in all_data:
    if len(row) >= 3:  # 最低3列必要
        status = row[2] if len(row) > 2 else ""  # C列 (インデックス2)
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
        print(f"  内容: {description[:80]}...")  # 長い場合は省略
        print(f"  status: {status}")
        print(f"  作成日: {created}")

        # 関連タスクを確認
        tasks = sheets_manager.read_range("pm_tasks!A2:K100")
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
    print("\n💡 目標を追加するには:")
    print('   python3 tools/local_development_request_v2.py "開発目標"')

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
