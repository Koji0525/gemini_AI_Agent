"""
CollaborationAgent - エージェント間の協調動作を管理

機能:
1. タスクの自動分配
2. 並行処理の最適化
3. エージェント間の依存関係解決
4. 負荷分散
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from collections import defaultdict


class CollaborationAgent:
    """エージェント間の協調動作を管理するエージェント"""

    def __init__(self, knowledge_path: str = "mvp_v4/knowledge/learned"):
        """
        初期化

        Args:
            knowledge_path: ナレッジ保存先パス
        """
        self.knowledge_path = knowledge_path
        self.registered_agents = {}
        self.task_queue = asyncio.Queue()
        self.task_history = []
        self.agent_performance = defaultdict(lambda: {"success": 0, "failure": 0, "avg_time": 0})

    def register_agent(self, agent_name: str, agent_instance: Any, capabilities: List[str]):
        """
        エージェントを登録

        Args:
            agent_name: エージェント名
            agent_instance: エージェントインスタンス
            capabilities: エージェントが処理できるタスクタイプのリスト
        """
        self.registered_agents[agent_name] = {
            "instance": agent_instance,
            "capabilities": capabilities,
            "status": "idle",
            "current_task": None,
        }
        print(f"✅ エージェント登録: {agent_name} (能力: {', '.join(capabilities)})")

    def get_available_agents(self, task_type: str) -> List[str]:
        """
        指定されたタスクタイプを処理できる利用可能なエージェントを取得

        Args:
            task_type: タスクタイプ

        Returns:
            利用可能なエージェント名のリスト
        """
        available = []
        for agent_name, agent_info in self.registered_agents.items():
            if task_type in agent_info["capabilities"] and agent_info["status"] == "idle":
                available.append(agent_name)
        return available

    def select_best_agent(self, task_type: str) -> Optional[str]:
        """
        パフォーマンス履歴に基づいて最適なエージェントを選択

        Args:
            task_type: タスクタイプ

        Returns:
            選択されたエージェント名（None = 利用可能なエージェントなし）
        """
        available_agents = self.get_available_agents(task_type)

        if not available_agents:
            return None

        # パフォーマンススコアで選択
        best_agent = None
        best_score = -1

        for agent_name in available_agents:
            perf = self.agent_performance[agent_name]
            total_tasks = perf["success"] + perf["failure"]

            if total_tasks == 0:
                # 未使用エージェントは中間スコア
                score = 0.5
            else:
                success_rate = perf["success"] / total_tasks
                # 成功率と速度を考慮（速度は逆数）
                avg_time = perf["avg_time"] if perf["avg_time"] > 0 else 1
                score = success_rate * (1 / avg_time)

            if score > best_score:
                best_score = score
                best_agent = agent_name

        return best_agent

    async def distribute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスクを適切なエージェントに分配して実行

        Args:
            task: タスク情報（type, paramsを含む）

        Returns:
            実行結果
        """
        task_type = task.get("type")
        task_id = task.get("id", f"task_{len(self.task_history)}")

        # 最適なエージェントを選択
        agent_name = self.select_best_agent(task_type)

        if not agent_name:
            return {
                "status": "error",
                "message": f"タスクタイプ '{task_type}' を処理できるエージェントが見つかりません",
                "task_id": task_id,
            }

        agent_info = self.registered_agents[agent_name]
        agent_instance = agent_info["instance"]

        # エージェントのステータスを更新
        agent_info["status"] = "busy"
        agent_info["current_task"] = task_id

        start_time = datetime.now()

        try:
            # タスク実行
            result = await agent_instance.execute(task)

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            # パフォーマンス更新
            perf = self.agent_performance[agent_name]
            if result.get("status") == "success":
                perf["success"] += 1
            else:
                perf["failure"] += 1

            # 平均時間を更新
            total_tasks = perf["success"] + perf["failure"]
            perf["avg_time"] = (
                (perf["avg_time"] * (total_tasks - 1)) + execution_time
            ) / total_tasks

            # 履歴に追加
            self.task_history.append(
                {
                    "task_id": task_id,
                    "task_type": task_type,
                    "agent": agent_name,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "execution_time": execution_time,
                    "status": result.get("status"),
                }
            )

            result["assigned_agent"] = agent_name
            result["execution_time"] = execution_time

        except Exception as e:
            result = {
                "status": "error",
                "message": str(e),
                "task_id": task_id,
                "assigned_agent": agent_name,
            }

            # エラーもパフォーマンスに記録
            self.agent_performance[agent_name]["failure"] += 1

        finally:
            # エージェントをアイドル状態に戻す
            agent_info["status"] = "idle"
            agent_info["current_task"] = None

        return result

    async def distribute_tasks_parallel(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        複数のタスクを並行処理

        Args:
            tasks: タスクリスト

        Returns:
            実行結果のリスト
        """
        # タスクを並行実行
        coroutines = [self.distribute_task(task) for task in tasks]
        results = await asyncio.gather(*coroutines, return_exceptions=True)

        # 例外をエラー結果に変換
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    {
                        "status": "error",
                        "message": str(result),
                        "task_id": tasks[i].get("id", f"task_{i}"),
                    }
                )
            else:
                processed_results.append(result)

        return processed_results

    async def resolve_dependencies(self, tasks: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        タスクの依存関係を解決して実行順序を決定

        Args:
            tasks: タスクリスト（各タスクは'dependencies'フィールドを持つ）

        Returns:
            実行グループのリスト（各グループは並行実行可能）
        """
        # タスクIDでインデックス化
        task_map = {task.get("id", f"task_{i}"): task for i, task in enumerate(tasks)}

        # 依存関係グラフを構築
        dependency_graph = defaultdict(list)
        in_degree = defaultdict(int)

        for task_id, task in task_map.items():
            dependencies = task.get("dependencies", [])
            in_degree[task_id] = len(dependencies)

            for dep_id in dependencies:
                dependency_graph[dep_id].append(task_id)

        # トポロジカルソートで実行順序を決定
        execution_groups = []
        current_group = []

        # 依存関係のないタスクから開始
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]

        while queue:
            current_group = []
            next_queue = []

            for task_id in queue:
                current_group.append(task_map[task_id])

                # このタスクに依存していたタスクの入次数を減らす
                for dependent_id in dependency_graph[task_id]:
                    in_degree[dependent_id] -= 1
                    if in_degree[dependent_id] == 0:
                        next_queue.append(dependent_id)

            if current_group:
                execution_groups.append(current_group)

            queue = next_queue

        return execution_groups

    async def execute_workflow(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        タスクワークフロー全体を実行（依存関係を考慮）

        Args:
            tasks: タスクリスト

        Returns:
            ワークフロー実行結果
        """
        start_time = datetime.now()

        # 依存関係を解決
        execution_groups = await self.resolve_dependencies(tasks)

        all_results = []

        # グループごとに並行実行
        for i, group in enumerate(execution_groups):
            print(f"📋 実行グループ {i+1}/{len(execution_groups)} ({len(group)}タスク)")

            group_results = await self.distribute_tasks_parallel(group)
            all_results.extend(group_results)

            # エラーがあればワークフローを中断
            if any(r.get("status") == "error" for r in group_results):
                print(f"⚠️ グループ {i+1} でエラー発生、ワークフロー中断")
                break

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()

        workflow_result = {
            "status": (
                "success" if all(r.get("status") == "success" for r in all_results) else "partial"
            ),
            "total_tasks": len(tasks),
            "completed_tasks": len(all_results),
            "execution_groups": len(execution_groups),
            "total_time": total_time,
            "results": all_results,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }

        return workflow_result

    def get_agent_statistics(self) -> Dict[str, Any]:
        """
        エージェントの統計情報を取得

        Returns:
            統計情報
        """
        stats = {
            "registered_agents": len(self.registered_agents),
            "total_tasks": len(self.task_history),
            "agent_performance": dict(self.agent_performance),
        }

        # エージェントごとの状態
        agent_status = {}
        for agent_name, agent_info in self.registered_agents.items():
            agent_status[agent_name] = {
                "status": agent_info["status"],
                "capabilities": agent_info["capabilities"],
                "current_task": agent_info["current_task"],
            }

        stats["agent_status"] = agent_status

        return stats

    async def save_knowledge(self, event: str, details: Dict[str, Any]) -> bool:
        """
        ナレッジベースに登録

        Args:
            event: イベント名
            details: 詳細情報

        Returns:
            成功/失敗
        """
        try:
            knowledge_file = f"{self.knowledge_path}/auto_registered_knowledge.json"

            # 既存データ読み込み
            if os.path.exists(knowledge_file):
                with open(knowledge_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {"knowledge_base": [], "total_entries": 0, "last_updated": None}

            # 新規エントリ追加
            entry = {
                "event": event,
                "details": details,
                "timestamp": datetime.now().isoformat(),
                "agent": "CollaborationAgent",
            }

            data["knowledge_base"].append(entry)
            data["total_entries"] = len(data["knowledge_base"])
            data["last_updated"] = datetime.now().isoformat()

            # 保存
            os.makedirs(os.path.dirname(knowledge_file), exist_ok=True)
            with open(knowledge_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"❌ ナレッジ登録失敗: {e}")
            return False

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスク実行（統一インターフェース）

        Args:
            task: タスク情報

        Returns:
            実行結果
        """
        task_type = task.get("type")

        if task_type == "distribute":
            # 単一タスクの分配
            single_task = task.get("task")
            result = await self.distribute_task(single_task)
            await self.save_knowledge("task_distributed", {"task": single_task, "result": result})
            return result

        elif task_type == "workflow":
            # ワークフロー実行
            tasks = task.get("tasks", [])
            result = await self.execute_workflow(tasks)
            await self.save_knowledge(
                "workflow_executed", {"tasks_count": len(tasks), "result": result}
            )
            return result

        elif task_type == "statistics":
            # 統計情報取得
            stats = self.get_agent_statistics()
            return {"status": "success", "statistics": stats}

        else:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}
