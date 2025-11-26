#!/usr/bin/env python3
"""
Phase 4-5 統合テスト

【テスト内容】
1. CompleteEngineUltimateV2の動作確認
2. 階層型コンポーネントの初期化
3. メッセージバスの通信
4. モック/実環境の切り替え

Google Docstring形式
"""
import sys
from pathlib import Path

# プロジェクトルート追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.complete_engine_ultimate_v2_fixed import CompleteEngineUltimateV2
from agents.hierarchy.messaging import Message, MessageBus


def test_mock_mode():
    """モックモードのテスト"""
    print("\n[TEST 1/5] Mock モードテスト")

    engine = CompleteEngineUltimateV2(mode="mock", mock=True)
    result = engine.execute_goal("test_goal_001")

    assert result["status"] == "success"
    assert result["mode"] == "mock"
    print("   ✅ 成功")


def test_hierarchical_mode():
    """階層型モードのテスト"""
    print("\n[TEST 2/5] Hierarchical モードテスト")

    engine = CompleteEngineUltimateV2(mode="hierarchical", mock=True)
    result = engine.execute_goal("test_goal_002")

    assert result["status"] == "success"
    assert result["mode"] == "hierarchical"
    print("   ✅ 成功")


def test_mode_switching():
    """モード切り替えのテスト"""
    print("\n[TEST 3/5] モード切り替えテスト")

    engine = CompleteEngineUltimateV2(mode="mock", mock=True)
    assert engine.mode == "mock"

    engine.switch_mode("hierarchical")
    assert engine.mode == "hierarchical"

    print("   ✅ 成功")


def test_message_bus():
    """メッセージバスのテスト"""
    print("\n[TEST 4/5] MessageBus テスト")

    bus = MessageBus()

    # メッセージ送信
    msg = Message(
        from_agent="agent_a",
        to_agent="agent_b",
        msg_type="task_assignment",
        content={"task_id": "123"},
        priority=5,
    )
    bus.send(msg)

    # メッセージ受信
    messages = bus.receive("agent_b")

    assert len(messages) == 1
    assert messages[0].from_agent == "agent_a"
    print("   ✅ 成功")


def test_executive_manager():
    """Executive Managerのテスト"""
    print("\n[TEST 5/5] Executive Manager テスト")

    from agents.hierarchy.executive_manager import ExecutiveManager

    manager = ExecutiveManager(mock=True)
    result = manager.manage_goal("test_goal_003")

    assert result["status"] == "success"
    assert result["mock"] == True
    print("   ✅ 成功")


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 4-5 統合テスト")
    print("=" * 60)

    try:
        test_mock_mode()
        test_hierarchical_mode()
        test_mode_switching()
        test_message_bus()
        test_executive_manager()

        print("\n" + "=" * 60)
        print("✅ 全テスト成功 (5/5)")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ テスト失敗: {e}")
        sys.exit(1)
