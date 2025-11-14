"""
強化版品質自動評価エンジン
要件定義書v4.5 F3機能を40%→80%に強化
既存のReviewAgentと連携
"""

import sys

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
from tools.base_data_accessor import BaseDataAccessor


class EnhancedQualityEvaluator(BaseDataAccessor):
    """強化版品質評価エンジン"""

    def __init__(self, sheets_manager=None):
        super().__init__(sheets_manager)
        self.knowledge_manager = KnowledgeManager()

        # 評価基準の定義
        self.evaluation_criteria = {
            "completeness": {
                "weight": 0.2,
                "threshold": 0.8,
                "description": "タスクの完了度と包括性",
            },
            "accuracy": {"weight": 0.25, "threshold": 0.9, "description": "出力の正確性と信頼性"},
            "efficiency": {
                "weight": 0.15,
                "threshold": 0.7,
                "description": "実行効率とリソース使用",
            },
            "maintainability": {
                "weight": 0.2,
                "threshold": 0.8,
                "description": "コードの保守性と拡張性",
            },
            "usability": {
                "weight": 0.2,
                "threshold": 0.7,
                "description": "使いやすさとユーザビリティ",
            },
        }

    def comprehensive_quality_evaluation(self, task_result: dict, task_data: dict) -> dict:
        """
        包括的品質評価の実行

        Args:
            task_result: タスク実行結果
            task_data: タスクデータ

        Returns:
            品質評価結果
        """
        print("🧪 強化版品質評価実行")

        # 詳細評価の実施
        detailed_scores = {}
        for criterion, config in self.evaluation_criteria.items():
            score = self._evaluate_single_criterion(criterion, task_result, task_data)
            detailed_scores[criterion] = {
                "score": score,
                "weight": config["weight"],
                "threshold": config["threshold"],
                "passed": score >= config["threshold"],
                "description": config["description"],
            }

        # 総合スコア計算
        total_score = sum(detail["score"] * detail["weight"] for detail in detailed_scores.values())

        # 改善提案の生成
        improvements = self._generate_improvement_suggestions(detailed_scores)

        # 品質レベル判定
        quality_level = self._determine_quality_level(total_score)

        # ナレッジ蓄積用データ準備
        knowledge_data = self._prepare_knowledge_data(
            task_data, total_score, detailed_scores, improvements
        )

        return {
            "total_score": round(total_score * 10, 2),  # 10点満点に変換
            "quality_level": quality_level,
            "detailed_scores": detailed_scores,
            "improvements": improvements,
            "overall_passed": all(detail["passed"] for detail in detailed_scores.values()),
            "knowledge_data": knowledge_data,
        }

    def _evaluate_single_criterion(
        self, criterion: str, task_result: dict, task_data: dict
    ) -> float:
        """個別評価基準の評価"""

        if criterion == "completeness":
            return self._evaluate_completeness(task_result, task_data)
        elif criterion == "accuracy":
            return self._evaluate_accuracy(task_result, task_data)
        elif criterion == "efficiency":
            return self._evaluate_efficiency(task_result, task_data)
        elif criterion == "maintainability":
            return self._evaluate_maintainability(task_result, task_data)
        elif criterion == "usability":
            return self._evaluate_usability(task_result, task_data)
        else:
            return 0.5  # デフォルト値

    def _evaluate_completeness(self, task_result: dict, task_data: dict) -> float:
        """完了度の評価"""
        score = 0.5  # ベーススコア

        # 出力の存在チェック
        if task_result.get("output"):
            score += 0.2

        # 出力の詳細度チェック
        output = task_result.get("output", "")
        if len(output) > 100:  # 十分な内容がある
            score += 0.2

        # タスク要件の満たし度
        if task_result.get("requirements_met", True):
            score += 0.1

        return min(score, 1.0)  # 最大1.0

    def _evaluate_accuracy(self, task_result: dict, task_data: dict) -> float:
        """正確性の評価"""
        score = 0.6  # ベーススコア

        # エラーチェック
        if not task_result.get("error"):
            score += 0.2

        # 出力の一貫性チェック
        output = task_result.get("output", "")
        if "error" not in output.lower() and "fail" not in output.lower():
            score += 0.1

        # 期待される出力形式の一致
        if task_result.get("output_format_correct", True):
            score += 0.1

        return min(score, 1.0)

    def _evaluate_efficiency(self, task_result: dict, task_data: dict) -> float:
        """効率性の評価"""
        score = 0.7  # ベーススコア

        # 実行時間の評価
        execution_time = task_result.get("execution_time", 0)
        if execution_time < 5:  # 5秒以内
            score += 0.2
        elif execution_time < 10:  # 10秒以内
            score += 0.1

        # リソース使用量
        if task_result.get("resource_efficient", True):
            score += 0.1

        return min(score, 1.0)

    def _evaluate_maintainability(self, task_result: dict, task_data: dict) -> float:
        """保守性の評価"""
        score = 0.5  # ベーススコア

        # コード構造の評価
        output = task_result.get("output", "")
        if "def " in output or "class " in output:  # 関数やクラス定義がある
            score += 0.3

        # ドキュメントの存在
        if "説明" in output or "document" in output.lower():
            score += 0.2

        return min(score, 1.0)

    def _evaluate_usability(self, task_result: dict, task_data: dict) -> float:
        """使いやすさの評価"""
        score = 0.6  # ベーススコア

        # 出力の明確さ
        output = task_result.get("output", "")
        if len(output.split("\n")) > 3:  # 複数行に分かれている
            score += 0.2

        # 具体性
        if "具体" in output or "example" in output.lower():
            score += 0.2

        return min(score, 1.0)

    def _generate_improvement_suggestions(self, detailed_scores: dict) -> list:
        """改善提案の生成"""
        improvements = []

        for criterion, data in detailed_scores.items():
            if not data["passed"]:
                suggestion = {
                    "criterion": criterion,
                    "current_score": data["score"],
                    "required_score": data["threshold"],
                    "suggestion": self._get_criterion_suggestion(criterion),
                    "priority": "high" if data["score"] < 0.5 else "medium",
                }
                improvements.append(suggestion)

        return improvements

    def _get_criterion_suggestion(self, criterion: str) -> str:
        """評価基準に基づく改善提案"""
        suggestions = {
            "completeness": "必要な機能や項目が全て実装されているか確認し、不足を補ってください",
            "accuracy": "出力結果の正確性を検証し、誤りや不正確な情報を修正してください",
            "efficiency": "処理時間やリソース使用量を最適化し、効率的な実装を心がけてください",
            "maintainability": "コードの可読性と保守性を高めるため、適切な構造化とドキュメント化を行ってください",
            "usability": "ユーザーが理解しやすく使いやすい出力形式を心がけてください",
        }
        return suggestions.get(criterion, "品質改善が必要です")

    def _determine_quality_level(self, total_score: float) -> str:
        """品質レベルの判定"""
        if total_score >= 0.9:
            return "優秀 (Excellent)"
        elif total_score >= 0.8:
            return "良好 (Good)"
        elif total_score >= 0.7:
            return "標準 (Average)"
        elif total_score >= 0.6:
            return "要改善 (Needs Improvement)"
        else:
            return "不良 (Poor)"

    def _prepare_knowledge_data(
        self, task_data: dict, total_score: float, detailed_scores: dict, improvements: list
    ) -> dict:
        """ナレッジ蓄積用データの準備"""
        return {
            "task_id": task_data.get("task_id", "unknown"),
            "task_description": task_data.get("description", ""),
            "quality_score": total_score,
            "evaluation_details": detailed_scores,
            "improvement_needed": len(improvements) > 0,
            "improvement_count": len(improvements),
        }


# テストコード
if __name__ == "__main__":
    print("🧪 強化版品質評価エンジンテスト")

    evaluator = EnhancedQualityEvaluator()

    # テストデータ
    test_task_result = {
        "output": 'サンプル出力です。これはテスト用の出力です。\n具体的な内容を含んでいます。\nコード例: def example(): return "Hello"',
        "execution_time": 3.2,
        "error": None,
        "requirements_met": True,
        "output_format_correct": True,
        "resource_efficient": True,
    }

    test_task_data = {"task_id": "test_task_001", "description": "テストタスクの説明"}

    result = evaluator.comprehensive_quality_evaluation(test_task_result, test_task_data)

    print(f"総合スコア: {result['total_score']}/10.0")
    print(f"品質レベル: {result['quality_level']}")
    print(f"合格状況: {'✅ 合格' if result['overall_passed'] else '❌ 不合格'}")
    print(f"改善提案: {len(result['improvements'])}件")

    for imp in result["improvements"]:
        print(f"  - {imp['criterion']}: {imp['suggestion']}")
