"""
Reflexionシステム統合テスト

目的: Reflexionループ、Critic、フィードバック生成、Executorラッパーの統合テスト
"""
import pytest
import sys
from pathlib import Path

# プロジェクトルート追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.quality.reflexion_loop import ReflexionLoop
from agents.quality.critic_agent import CriticAgent
from agents.quality.feedback_generator import FeedbackGenerator
from agents.quality.reflexion_executor_wrapper import ReflexionExecutorWrapper

class TestReflexionLoop:
    """ReflexionLoopの統合テスト"""
    
    def test_basic_loop(self):
        """基本的なループテスト"""
        loop = ReflexionLoop(task_id="test_basic", max_loops=2)
        
        def dummy_executor(task_data):
            return {'status': 'completed', 'output': 'test output'}
        
        result, success = loop.execute_with_reflexion(
            executor_func=dummy_executor,
            task_data={'description': 'test'}
        )
        
        assert result is not None
        assert 'status' in result
        # 2ループ実行されること
        assert len(loop.history) <= 2
    
    def test_quality_threshold(self):
        """品質基準達成テスト"""
        loop = ReflexionLoop(
            task_id="test_threshold",
            quality_threshold=70,
            max_loops=3
        )
        
        def dummy_executor(task_data):
            return {'status': 'completed', 'output': 'test'}
        
        result, success = loop.execute_with_reflexion(
            executor_func=dummy_executor,
            task_data={'description': 'test'}
        )
        
        # 70点基準なので成功するはず
        assert success is True
    
    def test_statistics(self):
        """統計情報テスト"""
        loop = ReflexionLoop(task_id="test_stats")
        
        def dummy_executor(task_data):
            return {'status': 'completed'}
        
        loop.execute_with_reflexion(
            executor_func=dummy_executor,
            task_data={'description': 'test'}
        )
        
        stats = loop.get_statistics()
        assert 'total_loops' in stats
        assert 'initial_score' in stats
        assert 'final_score' in stats

class TestCriticAgent:
    """Criticエージェントのテスト"""
    
    def test_dummy_evaluation(self):
        """ダミー評価テスト"""
        critic = CriticAgent()
        
        test_result = {
            'description': 'test task',
            'output': 'test output with some content'
        }
        
        score, feedback = critic.evaluate(test_result)
        
        assert isinstance(score, int)
        assert 0 <= score <= 100
        assert isinstance(feedback, str)
        assert len(feedback) > 0
    
    def test_rubric_structure(self):
        """評価基準の構造テスト"""
        critic = CriticAgent()
        rubric = critic.get_rubric()
        
        assert 'completeness' in rubric
        assert 'accuracy' in rubric
        assert 'detail' in rubric
        assert 'structure' in rubric

class TestFeedbackGenerator:
    """フィードバック生成システムのテスト"""
    
    def test_actionable_feedback(self):
        """実行可能フィードバック生成テスト"""
        generator = FeedbackGenerator()
        
        test_scores = {
            'completeness': 15,
            'accuracy': 18,
            'detail': 12,
            'structure': 10
        }
        
        feedback = generator.generate_actionable_feedback(
            scores=test_scores,
            original_feedback="Test feedback"
        )
        
        assert isinstance(feedback, str)
        assert len(feedback) > 0
        assert '改善提案' in feedback

class TestReflexionExecutorWrapper:
    """ReflexionExecutorWrapperの統合テスト"""
    
    def test_wrapper_basic(self):
        """基本的なラッパーテスト"""
        wrapper = ReflexionExecutorWrapper(
            base_executor=None,
            enable_reflexion=False
        )
        
        result = wrapper.execute_task({
            'task_id': 'test_001',
            'description': 'test task'
        })
        
        assert result is not None
        assert 'status' in result
    
    def test_wrapper_with_reflexion(self):
        """Reflexion有効時のテスト"""
        wrapper = ReflexionExecutorWrapper(
            base_executor=None,
            enable_reflexion=True,
            quality_threshold=80,
            max_loops=2
        )
        
        result = wrapper.execute_task({
            'task_id': 'test_002',
            'description': 'test task with reflexion'
        })
        
        assert result is not None
        assert 'reflexion_success' in result
        assert 'reflexion_loops' in result
    
    def test_wrapper_statistics(self):
        """統計情報取得テスト"""
        wrapper = ReflexionExecutorWrapper(
            base_executor=None,
            enable_reflexion=True
        )
        
        wrapper.execute_task({
            'task_id': 'test_003',
            'description': 'test'
        })
        
        stats = wrapper.get_statistics()
        assert isinstance(stats, dict)

class TestIntegration:
    """統合テスト"""
    
    def test_full_pipeline(self):
        """完全なパイプラインテスト"""
        # Executorラッパー作成
        wrapper = ReflexionExecutorWrapper(
            base_executor=None,
            enable_reflexion=True,
            quality_threshold=80,
            max_loops=3
        )
        
        # タスク実行
        result = wrapper.execute_task({
            'task_id': 'integration_test',
            'description': '統合テストタスク'
        })
        
        # 結果検証
        assert result['status'] == 'completed'
        assert 'reflexion_success' in result
        assert 'reflexion_loops' in result
        assert result['reflexion_loops'] > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
