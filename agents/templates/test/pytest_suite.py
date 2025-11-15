#!/usr/bin/env python3
"""
テストスイート - pytest

タスクID: {task_id}
説明: {description}
生成日時: {timestamp}
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict
import json


# ========================================
# フィクスチャ定義
# ========================================

@pytest.fixture
def sample_data():
    """サンプルデータ"""
    return {{
        "items": [
            {{"id": 1, "name": "Item 1", "value": 100}},
            {{"id": 2, "name": "Item 2", "value": 200}},
            {{"id": 3, "name": "Item 3", "value": 300}},
        ]
    }}


@pytest.fixture
def mock_api_client():
    """モックAPIクライアント"""
    client = Mock()
    client.get.return_value = {{"status": "success", "data": []}}
    client.post.return_value = {{"status": "created", "id": 1}}
    return client


@pytest.fixture
def temp_file(tmp_path):
    """一時ファイル"""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("test content")
    return file_path


# ========================================
# 基本テスト
# ========================================

class TestBasicFunctionality:
    """基本機能のテスト"""
    
    def test_simple_operation(self):
        """シンプルな操作テスト"""
        result = 2 + 2
        assert result == 4
    
    def test_string_operations(self):
        """文字列操作テスト"""
        text = "hello world"
        assert text.upper() == "HELLO WORLD"
        assert text.split() == ["hello", "world"]
        assert len(text) == 11
    
    def test_list_operations(self, sample_data):
        """リスト操作テスト"""
        items = sample_data["items"]
        
        assert len(items) == 3
        assert items[0]["id"] == 1
        assert all(item["value"] > 0 for item in items)


# ========================================
# パラメータ化テスト
# ========================================

@pytest.mark.parametrize("input_value,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (5, 10),
])
def test_double_value(input_value, expected):
    """値を2倍にするテスト（パラメータ化）"""
    result = input_value * 2
    assert result == expected


@pytest.mark.parametrize("text,expected_length", [
    ("hello", 5),
    ("world", 5),
    ("test", 4),
    ("", 0),
])
def test_string_length(text, expected_length):
    """文字列長テスト（パラメータ化）"""
    assert len(text) == expected_length


# ========================================
# 例外テスト
# ========================================

class TestExceptions:
    """例外処理のテスト"""
    
    def test_zero_division_error(self):
        """ゼロ除算エラーテスト"""
        with pytest.raises(ZeroDivisionError):
            result = 1 / 0
    
    def test_value_error(self):
        """値エラーテスト"""
        with pytest.raises(ValueError):
            int("not a number")
    
    def test_key_error(self):
        """キーエラーテスト"""
        data = {{"key": "value"}}
        with pytest.raises(KeyError):
            _ = data["nonexistent_key"]


# ========================================
# モックテスト
# ========================================

class TestWithMocks:
    """モックを使用したテスト"""
    
    def test_api_client_get(self, mock_api_client):
        """APIクライアントGETテスト"""
        response = mock_api_client.get("/items")
        
        assert response["status"] == "success"
        assert "data" in response
        mock_api_client.get.assert_called_once_with("/items")
    
    def test_api_client_post(self, mock_api_client):
        """APIクライアントPOSTテスト"""
        payload = {{"name": "New Item"}}
        response = mock_api_client.post("/items", json=payload)
        
        assert response["status"] == "created"
        assert "id" in response
        mock_api_client.post.assert_called_once()
    
    @patch('builtins.open', create=True)
    def test_file_read_with_patch(self, mock_open):
        """ファイル読み込みテスト（patch使用）"""
        mock_open.return_value.__enter__.return_value.read.return_value = "mocked content"
        
        with open("dummy.txt") as f:
            content = f.read()
        
        assert content == "mocked content"
        mock_open.assert_called_once_with("dummy.txt")


# ========================================
# ファイルI/Oテスト
# ========================================

class TestFileOperations:
    """ファイル操作のテスト"""
    
    def test_read_file(self, temp_file):
        """ファイル読み込みテスト"""
        content = temp_file.read_text()
        assert content == "test content"
    
    def test_write_file(self, tmp_path):
        """ファイル書き込みテスト"""
        file_path = tmp_path / "output.txt"
        file_path.write_text("new content")
        
        assert file_path.read_text() == "new content"
        assert file_path.exists()


# ========================================
# 統合テスト
# ========================================

class TestIntegration:
    """統合テスト"""
    
    def test_end_to_end_workflow(self, sample_data, tmp_path):
        """エンドツーエンドワークフローテスト"""
        # データ取得
        items = sample_data["items"]
        assert len(items) > 0
        
        # データ処理
        total_value = sum(item["value"] for item in items)
        assert total_value == 600
        
        # 結果保存
        output_file = tmp_path / "result.json"
        output_file.write_text(json.dumps({{"total": total_value}}))
        
        # 検証
        saved_data = json.loads(output_file.read_text())
        assert saved_data["total"] == 600


# ========================================
# マーカーを使用したテスト
# ========================================

@pytest.mark.slow
def test_slow_operation():
    """時間のかかる操作テスト"""
    import time
    time.sleep(0.1)
    assert True


@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    """未実装機能のテスト"""
    pass


@pytest.mark.xfail(reason="Known issue")
def test_known_issue():
    """既知の問題のテスト"""
    assert False


# ========================================
# セットアップ・ティアダウン
# ========================================

class TestWithSetupTeardown:
    """セットアップ・ティアダウンを使用したテスト"""
    
    def setup_method(self):
        """各テストメソッド実行前"""
        self.test_data = {{"initialized": True}}
    
    def teardown_method(self):
        """各テストメソッド実行後"""
        self.test_data = None
    
    def test_with_setup(self):
        """セットアップを使用したテスト"""
        assert self.test_data["initialized"] is True


# ========================================
# conftest.py に追加すべき内容のサンプル
# ========================================

"""
# conftest.py

import pytest

@pytest.fixture(scope="session")
def database():
    # データベース接続
    db = create_database_connection()
    yield db
    # クリーンアップ
    db.close()

@pytest.fixture(autouse=True)
def reset_state():
    # 各テスト前に状態をリセット
    yield
    # クリーンアップ
"""


# ========================================
# 実行方法
# ========================================

"""
# 全テスト実行
pytest

# 特定のファイル実行
pytest test_example.py

# 特定のテストクラス実行
pytest test_example.py::TestBasicFunctionality

# 特定のテストメソッド実行
pytest test_example.py::TestBasicFunctionality::test_simple_operation

# カバレッジ付き実行
pytest --cov=. --cov-report=html

# 並列実行
pytest -n auto

# マーカーでフィルタ
pytest -m "not slow"

# 詳細出力
pytest -v

# 失敗したテストのみ再実行
pytest --lf
"""
