#!/usr/bin/env python3
"""
エージェント間通信プロトコル設計
"""

import json
from datetime import datetime
from enum import Enum


class MessageType(Enum):
    GOAL_SUBMISSION = "goal_submission"
    TASK_DEFINITION = "task_definition"
    EXECUTION_REQUEST = "execution_request"
    PROGRESS_UPDATE = "progress_update"
    ERROR_EVENT = "error_event"
    HUMAN_INSTRUCTION = "human_instruction"
    SYSTEM_CONTROL = "system_control"


class AgentCommunicationProtocol:
    """エージェント間通信プロトコル"""

    @staticmethod
    def create_goal_message(goal, priority, source="github_actions"):
        """目標メッセージの作成"""
        return {
            "message_id": f"goal_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": MessageType.GOAL_SUBMISSION.value,
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "payload": {"goal": goal, "priority": priority, "status": "submitted"},
            "routing": {"from": "goal_input_agent", "to": ["pm_agent"], "required_ack": True},
        }

    @staticmethod
    def create_task_message(tasks, goal_id, agent_capabilities):
        """タスクメッセージの作成"""
        return {
            "message_id": f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": MessageType.TASK_DEFINITION.value,
            "timestamp": datetime.now().isoformat(),
            "source": "pm_agent",
            "payload": {
                "goal_id": goal_id,
                "tasks": tasks,
                "dependencies": AgentCommunicationProtocol.analyze_dependencies(tasks),
                "estimated_duration": "24 hours",
            },
            "routing": {"from": "pm_agent", "to": ["task_orchestrator_agent"], "required_ack": True},
        }

    @staticmethod
    def create_execution_message(task, target_agent, parameters):
        """実行メッセージの作成"""
        return {
            "message_id": f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": MessageType.EXECUTION_REQUEST.value,
            "timestamp": datetime.now().isoformat(),
            "source": "task_orchestrator_agent",
            "payload": {
                "task_id": task["id"],
                "task_type": task["type"],
                "target_agent": target_agent,
                "parameters": parameters,
                "deadline": (datetime.now() + timedelta(hours=6)).isoformat(),
            },
            "routing": {"from": "task_orchestrator_agent", "to": [target_agent], "required_ack": True},
        }

    @staticmethod
    def create_progress_message(agent, task_id, progress, details):
        """進捗メッセージの作成"""
        return {
            "message_id": f"progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": MessageType.PROGRESS_UPDATE.value,
            "timestamp": datetime.now().isoformat(),
            "source": agent,
            "payload": {
                "task_id": task_id,
                "progress": progress,  # 0-100%
                "status": "in_progress",
                "details": details,
                "timestamp": datetime.now().isoformat(),
            },
            "routing": {
                "from": agent,
                "to": ["progress_monitoring_agent", "task_orchestrator_agent"],
                "required_ack": False,
            },
        }

    @staticmethod
    def create_error_message(error, context, severity="medium"):
        """エラーメッセージの作成"""
        return {
            "message_id": f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": MessageType.ERROR_EVENT.value,
            "timestamp": datetime.now().isoformat(),
            "source": context["agent"],
            "payload": {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
                "severity": severity,
                "suggested_actions": ["retry", "escalate", "ignore"],
            },
            "routing": {
                "from": context["agent"],
                "to": ["self_healing_orchestrator_agent", "progress_monitoring_agent"],
                "required_ack": True,
            },
        }

    @staticmethod
    def create_human_instruction_message(instruction, issue_url, author):
        """人間指示メッセージの作成"""
        return {
            "message_id": f"human_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": MessageType.HUMAN_INSTRUCTION.value,
            "timestamp": datetime.now().isoformat(),
            "source": "human_interaction_agent",
            "payload": {
                "instruction": instruction,
                "issue_url": issue_url,
                "author": author,
                "parsed_action": AgentCommunicationProtocol.parse_human_instruction(instruction),
                "priority": "high",
            },
            "routing": {
                "from": "human_interaction_agent",
                "to": ["task_orchestrator_agent", "progress_monitoring_agent"],
                "required_ack": True,
            },
        }

    @staticmethod
    def analyze_dependencies(tasks):
        """タスクの依存関係分析"""
        dependencies = {}
        for task in tasks:
            if "requires" in task:
                dependencies[task["id"]] = task["requires"]
        return dependencies

    @staticmethod
    def parse_human_instruction(instruction):
        """人間の指示を解析"""
        instruction = instruction.lower()
        if "停止" in instruction or "stop" in instruction:
            return {"action": "pause", "target": "all"}
        elif "再開" in instruction or "resume" in instruction:
            return {"action": "resume", "target": "all"}
        elif "変更" in instruction or "change" in instruction:
            return {"action": "modify_strategy", "target": "specific"}
        elif "優先" in instruction or "priority" in instruction:
            return {"action": "reprioritize", "target": "tasks"}
        else:
            return {"action": "notify", "target": "human"}


