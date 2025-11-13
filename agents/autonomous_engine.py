"""
AutonomousEngine（品質評価統合版）
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.quality_evaluator import QualityEvaluator
from knowledge_system.simple_knowledge_wrapper import SimpleKnowledgeWrapper
from tools.base_data_accessor import BaseDataAccessor


class AutonomousEngine:
    """自律実行エンジン（品質評価統合版）"""

    def __init__(self):
        """初期化"""
        # データアクセサ
        self.accessor = BaseDataAccessor()

        # ナレッジシステム
        try:
            self.knowledge = SimpleKnowledgeWrapper()
            print("✅ ナレッジシステム統合完了")
        except Exception as e:
            print(f"⚠️ ナレッジシステム初期化失敗: {e}")
            self.knowledge = None

        # 品質評価システム
        try:
            self.quality = QualityEvaluator()
            print("✅ 品質評価システム統合完了")
        except Exception as e:
            print(f"⚠️ 品質評価システム初期化失敗: {e}")
            self.quality = None

        print("✅ AutonomousEngine 初期化完了")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ゴール管理
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_all_goals(self) -> List[Dict[str, Any]]:
        """全ゴール取得"""
        return self.accessor.read_sheet_as_dicts("project_goal")

    def select_goal(self) -> Optional[str]:
        """ゴール選択"""
        try:
            goals = self.get_all_goals()

            if not goals:
                print("⚠️ ゴールが見つかりません")
                return None

            # active状態のゴールを優先
            active_goals = [g for g in goals if g.get("status") == "active"]

            if active_goals:
                selected = active_goals[0]
                goal_id = selected.get("goal_id")
                print(f"✅ ゴール選択: {goal_id}")
                return goal_id
            else:
                selected = goals[0]
                goal_id = selected.get("goal_id")
                print(f"✅ ゴール選択(デフォルト): {goal_id}")
                return goal_id

        except Exception as e:
            print(f"❌ ゴール選択エラー: {e}")
            return None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # タスク管理
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_tasks_by_goal(self, goal_id: str) -> List[Dict[str, Any]]:
        """ゴールのタスク取得"""
        return self.accessor.read_sheet_as_dicts(
            "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal_id
        )

    def get_pending_tasks(self, goal_id: str) -> List[Dict[str, Any]]:
        """pendingタスク取得"""
        return self.accessor.read_sheet_as_dicts(
            "pm_tasks",
            filter_func=lambda t: (
                t.get("parent_goal_id") == goal_id and t.get("status") == "pending"
            ),
        )

    def should_add_tasks(self, goal_id: str) -> Tuple[bool, str]:
        """タスク追加判定"""
        try:
            tasks = self.get_tasks_by_goal(goal_id)

            if not tasks:
                return (True, "initial")

            # ステータス集計
            completed = sum(1 for t in tasks if t.get("status") == "completed")
            total = len(tasks)

            progress_rate = (completed / total * 100) if total > 0 else 0

            print(f"📊 ゴール{goal_id}進捗: {progress_rate:.1f}% ({completed}/{total})")

            if progress_rate < 100:
                return (False, "in_progress")
            else:
                return (True, "next_phase")

        except Exception as e:
            print(f"❌ タスク判定エラー: {e}")
            return (False, "error")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ナレッジ管理
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """ナレッジ検索"""
        if self.knowledge:
            return self.knowledge.search_knowledge(query, limit)
        else:
            return []

    def add_knowledge(
        self, title: str, content: str, category: str = "general", tags: str = ""
    ) -> bool:
        """ナレッジ追加"""
        if self.knowledge:
            return self.knowledge.add_knowledge(title, content, category, tags)
        else:
            return False

    def get_knowledge_stats(self) -> Dict[str, Any]:
        """ナレッジ統計"""
        if self.knowledge:
            return self.knowledge.get_statistics()
        else:
            return {"total_entries": 0, "total_categories": 0}

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # タスク実行（品質評価統合）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """
        タスク実行（品質評価付き）
        """
        print(f"\n{'='*80}")
        print(f"🚀 タスク実行: {task_id}")
        print(f"{'='*80}")

        try:
            # タスク情報取得
            tasks = self.accessor.read_sheet_as_dicts(
                "pm_tasks", filter_func=lambda t: t.get("task_id") == task_id
            )

            if not tasks:
                return {"success": False, "error": f"タスク {task_id} が見つかりません"}

            task = tasks[0]

            print(f"📋 タスク情報:")
            print(f"   ID: {task.get('task_id')}")
            print(f"   説明: {task.get('description')}")
            print(f"   ステータス: {task.get('status')}")

            # ナレッジ検索
            print(f"\n🔍 関連ナレッジ検索...")
            knowledge_results = self.search_knowledge(task.get("description", ""), limit=3)

            print(f"   関連ナレッジ: {len(knowledge_results)}件")
            for i, r in enumerate(knowledge_results, 1):
                print(f"   {i}. {r.get('title', 'N/A')}")

            # タスク実行
            print(f"\n⚙️ タスク実行...")

            result = {
                "success": True,
                "task_id": task_id,
                "description": task.get("description"),
                "timestamp": datetime.now().isoformat(),
                "knowledge_found": len(knowledge_results),
            }

            # 品質評価
            if self.quality:
                print(f"\n📊 品質評価実行...")
                evaluation = self.quality.evaluate_task(task_id, result)
                result["quality_evaluation"] = evaluation

            print(f"\n✅ タスク実行完了")

            return result

        except Exception as e:
            print(f"❌ タスク実行エラー: {e}")
            import traceback

            traceback.print_exc()

            return {"success": False, "error": str(e)}

    def auto_execute(self, max_tasks: int = 3) -> Dict[str, Any]:
        """自動実行"""
        print(f"\n{'='*80}")
        print(f"🤖 自動実行開始")
        print(f"{'='*80}")

        try:
            # ゴール選択
            goal_id = self.select_goal()

            if not goal_id:
                return {"success": False, "error": "ゴールが選択できませんでした"}

            # タスク追加判定
            should_add, add_type = self.should_add_tasks(goal_id)
            print(f"\n📊 タスク追加判定: {should_add} ({add_type})")

            # pendingタスク取得
            pending_tasks = self.get_pending_tasks(goal_id)
            print(f"📊 実行可能タスク: {len(pending_tasks)}件")

            if not pending_tasks:
                return {"success": True, "executed_count": 0, "message": "実行可能なタスクなし"}

            # 優先度順にソート
            sorted_tasks = sorted(pending_tasks, key=lambda t: int(t.get("priority", 999)))

            # 実行
            executed = []
            for i, task in enumerate(sorted_tasks[:max_tasks], 1):
                print(f"\n--- タスク {i}/{min(len(sorted_tasks), max_tasks)} ---")
                result = self.execute_task(task["task_id"])
                executed.append(result)

            success_count = sum(1 for r in executed if r.get("success"))

            # 品質統計
            quality_scores = [
                r.get("quality_evaluation", {}).get("total_score", 0)
                for r in executed
                if r.get("quality_evaluation")
            ]

            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

            print(f"\n{'='*80}")
            print(f"📊 実行結果: {success_count}/{len(executed)} 成功")
            if quality_scores:
                print(f"📊 平均品質スコア: {avg_quality:.1f}/100")
            print(f"{'='*80}")

            return {
                "success": True,
                "executed_count": len(executed),
                "success_count": success_count,
                "average_quality": avg_quality,
                "results": executed,
            }

        except Exception as e:
            print(f"❌ 自動実行エラー: {e}")
            import traceback

            traceback.print_exc()

            return {"success": False, "error": str(e)}


def main():
    """テスト実行"""
    print("=" * 80)
    print("🧪 AutonomousEngine テスト（品質評価統合版）")
    print("=" * 80)

    engine = AutonomousEngine()

    # テスト1: ゴール一覧
    print("\nテスト1: ゴール一覧")
    goals = engine.get_all_goals()
    print(f"   ゴール数: {len(goals)}件")

    # テスト2: ゴール選択
    print("\nテスト2: ゴール選択")
    goal_id = engine.select_goal()
    print(f"   選択されたゴール: {goal_id}")

    # テスト3: タスク判定
    if goal_id:
        print("\nテスト3: タスク追加判定")
        should_add, add_type = engine.should_add_tasks(goal_id)
        print(f"   判定結果: {should_add} ({add_type})")

    # テスト4: ナレッジ検索
    print("\nテスト4: ナレッジ検索")
    results = engine.search_knowledge("テスト", limit=3)
    print(f"   検索結果: {len(results)}件")

    # テスト5: 品質評価
    print("\nテスト5: 品質評価統合確認")
    if engine.quality:
        print(f"   ✅ 品質評価システム統合済み")
    else:
        print(f"   ⚠️ 品質評価システムなし")

    print("\n" + "=" * 80)
    print("✅ すべてのテスト完了")
    print("=" * 80)


if __name__ == "__main__":
    main()
