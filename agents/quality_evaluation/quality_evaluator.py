"""
品質自動評価エンジン
要件定義書v4.5 F3機能の完全実装 - 軽量版
"""

import sys

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from tools.base_data_accessor import BaseDataAccessor


class QualityEvaluator(BaseDataAccessor):
    """品質自動評価エンジン（軽量版）"""

    def __init__(self):
        super().__init__()

        # 品質基準の定義
        self.quality_standards = {
            "excellent": {"min_score": 9.0, "color": "🟢"},
            "good": {"min_score": 7.5, "color": "🟡"},
            "acceptable": {"min_score": 6.0, "color": "🟠"},
            "poor": {"min_score": 0.0, "color": "🔴"},
        }

    def evaluate_task_quality(self, task_result: dict) -> dict:
        """
        タスク品質の自動評価（軽量版）

        Args:
            task_result: タスク実行結果

        Returns:
            品質評価結果
        """
        print("=" * 50)
        print("🧪 品質自動評価（軽量版）")
        print("=" * 50)

        # 基本評価項目のチェック
        basic_checks = self._perform_basic_checks(task_result)

        # 品質スコアの計算
        final_score = self._calculate_quality_score(basic_checks)

        # 改善提案の生成
        improvement_suggestions = self._generate_improvement_suggestions(final_score, basic_checks)

        # 評価結果の統合
        evaluation_result = {
            "timestamp": self._get_current_timestamp(),
            "task_id": task_result.get("task_id", "unknown"),
            "quality_score": final_score,
            "quality_level": self._get_quality_level(final_score),
            "basic_checks": basic_checks,
            "improvement_suggestions": improvement_suggestions,
            "passed": final_score >= 6.0,  # 合格基準
        }

        print(f"✅ 品質評価完了: スコア {final_score:.1f}/10.0")
        print(f"�� 品質レベル: {evaluation_result['quality_level']}")

        return evaluation_result

    def _perform_basic_checks(self, task_result: dict) -> dict:
        """基本チェック項目の実行"""

        checks = {
            "output_exists": bool(task_result.get("output_file")),
            "output_readable": self._check_file_readability(task_result.get("output_file", "")),
            "execution_time_reasonable": self._check_execution_time(
                task_result.get("elapsed_time", 0)
            ),
            "error_free": not task_result.get("error_occurred", False),
            "completeness": self._assess_completeness(task_result),
            "description_quality": self._assess_description_quality(task_result),
        }

        # 基本スコア計算
        passed_checks = sum(checks.values())
        total_checks = len(checks)
        checks["score"] = (passed_checks / total_checks) * 10.0
        checks["passed_checks"] = passed_checks
        checks["total_checks"] = total_checks

        print(f"📋 基本チェック: {passed_checks}/{total_checks} 合格")

        return checks

    def _calculate_quality_score(self, basic_checks: dict) -> float:
        """品質スコアの計算"""
        base_score = basic_checks.get("score", 0)

        # 追加ボーナスポイント
        bonus_points = 0

        # すべてのチェックが合格ならボーナス
        if basic_checks.get("passed_checks", 0) == basic_checks.get("total_checks", 0):
            bonus_points += 1.0

        # 実行時間が優秀ならボーナス
        if basic_checks.get("execution_time_reasonable", False):
            bonus_points += 0.5

        final_score = min(10.0, base_score + bonus_points)
        return round(final_score, 1)

    def _generate_improvement_suggestions(self, final_score: float, basic_checks: dict) -> list:
        """改善提案の生成"""
        suggestions = []

        # スコアに基づく基本的な提案
        if final_score < 6.0:
            suggestions.append("🔴 根本的な改善が必要: タスクの再設計を検討")
        elif final_score < 7.5:
            suggestions.append("🟡 中程度の改善推奨: 実行プロセスの見直し")
        elif final_score < 9.0:
            suggestions.append("🟢 軽微な改善: 品質維持のための微調整")
        else:
            suggestions.append("💎 優れた品質: ベストプラクティスとして記録")

        # 基本チェックに基づく具体的な提案
        if not basic_checks["output_exists"]:
            suggestions.append("📝 出力ファイルの生成を確認")
        if not basic_checks["execution_time_reasonable"]:
            suggestions.append("⏱️ 実行時間の最適化を検討")
        if not basic_checks["completeness"]:
            suggestions.append("🎯 タスク完了基準の明確化")
        if not basic_checks["description_quality"]:
            suggestions.append("📋 タスク説明の詳細化")

        return suggestions

    def _check_file_readability(self, file_path: str) -> bool:
        """ファイルの可読性チェック"""
        import os

        if not file_path:
            return False
        return os.path.exists(file_path) and os.path.getsize(file_path) > 0

    def _check_execution_time(self, elapsed_time: float) -> bool:
        """実行時間の合理性チェック"""
        # 30分以上は非合理的と判断
        return elapsed_time < 1800  # 30分

    def _assess_completeness(self, task_result: dict) -> bool:
        """完了度の評価"""
        task_result.get("task_description", "").lower()
        output = task_result.get("output_summary", "").lower()

        # 簡単なキーワードマッチングによる完了度評価
        key_phrases = ["完了", "終了", "完成", "実装済み", "テスト済み", "success", "completed"]
        return any(phrase in output for phrase in key_phrases)

    def _assess_description_quality(self, task_result: dict) -> bool:
        """説明文の品質評価"""
        description = task_result.get("task_description", "")

        # 説明文が存在し、十分な長さがあるか
        if not description:
            return False

        # 最低文字数チェック
        if len(description.strip()) < 10:
            return False

        return True

    def _get_quality_level(self, score: float) -> str:
        """品質レベルの判定"""
        if score >= 9.0:
            return "優秀"
        elif score >= 7.5:
            return "良好"
        elif score >= 6.0:
            return "合格"
        else:
            return "要改善"

    def _get_current_timestamp(self):
        """現在のタイムスタンプ取得"""
        from datetime import datetime

        return datetime.now().isoformat()


# テスト用
if __name__ == "__main__":
    evaluator = QualityEvaluator()

    # テスト用タスク結果
    test_result = {
        "task_id": "test_001",
        "task_description": "サンプルタスクの実行と品質評価のテスト",
        "output_file": "agent_outputs/test_output.txt",
        "output_summary": "タスクが正常に完了しました。すべてのテストにパスしました。",
        "elapsed_time": 120.5,
        "error_occurred": False,
    }

    evaluation = evaluator.evaluate_task_quality(test_result)
    print(f"評価結果: {evaluation}")
