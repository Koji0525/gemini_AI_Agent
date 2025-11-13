"""
CompleteEngineWrapper
既存のCompleteEngineUltimateを拡張するラッパークラス

【設計方針】
- 既存ファイルは一切変更しない
- 継承で新機能を追加
- 既存機能は完全保護
"""

import os
import sys
from typing import Any, Dict, List, Optional, Tuple

project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.complete_engine_ultimate import CompleteEngineUltimate
from knowledge_system.simple_knowledge_wrapper import SimpleKnowledgeWrapper


class CompleteEngineWrapper(CompleteEngineUltimate):
    """
    CompleteEngine拡張版

    追加機能:
    - select_goal(): ゴール選択
    - should_add_tasks(): タスク追加判定
    - ナレッジシステム統合
    """

    def __init__(self):
        """初期化"""
        # 親クラス初期化
        super().__init__()

        # ナレッジシステム統合
        try:
            self.knowledge_wrapper = SimpleKnowledgeWrapper()
            print("✅ ナレッジシステム統合完了")
        except Exception as e:
            print(f"⚠️ ナレッジシステム初期化失敗: {e}")
            self.knowledge_wrapper = None

        print("✅ CompleteEngineWrapper 初期化完了")

    def select_goal(self) -> Optional[str]:
        """
        ゴール選択

        Returns:
            選択されたgoal_id
        """
        try:
            # project_goalシートを読み込み
            goals = self.read_sheet_as_dicts("project_goal")

            if not goals:
                print("⚠️ ゴールが見つかりません")
                return None

            # active状態のゴールを優先
            active_goals = [g for g in goals if g.get("status") == "active"]

            if active_goals:
                # 最初のactiveゴールを選択
                selected = active_goals[0]
                goal_id = selected["goal_id"]
                print(f"✅ ゴール選択: {goal_id}")
                return goal_id
            else:
                # activeがなければ最初のゴールを選択
                selected = goals[0]
                goal_id = selected["goal_id"]
                print(f"✅ ゴール選択(デフォルト): {goal_id}")
                return goal_id

        except Exception as e:
            print(f"❌ ゴール選択エラー: {e}")
            import traceback

            traceback.print_exc()
            return None

    def should_add_tasks(self, goal_id: str) -> Tuple[bool, str]:
        """
        タスク追加判定

        Args:
            goal_id: ゴールID

        Returns:
            (should_add, add_type)
        """
        try:
            # 既存タスクを取得
            tasks = self.read_sheet_as_dicts(
                "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal_id
            )

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

    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        ナレッジ検索

        Args:
            query: 検索クエリ
            limit: 取得件数

        Returns:
            検索結果
        """
        if self.knowledge_wrapper:
            return self.knowledge_wrapper.search_knowledge(query, limit)
        else:
            print("⚠️ ナレッジシステムが利用できません")
            return []

    def add_knowledge(
        self, title: str, content: str, category: str = "general", tags: str = ""
    ) -> bool:
        """
        ナレッジ追加

        Args:
            title: タイトル
            content: 内容
            category: カテゴリ
            tags: タグ

        Returns:
            成功可否
        """
        if self.knowledge_wrapper:
            return self.knowledge_wrapper.add_knowledge(title, content, category, tags)
        else:
            print("⚠️ ナレッジシステムが利用できません")
            return False

    def get_knowledge_stats(self) -> Dict[str, Any]:
        """
        ナレッジ統計取得

        Returns:
            統計情報
        """
        if self.knowledge_wrapper:
            return self.knowledge_wrapper.get_statistics()
        else:
            return {"total_entries": 0, "total_categories": 0}


def main():
    """テスト実行"""
    print("=" * 80)
    print("🧪 CompleteEngineWrapper テスト")
    print("=" * 80)

    # 初期化
    engine = CompleteEngineWrapper()

    # テスト1: ゴール選択
    print("\nテスト1: ゴール選択")
    goal_id = engine.select_goal()
    print(f"結果: {goal_id}")

    # テスト2: タスク判定
    if goal_id:
        print("\nテスト2: タスク追加判定")
        should_add, add_type = engine.should_add_tasks(goal_id)
        print(f"結果: should_add={should_add}, type={add_type}")

    # テスト3: ナレッジ検索
    print("\nテスト3: ナレッジ検索")
    results = engine.search_knowledge("テスト", limit=3)
    print(f"結果: {len(results)}件")

    # テスト4: ナレッジ統計
    print("\nテスト4: ナレッジ統計")
    stats = engine.get_knowledge_stats()
    print(f"総エントリ数: {stats.get('total_entries', 0)}件")

    # テスト5: 既存メソッド確認
    print("\nテスト5: 既存メソッド保護確認")
    tasks = engine.read_sheet_as_dicts("pm_tasks")
    print(f"✅ read_sheet_as_dicts: {len(tasks)}件")


if __name__ == "__main__":
    main()
