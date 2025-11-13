#!/usr/bin/env python3
"""
スマートタスク選択版エンジン - 重複実行を防止
"""

import sys
import time
from pathlib import Path

# プロジェクトルートを追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from agents.complete_engine_safe_integrated_v2 import \
        CompleteEngineSafeIntegratedV2

    print("✅ 安全版エンジンを継承")

    class CompleteEngineSmartSelection(CompleteEngineSafeIntegratedV2):
        """
        スマートタスク選択版エンジン
        重複実行を防止し、多様なタスクを実行
        """

        def __init__(self, sheets_manager=None):
            super().__init__(sheets_manager)
            self.executed_tasks = set()  # 実行済みタスクを記録
            print("✅ CompleteEngine Smart Selection 初期化完了")

        def get_next_pending_task(self, goal_id):
            """次の保留タスク取得（重複防止版）"""
            print(f"📋 スマートタスク検索: goal_id={goal_id}")

            try:
                tasks = self.read_sheet_as_dicts("pm_tasks")
                pending_tasks = [
                    t
                    for t in tasks
                    if str(t.get("parent_goal_id")) == str(goal_id)
                    and t.get("status") == "pending"
                    and t.get("task_id") not in self.executed_tasks  # 未実行タスクのみ
                ]

                if not pending_tasks:
                    print("⏸️ 新しい保留タスクなし")

                    # 実行済みタスクをリセットして再試行
                    if self.executed_tasks:
                        print("🔄 実行済みタスクをリセットして再検索")
                        self.executed_tasks.clear()
                        pending_tasks = [
                            t
                            for t in tasks
                            if str(t.get("parent_goal_id")) == str(goal_id)
                            and t.get("status") == "pending"
                        ]

                if not pending_tasks:
                    print("❌ 実行可能なタスクがありません")
                    return None

                # 最も古いタスクを選択（作成日時でソート）
                pending_tasks.sort(key=lambda x: x.get("created_at", ""))
                task = pending_tasks[0]

                print(f"✅ スマートタスク選択: {task.get('task_id')}")
                print(f"   説明: {task.get('description', 'N/A')[:50]}...")

                return task

            except Exception as e:
                print(f"❌ タスク取得エラー: {e}")
                return None

        def execute_task_with_healing(self, task):
            """タスク実行（実行記録付き）"""
            task_id = task.get("task_id")

            # 実行済みタスクとして記録
            self.executed_tasks.add(task_id)
            print(f"📝 タスク {task_id} を実行済みとして記録")

            # 親クラスのメソッドを呼び出し
            return super().execute_task_with_healing(task)

        def run_with_healing(self, count=1):
            """メイン実行ループ（重複防止版）"""
            print("=" * 80)
            print("🧠 CompleteEngine Smart Selection - 重複防止モード起動")
            print("=" * 80)

            try:
                goal_id = self.select_goal()
                if not goal_id:
                    print("❌ 実行対象のゴールが見つかりません")
                    return False

                print(f"🎯 対象ゴール: {goal_id}")

                success_count = 0
                for i in range(count):
                    print(f"\n--- 実行 {i+1}/{count} ---")

                    task = self.get_next_pending_task(goal_id)
                    if not task:
                        print("⏸️ 実行対象のタスクがありません")
                        break

                    result = self.execute_task_with_healing(task)
                    if self.process_execution_result(task, result):
                        success_count += 1
                        self.execution_count += 1

                    # 実行間隔を空ける（重複防止）
                    time.sleep(1)

                self.show_smart_stats(success_count, count)
                return success_count > 0

            except Exception as e:
                print(f"💥 システムエラー: {e}")
                return False

        def show_smart_stats(self, success_count, total_count):
            """スマート統計表示"""
            print("\n" + "=" * 80)
            print("📊 スマート実行統計")
            print("=" * 80)
            print(f"✅ 成功実行: {success_count}/{total_count}")
            print(f"📝 実行済みタスク記録数: {len(self.executed_tasks)}")
            print(f"🔁 重複実行防止: 有効")

            if self.executed_tasks:
                print("\n📋 実行済みタスク:")
                for task_id in list(self.executed_tasks)[:5]:  # 最大5件表示
                    print(f"  - {task_id}")

    print("✅ CompleteEngineSmartSelection クラス定義完了")

except Exception as e:
    print(f"❌ スマート版エンジン作成エラー: {e}")

# テスト用
if __name__ == "__main__":
    try:
        engine = CompleteEngineSmartSelection()
        print("🧪 スマート版エンジンテスト: 初期化成功")

        # テスト実行
        result = engine.run_with_healing(count=2)
        if result:
            print("🎉 スマート版エンジンテスト成功")
        else:
            print("❌ スマート版エンジンテスト失敗")

    except Exception as e:
        print(f"❌ スマート版エンジンテスト失敗: {e}")
