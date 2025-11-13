"""
完全フロー実装版システム
SYSTEM_FLOW_SPECIFICATION.mdに完全準拠
"""

import os
import sys
from typing import Tuple

project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
from tools.base_data_accessor import BaseDataAccessor


class CompleteSystemWithFlow(BaseDataAccessor):
    """完全フロー実装版システム"""

    def __init__(self, sheets_manager=None):
        super().__init__(sheets_manager)
        self.knowledge_manager = KnowledgeManager()
        self.output_dir = "/workspaces/gemini_AI_Agent/agent_outputs"
        os.makedirs(self.output_dir, exist_ok=True)

        print("✅ CompleteSystemWithFlow 初期化完了")
        print("📚 フロー定義書: SYSTEM_FLOW_SPECIFICATION.md")

    def select_goal(self) -> str:
        """ゴール選択（フロー定義書 3.1 準拠）"""
        print("\n[PHASE 1] ゴール選択")

        active_goals = self.read_sheet_as_dicts(
            "project_goal",
            filter_func=lambda g: g.get("status", "").lower() in ["active", "pending"],
        )

        if not active_goals:
            return None

        # 各ゴールのスコア計算
        goal_scores = {}

        for goal in active_goals:
            goal_id = goal.get("goal_id")
            tasks = self.read_sheet_as_dicts(
                "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal_id
            )

            pending_count = sum(1 for t in tasks if t.get("status", "").lower() == "pending")
            completed_count = sum(1 for t in tasks if t.get("status", "").lower() == "completed")
            total = len(tasks)

            score = 0

            if pending_count > 0:
                score += 1000

            if total > 0:
                progress = completed_count / total
                score += (1 - progress) * 100

            score += total * 10

            goal_scores[goal_id] = score

        selected = max(goal_scores.items(), key=lambda x: x[1])

        print(f"✅ 選択ゴール: {selected[0]} (スコア: {selected[1]:.0f})")

        return selected[0]

    def should_add_tasks(self, goal_id: str) -> Tuple[bool, str]:
        """タスク追加判定（フロー定義書 3.2 準拠）"""
        print("\n[PHASE 2] タスク状態分析")

        existing = self.read_sheet_as_dicts(
            "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal_id
        )

        if len(existing) == 0:
            print("判定: 初回タスク生成")
            return (True, "INITIAL")

        total = len(existing)
        completed = sum(1 for t in existing if t.get("status", "").lower() == "completed")
        pending = sum(1 for t in existing if t.get("status", "").lower() == "pending")
        failed = sum(1 for t in existing if t.get("status", "").lower() == "failed")

        progress = (completed / total * 100) if total > 0 else 0

        print(f"  総数: {total}, 完了: {completed}, 待機: {pending}, 失敗: {failed}")
        print(f"  進捗: {progress:.1f}%")

        if pending > 0:
            print("判定: pending存在 - 追加不要")
            return (False, "PENDING_EXISTS")

        if failed > 0:
            print("判定: 失敗タスクあり - 修正タスク追加")
            return (True, "FIX")

        if 40 <= progress < 60:
            test_exists = any("【テスト】" in t.get("description", "") for t in existing)
            if not test_exists:
                print("判定: 中間評価 - テストタスク追加")
                return (True, "TEST")

        elif 60 <= progress < 90:
            quality_exists = any("【品質改善】" in t.get("description", "") for t in existing)
            if not quality_exists:
                print("判定: 後期評価 - 品質改善タスク追加")
                return (True, "QUALITY")

        elif progress >= 90 and progress < 100:
            doc_exists = any("【ドキュメント】" in t.get("description", "") for t in existing)
            if not doc_exists:
                print("判定: 最終評価 - ドキュメントタスク追加")
                return (True, "DOCUMENTATION")

        elif progress >= 100:
            print("判定: 完全完了")
            return (False, "COMPLETED")

        print("判定: アクションなし")
        return (False, "NO_ACTION")

    async def run(self, max_cycles: int = 100):
        """メインループ実行"""
        print("\n" + "=" * 80)
        print("🚀 完全フロー実装版システム起動")
        print("=" * 80)

        for cycle in range(1, max_cycles + 1):
            print(f"\n{'='*80}")
            print(f"サイクル {cycle}")
            print(f"{'='*80}")

            # ゴール選択
            goal_id = self.select_goal()

            if not goal_id:
                print("⚠️ 処理可能なゴールなし")
                break

            # タスク追加判定
            should_add, add_type = self.should_add_tasks(goal_id)

            if should_add:
                print(f"\n[PHASE 3] タスク追加: {add_type}")
                # ここでタスク生成処理を呼ぶ

            print("\n⏳ 次のサイクルまで待機...")
            break  # デモ用に1サイクルで終了


if __name__ == "__main__":
    import asyncio

    system = CompleteSystemWithFlow()
    asyncio.run(system.run(max_cycles=1))
