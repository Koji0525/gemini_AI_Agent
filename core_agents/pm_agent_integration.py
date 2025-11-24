"""
PMエージェント統合モジュール
"""

from core_agents.pm_agent_v33_enhanced import PMAgentV33Enhanced


def create_detailed_tasks(goal_description: str, api_key: str) -> list:
    """詳細タスク作成"""
    try:
        pm_agent = PMAgentV33Enhanced(api_key)
        tasks = pm_agent.run_pm_cycle(goal_description)
        return tasks
    except Exception as e:
        print(f"タスク作成エラー: {e}")
        return []


# 使用例
if __name__ == "__main__":
    import os

    api_key = os.getenv("GEMINI_API_KEY")
    goal = "テストゴール"

    tasks = create_detailed_tasks(goal, api_key)
    for task in tasks:
        print(f"タスク: {task['task_name']}")
        print(f"説明: {task['description']}")
        print("-" * 50)
