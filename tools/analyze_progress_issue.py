#!/usr/bin/env python3
"""
進捗表示の問題分析
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.base_data_accessor import BaseDataAccessor

    class ProgressIssueAnalyzer(BaseDataAccessor):
        def analyze_issue(self):
            """進捗問題を詳細分析"""
            print("🔍 進捗表示問題分析")
            print("=" * 60)

            # 全タスクの取得
            tasks = self.read_sheet_as_dicts("pm_tasks")
            goals = self.read_sheet_as_dicts("project_goal")

            print(f"全タスク数: {len(tasks)}")
            print(f"全ゴール数: {len(goals)}")

            # show_progress.py が表示しているPhase 0-5の分析
            print("\n📊 show_progress.py が表示しているPhase 0-5:")
            phase_0_5_tasks = [
                t
                for t in tasks
                if str(t.get("parent_goal_id", "")).isdigit()
                and 0 <= int(t.get("parent_goal_id", -1)) <= 5
            ]
            phase_0_5_completed = [t for t in phase_0_5_tasks if t.get("status") == "completed"]

            print(f"Phase 0-5 タスク数: {len(phase_0_5_tasks)}")
            print(f"Phase 0-5 完了数: {len(phase_0_5_completed)}")

            # フェーズごとの詳細
            for phase in range(0, 6):
                phase_tasks = [t for t in tasks if str(t.get("parent_goal_id")) == str(phase)]
                completed_tasks = [t for t in phase_tasks if t.get("status") == "completed"]

                if phase_tasks:
                    progress = len(completed_tasks) / len(phase_tasks) * 100
                    print(
                        f"Phase {phase}: {len(completed_tasks)}/{len(phase_tasks)} ({progress:.1f}%)"
                    )
                else:
                    print(f"Phase {phase}: 0/0 (0.0%) - タスクなし")

            # 実際の全体進捗
            all_completed = len([t for t in tasks if t.get("status") == "completed"])
            all_total = len(tasks)
            actual_progress = all_completed / all_total * 100 if all_total > 0 else 0

            print(f"\n📈 実際の全体進捗: {all_completed}/{all_total} ({actual_progress:.1f}%)")
            print(f"📊 show_progress.py 表示: 10.0%")

            # 問題の原因分析
            print(f"\n🔎 問題原因:")
            print(f"1. show_progress.py は Phase 0-5 のみを表示")
            print(f"2. 実際には Phase 6以上にも多くのタスクが存在")
            print(f"3. Phase 0-5 の進捗が低いため、全体進捗が低く表示")
            print(f"4. 計算方法: Phase 0-5 の完了タスク合計 / Phase 0-5 の全タスク合計")

            # 推奨解決策
            print(f"\n💡 推奨解決策:")
            print(f"1. show_progress.py を全フェーズ表示するように修正")
            print(f"2. または、Phase 0-5 のタスクを実際の進捗に合わせて更新")
            print(f"3. 進捗計算方法を実際の全体進捗に変更")

    analyzer = ProgressIssueAnalyzer()
    analyzer.analyze_issue()

except Exception as e:
    print(f"❌ 分析エラー: {e}")
    import traceback

    traceback.print_exc()
