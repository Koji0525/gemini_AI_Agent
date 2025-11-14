"""
強化版品質自動評価エンジン
要件定義書v4.5 F3機能の完全実装 - レビューエージェント統合版
"""

import sys

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from tools.base_data_accessor import BaseDataAccessor


class QualityEvaluatorEnhanced(BaseDataAccessor):
    """強化版品質自動評価エンジン"""

    def __init__(self):
        super().__init__()

        # 品質基準の定義
        self.quality_standards = {
            "excellent": {"min_score": 9.0, "color": "🟢", "reward": 2.0},
            "good": {"min_score": 7.5, "color": "🟡", "reward": 1.0},
            "acceptable": {"min_score": 6.0, "color": "🟠", "reward": 0.5},
            "poor": {"min_score": 0.0, "color": "🔴", "reward": 0.0},
        }

        # レビュー基準
        self.review_criteria = {
            "completeness": {"weight": 0.3, "description": "タスク完了度"},
            "accuracy": {"weight": 0.25, "description": "正確性"},
            "efficiency": {"weight": 0.2, "description": "効率性"},
            "maintainability": {"weight": 0.15, "description": "保守性"},
            "documentation": {"weight": 0.1, "description": "ドキュメント品質"},
        }

    def evaluate_task_quality(self, task_result: dict) -> dict:
        """
        タスク品質の包括的評価

        Args:
            task_result: タスク実行結果

        Returns:
            品質評価結果
        """
        print("=" * 60)
        print("🧪 強化版品質自動評価")
        print("=" * 60)

        # 多段階評価の実施
        basic_checks = self._perform_comprehensive_checks(task_result)
        review_evaluation = self._perform_review_evaluation(task_result)
        historical_comparison = self._compare_with_historical_data(task_result)

        # 総合スコア計算
        final_score = self._calculate_comprehensive_score(
            basic_checks, review_evaluation, historical_comparison
        )

        # 詳細な改善提案
        improvement_plan = self._generate_detailed_improvement_plan(
            final_score, basic_checks, review_evaluation
        )

        # 評価結果の統合
        evaluation_result = {
            "timestamp": self._get_current_timestamp(),
            "task_id": task_result.get("task_id", "unknown"),
            "quality_score": final_score,
            "quality_level": self._get_quality_level(final_score),
            "basic_checks": basic_checks,
            "review_evaluation": review_evaluation,
            "historical_comparison": historical_comparison,
            "improvement_plan": improvement_plan,
            "passed": final_score >= 6.0,
            "needs_improvement": final_score < 7.5,
            "excellent_quality": final_score >= 9.0,
        }

        self._print_evaluation_summary(evaluation_result)
        return evaluation_result

    def _perform_comprehensive_checks(self, task_result: dict) -> dict:
        """包括的基本チェック"""

        checks = {
            "output_exists": bool(task_result.get("output_file")),
            "output_readable": self._check_file_readability(task_result.get("output_file", "")),
            "execution_time_optimal": self._check_execution_time_optimal(
                task_result.get("elapsed_time", 0)
            ),
            "error_free": not task_result.get("error_occurred", False),
            "completeness_high": self._assess_comprehensive_completeness(task_result),
            "description_quality_high": self._assess_detailed_description_quality(task_result),
            "output_structure_good": self._assess_output_structure(task_result),
            "code_quality_present": self._check_code_quality_indicators(task_result),
        }

        # 詳細スコア計算
        passed_checks = sum(checks.values())
        total_checks = len(checks)
        checks["score"] = (passed_checks / total_checks) * 10.0
        checks["passed_checks"] = passed_checks
        checks["total_checks"] = total_checks
        checks["completion_rate"] = (passed_checks / total_checks) * 100

        print(
            f"�� 包括的基本チェック: {passed_checks}/{total_checks} 合格 ({checks['completion_rate']:.1f}%)"
        )

        return checks

    def _perform_review_evaluation(self, task_result: dict) -> dict:
        """レビュー評価の実施"""
        review_scores = {}
        total_weight = 0
        weighted_score = 0

        for criterion, config in self.review_criteria.items():
            # 各基準に対するスコア評価 (0-10)
            criterion_score = self._evaluate_criterion(criterion, task_result)
            review_scores[criterion] = {
                "score": criterion_score,
                "weight": config["weight"],
                "description": config["description"],
                "weighted_score": criterion_score * config["weight"],
            }

            weighted_score += criterion_score * config["weight"]
            total_weight += config["weight"]

        # 正規化されたレビュースコア
        normalized_score = (weighted_score / total_weight) * 10.0 if total_weight > 0 else 0

        review_evaluation = {
            "scores": review_scores,
            "total_weighted_score": weighted_score,
            "normalized_score": round(normalized_score, 2),
            "overall_review": self._generate_review_summary(review_scores),
        }

        print(f"🔍 レビュー評価: {normalized_score:.1f}/10.0")

        return review_evaluation

    def _evaluate_criterion(self, criterion: str, task_result: dict) -> float:
        """個別基準の評価"""
        if criterion == "completeness":
            return self._evaluate_completeness(task_result)
        elif criterion == "accuracy":
            return self._evaluate_accuracy(task_result)
        elif criterion == "efficiency":
            return self._evaluate_efficiency(task_result)
        elif criterion == "maintainability":
            return self._evaluate_maintainability(task_result)
        elif criterion == "documentation":
            return self._evaluate_documentation(task_result)
        else:
            return 5.0  # デフォルトスコア

    def _evaluate_completeness(self, task_result: dict) -> float:
        """完了度の評価"""
        task_result.get("task_description", "").lower()
        output = task_result.get("output_summary", "").lower()

        score = 5.0  # ベーススコア

        # 完了を示すキーワード
        completion_keywords = [
            "完了",
            "終了",
            "完成",
            "実装済み",
            "テスト済み",
            "success",
            "completed",
            "done",
        ]
        if any(keyword in output for keyword in completion_keywords):
            score += 3.0

        # 詳細な出力があるか
        if len(output.strip()) > 50:
            score += 1.0

        # 出力ファイルが存在するか
        if task_result.get("output_file") and self._check_file_readability(
            task_result.get("output_file")
        ):
            score += 1.0

        return min(10.0, score)

    def _evaluate_accuracy(self, task_result: dict) -> float:
        """正確性の評価"""
        score = 6.0  # ベーススコア

        # エラーがないか
        if not task_result.get("error_occurred", False):
            score += 2.0

        # 実行時間が適切か
        elapsed_time = task_result.get("elapsed_time", 0)
        if 0 < elapsed_time < 300:  # 5分以内
            score += 1.0
        elif elapsed_time >= 300:
            score -= 1.0

        # 出力の一貫性
        output = task_result.get("output_summary", "")
        if output and len(output) > 10:
            score += 1.0

        return min(10.0, max(0.0, score))

    def _evaluate_efficiency(self, task_result: dict) -> float:
        """効率性の評価"""
        elapsed_time = task_result.get("elapsed_time", 0)

        if elapsed_time == 0:
            return 5.0

        # 実行時間に基づく効率性評価
        if elapsed_time < 10:
            return 9.0
        elif elapsed_time < 30:
            return 8.0
        elif elapsed_time < 60:
            return 7.0
        elif elapsed_time < 180:
            return 6.0
        elif elapsed_time < 300:
            return 5.0
        else:
            return 3.0

    def _evaluate_maintainability(self, task_result: dict) -> float:
        """保守性の評価"""
        score = 5.0

        # 出力ファイルの構造チェック
        output_file = task_result.get("output_file")
        if output_file and self._check_file_readability(output_file):
            try:
                with open(output_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # コードの構造化指標
                if "def " in content or "class " in content:
                    score += 2.0  # 関数やクラスがある

                if "import " in content or "from " in content:
                    score += 1.0  # インポートがある

                if "TODO" not in content and "FIXME" not in content:
                    score += 1.0  # TODO/FIXMEがない

                if len(content.split("\n")) > 5:
                    score += 1.0  # 十分な内容量

            except:
                pass

        return min(10.0, score)

    def _evaluate_documentation(self, task_result: dict) -> float:
        """ドキュメント品質の評価"""
        score = 5.0

        description = task_result.get("task_description", "")
        output = task_result.get("output_summary", "")

        # 説明文の品質
        if len(description.strip()) > 20:
            score += 2.0

        # 出力サマリーの品質
        if len(output.strip()) > 30:
            score += 2.0

        # 構造化された出力
        if any(marker in output for marker in ["##", "===", "---", "•", "- "]):
            score += 1.0

        return min(10.0, score)

    def _compare_with_historical_data(self, task_result: dict) -> dict:
        """過去データとの比較"""
        try:
            # 類似タスクの検索（簡易版）
            tasks = self.read_sheet_as_dicts("pm_tasks")
            similar_tasks = [
                t
                for t in tasks
                if t.get("parent_goal_id") == task_result.get("parent_goal_id")
                and t.get("status") == "completed"
            ]

            if not similar_tasks:
                return {
                    "comparison_score": 5.0,
                    "similar_tasks_count": 0,
                    "message": "比較対象となる過去タスクがありません",
                }

            # 平均実行時間の計算
            avg_execution_time = self._calculate_average_execution_time(similar_tasks)
            current_time = task_result.get("elapsed_time", 0)

            # 比較スコア
            if avg_execution_time > 0:
                time_ratio = current_time / avg_execution_time
                if time_ratio < 0.7:
                    time_score = 9.0
                elif time_ratio < 0.9:
                    time_score = 8.0
                elif time_ratio < 1.1:
                    time_score = 7.0
                elif time_ratio < 1.3:
                    time_score = 6.0
                else:
                    time_score = 4.0
            else:
                time_score = 7.0

            return {
                "comparison_score": time_score,
                "similar_tasks_count": len(similar_tasks),
                "average_execution_time": avg_execution_time,
                "current_execution_time": current_time,
                "time_ratio": time_ratio if avg_execution_time > 0 else 1.0,
                "message": f"過去{len(similar_tasks)}件の類似タスクと比較",
            }

        except Exception as e:
            return {
                "comparison_score": 5.0,
                "error": str(e),
                "message": "過去データ比較でエラーが発生しました",
            }

    def _calculate_comprehensive_score(
        self, basic_checks: dict, review_evaluation: dict, historical_comparison: dict
    ) -> float:
        """総合スコア計算"""
        weights = {"basic_checks": 0.4, "review_evaluation": 0.4, "historical_comparison": 0.2}

        basic_score = basic_checks.get("score", 0)
        review_score = review_evaluation.get("normalized_score", 5.0)
        historical_score = historical_comparison.get("comparison_score", 5.0)

        weighted_score = (
            basic_score * weights["basic_checks"]
            + review_score * weights["review_evaluation"]
            + historical_score * weights["historical_comparison"]
        )

        # ボーナスポイント
        bonus = 0

        if basic_checks.get("passed_checks", 0) == basic_checks.get("total_checks", 0):
            bonus += 0.5  # すべての基本チェック合格

        if review_score >= 8.0:
            bonus += 0.3  # 高レビュースコア

        if historical_score >= 8.0:
            bonus += 0.2  # 過去比較で優秀

        final_score = min(10.0, weighted_score + bonus)
        return round(final_score, 2)

    def _generate_detailed_improvement_plan(
        self, final_score: float, basic_checks: dict, review_evaluation: dict
    ) -> dict:
        """詳細な改善計画の生成"""
        improvements = []
        priorities = []

        # スコアに基づく全体的な改善提案
        if final_score < 6.0:
            improvements.append("🔴 根本的改善が必要: タスク設計の見直しを検討")
            priorities.append("high")
        elif final_score < 7.5:
            improvements.append("🟡 中程度の改善: 実行プロセスと品質管理の強化")
            priorities.append("medium")
        elif final_score < 9.0:
            improvements.append("🟢 軽微な改善: 品質維持のための継続的改善")
            priorities.append("low")
        else:
            improvements.append("💎 優秀な品質: ベストプラクティスとして記録・共有")
            priorities.append("none")

        # 基本チェックに基づく具体的な改善提案
        if not basic_checks["output_exists"]:
            improvements.append("�� 出力ファイルの生成を確実に実施")
            priorities.append("high")

        if not basic_checks["execution_time_optimal"]:
            improvements.append("⏱️ 実行時間の最適化: パフォーマンス改善を検討")
            priorities.append("medium")

        if not basic_checks["completeness_high"]:
            improvements.append("🎯 タスク完了基準の明確化と検証強化")
            priorities.append("high")

        # レビュー評価に基づく改善提案
        review_scores = review_evaluation.get("scores", {})
        for criterion, score_data in review_scores.items():
            score = score_data["score"]
            if score < 6.0:
                improvements.append(f"📊 {score_data['description']}の改善: 現在 {score}/10.0")
                priorities.append("high")
            elif score < 7.5:
                improvements.append(f"📊 {score_data['description']}の強化: 現在 {score}/10.0")
                priorities.append("medium")

        return {
            "improvements": improvements,
            "priorities": priorities,
            "high_priority_count": priorities.count("high"),
            "medium_priority_count": priorities.count("medium"),
            "low_priority_count": priorities.count("low"),
        }

    def _generate_review_summary(self, review_scores: dict) -> str:
        """レビューサマリーの生成"""
        strengths = []
        weaknesses = []

        for criterion, score_data in review_scores.items():
            score = score_data["score"]
            if score >= 8.0:
                strengths.append(score_data["description"])
            elif score <= 6.0:
                weaknesses.append(score_data["description"])

        summary = ""
        if strengths:
            summary += f"強み: {', '.join(strengths)}. "
        if weaknesses:
            summary += f"改善点: {', '.join(weaknesses)}."

        return summary if summary else "標準的な品質です"

    def _print_evaluation_summary(self, evaluation_result: dict):
        """評価サマリーの表示"""
        print(f"✅ 品質評価完了: スコア {evaluation_result['quality_score']:.1f}/10.0")
        print(f"📊 品質レベル: {evaluation_result['quality_level']}")
        print(f"🎯 合格状態: {'✅ 合格' if evaluation_result['passed'] else '❌ 不合格'}")

        if evaluation_result["improvement_plan"]["high_priority_count"] > 0:
            print(
                f"⚠️ 高優先度改善項目: {evaluation_result['improvement_plan']['high_priority_count']}件"
            )

    def _check_execution_time_optimal(self, elapsed_time: float) -> bool:
        """実行時間の最適性チェック"""
        return 0 < elapsed_time < 600  # 10分以内

    def _assess_comprehensive_completeness(self, task_result: dict) -> bool:
        """包括的完了度評価"""
        output = task_result.get("output_summary", "").lower()

        completion_indicators = [
            "完了",
            "終了",
            "完成",
            "実装済み",
            "テスト済み",
            "success",
            "completed",
            "done",
            "finished",
        ]

        # 複数の完了指標を確認
        indicators_found = sum(1 for indicator in completion_indicators if indicator in output)
        return indicators_found >= 2  # 2つ以上の指標がある

    def _assess_detailed_description_quality(self, task_result: dict) -> bool:
        """詳細な説明文品質評価"""
        description = task_result.get("task_description", "")

        # 長さ、具体性、明確さの複合評価
        if len(description.strip()) < 15:
            return False

        # 具体的なアクション動詞があるか
        action_verbs = ["実装", "作成", "開発", "テスト", "評価", "分析", "設計", "修正"]
        has_action_verb = any(verb in description for verb in action_verbs)

        # 具体的な対象があるか
        has_specific_target = len(description.split()) >= 5

        return has_action_verb and has_specific_target

    def _assess_output_structure(self, task_result: dict) -> bool:
        """出力構造の評価"""
        output = task_result.get("output_summary", "")

        # 構造化の指標
        structure_indicators = ["##", "===", "---", "•", "- ", "* "]
        has_structure = any(indicator in output for indicator in structure_indicators)

        # 十分な内容量
        has_sufficient_content = len(output.strip()) > 50

        return has_structure and has_sufficient_content

    def _check_code_quality_indicators(self, task_result: dict) -> bool:
        """コード品質指標のチェック"""
        output_file = task_result.get("output_file")
        if not output_file:
            return False

        try:
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()

            # コード品質の簡易指標
            quality_indicators = [
                "def " in content,  # 関数定義
                "import " in content or "from " in content,  # インポート
                "class " in content,  # クラス定義
                "TODO" not in content and "FIXME" not in content,  # 未解決事項がない
                len(content.split("\n")) > 3,  # 十分な行数
            ]

            return sum(quality_indicators) >= 3  # 3つ以上の指標を満たす

        except:
            return False

    def _calculate_average_execution_time(self, tasks: list) -> float:
        """平均実行時間の計算"""
        execution_times = []

        for task in tasks:
            # 実行ログから実行時間を取得（簡易版）
            if "execution_time" in task:
                try:
                    time_val = float(task["execution_time"])
                    execution_times.append(time_val)
                except:
                    pass

        return sum(execution_times) / len(execution_times) if execution_times else 0

    def _check_file_readability(self, file_path: str) -> bool:
        """ファイルの可読性チェック"""
        import os

        if not file_path:
            return False
        return os.path.exists(file_path) and os.path.getsize(file_path) > 0

    def _get_quality_level(self, score: float) -> str:
        """品質レベルの判定"""
        if score >= 9.0:
            return "優秀 (Excellent)"
        elif score >= 7.5:
            return "良好 (Good)"
        elif score >= 6.0:
            return "合格 (Acceptable)"
        else:
            return "要改善 (Needs Improvement)"

    def _get_current_timestamp(self):
        """現在のタイムスタンプ取得"""
        from datetime import datetime

        return datetime.now().isoformat()


# テスト用
if __name__ == "__main__":
    evaluator = QualityEvaluatorEnhanced()

    # テスト用タスク結果
    test_result = {
        "task_id": "test_001",
        "task_description": "サンプルタスクの実行と詳細な品質評価のテスト実施",
        "output_file": "agent_outputs/test_output.txt",
        "output_summary": "タスクが正常に完了しました。すべてのテストにパスし、品質基準を満たしています。\n## 実行結果\n• 機能テスト: 完了\n• パフォーマンステスト: 完了\n• 品質評価: 実施済み",
        "elapsed_time": 45.5,
        "error_occurred": False,
        "parent_goal_id": "test_goal",
    }

    evaluation = evaluator.evaluate_task_quality(test_result)
    print(f"\n詳細評価結果: {evaluation}")
