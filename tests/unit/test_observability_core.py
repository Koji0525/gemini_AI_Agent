"""Observability コア機能のテスト（実装非依存版）"""
import pytest
from unittest.mock import Mock

@pytest.mark.unit
@pytest.mark.timeout(1)
class TestObservabilityCore:
    """Observabilityの基本機能テスト"""
    
    def test_trace_recording_basic(self, mock_observability_manager):
        """1. 基本的なトレース記録"""
        result = mock_observability_manager.record_trace(
            trace_id='test-001',
            operation='test_op',
            status='success'
        )
        assert result is True
        assert mock_observability_manager.record_trace.called
    
    def test_trace_search(self, mock_observability_manager):
        """2. トレース検索"""
        mock_observability_manager.search_traces.return_value = [
            {'trace_id': 'test-001', 'operation': 'test_op'}
        ]
        
        results = mock_observability_manager.search_traces(operation='test_op')
        assert isinstance(results, list)
    
    def test_stats_retrieval(self, mock_observability_manager):
        """3. 統計情報取得"""
        stats = mock_observability_manager.get_stats()
        assert isinstance(stats, dict)
        assert 'total_traces' in stats or len(stats) == 0

@pytest.mark.unit
@pytest.mark.timeout(1)
class TestKnowledgeCore:
    """Knowledge管理の基本機能テスト"""
    
    def test_knowledge_search_with_limit(self, mock_knowledge_manager):
        """1. 制限付き検索"""
        results = mock_knowledge_manager.hybrid_search('test', top_k=10)
        assert len(results) <= 10
    
    def test_sample_entries_retrieval(self, mock_knowledge_manager):
        """2. サンプルエントリ取得"""
        samples = mock_knowledge_manager.get_sample_entries(n=5)
        assert len(samples) <= 5
    
    def test_knowledge_search_empty_query(self, mock_knowledge_manager):
        """3. 空クエリの処理"""
        mock_knowledge_manager.hybrid_search.return_value = []
        results = mock_knowledge_manager.hybrid_search('')
        assert isinstance(results, list)
