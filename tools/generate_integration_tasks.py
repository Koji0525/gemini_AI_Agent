#!/usr/bin/env python3
"""
連携実装タスク生成
"""

integration_tasks = [
    {
        "id": "P1-INT-1",
        "name": "CompleteEngineとの連携実装",
        "description": "既存のSelfHealingAgentをCompleteEngineに組み込み、タスク実行時に自動修復が動作するようにする",
        "files": [
            "agents/complete_engine_ultimate.py",
            "agents/self_healing/self_healing_agent.py",
        ],
        "time": "4時間",
        "priority": "高",
        "test_required": True,
    },
    {
        "id": "P1-INT-2",
        "name": "KnowledgeManager連携実装",
        "description": "過去の修復事例をナレッジベースから検索できるようにする",
        "files": [
            "agents/self_healing/self_healing_agent.py",
            "knowledge_system/core_agents/knowledge_manager.py",
        ],
        "time": "3時間",
        "priority": "高",
        "test_required": True,
    },
    {
        "id": "P1-INT-3",
        "name": "修復ログ記録システム実装",
        "description": "修復結果をhealing_logシートに記録する",
        "files": ["agents/self_healing/self_healing_agent.py", "tools/base_data_accessor.py"],
        "time": "2時間",
        "priority": "中",
        "test_required": True,
    },
    {
        "id": "P1-INT-4",
        "name": "ErrorClassifier独立化",
        "description": "内部クラスを独立ファイルに移動し、他のエージェントからも利用可能にする",
        "files": [
            "agents/self_healing/error_classifier.py",
            "agents/self_healing/self_healing_agent.py",
        ],
        "time": "1時間",
        "priority": "低",
        "test_required": False,
    },
    {
        "id": "P1-INT-5",
        "name": "RetryManager独立化",
        "description": "内部クラスを独立ファイルに移動",
        "files": [
            "agents/self_healing/retry_manager.py",
            "agents/self_healing/self_healing_agent.py",
        ],
        "time": "1時間",
        "priority": "低",
        "test_required": False,
    },
]


def show_integration_tasks():
    print("=" * 80)
    print("🔗 連携実装タスク - 既存実装をシステムに統合")
    print("=" * 80)

    for i, task in enumerate(integration_tasks, 1):
        print(f"\n{i}. [{task['id']}] {task['name']}")
        print(f"   📝 {task['description']}")
        print(f"   📁 対象ファイル: {', '.join(task['files'])}")
        print(f"   ⏱️ 所要時間: {task['time']}")
        print(f"   🚨 優先度: {task['priority']}")
        print(f"   🧪 テスト要: {'✅' if task['test_required'] else '➖'}")

    print("\n" + "=" * 80)
    print("💡 次のステップ: まずP1-INT-1から開始（CompleteEngine連携）")
    print("=" * 80)


if __name__ == "__main__":
    show_integration_tasks()
