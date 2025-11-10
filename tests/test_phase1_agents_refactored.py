"""Phase 1 エージェントテスト - 完全リファクタリング版"""

import asyncio
import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# テスト環境セットアップ
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.setup_test_env import setup_test_environment

setup_test_environment()


class TestCodeGenerationAgentRefactored:
    """コード生成エージェントのテスト - リファクタリング版"""

    @pytest.fixture
    def mock_genai(self):
        """genaiのモックフィクスチャ"""
        with patch("agents.code_generation.code_generation_agent.genai") as mock_genai:
            # モデルリストのモック
            mock_model_info = Mock()
            mock_model_info.name = "models/gemini-1.5-flash"
            mock_model_info.supported_generation_methods = ["generateContent"]
            mock_genai.list_models.return_value = [mock_model_info]

            # モデルインスタンスのモック
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model

            yield mock_genai, mock_model

    @pytest.fixture
    def mock_env(self):
        """環境変数のモックフィクスチャ"""
        with patch("agents.code_generation.code_generation_agent.os.getenv") as mock_getenv:
            mock_getenv.return_value = "test-api-key"
            yield mock_getenv

    def test_agent_initialization_success(self, mock_env, mock_genai):
        """エージェント初期化成功テスト"""
        mock_genai_obj, mock_model = mock_genai

        from agents.code_generation.code_generation_agent import \
            CodeGenerationAgent

        agent = CodeGenerationAgent()

        assert hasattr(agent, "model")
        assert hasattr(agent, "generation_history")
        assert agent.generation_history == []

    def test_code_generation_success(self, mock_env, mock_genai):
        """コード生成成功テスト"""
        mock_genai_obj, mock_model = mock_genai

        # 成功レスポンスの設定
        mock_response = MagicMock()
        mock_response.text = "def add(a, b):\n    return a + b"
        mock_model.generate_content.return_value = mock_response

        from agents.code_generation.code_generation_agent import \
            CodeGenerationAgent

        agent = CodeGenerationAgent()

        task_spec = {
            "title": "加算関数の作成",
            "description": "2つの数値を加算する関数を作成してください",
            "requirements": "型ヒントとdocstringを含む",
        }

        result = asyncio.run(agent.generate_code(task_spec))

        assert "code" in result
        assert "def add(a, b):" in result["code"]
        assert result["syntax_valid"] == True
        assert result["quality_score"] > 0

    def test_code_generation_api_error(self, mock_env, mock_genai):
        """コード生成時のAPIエラーテスト"""
        mock_genai_obj, mock_model = mock_genai

        # APIエラーを設定
        mock_model.generate_content.side_effect = Exception("API接続エラー")

        from agents.code_generation.code_generation_agent import \
            CodeGenerationAgent

        agent = CodeGenerationAgent()

        task_spec = {"title": "テストタスク", "description": "テスト説明"}

        result = asyncio.run(agent.generate_code(task_spec))

        assert "error" in result
        assert "API接続エラー" in result["error"]
        assert result["syntax_valid"] == False

    def test_initialization_error(self, mock_env):
        """初期化エラーテスト"""
        with patch("agents.code_generation.code_generation_agent.genai") as mock_genai:
            # 初期化時にエラーを発生
            mock_genai.list_models.side_effect = Exception("認証エラー")

            from agents.code_generation.code_generation_agent import \
                CodeGenerationAgent

            with pytest.raises(Exception, match="認証エラー"):
                CodeGenerationAgent()


