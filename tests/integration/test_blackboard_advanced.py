"""共有黒板の高度なテスト"""
import pytest
import time
from agents.integration.shared_blackboard_manager import SharedBlackboardManager

def test_concurrent_writes():
    """並行書き込みのテスト"""
    blackboard = SharedBlackboardManager(goal_id="test_concurrent")
    
    # 複数回書き込み
    for i in range(5):
        success = blackboard.write_section(f"section_{i}", {
            "iteration": i,
            "timestamp": time.time()
        })
        assert success is True
    
    # バージョンが増加しているか確認
    version = blackboard.get_version()
    assert version >= 5

def test_alert_system():
    """アラートシステムのテスト"""
    blackboard = SharedBlackboardManager(goal_id="test_alert")
    
    # アラート追加
    blackboard.add_alert("warning", "テストアラート")
    
    # 確認
    state = blackboard.read_full_state()
    assert len(state["alerts"]) > 0
    assert state["alerts"][0]["level"] == "warning"

def test_quality_metrics():
    """品質メトリクス更新のテスト"""
    blackboard = SharedBlackboardManager(goal_id="test_quality")
    
    # メトリクス更新
    blackboard.update_quality_metrics({
        "avg_score": 85.5,
        "reflexion_loops_total": 10
    })
    
    # 確認
    state = blackboard.read_full_state()
    assert state["quality_metrics"]["avg_score"] == 85.5

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
