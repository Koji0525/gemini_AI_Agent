"""
project_goal から pm_tasks へのタスク分解モジュール
"""

import sys
import os

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from tools.sheets_manager import GoogleSheetsManager
from datetime import datetime


class TaskDecomposer:
    def __init__(self):
        self.sheets = GoogleSheetsManager()

    def decompose_goals_to_tasks(self):
        """project_goal から pm_tasks へのタスク分解を実行"""
        try:
            if not self.sheets.authenticated:
                print("❌ スプレッドシート認証されていません")
                print("💡 認証設定を確認してください:")
                print(
                    f"  - GOOGLE_SERVICE_ACCOUNT_FILE: {os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')}"
                )
                print(
                    f"  - ファイル存在: {os.path.exists(os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', ''))}"
                )
                return False

            # project_goal を読み込み
            goals = self.sheets.read_sheet("project_goal")
            if not goals:
                print("ℹ️ project_goal にデータがありません")
                print("💡 project_goal シートにゴールを追加してください")
                return False

            print(f"📊 project_goal から {len(goals)} 件のゴールを読み込み")

            # pm_tasks を読み込み（既存タスク確認用）
            existing_tasks = self.sheets.read_sheet("pm_tasks")
            existing_task_titles = [
                task.get("title", "") for task in existing_tasks if task.get("title")
            ]

            new_tasks = []

            for goal in goals:
                goal_title = goal.get("goal_title", "")
                goal_description = goal.get("description", "")
                goal_priority = goal.get("priority", "medium")

                if not goal_title:
                    continue

                # ゴールからタスクを分解
                tasks_from_goal = self._create_tasks_from_goal(
                    goal_title, goal_description, goal_priority
                )

                for task in tasks_from_goal:
                    # 既存タスクと重複していないか確認
                    if task["title"] not in existing_task_titles:
                        new_tasks.append(task)
                        existing_task_titles.append(task["title"])

            if new_tasks:
                print(f"🎯 {len(new_tasks)} 件の新しいタスクを作成")

                # 新しいタスクを pm_tasks に追加
                success = self._add_tasks_to_sheet(new_tasks)
                return success
            else:
                print("ℹ️ 新しいタスクはありません")
                return True

        except Exception as e:
            print(f"❌ タスク分解エラー: {e}")
            return False

    def _create_tasks_from_goal(self, goal_title, goal_description, priority):
        """ゴールからタスクを作成"""
        tasks = []

        base_tasks = [
            {
                "title": f"分析: {goal_title}",
                "description": f"ゴールの分析: {goal_description}",
                "status": "pending",
                "priority": priority,
                "type": "analysis",
                "estimated_hours": 2,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            {
                "title": f"設計: {goal_title}",
                "description": f"実装設計の作成",
                "status": "pending",
                "priority": priority,
                "type": "design",
                "estimated_hours": 4,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            {
                "title": f"実装: {goal_title}",
                "description": f"コア機能の実装",
                "status": "pending",
                "priority": priority,
                "type": "implementation",
                "estimated_hours": 8,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            {
                "title": f"テスト: {goal_title}",
                "description": f"機能テストの実施",
                "status": "pending",
                "priority": priority,
                "type": "testing",
                "estimated_hours": 3,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
        ]

        return base_tasks

    def _add_tasks_to_sheet(self, tasks):
        """タスクをシートに追加"""
        try:
            # 既存のタスクを読み込み
            existing_tasks = self.sheets.read_sheet("pm_tasks")

            # 新しいタスクを追加
            all_tasks = existing_tasks + tasks

            # シートをクリアして再書き込み
            sheet = self.sheets.spreadsheet.worksheet("pm_tasks")

            # ヘッダーを取得
            if existing_tasks:
                headers = list(existing_tasks[0].keys())
            else:
                headers = list(tasks[0].keys()) if tasks else []

            # データ行を作成
            rows = [headers]  # ヘッダー行
            for task in all_tasks:
                row = [task.get(header, "") for header in headers]
                rows.append(row)

            # シートを更新
            sheet.clear()
            sheet.update("A1", rows)

            print(f"✅ pm_tasks に {len(tasks)} 件のタスクを追加")
            return True

        except Exception as e:
            print(f"❌ タスク追加エラー: {e}")
            return False


def main():
    """メイン実行関数"""
    decomposer = TaskDecomposer()
    success = decomposer.decompose_goals_to_tasks()

    if success:
        print("🎉 タスク分解完了")
    else:
        print("❌ タスク分解失敗 - 認証またはデータの問題")

    return success


if __name__ == "__main__":
    main()
