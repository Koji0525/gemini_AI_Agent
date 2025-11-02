#!/usr/bin/env python3
"""
目標進捗確認ツール（修正版）

正しいシート: project_goal
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.sheets_manager import GoogleSheetsManager

sheets_manager = GoogleSheetsManager()

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("📊 アクティブな目標一覧（修正版）")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# project_goalシートから取得（正しいシート名）
goals = sheets_manager.read_range("project_goal!A2:F100")
active_goals = [g for g in goals if len(g) > 3 and g[3] == "active"]

if active_goals:
    print(f"\n🎯 アクティブな目標: {len(active_goals)}件\n")

    for goal in active_goals:
        print(f"目標ID: {goal[0]}")
        print(f"  内容: {goal[1]}")
        print(f"  優先度: {goal[2]}")
        print(f"  進捗: {goal[4]}")
        print()

        # 関連タスクを確認
        tasks = sheets_manager.read_range("pm_tasks!A2:K100")
        related_tasks = [t for t in tasks if len(t) > 1 and goal[0] in str(t[1])]

        if related_tasks:
            total = len(related_tasks)
            completed = sum(1 for t in related_tasks if len(t) > 3 and t[3] == "completed")
            pending = sum(1 for t in related_tasks if len(t) > 3 and t[3] == "pending")
            in_progress = sum(1 for t in related_tasks if len(t) > 3 and t[3] == "in_progress")

            print(f"  📋 タスク状況:")
            print(f"     総数: {total}")
            print(f"     完了: {completed}")
            print(f"     実行中: {in_progress}")
            print(f"     保留: {pending}")
        else:
            print(f"  ⚠️ まだタスクに分解されていません")

        print()
else:
    print("\n⚠️ アクティブな目標はありません")
    print("\n💡 目標を追加するには:")
    print('   python3 tools/local_development_request_fixed.py "開発目標" high')

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
