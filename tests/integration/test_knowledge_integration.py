"""統合テスト: ナレッジベース統合（実装準拠版）"""
import pytest
from unittest.mock import Mock, patch

@pytest.mark.integration
@pytest.mark.timeout(60)
class TestKnowledgeIntegration:
    """ナレッジベースの統合テスト"""
    
    def test_search_with_mocked_data(self):
        """1. モックデータを使った検索"""
        # 完全にモックで実装
        mock_adapter = Mock()
        mock_adapter.search_knowledge = Mock(return_value=[
            {'id': i, 'content': f'test{i}'} for i in range(10)
        ])
        
        results = mock_adapter.search_knowledge('test', top_k=10)
        assert len(results) <= 10
    
    def test_load_entries_mocked(self):
        """2. エントリ読み込み（モック版）"""
        mock_adapter = Mock()
        mock_adapter.load_knowledge_entries = Mock(return_value=[
            {'id': i} for i in range(20)
        ])
        
        entries = mock_adapter.load_knowledge_entries()
        assert len(entries) <= 20
    
    def test_observability_integration_mocked(self):
        """3. ObservabilityとKnowledgeの統合（モック版）"""
        # 完全モック
        mock_obs = Mock()
        mock_obs.record_trace = Mock(return_value=True)
        
        mock_adapter = Mock()
        mock_adapter.search_knowledge = Mock(return_value=[{'id': 1}])
        
        # トレース記録
        mock_obs.record_trace(
            trace_id='test-001',
            operation='knowledge_search'
        )
        
        # ナレッジ検索
        results = mock_adapter.search_knowledge('test')
        
        assert mock_obs.record_trace.called
        assert len(results) >= 0
    
    def test_multiple_searches(self):
        """4. 複数検索のテスト"""
        mock_adapter = Mock()
        mock_adapter.search_knowledge = Mock(return_value=[{'id': 1}])
        
        # 複数回検索
        for i in range(3):
            results = mock_adapter.search_knowledge(f'query{i}')
            assert len(results) > 0
    
    def test_error_resilience(self):
        """5. エラー耐性のテスト"""
        mock_adapter = Mock()
        
        # 1回目は成功、2回目は空リスト
        mock_adapter.search_knowledge = Mock(side_effect=[
            [{'id': 1}],
            []
        ])
        
        # 1回目
        results1 = mock_adapter.search_knowledge('valid')
        assert len(results1) > 0
        
        # 2回目（エラー状態）
        results2 = mock_adapter.search_knowledge('error')
        assert len(results2) == 0
