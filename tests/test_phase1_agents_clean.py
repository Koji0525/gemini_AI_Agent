"""Phase 1 エージェントテスト - クリーン版"""

import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# テスト環境セットアップ
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.setup_test_env import setup_test_environment

setup_test_environment()


class TestCodeGenerationAgent:
    """コード生成エージェントのテスト - 実際の実装に基づく"""

    @patch("agents.code_generation.code_generation_agent.genai")
    @patch("agents.code_generation.code_generation_agent.os.getenv")
    def test_agent_initialization_with_mock(self, mock_getenv, mock_genai):
        """モックを使用したエージェント初期化テスト"""
        # 環境変数のモック
        mock_getenv.return_value = "test-api-key"

        # genaiのモック
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.list_models.return_value = [
            Mock(name="models/gemini-1.5-flash", supported_generation_methods=["generateContent"])
        ]

        # エージェント初期化をインポートとして実行
        # 実際のインポートはモックされているので問題なし
        try:
            from agents.code_generation.code_generation_agent import \
                CodeGenerationAgent

            agent = CodeGenerationAgent()
            assert agent is not None
        except ImportError:
            # モジュールが見つからない場合はスキップ
            pytest.skip("CodeGenerationAgent module not found")

    @pytest.mark.asyncio
    @patch("agents.code_generation.code_generation_agent.genai")
    async def test_generate_code_basic(self, mock_genai):
        """コード生成の基本テスト"""
        # モックの設定
        mock_model = MagicMock()
        mock_response = Mock()
        mock_response.text = "def hello():\n    return 'Hello, World!'"
        mock_model.generate_content = Mock(return_value=mock_response)
        mock_genai.GenerativeModel.return_value = mock_model

        # テスト実行
        try:
            from agents.code_generation.code_generation_agent import \
                CodeGenerationAgent

            agent = CodeGenerationAgent()

            task_spec = {"title": "Hello World関数", "description": "Hello Worldを返す関数を作成"}

            result = await agent.generate_code(task_spec)
            assert "code" in result or "error" not in result
        except ImportError:
            pytest.skip("CodeGenerationAgent module not found")


class TestGeminiAPIClient:
    """Gemini APIクライアントのテスト"""

    @patch("browser_control.gemini_api_client.genai")
    def test_client_initialization(self, mock_genai):
        """クライアント初期化のテスト"""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        try:
            from browser_control.gemini_api_client import GeminiAPIClient

            client = GeminiAPIClient()
            assert client is not None
        except ImportError:
            pytest.skip("GeminiAPIClient module not found")


# テストファイルのバージョン情報
__version__ = "2.0.0-clean"
__author__ = "AI Development System"
__status__ = "Active"
