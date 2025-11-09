"""Phase 1 エージェントテスト - 失敗部分の修正"""

import asyncio
from unittest.mock import MagicMock, Mock, patch

import pytest


# 失敗しているテストを修正したバージョン
class TestCodeGenerationAgentFixed:
    """コード生成エージェントのテスト - 修正版"""

    @patch("agents.code_generation.code_generation_agent.genai")
    @patch("agents.code_generation.code_generation_agent.os.getenv")
    def test_code_generation_api_error_fixed(self, mock_getenv, mock_genai):
        """APIエラーテスト - 初期化成功、実行時エラーに修正"""
        # 環境変数のモック
        mock_getenv.return_value = "test-api-key"

        # モデル初期化は成功、generate_contentでエラー
        mock_response = MagicMock()
        mock_response.text = "def test():\n    return 'test'"

        mock_model = MagicMock()
        # 初回呼び出しは成功、2回目でエラー（実際の使用パターンに合わせる）
        mock_model.generate_content.side_effect = [
            mock_response,  # モデル初期化用（list_modelsの代わり）
            Exception("API接続エラー"),  # 実際の生成時エラー
        ]

        mock_genai.GenerativeModel.return_value = mock_model

        # 利用可能なモデルをモック
        mock_model_info = Mock()
        mock_model_info.name = "models/gemini-1.5-flash"
        mock_model_info.supported_generation_methods = ["generateContent"]
        mock_genai.list_models.return_value = [mock_model_info]

        from agents.code_generation.code_generation_agent import \
            CodeGenerationAgent

        # エージェント初期化（成功するはず）
        agent = CodeGenerationAgent()

        # テスト実行 - 実行時エラーをテスト
        task_spec = {"title": "テストタスク", "description": "テスト説明"}

        # 非同期メソッドを実行
        result = asyncio.run(agent.generate_code(task_spec))

        # エラー時の結果を検証
        assert "error" in result
        assert "API接続エラー" in result["error"]

    @patch("agents.code_generation.code_generation_agent.genai")
    @patch("agents.code_generation.code_generation_agent.os.getenv")
    def test_code_generation_initialization_error(self, mock_getenv, mock_genai):
        """初期化エラーのテスト - 別途定義"""
        # 環境変数のモック
        mock_getenv.return_value = "test-api-key"

        # 初期化時にエラーを発生
        mock_genai.list_models.side_effect = Exception("初期化エラー")

        from agents.code_generation.code_generation_agent import \
            CodeGenerationAgent

        # 初期化エラーを期待
        with pytest.raises(Exception, match="初期化エラー"):
            CodeGenerationAgent()


class TestGeminiAPIClientFixed:
    """Gemini APIクライアントのテスト - 修正版"""

    @pytest.mark.asyncio
    @patch("browser_control.gemini_api_client.genai")
    @patch("browser_control.gemini_api_client.os.getenv")
    @patch("browser_control.gemini_api_client.load_dotenv")
    async def test_gemini_client_send_prompt_async(self, mock_load_dotenv, mock_getenv, mock_genai):
        """プロンプト送信テスト - 非同期版"""
        # モック設定
        mock_getenv.return_value = "test-api-key"
        mock_load_dotenv.return_value = None

        # レスポンスのモック
        mock_response = MagicMock()
        mock_response.text = "これはテストレスポンスです"

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        from browser_control.gemini_api_client import GeminiAPIClient

        client = GeminiAPIClient()
        result = await client.send_prompt("テストプロンプト")

        # 結果の検証
        assert result == "これはテストレスポンスです"

    @patch("browser_control.gemini_api_client.genai")
    @patch("browser_control.gemini_api_client.os.getenv")
    @patch("browser_control.gemini_api_client.load_dotenv")
    def test_gemini_client_send_prompt_sync_wrapper(
        self, mock_load_dotenv, mock_getenv, mock_genai
    ):
        """プロンプト送信テスト - 同期ラッパー版"""
        # モック設定
        mock_getenv.return_value = "test-api-key"
        mock_load_dotenv.return_value = None

        # レスポンスのモック
        mock_response = MagicMock()
        mock_response.text = "これはテストレスポンスです"

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        from browser_control.gemini_api_client import GeminiAPIClient

        client = GeminiAPIClient()

        # 非同期メソッドを同期コンテキストで実行
        result = asyncio.run(client.send_prompt("テストプロンプト"))

        # 結果の検証
        assert result == "これはテストレスポンスです"
