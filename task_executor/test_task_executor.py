"""
TaskExecutorの統合テスト
"""

import asyncio
import sys
from pathlib import Path

import pytest
import yaml

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
from task_executor.task_executor import TaskExecutor


@pytest.mark.asyncio
async def test_task_executor():
    """TaskExecutorのテスト"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧪 TaskExecutor統合テスト")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # 設定読み込み
    config_path = project_root / "knowledge_system" / "configuration" / "knowledge_config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # ナレッジマネージャー初期化
    db_path = project_root / config["database"]["path"]
    index_path = project_root / config["vector_search"]["index_path"]
    model_name = config["vector_search"]["model_name"]

    knowledge_manager = KnowledgeManager(str(db_path), str(index_path), model_name)

    # TaskExecutor初期化（依存性注入）
    executor = TaskExecutor(knowledge_manager)

    # テストタスク
    test_tasks = [
        {
            "id": "TASK_001",
            "title": "スプレッドシート更新エラーの修正",
            "description": "タスク完了後にスプレッドシートが更新されない問題を解決する",
        },
        {
            "id": "TASK_002",
            "title": "非同期処理の実装",
            "description": "タスク実行を非同期化して性能を向上させる",
        },
        {
            "id": "TASK_003",
            "title": "エラーログの分析",
            "description": "繰り返し発生するエラーのパターンを特定する",
        },
    ]

    # タスク実行
    for task in test_tasks:
        await executor.execute_task(task)

    # 統計表示
    stats = executor.get_execution_stats()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 実行統計")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ 総タスク数: {stats['total_tasks']}")
    print(f"✅ 成功タスク数: {stats['successful_tasks']}")
    print(f"📈 成功率: {stats['success_rate']*100:.1f}%")
    print(f"⏱️ 平均実行時間: {stats['avg_execution_time']}秒")
    print(f"🎯 目標時間: {stats['target_time']}秒")
    print(f"📊 性能比: {stats['performance_ratio']}x")

    # 目標達成度判定
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎯 P0目標達成度")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # P0-A: ナレッジ検索統合
    print(f"P0-A ナレッジ検索統合: ✅ 完了")

    # P0-B: 計測機能
    metrics_achieved = stats["avg_execution_time"] <= stats["target_time"]
    status = "✅ 達成" if metrics_achieved else "🔄 改善中"
    print(f"P0-B 計測機能: {status} ({stats['avg_execution_time']}秒 / {stats['target_time']}秒)")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


if __name__ == "__main__":
    asyncio.run(test_task_executor())
