"""
AgentRegistry - 全エージェント登録・監視

【問題】
- CollaborationAgentに登録されていないエージェントが見えない
- 実際には14個以上のエージェントがいる

【解決】
- v1.23.0の全エージェントを自動登録
- 各エージェントの健全性を個別チェック
"""

import logging
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)


class AgentRegistry:
    """全エージェント登録・監視"""

    def __init__(self):
        self.registered_agents = {}
        self.agent_health_checks = {}
        logger.info("✅ AgentRegistry初期化完了")

    def register_all_agents(self, orchestrator) -> int:
        """
        v1.23.0のすべてのエージェントを登録

        Args:
            orchestrator: AutonomousOrchestratorインスタンス

        Returns:
            登録されたエージェント数
        """
        agents_to_register = [
            # Loop 1: 基本タスク実行
            ("PMAgent", orchestrator.pm_agent, ["planning", "task_decomposition"]),
            ("TaskExecutor", orchestrator.task_executor, ["execution", "task_processing"]),
            ("ReviewAgent", orchestrator.review_agent, ["review", "quality_check"]),
            # エージェント（初期化されている場合）
            ("GoalEvaluator", getattr(orchestrator, "goal_evaluator", None), ["goal_evaluation"]),
            ("CollaborationAgent", orchestrator.collab_agent, ["coordination", "load_balancing"]),
            # Loop 2: 自己修復
            (
                "ErrorClassifier",
                getattr(orchestrator, "error_classifier", None),
                ["error_classification"],
            ),
            (
                "DecisionSupportSystem",
                getattr(orchestrator, "decision_system", None),
                ["decision_making"],
            ),
            (
                "RollbackAgent",
                getattr(orchestrator, "rollback_agent", None),
                ["rollback", "recovery"],
            ),
            (
                "QualityFeedbackLoop",
                getattr(orchestrator, "quality_loop", None),
                ["quality_feedback"],
            ),
            # Loop 3: 学習・最適化
            (
                "LearningOptimizer",
                getattr(orchestrator, "learning_optimizer", None),
                ["optimization", "learning"],
            ),
            (
                "KnowledgeBaseManager",
                getattr(orchestrator, "kb_manager", None),
                ["knowledge_management"],
            ),
            (
                "SelfLearningPipeline",
                getattr(orchestrator, "learning_pipeline", None),
                ["self_learning"],
            ),
            # 監視・分析
            ("MonitoringAgent", orchestrator.monitoring_agent, ["monitoring", "resource_tracking"]),
            (
                "ExecutionAnalyzer",
                orchestrator.execution_analyzer,
                ["analysis", "performance_tracking"],
            ),
            (
                "SystemObserver",
                getattr(orchestrator, "system_observer", None),
                ["observation", "visualization"],
            ),
        ]

        registered_count = 0

        for agent_id, agent_instance, capabilities in agents_to_register:
            if agent_instance is not None:
                self.registered_agents[agent_id] = {
                    "instance": agent_instance,
                    "capabilities": capabilities,
                    "status": "idle",
                    "health": "unknown",
                    "total_executions": 0,
                    "success_rate": 1.0,
                    "last_check": None,
                    "registered_at": datetime.now().isoformat(),
                }
                registered_count += 1
                logger.info(f"✅ {agent_id}を登録（機能: {', '.join(capabilities)}）")

        print(f"\n📋 エージェント登録完了: {registered_count}個")
        return registered_count

    def check_agent_health(self, agent_id: str) -> Dict[str, Any]:
        """
        エージェントの健全性をチェック

        Returns:
            健全性情報
        """
        if agent_id not in self.registered_agents:
            return {"status": "not_found"}

        agent_info = self.registered_agents[agent_id]
        agent_instance = agent_info["instance"]

        health_status = {
            "agent_id": agent_id,
            "is_initialized": agent_instance is not None,
            "has_required_methods": False,
            "memory_usage": "unknown",
            "health": "healthy",
            "issues": [],
            "checked_at": datetime.now().isoformat(),
        }

        # 基本的な健全性チェック
        if agent_instance is None:
            health_status["health"] = "critical"
            health_status["issues"].append("エージェントインスタンスがNone")
            return health_status

        # 必須メソッドの存在チェック（エージェントによって異なる）
        expected_methods = {
            "PMAgent": ["create_task", "decompose_task"],
            "TaskExecutor": ["execute_task"],
            "ReviewAgent": ["review_result"],
            "MonitoringAgent": ["collect_metrics"],
        }

        if agent_id in expected_methods:
            for method in expected_methods[agent_id]:
                if not hasattr(agent_instance, method):
                    health_status["issues"].append(f"メソッド '{method}' が見つかりません")
                    health_status["health"] = "warning"

        if not health_status["issues"]:
            health_status["has_required_methods"] = True

        # 健全性情報を更新
        agent_info["health"] = health_status["health"]
        agent_info["last_check"] = health_status["checked_at"]

        return health_status

    def get_all_agents_status(self) -> Dict[str, Any]:
        """全エージェントの状態を取得"""
        agents_list = []

        for agent_id, agent_info in self.registered_agents.items():
            # 健全性チェック（キャッシュされている場合はスキップ）
            if agent_info.get("last_check") is None:
                self.check_agent_health(agent_id)

            agents_list.append(
                {
                    "agent_id": agent_id,
                    "status": agent_info.get("status", "idle"),
                    "health": agent_info.get("health", "unknown"),
                    "capabilities": agent_info.get("capabilities", []),
                    "success_rate": agent_info.get("success_rate", 1.0),
                    "total_executions": agent_info.get("total_executions", 0),
                    "last_check": agent_info.get("last_check"),
                }
            )

        return {
            "total_agents": len(agents_list),
            "active_agents": len([a for a in agents_list if a["status"] == "active"]),
            "idle_agents": len([a for a in agents_list if a["status"] == "idle"]),
            "healthy_agents": len([a for a in agents_list if a["health"] == "healthy"]),
            "warning_agents": len([a for a in agents_list if a["health"] == "warning"]),
            "critical_agents": len([a for a in agents_list if a["health"] == "critical"]),
            "agents": agents_list,
        }


if __name__ == "__main__":
    print("🧪 AgentRegistry テスト")

    registry = AgentRegistry()

    # ダミーオーケストレーター
    class DummyOrchestrator:
        def __init__(self):
            self.pm_agent = "PMAgent Instance"
            self.task_executor = "TaskExecutor Instance"
            self.review_agent = "ReviewAgent Instance"
            self.monitoring_agent = "MonitoringAgent Instance"
            self.execution_analyzer = "ExecutionAnalyzer Instance"
            self.collab_agent = "CollaborationAgent Instance"

    orchestrator = DummyOrchestrator()
    count = registry.register_all_agents(orchestrator)

    print(f"\n✅ 登録完了: {count}個のエージェント")

    # 状態取得
    status = registry.get_all_agents_status()
    print(f"\n📊 エージェント状態:")
    print(f"  総数: {status['total_agents']}個")
    print(f"  健全: {status['healthy_agents']}個")

    for agent in status["agents"][:5]:
        print(
            f"  - {agent['agent_id']}: {agent['health']} (機能: {', '.join(agent['capabilities'])})"
        )