def demonstrate_communication_flow():
    """通信フローのデモンストレーション"""
    print("🔄 エージェント間通信フローデモンストレーション")
    print("=" * 60)

    # 1. 目標入力
    goal_msg = AgentCommunicationProtocol.create_goal_message("M&Aポータルの検索機能強化", "high")
    print(f"1. 🎯 目標入力メッセージ:")
    print(f"   発信: {goal_msg['routing']['from']} → {goal_msg['routing']['to']}")
    print(f"   内容: {goal_msg['payload']['goal']}")

    # 2. タスク分解
    tasks = [
        {"id": "task_1", "type": "analysis", "description": "現状分析", "requires": []},
        {"id": "task_2", "type": "design", "description": "改善設計", "requires": ["task_1"]},
        {"id": "task_3", "type": "wordpress", "description": "実装", "requires": ["task_2"]},
    ]
    task_msg = AgentCommunicationProtocol.create_task_message(tasks, goal_msg["message_id"], {})
    print(f"\n2. 📋 タスク分解メッセージ:")
    print(f"   発信: {task_msg['routing']['from']} → {task_msg['routing']['to']}")
    print(f"   タスク数: {len(task_msg['payload']['tasks'])}")

    # 3. 実行依頼
    exec_msg = AgentCommunicationProtocol.create_execution_message(
        tasks[2], "wordpress_development_agent", {"site": "uzbek-ma.com"}
    )
    print(f"\n3. 🚀 実行依頼メッセージ:")
    print(f"   発信: {exec_msg['routing']['from']} → {exec_msg['routing']['to']}")
    print(f"   タスク: {exec_msg['payload']['task_type']}")

    # 4. 進捗報告
    progress_msg = AgentCommunicationProtocol.create_progress_message(
        "wordpress_development_agent", "task_3", 75, "WordPressカスタマイズ実行中"
    )
    print(f"\n4. �� 進捗報告メッセージ:")
    print(f"   発信: {progress_msg['source']} → {progress_msg['routing']['to']}")
    print(f"   進捗: {progress_msg['payload']['progress']}%")

    # 5. 人間指示
    human_msg = AgentCommunicationProtocol.create_human_instruction_message(
        "検索機能の実装を優先して進めてください", "https://github.com/owner/repo/issues/123", "project_owner"
    )
    print(f"\n5. 💬 人間指示メッセージ:")
    print(f"   発信: {human_msg['routing']['from']} → {human_msg['routing']['to']}")
    print(f"   アクション: {human_msg['payload']['parsed_action']['action']}")


def main():
    print("=" * 80)
    print("�� 24時間自律開発システム - エージェント間通信プロトコル設計")
    print("=" * 80)

    demonstrate_communication_flow()

    print(f"\n" + "=" * 80)
    print("🎯 通信プロトコル設計完了 - メッセージ駆動アーキテクチャ準備OK")
    print("=" * 80)


if __name__ == "__main__":
    main()
