"""
システム保護用テストスイート
既存システムの機能が破壊されていないかを確認
"""

import sys
import os
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

def test_f1_goal_concrete():
    """F1: ゴール具体化エージェントの存在確認"""
    try:
        from agents.complete_engine_ultimate import CompleteEngineUltimate
        engine = CompleteEngineUltimate()
        assert hasattr(engine, 'goal_concrete'), "F1: goal_concrete not found"
        return True
    except Exception as e:
        print(f"❌ F1テスト失敗: {e}")
        return False

def test_f2_task_execution():
    """F2: タスク実行機能の存在確認"""
    try:
        from agents.complete_engine_ultimate import CompleteEngineUltimate
        engine = CompleteEngineUltimate()
        assert hasattr(engine, 'execute_task'), "F2: execute_task not found"
        return True
    except Exception as e:
        print(f"❌ F2テスト失敗: {e}")
        return False

def test_f3_quality_evaluator():
    """F3: 品質評価機能の存在確認"""
    try:
        from agents.complete_engine_ultimate import CompleteEngineUltimate
        engine = CompleteEngineUltimate()
        assert hasattr(engine, 'quality_evaluator'), "F3: quality_evaluator not found"
        return True
    except Exception as e:
        print(f"❌ F3テスト失敗: {e}")
        return False

def test_f4_knowledge_system():
    """F4: ナレッジシステムの動作確認"""
    try:
        from agents.complete_engine_ultimate import CompleteEngineUltimate
        engine = CompleteEngineUltimate()
        
        # ナレッジ追加テスト
        result = engine.knowledge_wrapper.add_knowledge(
            title="システム保護テスト",
            content="テスト内容",
            category="test",
            tags="system_protection"
        )
        assert result is not None, "F4: Knowledge addition failed"
        return True
    except Exception as e:
        print(f"❌ F4テスト失敗: {e}")
        return False

def test_f7_self_healing():
    """F7: 自己修復機能の存在確認"""
    try:
        from agents.complete_engine_ultimate import CompleteEngineUltimate
        engine = CompleteEngineUltimate()
        assert hasattr(engine, 'self_healing'), "F7: self_healing not found"
        return True
    except Exception as e:
        print(f"❌ F7テスト失敗: {e}")
        return False

def test_f8_self_evolution():
    """F8: 自己進化機能の存在確認"""
    try:
        from agents.complete_engine_ultimate import CompleteEngineUltimate
        engine = CompleteEngineUltimate()
        assert hasattr(engine, 'self_evolution'), "F8: self_evolution not found"
        return True
    except Exception as e:
        print(f"❌ F8テスト失敗: {e}")
        return False

def test_f9_human_collaboration():
    """F9: 人間連携機能の存在確認"""
    try:
        from agents.complete_engine_ultimate import CompleteEngineUltimate
        engine = CompleteEngineUltimate()
        assert hasattr(engine, 'human_collaboration'), "F9: human_collaboration not found"
        return True
    except Exception as e:
        print(f"❌ F9テスト失敗: {e}")
        return False

def run_all_tests():
    """全テストを実行"""
    tests = [
        ("F1: ゴール具体化", test_f1_goal_concrete),
        ("F2: タスク実行", test_f2_task_execution),
        ("F3: 品質評価", test_f3_quality_evaluator),
        ("F4: ナレッジシステム", test_f4_knowledge_system),
        ("F7: 自己修復", test_f7_self_healing),
        ("F8: 自己進化", test_f8_self_evolution),
        ("F9: 人間連携", test_f9_human_collaboration),
    ]
    
    results = []
    print("━" * 60)
    print("🧪 システム保護テスト実行")
    print("━" * 60)
    
    for name, test_func in tests:
        print(f"\n【{name}】")
        result = test_func()
        results.append(result)
        print(f"  {'✅ 成功' if result else '❌ 失敗'}")
    
    print("\n" + "━" * 60)
    print("📊 テスト結果")
    print("━" * 60)
    success_count = sum(results)
    total_count = len(results)
    success_rate = success_count * 100 / total_count
    
    print(f"  成功: {success_count}/{total_count} ({success_rate:.1f}%)")
    
    if success_rate >= 85:
        print("  ✅ システム保護テスト合格")
        return 0
    else:
        print("  ❌ システム保護テスト不合格（85%以上必要）")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())

