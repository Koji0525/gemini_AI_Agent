"""
Phase 3 エージェント統合テスト

テスト対象:
- CollaborationAgent
- LearningOptimizer
"""

import asyncio
import os
import sys
import pytest

# パスを追加
sys.path.insert(0, os.path.abspath("."))

from agents.collaboration.collaboration_agent import CollaborationAgent
from agents.learning.learning_optimizer import LearningOptimizer
from agents.documentation.documentation_agent import DocumentationAgent
from agents.monitoring.monitoring_agent import MonitoringAgent


@pytest.mark.asyncio
async def test_collaboration_agent():
    """CollaborationAgent のテスト"""
    print("\n" + "=" * 60)
    print("🤝 CollaborationAgent テスト開始")
    print("=" * 60)

    collab = CollaborationAgent()

    # エージェント登録
    doc_agent = DocumentationAgent()
    collab.register_agent("DocumentationAgent", doc_agent, ["analyze"])

    mon_agent = MonitoringAgent()
    collab.register_agent("MonitoringAgent", mon_agent, ["collect"])

    # タスク分配テスト
    result = await collab.execute(
        {"type": "distribute", "task": {"id": "test_1", "type": "collect"}}
    )

    assert result["status"] == "success"
    assert "assigned_agent" in result

    print("✅ CollaborationAgent テスト成功")


@pytest.mark.asyncio
async def test_learning_optimizer():
    """LearningOptimizer のテスト"""
    print("\n" + "=" * 60)
    print("🧠 LearningOptimizer テスト開始")
    print("=" * 60)

    optimizer = LearningOptimizer()

    # ナレッジベース分析
    result = await optimizer.execute({"type": "analyze"})
    assert result["status"] == "success"
    print(f"✅ 分析完了: {result['analysis']['total_entries']}件")

    # 最適化
    result = await optimizer.execute({"type": "optimize"})
    assert result["status"] == "success"
    print(f"✅ 最適化完了: {result['optimization']['final_count']}件")

    # 推奨生成
    result = await optimizer.execute({"type": "recommend"})
    assert result["status"] == "success"
    print(f"✅ 推奨生成: {len(result['recommendations'])}件")

    print("✅ LearningOptimizer テスト成功")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Phase 3 エージェント統合テスト")
    print("=" * 60)

    asyncio.run(test_collaboration_agent())
    asyncio.run(test_learning_optimizer())

    print("\n" + "=" * 60)
    print("✅ 全テスト完了")
    print("=" * 60)
