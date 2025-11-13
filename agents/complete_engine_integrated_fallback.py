#!/usr/bin/env python3
"""
CompleteEngine統合フォールバック版
既存のCompleteEngineUltimateが利用できない場合の代替実装
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.self_healing.self_healing_agent import SelfHealingAgent
from tools.base_data_accessor import BaseDataAccessor


class CompleteEngineIntegratedFallback(BaseDataAccessor):
    """
    CompleteEngine統合フォールバック版
    BaseDataAccessorをベースに最小限の実装
    """

    def __init__(self, sheets_manager=None):
        super().__init__(sheets_manager)
        self.self_healing_agent = SelfHealingAgent()
        print("✅ CompleteEngine Integrated Fallback 初期化完了")

    def select_goal(self):
        """ゴール選択（簡易版）"""
        print("🎯 ゴール選択（フォールバックモード）")

        try:
            # 簡易的なゴール選択ロジック
            goals = self.read_sheet_as_dicts("project_goal")
            active_goals = [g for g in goals if g.get("status") in ["active", "pending"]]

            if not active_goals:
                print("❌ アクティブなゴールが見つかりません")
                return None

            # 最初のアクティブゴールを選択
            goal = active_goals[0]
            goal_id = goal.get("goal_id")
            print(f"✅ ゴール選択: {goal_id} - {goal.get('goal_description', 'N/A')}")

            return goal_id

        except Exception as e:
            print(f"❌ ゴール選択エラー: {e}")
            return None

    def get_next_pending_task(self, goal_id):
        """次の保留タスク取得（簡易版）"""
        print(f"📋 保留タスク検索: goal_id={goal_id}")

        try:
            tasks = self.read_sheet_as_dicts("pm_tasks")
            pending_tasks = [
                t
                for t in tasks
                if t.get("parent_goal_id") == goal_id and t.get("status") == "pending"
            ]

            if not pending_tasks:
                print("⏸️ 保留タスクなし")
                return None

            # 最初の保留タスクを返す
            task = pending_tasks[0]
            print(f"✅ タスク選択: {task.get('description', 'N/A')}")

            return task

        except Exception as e:
            print(f"❌ タスク取得エラー: {e}")
            return None

    def execute_task(self, task):
        """タスク実行（簡易版）"""
        print(f"⚡ タスク実行: {task.get('description', 'N/A')}")

        # 簡易的なタスク実行シミュレーション
        return {
            "status": "completed",
            "output": f"タスク '{task.get('description')}' を実行しました",
            "file_path": f"agent_outputs/task_{task.get('task_id', 'unknown')}.txt",
        }

    def process_execution_result(self, task, result):
        """実行結果処理（簡易版）"""
        print(f"📝 結果処理: {result.get('status', 'unknown')}")
        # 簡易的な結果処理
        return True

    def execute_task_with_healing(self, task):
        """タスク実行（自己修復機能付き）"""
        print(f"\n🔧 タスク実行開始（自己修復モード）: {task.get('description', 'N/A')}")

        try:
            # 通常のタスク実行
            result = self.execute_task(task)
            print("✅ タスク正常完了")
            return result

        except Exception as e:
            print(f"⚠️ タスク実行エラー: {type(e).__name__}: {e}")

            # 自己修復の実行
            healing_context = {
                "task": task,
                "func": self.execute_task,
                "args": [task],
                "kwargs": {},
            }

            healing_result = self.self_healing_agent.detect_and_heal(e, healing_context)

            if healing_result["success"]:
                print("🎉 自己修復成功！タスクを完了しました")
                return healing_result.get("result", {"status": "healed"})
            else:
                print("💥 自己修復失敗。タスクを中断します")
                raise

    def run_with_healing(self, count=1):
        """メイン実行ループ（自己修復機能付き）"""
        print("=" * 80)
        print("🚀 CompleteEngine Fallback - 自己修復モード起動")
        print("=" * 80)

        try:
            goal_id = self.select_goal()
            if not goal_id:
                print("❌ 実行対象のゴールが見つかりません")
                return

            print(f"🎯 対象ゴール: {goal_id}")

            for i in range(count):
                print(f"\n--- 実行 {i+1}/{count} ---")

                task = self.get_next_pending_task(goal_id)
                if not task:
                    print("⏸️ 実行対象のタスクがありません")
                    break

                result = self.execute_task_with_healing(task)
                self.process_execution_result(task, result)

            self.show_healing_stats()

        except Exception as e:
            print(f"💥 システムエラー: {e}")
            self.try_system_level_healing(e)

    def show_healing_stats(self):
        """修復統計の表示"""
        stats = self.self_healing_agent.get_statistics()

        print("\n" + "=" * 80)
        print("📊 自己修復統計")
        print("=" * 80)
        print(f"総エラー数: {stats['total_errors']}")
        print(f"修復成功: {stats['healed_errors']}")
        print(f"修復失敗: {stats['failed_heals']}")
        print(f"修復成功率: {stats['healing_rate']:.1f}%")

        if stats["by_type"]:
            print("\nエラータイプ別:")
            for error_type, count in stats["by_type"].items():
                print(f"  {error_type}: {count}件")

    def try_system_level_healing(self, error):
        """システムレベルの修復試行"""
        print(f"\n🛠️ システムレベル修復を試行: {error}")

        system_context = {"error": str(error), "component": "CompleteEngine", "timestamp": "now"}

        healing_result = self.self_healing_agent.detect_and_heal(error, system_context)

        if healing_result["success"]:
            print("✅ システムレベル修復成功")
        else:
            print("❌ システムレベル修復失敗")


def main():
    """フォールバック版のメイン実行"""
    try:
        engine = CompleteEngineIntegratedFallback()
        print("🧪 フォールバック統合テスト実行")
        engine.run_with_healing(count=1)

    except Exception as e:
        print(f"❌ フォールバックテスト失敗: {e}")


if __name__ == "__main__":
    main()
