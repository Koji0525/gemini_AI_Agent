"""
動的タスク追加機能の強化
要件定義書v4.5 F6機能を60%→90%に強化
既存システムと連携
"""

import sys

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

import random
from datetime import datetime

from tools.base_data_accessor import BaseDataAccessor


class DynamicTaskEnhancer(BaseDataAccessor):
    """強化版動的タスク追加"""

    def __init__(self, sheets_manager=None):
        super().__init__(sheets_manager)
        self.task_templates = self._load_task_templates()

    def _load_task_templates(self) -> dict:
        """タスクテンプレートの読み込み"""
        return {
            "quality_improvement": {
                "description": "品質改善タスク: {aspect}の向上",
                "required_role": "品質保証",
                "priority": "high",
                "estimated_time": "2時間",
                "execution_type": "改善",
            },
            "testing": {
                "description": "テスト実施: {component}の検証",
                "required_role": "テスター",
                "priority": "medium",
                "estimated_time": "1時間",
                "execution_type": "テスト",
            },
            "documentation": {
                "description": "ドキュメント作成: {topic}の文書化",
                "required_role": "技術文書",
                "priority": "medium",
                "estimated_time": "1.5時間",
                "execution_type": "ドキュメント",
            },
            "optimization": {
                "description": "最適化タスク: {area}のパフォーマンス改善",
                "required_role": "パフォーマンス",
                "priority": "medium",
                "estimated_time": "3時間",
                "execution_type": "最適化",
            },
        }

    def should_add_tasks(self, goal_id: str) -> bool:
        """
        タスク追加が必要か判定

        Args:
            goal_id: ゴールID

        Returns:
            タスク追加が必要な場合はTrue
        """
        print(f"🔍 ゴール {goal_id} のタスク追加必要性を判定")

        # 現在のタスク状況を取得
        tasks = self.read_sheet_as_dicts(
            "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal_id
        )

        if not tasks:
            print("  ⚠️ ゴールに紐づくタスクがありません。タスク追加が必要です")
            return True

        # 保留中タスクの数をカウント
        pending_tasks = [t for t in tasks if t.get("status") == "pending"]
        completed_tasks = [t for t in tasks if t.get("status") == "completed"]

        print(f"  📊 タスク状況: 保留中 {len(pending_tasks)}件, 完了 {len(completed_tasks)}件")

        # 判定ロジック
        if len(pending_tasks) == 0:
            # 保留中タスクがなく、完了タスクがある場合は追加検討
            completion_rate = len(completed_tasks) / len(tasks)
            if completion_rate >= 0.7:  # 70%以上完了
                print("  ✅ タスク追加が必要: 高完了率かつ保留中タスクなし")
                return True

        print("  ⏭️ タスク追加は不要")
        return False

    def generate_additional_tasks(self, goal_id: str, goal_description: str) -> list:
        """
        追加タスクの生成

        Args:
            goal_id: ゴールID
            goal_description: ゴール説明

        Returns:
            生成されたタスクリスト
        """
        print(f"🎯 ゴール {goal_id} の追加タスクを生成")

        additional_tasks = []

        # ゴールに基づいて適切なタスクタイプを選択
        task_types = self._select_task_types(goal_description)

        for i, task_type in enumerate(task_types):
            task_data = self._create_task_data(goal_id, goal_description, task_type, i + 1)
            additional_tasks.append(task_data)

        print(f"  ✅ {len(additional_tasks)}件の追加タスクを生成")
        return additional_tasks

    def _select_task_types(self, goal_description: str) -> list:
        """ゴール説明に基づくタスクタイプの選択"""
        goal_lower = goal_description.lower()
        selected_types = []

        # キーワードに基づくタスクタイプ選択
        if any(word in goal_lower for word in ["品質", "改善", "向上"]):
            selected_types.append("quality_improvement")

        if any(word in goal_lower for word in ["テスト", "検証", "確認"]):
            selected_types.append("testing")

        if any(word in goal_lower for word in ["文書", "ドキュメント", "説明"]):
            selected_types.append("documentation")

        if any(word in goal_lower for word in ["最適化", "効率", "パフォーマンス"]):
            selected_types.append("optimization")

        # デフォルトタスク
        if not selected_types:
            selected_types = ["quality_improvement", "testing"]

        return selected_types

    def _create_task_data(
        self, goal_id: str, goal_description: str, task_type: str, sequence: int
    ) -> dict:
        """タスクデータの作成"""
        template = self.task_templates.get(task_type, self.task_templates["quality_improvement"])

        # タスク説明のカスタマイズ
        aspect = self._get_task_aspect(goal_description, task_type)
        description = template["description"].format(
            aspect=aspect, component=aspect, topic=aspect, area=aspect
        )

        task_id = f"{goal_id}_dynamic_{task_type}_{sequence}"

        return {
            "task_id": task_id,
            "parent_goal_id": goal_id,
            "description": description,
            "required_role": template["required_role"],
            "status": "pending",
            "priority": template["priority"],
            "estimated_time": template["estimated_time"],
            "dependencies": "",
            "created_at": datetime.now().isoformat(),
            "batch_id": f"dynamic_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "detail_file_path": "",
            "blank": "",
            "execution_type": template["execution_type"],
        }

    def _get_task_aspect(self, goal_description: str, task_type: str) -> str:
        """タスクの側面を取得"""
        aspects = {
            "quality_improvement": [
                "コード品質",
                "テストカバレッジ",
                "パフォーマンス",
                "セキュリティ",
            ],
            "testing": ["ユニットテスト", "統合テスト", "システムテスト", "回帰テスト"],
            "documentation": ["APIドキュメント", "ユーザーガイド", "設計書", "チュートリアル"],
            "optimization": ["データベース", "アルゴリズム", "メモリ使用", "応答時間"],
        }

        available_aspects = aspects.get(task_type, aspects["quality_improvement"])
        return random.choice(available_aspects)


# テストコード
if __name__ == "__main__":
    print("🧪 強化版動的タスク追加テスト")

    enhancer = DynamicTaskEnhancer()

    # テストゴール
    test_goal_id = "test_goal_001"
    test_goal_description = "システムの品質向上とテスト自動化の実現"

    # タスク追加必要性の判定
    should_add = enhancer.should_add_tasks(test_goal_id)
    print(f"タスク追加必要性: {should_add}")

    if should_add:
        tasks = enhancer.generate_additional_tasks(test_goal_id, test_goal_description)
        print(f"生成されたタスク: {len(tasks)}件")
        for task in tasks:
            print(f"  - {task['description']}")
