"""SMART準拠の進捗計算システム"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from typing import Any, Dict, List

from tools.base_data_accessor import BaseDataAccessor


class SmartProgressCalculator:
    """SMART基準に基づく進捗計算

    進捗率の計算方法：
    1. タスクの重み付け（工数、重要度）
    2. 成果物の有無
    3. 品質スコア
    4. SMART達成基準との照合
    """

    def __init__(self):
        self.accessor = BaseDataAccessor()
        self.goal_dir = Path("/workspaces/gemini_AI_Agent/agent_outputs/goal")

    def calculate_progress(self, goal_id: str) -> Dict[str, Any]:
        """進捗計算

        Args:
            goal_id: ゴールID

        Returns:
            進捗情報
        """
        # タスク取得
        tasks = self.accessor.read_sheet_as_dicts(
            "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal_id
        )

        # 実行ログ取得
        logs = self.accessor.read_sheet_as_dicts("task_execution_log")

        # SMART基準取得
        smart_criteria = self._load_smart_criteria(goal_id)

        # 進捗計算
        total_weight = 0
        completed_weight = 0

        task_details = []

        for task in tasks:
            task_id = task.get("task_id")
            exec_type = task.get("execution_type", "general")
            status = task.get("status")

            # タスクの重み（execution_typeによる）
            weight = self._get_task_weight(exec_type)
            total_weight += weight

            # 実完了判定
            if status == "completed":
                task_logs = [log for log in logs if log.get("task_id") == task_id]

                if task_logs:
                    latest_log = task_logs[-1]

                    # 完了度判定
                    completion_score = self._evaluate_completion(latest_log)

                    # 重み付き完了度
                    completed_weight += weight * completion_score

                    task_details.append(
                        {
                            "task_id": task_id,
                            "weight": weight,
                            "completion_score": completion_score,
                            "weighted_completion": weight * completion_score,
                        }
                    )

        # 進捗率計算
        if total_weight == 0:
            progress_rate = 0
        else:
            progress_rate = (completed_weight / total_weight) * 100

        # SMART達成度
        smart_achievement = self._evaluate_smart_achievement(goal_id, tasks, logs, smart_criteria)

        return {
            "goal_id": goal_id,
            "total_tasks": len(tasks),
            "total_weight": total_weight,
            "completed_weight": completed_weight,
            "progress_rate": progress_rate,
            "smart_achievement": smart_achievement,
            "task_details": task_details,
        }

    def _get_task_weight(self, exec_type: str) -> float:
        """タスクタイプ別の重み"""
        weights = {
            "research": 1.0,
            "design": 1.5,
            "implementation": 3.0,  # 実装が最重要
            "test": 2.0,
            "validation": 2.0,
            "validation_prep": 1.5,
            "quality_improvement": 1.0,
            "documentation": 1.0,
            "general": 1.0,
        }
        return weights.get(exec_type, 1.0)

    def _evaluate_completion(self, log: Dict[str, Any]) -> float:
        """完了度評価（0.0-1.0）

        評価基準：
        - 品質スコア: 40%
        - 成果物の有無: 30%
        - 出力の具体性: 30%
        """
        # 品質スコア（0-10 → 0.0-1.0）
        quality_score_raw = log.get("Quality_Score", "0")
        # 空文字列や無効な値の処理
        try:
            quality_score = float(quality_score_raw) / 10 if quality_score_raw else 0.0
        except (ValueError, TypeError):
            quality_score = 0.0
        quality_factor = min(quality_score / 7.0, 1.0) * 0.4  # 7点以上で満点

        # 出力の具体性
        output = log.get("output_data", "")
        output_length = len(output)
        has_structure = "実行内容" in output or "【" in output

        if output_length > 500 and has_structure:
            output_factor = 0.3
        elif output_length > 200:
            output_factor = 0.2
        else:
            output_factor = 0.1

        # 成果物の有無（簡易判定）
        has_file_reference = "agent_outputs/" in output or ".py" in output or ".json" in output
        artifact_factor = 0.3 if has_file_reference else 0.0

        # 総合評価
        completion_score = quality_factor + output_factor + artifact_factor

        return min(completion_score, 1.0)

    def _load_smart_criteria(self, goal_id: str) -> Dict[str, Any]:
        """SMART基準の読み込み"""
        files = list(self.goal_dir.glob(f"{goal_id}_*.json"))

        if not files:
            return {}

        latest_file = max(files, key=lambda f: f.stat().st_mtime)

        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("smart", {})
        except:
            return {}

    def _evaluate_smart_achievement(
        self,
        goal_id: str,
        tasks: List[Dict[str, Any]],
        logs: List[Dict[str, Any]],
        smart_criteria: Dict[str, Any],
    ) -> Dict[str, float]:
        """SMART各項目の達成度評価"""

        if not smart_criteria:
            return {}

        achievement = {}

        # Measurable（測定可能）の達成度
        measurable = smart_criteria.get("measurable", "")

        if "品質スコア" in measurable:
            # 品質スコアの平均
            goal_logs = [
                log for log in logs if any(t.get("task_id") == log.get("task_id") for t in tasks)
            ]

            if goal_logs:
                avg_quality = sum(float(log.get("Quality_Score", 0)) for log in goal_logs) / len(
                    goal_logs
                )

                achievement["quality_score"] = min(avg_quality / 7.0, 1.0)

        # Time-bound（期限）の達成度
        # TODO: 期限との比較実装

        return achievement


if __name__ == "__main__":
    calculator = SmartProgressCalculator()
    result = calculator.calculate_progress("6")

    print("=" * 80)
    print("SMART準拠の進捗計算")
    print("=" * 80)
    print(f"\nゴールID: {result['goal_id']}")
    print(f"総タスク: {result['total_tasks']}個")
    print(f"総重み: {result['total_weight']:.1f}")
    print(f"完了重み: {result['completed_weight']:.1f}")
    print(f"\n進捗率: {result['progress_rate']:.1f}%")

    if result["smart_achievement"]:
        print(f"\nSMART達成度:")
        for key, value in result["smart_achievement"].items():
            print(f"  {key}: {value*100:.1f}%")
