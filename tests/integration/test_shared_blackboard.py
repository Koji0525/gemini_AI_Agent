"""共有黒板マネージャーの統合テスト"""
import pytest
import json
from pathlib import Path
from agents.integration.shared_blackboard_manager import SharedBlackboardManager

def test_shared_blackboard_basic():
    """基本的な読み書きテスト"""
    blackboard = SharedBlackboardManager(goal_id="test_basic")
    
    # 書き込み
    success = blackboard.write_section("test_section", {
        "status": "completed",
        "value": 42
    })
    assert success is True
    
    # 読み取り
    data = blackboard.read_section("test_section")
    assert data is not None
    assert data["status"] == "completed"
    assert data["value"] == 42

def test_optimistic_locking():
    """楽観的ロックのテスト"""
    blackboard = SharedBlackboardManager(goal_id="test_lock")
    
    # 初回書き込み
    version_1 = blackboard.get_version()
    blackboard.write_section("section_a", {"data": "v1"})
    
    # バージョン確認
    version_2 = blackboard.get_version()
    assert version_2 > version_1

def test_progress_update():
    """進捗更新のテスト"""
    blackboard = SharedBlackboardManager(goal_id="test_progress")
    
    blackboard.update_progress({
        "total_tasks": 100,
        "completed": 50,
        "percentage": 50.0
    })
    
    state = blackboard.read_full_state()
    assert state["progress"]["percentage"] == 50.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
