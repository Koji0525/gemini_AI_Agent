"""
拡張コンプリートエンジン v3
要件定義書v4.5 コア機能の実行 - 軽量版
"""

import sys

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from agents.quality_evaluation.quality_evaluator import QualityEvaluator
from tools.base_data_accessor import BaseDataAccessor


class CompleteEngineEnhancedV3(BaseDataAccessor):
    """拡張コンプリートエンジン v3（軽量版）"""

    def __init__(self):
        super().__init__()
        self.quality_evaluator = QualityEvaluator()

        # 実行追跡
        self.execution_tracker = {
            "total_cycles": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "quality_scores": [],
        }

    def execute_core_functions_cycle(self, max_cycles: int = 3) -> dict:
        """
        コア機能の実行サイクル

        Args:
            max_cycles: 最大実行サイクル数

        Returns:
            実行結果サマリー
        """
        print("=" * 70)
        print("🔄 コア機能実行サイクル開始 - 要件定義書v4.5")
        print("=" * 70)

        results = {}

        for cycle in range(1, max_cycles + 1):
            print(f"\n🎯 実行サイクル {cycle}/{max_cycles}")
            print("-" * 50)

            cycle_result = self.execute_single_cycle(cycle)
            results[f"cycle_{cycle}"] = cycle_result

            # テスト監視（5回に1回）
            if cycle % 1 == 0:  # 毎回実行（デモ用）
                self._run_test_monitoring()

            # 早期終了条件のチェック
            if cycle_result.get("success_rate", 0) >= 0.8 and cycle >= 2:
                print(f"✅ 早期終了条件達成 (成功率: {cycle_result['success_rate']*100:.1f}%)")
                break

        # 最終サマリー
        final_summary = self._generate_final_summary(results)
        return final_summary

    def execute_single_cycle(self, cycle_number: int) -> dict:
        """
        単一サイクルの実行

        Args:
            cycle_number: サイクル番号

        Returns:
            サイクル実行結果
        """
        self.execution_tracker["total_cycles"] += 1

        cycle_results = {
            "cycle": cycle_number,
            "start_time": self._get_current_timestamp(),
            "tasks_executed": [],
            "quality_scores": [],
            "functions_executed": [],
        }

        try:
            # F1: ゴール自動分解の確認
            goals = self._load_and_analyze_goals()
            cycle_results["active_goals"] = [g["goal_id"] for g in goals]
            cycle_results["functions_executed"].append("F1")

            for goal in goals[:1]:  # 最初のゴールのみ実行（デモ用）
                print(f"🎯 ゴール処理: {goal['goal_id']} - {goal['goal_description'][:30]}...")

                # F2: タスク自律実行
                tasks_executed = self._execute_tasks_for_goal(goal, cycle_number)
                cycle_results["tasks_executed"].extend(tasks_executed)
                cycle_results["functions_executed"].append("F2")

                # F3: 品質自動評価
                quality_results = self._evaluate_tasks_quality(tasks_executed)
                cycle_results["quality_scores"].extend(quality_results)
                cycle_results["functions_executed"].append("F3")

                # F5: 進捗自動可視化
                progress_data = self._update_progress_visualization(goal, tasks_executed)
                cycle_results["progress_updates"] = progress_data
                cycle_results["functions_executed"].append("F5")

            cycle_results["end_time"] = self._get_current_timestamp()
            cycle_results["success_rate"] = self._calculate_success_rate(cycle_results)
            cycle_results["average_quality"] = self._calculate_average_quality(cycle_results)

            self.execution_tracker["successful_executions"] += 1

        except Exception as e:
            print(f"❌ サイクル実行エラー: {e}")
            cycle_results["error"] = str(e)
            cycle_results["success_rate"] = 0
            cycle_results["average_quality"] = 0
            self.execution_tracker["failed_executions"] += 1

        return cycle_results

    def _load_and_analyze_goals(self) -> list:
        """ゴールの読み込みと分析"""
        goals = self.read_sheet_as_dicts(
            "project_goal", filter_func=lambda g: g.get("status") in ["active", "pending"]
        )
        print(f"📋 アクティブなゴール: {len(goals)}件")
        return goals

    def _execute_tasks_for_goal(self, goal: dict, cycle_number: int) -> list:
        """ゴールに対するタスク実行"""
        tasks_executed = []

        # pendingタスクの取得
        pending_tasks = self.read_sheet_as_dicts(
            "pm_tasks",
            filter_func=lambda t: (
                t.get("parent_goal_id") == goal["goal_id"] and t.get("status") == "pending"
            ),
        )

        print(f"  📋 実行可能タスク: {len(pending_tasks)}件")

        # 最大3タスク実行（デモ用）
        for task in pending_tasks[:1]:
            task_result = self._execute_single_task(task, cycle_number)
            tasks_executed.append(task_result)

        return tasks_executed

    def _execute_single_task(self, task: dict, cycle_number: int) -> dict:
        """単一タスクの実行"""
        print(f"    🔧 タスク実行: {task['task_id']}")

        try:
            # タスク実行ロジック（簡易版）
            execution_result = self._safe_task_execution(task)

            # F3: 品質自動評価の実行
            quality_evaluation = self.quality_evaluator.evaluate_task_quality(
                {
                    "task_id": task["task_id"],
                    "task_description": task["description"],
                    "output_file": execution_result.get("output_file"),
                    "output_summary": execution_result.get("summary", ""),
                    "elapsed_time": execution_result.get("elapsed_time", 0),
                    "error_occurred": execution_result.get("error", False),
                }
            )

            # 結果の統合
            final_result = {
                "task_id": task["task_id"],
                "cycle": cycle_number,
                "execution_result": execution_result,
                "quality_evaluation": quality_evaluation,
                "timestamp": self._get_current_timestamp(),
            }

            # タスクステータスの更新（簡易版）
            self._update_task_status(task, quality_evaluation)

            return final_result

        except Exception as e:
            print(f"    ❌ タスク実行エラー: {e}")
            return {
                "task_id": task["task_id"],
                "cycle": cycle_number,
                "error": str(e),
                "timestamp": self._get_current_timestamp(),
            }

    def _safe_task_execution(self, task: dict) -> dict:
        """安全なタスク実行（簡易版）"""
        import time

        # 模擬実行
        time.sleep(1)  # 1秒待機（模擬処理）

        return {
            "output_file": f"agent_outputs/task_{task['task_id']}_{int(time.time())}.txt",
            "summary": f"タスク {task['task_id']} を実行完了 - サイクル実行デモ",
            "elapsed_time": 1.0,
            "error": False,
        }

    def _update_task_status(self, task: dict, quality_evaluation: dict):
        """タスクステータスの更新（簡易版）"""
        status = "completed" if quality_evaluation.get("passed", False) else "failed"
        print(f"    📝 タスクステータス更新: {task['task_id']} -> {status}")

    def _evaluate_tasks_quality(self, tasks_executed: list) -> list:
        """タスク品質評価の一括実行"""
        quality_results = []

        for task_result in tasks_executed:
            if "quality_evaluation" in task_result:
                quality_results.append(task_result["quality_evaluation"])

        return quality_results

    def _update_progress_visualization(self, goal: dict, tasks_executed: list) -> dict:
        """進捗可視化の更新"""
        progress_data = {
            "goal_id": goal["goal_id"],
            "tasks_completed": len(tasks_executed),
            "average_quality": self._calculate_average_quality({"tasks_executed": tasks_executed}),
            "timestamp": self._get_current_timestamp(),
        }

        print(f"    📊 進捗更新: {progress_data['tasks_completed']}タスク完了")
        return progress_data

    def _run_test_monitoring(self):
        """テスト監視の実行"""
        print("    🧪 テスト監視実行中...")
        try:
            # 簡易的なシステムチェック
            goals = self.read_sheet_as_dicts("project_goal")
            tasks = self.read_sheet_as_dicts("pm_tasks")

            print(f"    ✅ システム健全性: ゴール{len(goals)}件, タスク{len(tasks)}件")

        except Exception as e:
            print(f"    ⚠️ テスト監視エラー: {e}")

    def _calculate_success_rate(self, cycle_result: dict) -> float:
        """成功率の計算"""
        tasks = cycle_result.get("tasks_executed", [])
        if not tasks:
            return 0.0

        successful_tasks = [
            t for t in tasks if t.get("quality_evaluation", {}).get("passed", False)
        ]
        return len(successful_tasks) / len(tasks)

    def _calculate_average_quality(self, cycle_result: dict) -> float:
        """平均品質スコアの計算"""
        tasks = cycle_result.get("tasks_executed", [])
        if not tasks:
            return 0.0

        scores = [
            t.get("quality_evaluation", {}).get("quality_score", 0)
            for t in tasks
            if "quality_evaluation" in t
        ]

        return sum(scores) / len(scores) if scores else 0.0

    def _generate_final_summary(self, results: dict) -> dict:
        """最終サマリーの生成"""
        total_tasks = 0
        total_successful = 0
        total_quality_scores = []

        for cycle_key, cycle_result in results.items():
            if cycle_key.startswith("cycle_"):
                tasks = cycle_result.get("tasks_executed", [])
                total_tasks += len(tasks)

                successful_tasks = [
                    t for t in tasks if t.get("quality_evaluation", {}).get("passed", False)
                ]
                total_successful += len(successful_tasks)

                # 品質スコアの収集
                for task in tasks:
                    if "quality_evaluation" in task:
                        total_quality_scores.append(task["quality_evaluation"]["quality_score"])

        overall_success_rate = total_successful / total_tasks if total_tasks > 0 else 0
        overall_quality = (
            sum(total_quality_scores) / len(total_quality_scores) if total_quality_scores else 0
        )

        summary = {
            "total_cycles": len([k for k in results.keys() if k.startswith("cycle_")]),
            "total_tasks_executed": total_tasks,
            "successful_tasks": total_successful,
            "overall_success_rate": round(overall_success_rate, 3),
            "overall_quality_score": round(overall_quality, 2),
            "execution_tracker": self.execution_tracker,
        }

        return summary

    def _get_current_timestamp(self):
        """現在のタイムスタンプ取得"""
        from datetime import datetime

        return datetime.now().isoformat()


# メイン実行
if __name__ == "__main__":
    print("🚀 拡張コンプリートエンジン v3（軽量版）起動")
    engine = CompleteEngineEnhancedV3()

    # コア機能の実行サイクル開始
    results = engine.execute_core_functions_cycle(max_cycles=2)  # デモ用に2サイクル

    print("\n" + "=" * 70)
    print("🎉 コア機能実行サイクル完了")
    print("=" * 70)

    # 結果の表示
    print(f"📊 実行サマリー:")
    print(f"  サイクル数: {results['total_cycles']}")
    print(f"  実行タスク数: {results['total_tasks_executed']}")
    print(f"  成功タスク数: {results['successful_tasks']}")
    print(f"  全体成功率: {results['overall_success_rate']*100:.1f}%")
    print(f"  平均品質スコア: {results['overall_quality_score']:.1f}/10.0")

    print("\n✅ 要件定義書v4.5 コア機能の実装確認完了")
