"""
オブザーバビリティダッシュボード
"""

import os
import sys
from datetime import datetime

project_root = os.path.abspath(os.path.dirname(__file__) + "/../..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.base_data_accessor import BaseDataAccessor


class Dashboard(BaseDataAccessor):
    """進捗ダッシュボード"""

    def __init__(self, sheets_manager=None):
        super().__init__(sheets_manager)

    def display_all_progress(self):
        """全ゴールの進捗表示"""
        print("\n" + "=" * 80)
        print("📊 全体進捗ダッシュボード")
        print("=" * 80)

        # 全ゴール取得
        goals = self.read_sheet_as_dicts("project_goal")

        active_goals = [g for g in goals if g.get("status", "").lower() in ["active", "pending"]]

        print(f"\n総ゴール数: {len(goals)}件")
        print(f"アクティブゴール: {len(active_goals)}件")

        for goal in active_goals:
            goal_id = goal.get("goal_id")
            self.display_goal_progress(goal_id)

    def display_goal_progress(self, goal_id: str):
        """ゴール進捗表示"""
        print("\n" + "─" * 80)
        print(f"📊 ゴール進捗: {goal_id}")
        print("─" * 80)

        # ゴール情報
        goals = self.read_sheet_as_dicts(
            "project_goal", filter_func=lambda g: g.get("goal_id") == goal_id
        )

        if not goals:
            print("⚠️ ゴールが見つかりません")
            return

        goal = goals[0]
        print(f"\n目標: {goal.get('goal_description', '')[:100]}...")
        print(f"ステータス: {goal.get('status')}")

        # タスク情報
        tasks = self.read_sheet_as_dicts(
            "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal_id
        )

        if not tasks:
            print("\n⚠️ タスクがありません")
            return

        total = len(tasks)
        completed = sum(1 for t in tasks if t.get("status", "").lower() == "completed")
        pending = sum(1 for t in tasks if t.get("status", "").lower() == "pending")
        failed = sum(1 for t in tasks if t.get("status", "").lower() == "failed")

        progress = (completed / total * 100) if total > 0 else 0

        print(f"\n📈 進捗状況:")
        print(f"  全体: {completed}/{total}件完了 ({progress:.1f}%)")
        print(f"  ✅ 完了: {completed}件")
        print(f"  ⏳ 待機中: {pending}件")
        print(f"  ❌ 失敗: {failed}件")

        # プログレスバー
        bar_length = 50
        filled = int(bar_length * progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\n  [{bar}] {progress:.1f}%")

        # タスク詳細
        print(f"\n📋 タスク一覧:")
        for i, task in enumerate(tasks[:10], 1):
            status = task.get("status", "unknown").lower()
            status_icon = {
                "completed": "✅",
                "pending": "⏳",
                "failed": "❌",
                "in_progress": "🔄",
            }.get(status, "❓")

            desc = task.get("description", "")[:50]
            print(f"  {i}. {status_icon} {task.get('task_id')} - {desc}...")

        if len(tasks) > 10:
            print(f"  ... 他 {len(tasks)-10}件")

        # 品質スコア
        logs = self.read_sheet_as_dicts("task_execution_log")
        goal_logs = [
            log
            for log in logs
            if any(log.get("task_id", "").startswith(f"{goal_id}_") for _ in [0])
        ]

        if goal_logs:
            scores = []
            for log in goal_logs:
                try:
                    score_str = log.get("Quality_Score", "0")
                    if score_str and score_str.strip():
                        score = float(score_str)
                        if score > 0:
                            scores.append(score)
                except:
                    pass

            if scores:
                avg_quality = sum(scores) / len(scores)
                print(f"\n⭐ 品質スコア: {avg_quality:.1f}/10 (平均)")

        # 次のアクション
        print(f"\n🎯 次のアクション:")
        if pending > 0:
            print(f"  • {pending}件のpendingタスクを実行")
            print(f"    → python3 agents/task_execution/real_executor.py")
        elif progress >= 100:
            print(f"  • ゴール達成！🎉")
        else:
            print(f"  • すべてのタスクが完了しています")

        print("─" * 80)

    def display_recent_outputs(self, limit: int = 5):
        """最近の出力ファイル表示"""
        output_dir = "/workspaces/gemini_AI_Agent/agent_outputs"

        print("\n" + "─" * 80)
        print("📂 最近の出力ファイル")
        print("─" * 80)

        if not os.path.exists(output_dir):
            print("\n⚠️ 出力ディレクトリなし")
            return

        files = []
        for f in os.listdir(output_dir):
            if f.endswith(".txt"):
                path = os.path.join(output_dir, f)
                mtime = os.path.getmtime(path)
                size = os.path.getsize(path)
                files.append((f, mtime, size))

        files.sort(key=lambda x: x[1], reverse=True)

        if not files:
            print("\n⚠️ 出力ファイルなし")
            return

        print()
        for i, (filename, mtime, size) in enumerate(files[:limit], 1):
            dt = datetime.fromtimestamp(mtime)
            size_kb = size / 1024
            print(f"  {i}. {filename}")
            print(f"     時刻: {dt.strftime('%Y-%m-%d %H:%M:%S')} | サイズ: {size_kb:.1f}KB")

        if len(files) > limit:
            print(f"\n  ... 他 {len(files)-limit}件")

        print("─" * 80)


if __name__ == "__main__":
    print("=" * 80)
    print("🚀 オブザーバビリティダッシュボード")
    print("=" * 80)

    dashboard = Dashboard()
    dashboard.display_all_progress()
    dashboard.display_recent_outputs()

    print("\n" + "=" * 80)
    print("📊 ダッシュボード表示完了")
    print("=" * 80)
