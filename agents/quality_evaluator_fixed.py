"""品質評価エージェント（完全版）"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Any, Dict, List

from tools.base_data_accessor import BaseDataAccessor


class QualityEvaluator:
    """品質自動評価エージェント（F3）"""

    def __init__(self):
        """初期化"""
        self.accessor = BaseDataAccessor()
        print("✅ QualityEvaluator 初期化完了")

    def evaluate_task(self, task_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """タスクの品質評価

        Args:
            task_id: タスクID
            result: タスク実行結果

        Returns:
            品質評価結果（overall_score含む）
        """
        print("")
        print("=" * 80)
        print(f"🎯 品質評価: {task_id}")
        print("=" * 80)

        try:
            # 実行結果から情報を取得
            output = str(result.get("output", ""))
            status = result.get("status", "unknown")
            elapsed_time = result.get("elapsed_time", 0)
            knowledge_used = result.get("knowledge_used", 0)

            # ===================================
            # スコア計算（0-100点）
            # ===================================

            # 1. 完了度（0-25点）
            completion_score = 25 if status == "completed" else 0

            # 2. 正確性（0-25点）：出力の詳細度
            output_length = len(output)
            if output_length > 500:
                accuracy_score = 25
            elif output_length > 200:
                accuracy_score = 20
            elif output_length > 100:
                accuracy_score = 15
            else:
                accuracy_score = 10

            # 3. 効率性（0-25点）：実行時間とナレッジ活用
            if elapsed_time < 2:
                efficiency_score = 15
            elif elapsed_time < 5:
                efficiency_score = 10
            else:
                efficiency_score = 5

            if knowledge_used > 0:
                efficiency_score += 10

            # 4. 保守性（0-25点）：出力の構造化
            has_structure = any(
                kw in output for kw in ["実行内容", "ナレッジ活用", "実行時間", "【", "】"]
            )
            maintainability_score = 20 if has_structure else 10

            # 総合スコア
            overall_score = (
                completion_score + accuracy_score + efficiency_score + maintainability_score
            )

            # ===================================
            # 評価判定
            # ===================================

            if overall_score >= 90:
                grade = "A (優秀)"
            elif overall_score >= 75:
                grade = "B (良好)"
            elif overall_score >= 60:
                grade = "C (可)"
            elif overall_score >= 50:
                grade = "D (不可)"
            else:
                grade = "F (要改善)"

            # ===================================
            # 改善提案
            # ===================================

            improvements = []

            if completion_score < 25:
                improvements.append("完了度を向上: タスクの完全実行を目指す")

            if accuracy_score < 20:
                improvements.append("正確性を向上: より詳細な出力を記録する")

            if efficiency_score < 15:
                improvements.append("効率性を向上: ナレッジの活用を増やす")

            if maintainability_score < 15:
                improvements.append("保守性を向上: 出力を構造化する")

            # ===================================
            # 結果出力
            # ===================================

            print(f"\n📊 評価結果:")
            print(f"   総合スコア: {overall_score:.1f}/100")
            print(f"   評価: {grade}")

            print(f"\n📋 詳細スコア:")
            print(f"   完了度: {completion_score:.1f}/25")
            print(f"   正確性: {accuracy_score:.1f}/25")
            print(f"   効率性: {efficiency_score:.1f}/25")
            print(f"   保守性: {maintainability_score:.1f}/25")

            if improvements:
                print(f"\n💡 改善提案:")
                for i, imp in enumerate(improvements, 1):
                    print(f"   {i}. {imp}")

            return {
                "success": True,
                "overall_score": overall_score,
                "quality_score": overall_score,  # 互換性のため
                "grade": grade,
                "completion_score": completion_score,
                "accuracy_score": accuracy_score,
                "efficiency_score": efficiency_score,
                "maintainability_score": maintainability_score,
                "quality_description": (
                    f"{grade}: " + ", ".join(improvements) if improvements else f"{grade}"
                ),
                "improvements": improvements,
                "task_id": task_id,
                "error": "",
            }

        except Exception as e:
            print(f"❌ 評価エラー: {e}")
            import traceback

            traceback.print_exc()

            return {
                "success": False,
                "overall_score": 0,
                "quality_score": 0,
                "error": str(e),
                "task_id": task_id,
            }

    def get_quality_history(self, task_id: str = None) -> List[Dict[str, Any]]:
        """品質評価履歴を取得"""
        try:
            logs = self.accessor.read_sheet_as_dicts("task_execution_log")

            if task_id:
                logs = [log for log in logs if log.get("task_id") == task_id]

            # 品質スコアがあるものだけ
            quality_logs = [
                log
                for log in logs
                if log.get("Quality_Score") and float(log.get("Quality_Score", 0)) > 0
            ]

            return quality_logs

        except Exception as e:
            print(f"❌ 履歴取得エラー: {e}")
            return []


if __name__ == "__main__":
    # テスト実行
    evaluator = QualityEvaluator()

    test_result = {
        "task_id": "test_001",
        "output": "【研究タスク実行】\nタスクID: test_001\n説明: テストタスク\n\n【実行内容】\n- 既存ナレッジベースから関連情報を検索\n- 検索結果を分析し、重要なポイントを抽出\n- 調査結果をagent_outputs/に保存\n\n【ナレッジ活用】\n- 関連ナレッジ: 3件参照\n  1. ナレッジ1\n  2. ナレッジ2\n  3. ナレッジ3\n\n【実行時間】1.50秒",
        "status": "completed",
        "elapsed_time": 1.5,
        "knowledge_used": 3,
    }

    result = evaluator.evaluate_task(task_id="test_001", result=test_result)

    print("\n" + "=" * 80)
    print("テスト結果:")
    print(f"  スコア: {result.get('overall_score', 0)}/100")
    print(f"  成功: {result.get('success', False)}")
