"""
QualityEvaluator
品質自動評価機能

【機能】
- タスク実行結果の品質評価
- 自動改善提案
- 品質メトリクスの記録
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.base_data_accessor import BaseDataAccessor


class QualityEvaluator:
    """品質自動評価機能"""

    def __init__(self):
        """初期化"""
        self.accessor = BaseDataAccessor()

        # 評価基準
        self.criteria = {
            "completion": {"weight": 0.4, "description": "完了度"},
            "accuracy": {"weight": 0.3, "description": "正確性"},
            "efficiency": {"weight": 0.2, "description": "効率性"},
            "maintainability": {"weight": 0.1, "description": "保守性"},
        }

        print("✅ QualityEvaluator 初期化完了")

    def evaluate_task(self, task_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスクの品質評価

        Args:
            task_id: タスクID
            result: タスク実行結果

        Returns:
            評価結果
        """
        print(f"\n{'='*80}")
        print(f"🎯 品質評価: {task_id}")
        print(f"{'='*80}")

        try:
            # タスク情報取得
            tasks = self.accessor.read_sheet_as_dicts(
                "pm_tasks", filter_func=lambda t: t.get("task_id") == task_id
            )

            if not tasks:
                return {"success": False, "error": f"タスク {task_id} が見つかりません"}

            task = tasks[0]

            # 各基準で評価
            scores = {}

            # 1. 完了度
            completion_score = self._evaluate_completion(task, result)
            scores["completion"] = completion_score

            # 2. 正確性
            accuracy_score = self._evaluate_accuracy(task, result)
            scores["accuracy"] = accuracy_score

            # 3. 効率性
            efficiency_score = self._evaluate_efficiency(task, result)
            scores["efficiency"] = efficiency_score

            # 4. 保守性
            maintainability_score = self._evaluate_maintainability(task, result)
            scores["maintainability"] = maintainability_score

            # 総合スコア計算
            total_score = sum(scores[key] * self.criteria[key]["weight"] for key in scores)

            # 評価結果
            evaluation = {
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                "scores": scores,
                "total_score": total_score,
                "grade": self._get_grade(total_score),
                "suggestions": self._generate_suggestions(scores),
            }

            # 結果表示
            print(f"\n📊 評価結果:")
            print(f"   総合スコア: {total_score:.1f}/100")
            print(f"   評価: {evaluation['grade']}")

            print(f"\n📋 詳細スコア:")
            for key, score in scores.items():
                desc = self.criteria[key]["description"]
                print(f"   {desc}: {score:.1f}/100")

            if evaluation["suggestions"]:
                print(f"\n💡 改善提案:")
                for i, suggestion in enumerate(evaluation["suggestions"], 1):
                    print(f"   {i}. {suggestion}")

            return evaluation

        except Exception as e:
            print(f"❌ 品質評価エラー: {e}")
            import traceback

            traceback.print_exc()

            return {"success": False, "error": str(e)}

    def _evaluate_completion(self, task: Dict[str, Any], result: Dict[str, Any]) -> float:
        """完了度評価"""
        if result.get("success"):
            return 100.0
        else:
            return 50.0

    def _evaluate_accuracy(self, task: Dict[str, Any], result: Dict[str, Any]) -> float:
        """正確性評価"""
        # 現在は基本的な評価
        if result.get("success"):
            # エラーがなければ高評価
            if not result.get("error"):
                return 90.0
            else:
                return 70.0
        else:
            return 50.0

    def _evaluate_efficiency(self, task: Dict[str, Any], result: Dict[str, Any]) -> float:
        """効率性評価"""
        # ナレッジ活用度で評価
        knowledge_found = result.get("knowledge_found", 0)

        if knowledge_found > 3:
            return 90.0
        elif knowledge_found > 0:
            return 70.0
        else:
            return 50.0

    def _evaluate_maintainability(self, task: Dict[str, Any], result: Dict[str, Any]) -> float:
        """保守性評価"""
        # 現在は基本評価
        return 80.0

    def _get_grade(self, score: float) -> str:
        """スコアから評価を取得"""
        if score >= 90:
            return "S (優秀)"
        elif score >= 80:
            return "A (良好)"
        elif score >= 70:
            return "B (普通)"
        elif score >= 60:
            return "C (要改善)"
        else:
            return "D (不可)"

    def _generate_suggestions(self, scores: Dict[str, float]) -> List[str]:
        """改善提案生成"""
        suggestions = []

        for key, score in scores.items():
            if score < 70:
                desc = self.criteria[key]["description"]

                if key == "completion":
                    suggestions.append(f"{desc}を向上: タスクの完全実行を目指す")
                elif key == "accuracy":
                    suggestions.append(f"{desc}を向上: エラーハンドリングの強化")
                elif key == "efficiency":
                    suggestions.append(f"{desc}を向上: ナレッジの活用を増やす")
                elif key == "maintainability":
                    suggestions.append(f"{desc}を向上: ドキュメント化を充実")

        return suggestions

    def get_quality_history(self, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """品質評価履歴取得"""
        # 現在は基本実装
        return []


def main():
    """テスト実行"""
    print("=" * 80)
    print("🧪 QualityEvaluator テスト")
    print("=" * 80)

    evaluator = QualityEvaluator()

    # テスト用の結果データ
    test_result = {
        "success": True,
        "task_id": "test-001",
        "description": "テストタスク",
        "knowledge_found": 3,
    }

    # 品質評価実行
    evaluator.evaluate_task("test-001", test_result)

    print("\n" + "=" * 80)
    print("✅ テスト完了")
    print("=" * 80)


if __name__ == "__main__":
    main()
