"""
次タスク表示ツール
未着手タスクのうち優先度が高いものを表示
"""


def show_next_tasks():
    """次タスク表示"""
    print("=" * 80)
    print("📋 次の実行タスク")
    print("=" * 80)

    next_tasks = [
        {
            "id": "P1-1-1",
            "name": "SelfHealingAgent基本構造実装",
            "file": "agents/self_healing/self_healing_agent.py",
            "time": "8時間",
            "priority": "高",
        },
        {
            "id": "P1-1-2",
            "name": "ErrorClassifier実装",
            "file": "agents/self_healing/error_classifier.py",
            "time": "4時間",
            "priority": "高",
        },
        {
            "id": "P1-1-3",
            "name": "RetryManager実装",
            "file": "agents/self_healing/retry_manager.py",
            "time": "4時間",
            "priority": "高",
        },
    ]

    for i, task in enumerate(next_tasks, 1):
        print(f"\n{i}. [{task['id']}] {task['name']}")
        print(f"   ファイル: {task['file']}")
        print(f"   所要時間: {task['time']}")
        print(f"   優先度: {task['priority']}")

    print("\n" + "=" * 80)
    print("開始コマンド:")
    print(f"  git checkout -b feature/{next_tasks[0]['id'].lower()}")
    print("=" * 80)


if __name__ == "__main__":
    show_next_tasks()
