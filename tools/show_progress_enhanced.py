#!/usr/bin/env python3
"""
強化版進捗表示 - 全フェーズを表示
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.base_data_accessor import BaseDataAccessor

    class EnhancedProgressTracker(BaseDataAccessor):
        def show_enhanced_progress(self):
            """強化版進捗表示"""
            print("=" * 80)
            print("📊 プロジェクト進捗（全フェーズ表示）")
            print("=" * 80)

            # 全タスクの取得
            tasks = self.read_sheet_as_dicts("pm_tasks")
            goals = self.read_sheet_as_dicts("project_goal")

            if not tasks:
                print("❌ タスクデータがありません")
                return

            # ゴールIDからゴール名へのマッピング
            goal_names = {}
            for goal in goals:
                goal_id = goal.get("goal_id")
                goal_names[str(goal_id)] = goal.get("goal_description", "Unknown")[:50] + "..."

            # フェーズごとの集計
            phases = {}
            for task in tasks:
                phase_id = str(task.get("parent_goal_id", "unknown"))
                if phase_id not in phases:
                    phases[phase_id] = {
                        "total": 0,
                        "completed": 0,
                        "name": goal_names.get(phase_id, "Unknown"),
                    }

                phases[phase_id]["total"] += 1
                if task.get("status") == "completed":
                    phases[phase_id]["completed"] += 1

            # 進捗バーの表示関数
            def progress_bar(percentage, width=20):
                filled = int(width * percentage / 100)
                empty = width - filled
                return "[" + "█" * filled + "░" * empty + "]"

            # フェーズごとに表示
            total_completed_all = 0
            total_tasks_all = 0

            # 数値でソートして表示
            sorted_phases = sorted(
                phases.keys(), key=lambda x: int(x) if x.isdigit() else float("inf")
            )

            for phase_id in sorted_phases:
                stats = phases[phase_id]
                total = stats["total"]
                completed = stats["completed"]

                if total > 0:
                    progress = (completed / total) * 100
                    total_completed_all += completed
                    total_tasks_all += total

                    print(f"\nPhase {phase_id} - {stats['name']}")
                    print(f"  {progress_bar(progress)} {progress:.1f}%")
                    print(f"  完了: {completed}/{total} タスク")

            # 全体進捗
            if total_tasks_all > 0:
                overall_progress = (total_completed_all / total_tasks_all) * 100
                print("\n" + "=" * 80)
                print(f"📈 全体進捗: {progress_bar(overall_progress)} {overall_progress:.1f}%")
                print(f"   完了: {total_completed_all}/{total_tasks_all} タスク")
                print("=" * 80)

                # 追加情報
                active_goals = [g for g in goals if g.get("status") in ["active", "pending"]]
                if active_goals:
                    print(f"\n🎯 アクティブなゴール: {len(active_goals)}件")
                    for goal in active_goals[:3]:  # 最大3件表示
                        print(f"   - {goal.get('goal_description', 'Unknown')[:60]}...")

            return total_completed_all, total_tasks_all

    tracker = EnhancedProgressTracker()
    completed, total = tracker.show_enhanced_progress()

except Exception as e:
    print(f"❌ 進捗表示エラー: {e}")
    import traceback

    traceback.print_exc()
