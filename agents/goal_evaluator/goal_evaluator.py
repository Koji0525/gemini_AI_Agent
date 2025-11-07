#!/usr/bin/env python3
"""
GoalEvaluator - ゴール達成度評価エージェント

Phase C: 24時間稼働システムの高度な自律機能
- task_execution_logを分析してゴール達成度を評価
- 不足タスクを検出してpm_tasksに追加提案
- タスク優先度の動的調整
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json

from tools.sheets_manager import GoogleSheetsManager
from tools.safe_sheets_wrapper import SafeSheetsWrapper


class GoalEvaluator:
    """ゴール達成度評価とタスク優先度調整"""

    def __init__(self, sheets_manager: GoogleSheetsManager):
        """
        初期化

        Args:
            sheets_manager: Google Sheetsマネージャー
        """
        self.sheets_manager = sheets_manager
        self.safe_sheets = SafeSheetsWrapper(sheets_manager)
        self.logger = logging.getLogger(__name__)

        # 統計情報
        self.stats = {
            "evaluations_performed": 0,
            "goals_evaluated": 0,
            "missing_tasks_detected": 0,
            "priorities_adjusted": 0,
            "started_at": datetime.now(),
        }

        # ナレッジベース
        self.knowledge_file = Path("mvp_v4/knowledge/learned/auto_registered_knowledge.json")

        self.logger.info("✅ GoalEvaluator を初期化しました")

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスク実行（統一インターフェース）

        Args:
            task: タスク情報
                - type: "evaluate" | "detect_missing" | "prioritize"
                - goal_id: ゴールID（optional）

        Returns:
            実行結果
        """
        task_type = task.get("type", "evaluate")
        goal_id = task.get("goal_id")

        try:
            if task_type == "evaluate":
                # ゴール達成度評価
                if goal_id:
                    result = await self.evaluate_goal(goal_id)
                else:
                    result = await self.evaluate_all_goals()

                await self.save_knowledge("goal_evaluated", result)
                return {"status": "success", "evaluation": result}

            elif task_type == "detect_missing":
                # 不足タスク検出
                if not goal_id:
                    return {"status": "error", "error": "goal_id is required"}

                goal = await self._load_goal(goal_id)
                if not goal:
                    return {"status": "error", "error": f"Goal {goal_id} not found"}

                missing_tasks = await self.detect_missing_tasks(goal)
                await self.save_knowledge(
                    "missing_tasks_detected", {"goal_id": goal_id, "count": len(missing_tasks)}
                )

                return {"status": "success", "missing_tasks": missing_tasks}

            elif task_type == "prioritize":
                # タスク優先度調整
                prioritized = await self.prioritize_tasks()
                await self.save_knowledge("tasks_prioritized", {"count": len(prioritized)})

                return {"status": "success", "prioritized_tasks": prioritized}

            else:
                return {"status": "error", "error": f"Unknown task type: {task_type}"}

        except Exception as e:
            self.logger.error(f"❌ タスク実行エラー: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    async def evaluate_goal(self, goal_id: str) -> Dict[str, Any]:
        """
        特定のゴール達成度を評価

        Args:
            goal_id: ゴールID

        Returns:
            評価結果
        """
        self.logger.info(f"📊 ゴール評価開始: {goal_id}")

        try:
            # ゴール情報の取得
            goal = await self._load_goal(goal_id)
            if not goal:
                return {"goal_id": goal_id, "status": "not_found", "completion_rate": 0.0}

            # 関連タスクの取得
            tasks = await self._load_tasks_for_goal(goal_id)
            if not tasks:
                return {
                    "goal_id": goal_id,
                    "status": "no_tasks",
                    "completion_rate": 0.0,
                    "total_tasks": 0,
                    "completed_tasks": 0,
                }

            # 実行ログの取得
            execution_logs = await self._load_execution_logs(goal_id)

            # 達成度計算
            total_tasks = len(tasks)
            completed_tasks = sum(1 for log in execution_logs if log.get("status") == "success")
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

            # タスクタイプ別の分析
            task_type_analysis = self._analyze_task_types(tasks, execution_logs)

            # ボトルネックの検出
            bottlenecks = self._detect_bottlenecks(tasks, execution_logs)

            result = {
                "goal_id": goal_id,
                "goal_description": goal.get("goal_description", "N/A")[:50] + "...",
                "status": "active",
                "completion_rate": round(completion_rate, 2),
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": total_tasks - completed_tasks,
                "task_type_analysis": task_type_analysis,
                "bottlenecks": bottlenecks,
                "evaluated_at": datetime.now().isoformat(),
            }

            self.stats["evaluations_performed"] += 1
            self.stats["goals_evaluated"] += 1

            self.logger.info(
                f"✅ ゴール評価完了: {completion_rate:.1f}% ({completed_tasks}/{total_tasks})"
            )

            return result

        except Exception as e:
            self.logger.error(f"❌ ゴール評価エラー: {e}", exc_info=True)
            return {"goal_id": goal_id, "status": "error", "error": str(e)}

    async def evaluate_all_goals(self) -> Dict[str, Any]:
        """
        全ゴールの達成度を評価

        Returns:
            全ゴールの評価結果
        """
        self.logger.info("📊 全ゴール評価開始")

        try:
            # 全ゴールの取得
            goals_data = self.safe_sheets.safe_get_data("project_goal", default=[])

            if not goals_data:
                return {"status": "no_goals", "total_goals": 0, "evaluations": []}

            # 各ゴールを評価
            evaluations = []
            for goal in goals_data:
                goal_id = goal.get("goal_id")
                if goal_id:
                    eval_result = await self.evaluate_goal(goal_id)
                    evaluations.append(eval_result)

            # 全体統計
            total_completion = sum(e.get("completion_rate", 0) for e in evaluations)
            avg_completion = total_completion / len(evaluations) if evaluations else 0.0

            result = {
                "status": "success",
                "total_goals": len(evaluations),
                "average_completion_rate": round(avg_completion, 2),
                "evaluations": evaluations,
                "evaluated_at": datetime.now().isoformat(),
            }

            self.logger.info(
                f"✅ 全ゴール評価完了: {len(evaluations)}個、平均{avg_completion:.1f}%"
            )

            return result

        except Exception as e:
            self.logger.error(f"❌ 全ゴール評価エラー: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    async def detect_missing_tasks(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        不足タスクを検出

        Args:
            goal: ゴール情報

        Returns:
            不足タスクのリスト
        """
        self.logger.info(f"🔍 不足タスク検出: {goal.get('goal_id')}")

        try:
            goal_id = goal.get("goal_id")
            goal_description = goal.get("goal_description", "")

            # 既存タスクの取得
            existing_tasks = await self._load_tasks_for_goal(goal_id)
            existing_types = {task.get("task_type") for task in existing_tasks}

            # 実行ログから失敗したタスクを確認
            execution_logs = await self._load_execution_logs(goal_id)
            failed_types = {
                log.get("task_type") for log in execution_logs if log.get("status") == "failed"
            }

            # 必要なタスクタイプを推定
            required_types = self._estimate_required_task_types(goal_description)

            # 不足タスクの検出
            missing_tasks = []

            # 1. 必要だが存在しないタスクタイプ
            for task_type in required_types:
                if task_type not in existing_types:
                    missing_tasks.append(
                        {
                            "task_type": task_type,
                            "priority": "high",
                            "reason": f"{task_type}タスクが存在しません",
                            "suggested_action": f"{task_type}タスクを作成してください",
                        }
                    )

            # 2. 失敗したタスクの再試行
            for task_type in failed_types:
                missing_tasks.append(
                    {
                        "task_type": task_type,
                        "priority": "medium",
                        "reason": f"{task_type}タスクが失敗しました",
                        "suggested_action": "エラーを修正して再実行してください",
                    }
                )

            # 3. テストカバレッジの確認
            if "code" in existing_types and "test" not in existing_types:
                missing_tasks.append(
                    {
                        "task_type": "test",
                        "priority": "high",
                        "reason": "コードが存在しますがテストがありません",
                        "suggested_action": "テストケースを作成してください",
                    }
                )

            # 4. ドキュメントの確認
            if len(existing_tasks) > 5 and "documentation" not in existing_types:
                missing_tasks.append(
                    {
                        "task_type": "documentation",
                        "priority": "medium",
                        "reason": "タスクが多いがドキュメントがありません",
                        "suggested_action": "ドキュメントを作成してください",
                    }
                )

            self.stats["missing_tasks_detected"] += len(missing_tasks)

            self.logger.info(f"✅ 不足タスク検出完了: {len(missing_tasks)}個")

            return missing_tasks

        except Exception as e:
            self.logger.error(f"❌ 不足タスク検出エラー: {e}", exc_info=True)
            return []

    async def prioritize_tasks(self) -> List[Dict[str, Any]]:
        """
        タスクの優先度を動的に調整

        Returns:
            優先度調整済みタスクのリスト
        """
        self.logger.info("📊 タスク優先度調整開始")

        try:
            # 全タスクの取得
            all_tasks = self.safe_sheets.safe_get_data("pm_tasks", default=[])

            if not all_tasks:
                return []

            # 実行ログの取得
            all_logs = self.safe_sheets.safe_get_data("task_execution_log", default=[])

            # 各タスクの優先度を計算
            prioritized_tasks = []
            for task in all_tasks:
                task_id = task.get("task_id")

                # 基本優先度
                base_priority = self._calculate_base_priority(task)

                # 依存関係による調整
                dependency_boost = self._calculate_dependency_boost(task, all_tasks)

                # エラー率による調整
                error_penalty = self._calculate_error_penalty(task_id, all_logs)

                # 最終優先度
                final_priority = base_priority + dependency_boost - error_penalty

                prioritized_tasks.append(
                    {
                        "task_id": task_id,
                        "task_type": task.get("task_type"),
                        "priority_score": round(final_priority, 2),
                        "base_priority": base_priority,
                        "dependency_boost": dependency_boost,
                        "error_penalty": error_penalty,
                    }
                )

            # 優先度でソート
            prioritized_tasks.sort(key=lambda x: x["priority_score"], reverse=True)

            self.stats["priorities_adjusted"] += len(prioritized_tasks)

            self.logger.info(f"✅ タスク優先度調整完了: {len(prioritized_tasks)}個")

            return prioritized_tasks

        except Exception as e:
            self.logger.error(f"❌ タスク優先度調整エラー: {e}", exc_info=True)
            return []

    # ========== 内部ヘルパーメソッド ==========

    async def _load_goal(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """ゴール情報を取得"""
        goals = self.safe_sheets.safe_get_data("project_goal", default=[])
        for goal in goals:
            if goal.get("goal_id") == goal_id:
                return goal
        return None

    async def _load_tasks_for_goal(self, goal_id: str) -> List[Dict[str, Any]]:
        """ゴールに関連するタスクを取得"""
        all_tasks = self.safe_sheets.safe_get_data("pm_tasks", default=[])
        return [task for task in all_tasks if task.get("goal_id") == goal_id]

    async def _load_execution_logs(self, goal_id: str) -> List[Dict[str, Any]]:
        """ゴールに関連する実行ログを取得"""
        all_logs = self.safe_sheets.safe_get_data("task_execution_log", default=[])
        return [log for log in all_logs if log.get("goal_id") == goal_id]

    def _analyze_task_types(
        self, tasks: List[Dict[str, Any]], logs: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, int]]:
        """タスクタイプ別の分析"""
        analysis = {}

        for task in tasks:
            task_type = task.get("task_type", "unknown")
            if task_type not in analysis:
                analysis[task_type] = {"total": 0, "completed": 0, "failed": 0}
            analysis[task_type]["total"] += 1

        for log in logs:
            task_type = log.get("task_type", "unknown")
            status = log.get("status", "unknown")

            if task_type in analysis:
                if status == "success":
                    analysis[task_type]["completed"] += 1
                elif status == "failed":
                    analysis[task_type]["failed"] += 1

        return analysis

    def _detect_bottlenecks(
        self, tasks: List[Dict[str, Any]], logs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """ボトルネックを検出"""
        bottlenecks = []

        # タスクタイプ別の失敗率
        type_failures = {}
        for log in logs:
            task_type = log.get("task_type", "unknown")
            status = log.get("status", "unknown")

            if task_type not in type_failures:
                type_failures[task_type] = {"total": 0, "failed": 0}

            type_failures[task_type]["total"] += 1
            if status == "failed":
                type_failures[task_type]["failed"] += 1

        # 失敗率が高いタスクタイプを検出
        for task_type, counts in type_failures.items():
            if counts["total"] > 0:
                failure_rate = counts["failed"] / counts["total"]
                if failure_rate > 0.5:  # 50%以上失敗
                    bottlenecks.append(
                        {
                            "task_type": task_type,
                            "failure_rate": round(failure_rate * 100, 2),
                            "total_attempts": counts["total"],
                            "failed_attempts": counts["failed"],
                        }
                    )

        return bottlenecks

    def _estimate_required_task_types(self, goal_description: str) -> List[str]:
        """ゴール説明から必要なタスクタイプを推定"""
        required_types = []
        description_lower = goal_description.lower()

        # キーワードベースの推定
        if any(keyword in description_lower for keyword in ["実装", "開発", "作成", "構築"]):
            required_types.extend(["code", "test"])

        if any(keyword in description_lower for keyword in ["テスト", "検証", "確認"]):
            required_types.append("test")

        if any(keyword in description_lower for keyword in ["ドキュメント", "文書", "説明"]):
            required_types.append("documentation")

        if any(keyword in description_lower for keyword in ["最適化", "改善", "パフォーマンス"]):
            required_types.append("optimization")

        return list(set(required_types))  # 重複削除

    def _calculate_base_priority(self, task: Dict[str, Any]) -> float:
        """基本優先度を計算"""
        # タスクタイプによる優先度
        type_priorities = {
            "error": 10.0,
            "test": 8.0,
            "code": 7.0,
            "optimization": 5.0,
            "documentation": 3.0,
        }

        task_type = task.get("task_type", "unknown")
        return type_priorities.get(task_type, 5.0)

    def _calculate_dependency_boost(
        self, task: Dict[str, Any], all_tasks: List[Dict[str, Any]]
    ) -> float:
        """依存関係による優先度ブースト"""
        # 簡易実装: 他のタスクに依存されているタスクの優先度を上げる
        task_id = task.get("task_id")

        dependent_count = sum(1 for t in all_tasks if task_id in t.get("dependencies", []))

        return dependent_count * 2.0

    def _calculate_error_penalty(self, task_id: str, logs: List[Dict[str, Any]]) -> float:
        """エラー率によるペナルティ"""
        task_logs = [log for log in logs if log.get("task_id") == task_id]

        if not task_logs:
            return 0.0

        failed_count = sum(1 for log in task_logs if log.get("status") == "failed")
        failure_rate = failed_count / len(task_logs)

        return failure_rate * 5.0  # 失敗率に応じてペナルティ

    async def save_knowledge(self, event: str, details: Dict[str, Any]) -> bool:
        """ナレッジベースに保存"""
        try:
            self.knowledge_file.parent.mkdir(parents=True, exist_ok=True)

            # 既存ナレッジの読み込み
            if self.knowledge_file.exists():
                with open(self.knowledge_file, "r", encoding="utf-8") as f:
                    knowledge = json.load(f)
                    if isinstance(knowledge, list):
                        knowledge = {}
            else:
                knowledge = {}

            # 新規ナレッジの追加
            timestamp = datetime.now().isoformat()
            key = f"goal_evaluator_{event}_{timestamp}"

            knowledge[key] = {
                "timestamp": timestamp,
                "agent": "GoalEvaluator",
                "event": event,
                "details": details,
            }

            # 保存
            with open(self.knowledge_file, "w", encoding="utf-8") as f:
                json.dump(knowledge, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            self.logger.error(f"❌ ナレッジ保存エラー: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """統計情報を取得"""
        return {
            **self.stats,
            "uptime_seconds": (datetime.now() - self.stats["started_at"]).total_seconds(),
        }


# テスト用のmain関数
async def main():
    """テスト実行"""
    from tools.sheets_manager import get_sheets_manager

    print("🧪 GoalEvaluatorのテスト")
    print("=" * 60)

    # SheetsManager取得
    sheets_manager = get_sheets_manager()
    if not sheets_manager.authenticate():
        print("❌ 認証失敗")
        return

    # GoalEvaluator初期化
    evaluator = GoalEvaluator(sheets_manager)

    # テスト1: 全ゴール評価
    print("\n📊 テスト1: 全ゴール評価")
    result = await evaluator.execute({"type": "evaluate"})
    print(f"   結果: {result['status']}")
    if result["status"] == "success":
        eval_data = result["evaluation"]
        print(f"   ゴール数: {eval_data.get('total_goals', 0)}")
        print(f"   平均達成率: {eval_data.get('average_completion_rate', 0)}%")

    # テスト2: タスク優先度調整
    print("\n📊 テスト2: タスク優先度調整")
    result = await evaluator.execute({"type": "prioritize"})
    print(f"   結果: {result['status']}")
    if result["status"] == "success":
        tasks = result.get("prioritized_tasks", [])
        print(f"   調整タスク数: {len(tasks)}")
        if tasks:
            top3 = tasks[:3]
            print("   Top 3:")
            for i, task in enumerate(top3, 1):
                print(f"      {i}. {task['task_id']} (優先度: {task['priority_score']})")

    # 統計情報
    print("\n📊 統計情報:")
    stats = evaluator.get_statistics()
    print(f"   評価実行数: {stats['evaluations_performed']}")
    print(f"   不足タスク検出: {stats['missing_tasks_detected']}")
    print(f"   優先度調整: {stats['priorities_adjusted']}")

    print("\n✅ テスト完了")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
