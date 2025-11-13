#!/usr/bin/env python3
"""
進捗集計方法の分析
"""

import sys
from pathlib import Path

# プロジェクトルートを追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.base_data_accessor import BaseDataAccessor

    class ProgressAnalyzer(BaseDataAccessor):
        def analyze_progress(self):
            """進捗計算方法を分析"""
            print("📊 進捗計算分析")
            print("=" * 60)

            # フェーズとタスクの取得
            tasks = self.read_sheet_as_dicts("pm_tasks")
            if not tasks:
                print("❌ タスクデータがありません")
                return

            # フェーズごとの集計
            phases = {}
            for task in tasks:
                phase = task.get("parent_goal_id", "unknown")
                if phase not in phases:
                    phases[phase] = {"total": 0, "completed": 0}

                phases[phase]["total"] += 1
                if task.get("status") == "completed":
                    phases[phase]["completed"] += 1

            print("フェーズ別進捗:")
            total_tasks = 0
            total_completed = 0

            for phase_id, stats in phases.items():
                total = stats["total"]
                completed = stats["completed"]
                progress = (completed / total * 100) if total > 0 else 0

                total_tasks += total
                total_completed += completed

                print(f"Phase {phase_id}: {completed}/{total} ({progress:.1f}%)")

            overall_progress = (total_completed / total_tasks * 100) if total_tasks > 0 else 0
            print(f"\n全体進捗: {total_completed}/{total_tasks} ({overall_progress:.1f}%)")

            # show_progress.pyの計算方法を推測
            print("\n🔍 show_progress.pyの計算方法推測:")
            print("Phase 0: 3/3 = 100%")
            print("Phase 1-5: 0/22 = 0%")
            print("全体: (3 + 0) / (3 + 22) = 3/25 = 12% → 表示は10% (切り捨てまたは別の計算)")

    analyzer = ProgressAnalyzer()
    analyzer.analyze_progress()

except Exception as e:
    print(f"❌ 分析エラー: {e}")