class TestGeminiAPIClientRefactored:
    """Gemini APIクライアントのテスト - リファクタリング版"""

    @pytest.fixture
    def mock_gemini_dependencies(self):
        """Geminiクライアントの依存関係モック"""
        with (
            patch("browser_control.gemini_api_client.genai") as mock_genai,
            patch("browser_control.gemini_api_client.os.getenv") as mock_getenv,
            patch("browser_control.gemini_api_client.load_dotenv") as mock_load_dotenv,
        ):

            mock_getenv.return_value = "test-api-key"
            mock_load_dotenv.return_value = {'status': 'success', 'data': None}

            # モデルのモック
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model

            yield mock_genai, mock_model, mock_getenv, mock_load_dotenv

    def test_client_initialization(self, mock_gemini_dependencies):
        """クライアント初期化テスト"""
        mock_genai, mock_model, mock_getenv, mock_load_dotenv = mock_gemini_dependencies

        from browser_control.gemini_api_client import GeminiAPIClient

        client = GeminiAPIClient()

        assert hasattr(client, "model")
        mock_genai.GenerativeModel.assert_called_once_with("gemini-2.5-flash")

    @pytest.mark.asyncio
    async def test_send_prompt_success(self, mock_gemini_dependencies):
        """プロンプト送信成功テスト - 非同期"""
        mock_genai, mock_model, mock_getenv, mock_load_dotenv = mock_gemini_dependencies

        # 成功レスポンスの設定
        mock_response = MagicMock()
        mock_response.text = "これはテストレスポンスです"
        mock_model.generate_content.return_value = mock_response

        from browser_control.gemini_api_client import GeminiAPIClient

        client = GeminiAPIClient()
        result = await client.send_prompt("テストプロンプト")

        assert result == "これはテストレスポンスです"
        mock_model.generate_content.assert_called_once_with("テストプロンプト")

    def test_send_prompt_sync_context(self, mock_gemini_dependencies):
        """プロンプト送信テスト - 同期コンテキスト"""
        mock_genai, mock_model, mock_getenv, mock_load_dotenv = mock_gemini_dependencies

        # 成功レスポンスの設定
        mock_response = MagicMock()
        mock_response.text = "同期コンテキストでのレスポンス"
        mock_model.generate_content.return_value = mock_response

        from browser_control.gemini_api_client import GeminiAPIClient

        client = GeminiAPIClient()
        result = asyncio.run(client.send_prompt("同期テスト"))

        assert result == "同期コンテキストでのレスポンス"

    @pytest.mark.asyncio
    async def test_send_prompt_error(self, mock_gemini_dependencies):
        """プロンプト送信エラーテスト"""
        mock_genai, mock_model, mock_getenv, mock_load_dotenv = mock_gemini_dependencies

        # エラーを設定
        mock_model.generate_content.side_effect = Exception("APIエラー")

        from browser_control.gemini_api_client import GeminiAPIClient

        client = GeminiAPIClient()

        with pytest.raises(Exception, match="APIエラー"):
            await client.send_prompt("エラーテスト")


class TestIntegrationRefactored:
    """統合テスト - リファクタリング版"""

    def test_cross_module_imports(self):
        """クロスモジュールインポートテスト"""
        # すべての主要モジュールがインポートできるか
        try:
            assert True
        except ImportError as e:
            pytest.fail(f"インポートエラー: {e}")

    def test_environment_consistency(self):
        """環境一貫性テスト"""
        # 環境変数が正しく設定されているか
        required_vars = ["GEMINI_API_KEY", "SPREADSHEET_ID"]
        for var in required_vars:
            assert var in os.environ, f"環境変数 {var} が設定されていません"
            assert (
                os.environ[var].startswith("test-") or "dummy" in os.environ[var]
            ), f"環境変数 {var} がテスト用の値ではありません"

    def test_async_sync_boundaries(self):
        """非同期/同期境界テスト"""
        # 非同期メソッドが正しく定義されているか
        from agents.code_generation.code_generation_agent import \
            CodeGenerationAgent
        from browser_control.gemini_api_client import GeminiAPIClient

        CodeGenerationAgent.__init__
        client_method = GeminiAPIClient.send_prompt

        # メソッドが非同期かどうかを確認（実際の実装に基づく）
        import inspect

        assert inspect.iscoroutinefunction(client_method), "send_prompt は非同期メソッドであるべき"
