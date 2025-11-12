"""
オブザーバビリティダッシュボード
進捗表示・品質監視・アラート機能
"""

import os
import sys
from datetime import datetime

project_root = os.path.abspath(os.path.dirname(__file__) + "/../..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.base_data_accessor import BaseDataAccessor


class ObservabilityDashboard(BaseDataAccessor):
    """リアルタイム進捗ダッシュボード"""

    def __init__(self, sheets_manager=None):
        super().__init__(sheets_manager)

    def display_goal_progress(self, goal_id: str):
        """ゴール進捗表示"""
        print("\n" + "=" * 80)
        print(f"📊 ゴール進捗ダッシュボード - Goal ID: {goal_id}")
        print("=" * 80)

        # ゴール情報取得
        goals = self.read_sheet_as_dicts(
            "project_goal", filter_func=lambda g: g.get("goal_id") == goal_id
        )

        if not goals:
            print("⚠️ ゴールが見つかりません")
            return

        goal = goals[0]
        print(f"\n目標: {goal.get('goal_description', '')[:100]}...")
        print(f"ステータス: {goal.get('status')}")
        print(f"作成日: {goal.get('created_at')}")

        # タスク情報取得
        tasks = self.read_sheet_as_dicts(
            "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal_id
        )

        total = len(tasks)
        if total == 0:
            print("\n⚠️ タスクがありません")
            return

        completed = sum(1 for t in tasks if t.get("status", "").lower() == "completed")
        pending = sum(1 for t in tasks if t.get("status", "").lower() == "pending")
        in_progress = sum(1 for t in tasks if t.get("status", "").lower() == "in_progress")

        progress = (completed / total * 100) if total > 0 else 0

        print(f"\n📈 進捗状況:")
        print(f"  全体: {completed}/{total}件完了 ({progress:.1f}%)")
        print(f"  完了: {completed}件")
        print(f"  実行中: {in_progress}件")
        print(f"  待機中: {pending}件")

        # プログレスバー
        bar_length = 50
        filled = int(bar_length * progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\n  [{bar}] {progress:.1f}%")

        # タスク詳細
        print(f"\n📋 タスク一覧:")
        for i, task in enumerate(tasks[:10], 1):
            status_icon = {
                "completed": "✅",
                "in_progress": "🔄",
                "pending": "⏳",
                "failed": "❌",
            }.get(task.get("status", "").lower(), "❓")

            print(
                f"  {i}. {status_icon} {task.get('task_id')} - {task.get('description', '')[:50]}..."
            )

        if len(tasks) > 10:
            print(f"  ... 他 {len(tasks)-10}件")

        # 品質スコア
        logs = self.read_sheet_as_dicts(
            "task_execution_log",
            filter_func=lambda l: any(
                l.get("task_id", "").startswith(f"{goal_id}_TASK") for _ in [0]
            ),
        )

        if logs:
            scores = []
            for log in logs:
                try:
                    score = float(log.get("Quality_Score", 0))
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
            print(f"  • {pending}件のタスクを実行")
        elif in_progress > 0:
            print(f"  • {in_progress}件のタスクを完了")
        elif progress >= 100:
            print(f"  • ゴール達成！🎉")
        else:
            print(f"  • 追加タスクの検討")

        print("=" * 80 + "\n")

    def display_recent_outputs(self, limit: int = 5):
        """最近の出力ファイル表示"""
        output_dir = "/workspaces/gemini_AI_Agent/agent_outputs"

        if not os.path.exists(output_dir):
            print("⚠️ 出力ディレクトリなし")
            return

        files = []
        for f in os.listdir(output_dir):
            if f.endswith(".txt"):
                path = os.path.join(output_dir, f)
                mtime = os.path.getmtime(path)
                files.append((f, mtime))

        files.sort(key=lambda x: x[1], reverse=True)

        print("\n📂 最近の出力ファイル:")
        for i, (filename, mtime) in enumerate(files[:limit], 1):
            dt = datetime.fromtimestamp(mtime)
            print(f"  {i}. {filename} - {dt.strftime('%Y-%m-%d %H:%M:%S')}")

        if len(files) > limit:
            print(f"  ... 他 {len(files)-limit}件")
        print()


if __name__ == "__main__":
    dashboard = ObservabilityDashboard()
    dashboard.display_goal_progress("6")
    dashboard.display_recent_outputs()
