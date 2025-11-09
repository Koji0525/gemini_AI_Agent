"""Pytest設定ファイル - 全フィクスチャ定義"""
import os
import sys
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================
# 環境設定フィクスチャ
# ============================================

@pytest.fixture(scope="session", autouse=True)
def auto_setup_test_environment():
    """テスト環境の自動セットアップ"""
    from tests.setup_test_env import setup_test_environment
    setup_test_environment()


# ============================================
# 基本モックフィクスチャ
# ============================================

@pytest.fixture
def mock_gemini_client():
    """Gemini APIクライアントのモック"""
    mock = Mock()
    mock.generate_content = Mock(return_value={'text': 'test response'})
    mock.chat = Mock(return_value={'response': 'test chat response'})
    return mock


@pytest.fixture
def mock_sheets_manager():
    """Google Sheetsマネージャーのモック"""
    mock = Mock()
    mock.read_range = Mock(return_value=[['test', 'data']])
    mock.write_range = Mock(return_value=True)
    mock.append_row = Mock(return_value=True)
    return mock


@pytest.fixture
def mock_genai():
    """Google GenAI APIのモック"""
    with patch('google.generativeai') as mock:
        mock_model = MagicMock()
        mock_model.generate_content = Mock(return_value=Mock(text='test'))
        mock.GenerativeModel = Mock(return_value=mock_model)
        yield mock


# ============================================
# Observabilityフィクスチャ
# ============================================

@pytest.fixture
def mock_observability_manager():
    """ObservabilityManagerのモック"""
    mock = Mock()
    mock.record_trace = Mock(return_value=True)
    mock.search_traces = Mock(return_value=[])
    mock.get_stats = Mock(return_value={
        'total_traces': 0,
        'success_count': 0,
        'failure_count': 0
    })
    return mock


# ============================================
# KnowledgeManagerフィクスチャ
# ============================================

@pytest.fixture
def mock_knowledge_manager():
    """KnowledgeManagerのモック"""
    mock = Mock()
    
    # search_knowledge メソッド
    mock.search_knowledge = Mock(return_value=[
        {'id': 1, 'content': 'test knowledge 1', 'confidence': 0.95},
        {'id': 2, 'content': 'test knowledge 2', 'confidence': 0.85}
    ])
    
    # get_sample_entries メソッド
    mock.get_sample_entries = Mock(return_value=[
        {'id': 1, 'content': 'sample 1'},
        {'id': 2, 'content': 'sample 2'}
    ])
    
    # load_knowledge_entries メソッド
    mock.load_knowledge_entries = Mock(return_value=[
        {'id': i, 'content': f'entry {i}'} for i in range(10)
    ])
    
    # hybrid_search メソッド
    mock.hybrid_search = Mock(return_value=[
        {'id': 1, 'content': 'hybrid result 1', 'score': 0.9}
    ])
    
    # get_statistics メソッド
    mock.get_statistics = Mock(return_value={
        'total_entries': 100,
        'avg_confidence': 0.85
    })
    
    return mock


@pytest.fixture
def mock_knowledge_base_adapter():
    """KnowledgeBaseAdapterのモック"""
    mock = Mock()
    
    mock.search_knowledge = Mock(return_value=[
        {'id': 1, 'content': 'adapter result'}
    ])
    
    mock.load_knowledge_entries = Mock(return_value=[
        {'id': i} for i in range(5)
    ])
    
    return mock


# ============================================
# タスク実行フィクスチャ
# ============================================

@pytest.fixture
def sample_code_generation_task():
    """コード生成タスクのサンプルデータ"""
    return {
        'task_id': 'test-001',
        'title': 'サンプルタスク',
        'description': 'テスト用のタスク',
        'requirements': ['要件1', '要件2'],
        'expected_output': 'コード'
    }


# ============================================
# 非同期テストフィクスチャ
# ============================================

@pytest.fixture
def event_loop():
    """イベントループの提供"""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def async_test(event_loop):
    """非同期テスト用のヘルパー"""
    def _async_test(coro):
        return event_loop.run_until_complete(coro)
    return _async_test


# ============================================
# クリーンアップフィクスチャ
# ============================================

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """各テスト後のクリーンアップ"""
    yield
    # テスト後の処理（必要に応じて）


# ============================================
# マーカー設定
# ============================================

def pytest_configure(config):
    """pytest設定"""
    config.addinivalue_line("markers", "unit: ユニットテスト")
    config.addinivalue_line("markers", "integration: 統合テスト")
    config.addinivalue_line("markers", "e2e: E2Eテスト")
    config.addinivalue_line("markers", "slow: 実行時間が長いテスト")
    config.addinivalue_line("markers", "regression: リグレッションテスト")
