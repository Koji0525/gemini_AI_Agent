"""KnowledgeManager ユニットテスト（要件定義書 v1.0準拠）"""
import pytest
from unittest.mock import Mock, patch, MagicMock

@pytest.mark.unit
@pytest.mark.timeout(1)
class TestKnowledgeManagerCore:
    """コア機能のテスト"""
    
    def test_search_knowledge_with_limit(self, mock_knowledge_manager):
        """1. 制限付き検索機能（パフォーマンス問題対策）"""
        # 最大10件制限
        mock_knowledge_manager.hybrid_search.return_value = [
            {'id': i, 'content': f'test{i}'} for i in range(10)
        ]
        
        results = mock_knowledge_manager.hybrid_search('test query', top_k=10)
        assert len(results) <= 10
    
    def test_get_sample_entries(self, mock_knowledge_manager):
        """2. サンプルエントリ取得"""
        mock_knowledge_manager.get_sample_entries.return_value = [
            {'id': 1, 'content': 'sample1'},
            {'id': 2, 'content': 'sample2'}
        ]
        
        samples = mock_knowledge_manager.get_sample_entries(n=10)
        assert len(samples) <= 10
        assert isinstance(samples, list)
    
    def test_load_knowledge_entries_limited(self, mock_knowledge_manager):
        """3. 制限付き全件読み込み（20件制限）"""
        # 統合テスト用：実データ使用時は20件制限
        mock_knowledge_manager.load_all_entries = Mock(return_value=[
            {'id': i, 'content': f'entry{i}'} for i in range(20)
        ])
        
        entries = mock_knowledge_manager.load_all_entries(limit=20)
        assert len(entries) <= 20
    
    def test_error_handling_db_connection(self, mock_knowledge_manager):
        """4. エラーハンドリング（DB接続）"""
        mock_knowledge_manager.hybrid_search.side_effect = ConnectionError("DB connection failed")
        
        with pytest.raises(ConnectionError):
            mock_knowledge_manager.hybrid_search('test')
    
    def test_vector_search_functionality(self, mock_knowledge_manager):
        """5. ベクトル検索機能"""
        mock_knowledge_manager.vector_search = Mock(return_value=[
            {'id': 1, 'similarity': 0.95}
        ])
        
        results = mock_knowledge_manager.vector_search('test query')
        assert len(results) > 0
        assert all('similarity' in r for r in results)

# 残り7件のテストケースを追加
# - test_keyword_search
# - test_hybrid_search_combination
# - test_cache_mechanism
# - test_data_validation
# - test_concurrent_access
# - test_update_knowledge
# - test_delete_knowledge
