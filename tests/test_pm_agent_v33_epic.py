#!/usr/bin/env python3
"""
PMAgent v33 Epic 単体テスト（修正版）

【修正内容】
- 環境変数の適切なクリア
- モックの改善
- 既存システムへの影響ゼロ

【Phase 1: M1.2 T1.2.1】
- テストケース: 13件
- カバレッジ目標: 90%以上
- 実行時間: <10秒
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# プロジェクトルート設定
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core_agents.pm_agent_v33_epic import EpicTaskGenerator, PMAgentV33Epic


class TestEpicTaskGenerator:
    """EpicTaskGeneratorクラスのテスト"""

    @pytest.fixture
    def mock_api_key(self, monkeypatch):
        """GEMINI_API_KEYをモック"""
        monkeypatch.setenv("GEMINI_API_KEY", "test_api_key_12345")
        return "test_api_key_12345"

    @pytest.fixture
    def epic_generator(self, mock_api_key):
        """EpicTaskGeneratorインスタンス"""
        with patch("google.generativeai.configure"):
            with patch("google.generativeai.GenerativeModel"):
                generator = EpicTaskGenerator(api_key=mock_api_key)
                return generator

    def test_initialization_success(self, epic_generator):
        """テスト1: 正常初期化"""
        assert epic_generator is not None
        assert epic_generator.api_key == "test_api_key_12345"

    def test_initialization_without_api_key(self, monkeypatch):
        """テスト2: API KEY未設定時のエラー（修正版）"""
        # 環境変数を完全にクリア
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        with patch("google.generativeai.configure"):
            with pytest.raises(ValueError) as exc_info:
                EpicTaskGenerator(api_key=None)
            assert "GEMINI_API_KEY" in str(exc_info.value)

    def test_create_epic_breakdown_prompt(self, epic_generator):
        """テスト3: プロンプト生成"""
        prompt = epic_generator._create_epic_breakdown_prompt(
            epic_description="テストEpic", num_stories=10, target_lines=1000, knowledge_context=""
        )

        assert isinstance(prompt, str)
        assert len(prompt) > 1000
        assert "テストEpic" in prompt
        assert "10個" in prompt
        assert "JSON" in prompt

    def test_create_epic_breakdown_prompt_with_knowledge(self, epic_generator):
        """テスト4: ナレッジコンテキスト付きプロンプト生成"""
        knowledge_context = "参考情報: 過去の成功事例"
        prompt = epic_generator._create_epic_breakdown_prompt(
            epic_description="テストEpic",
            num_stories=5,
            target_lines=500,
            knowledge_context=knowledge_context,
        )

        assert knowledge_context in prompt
        assert "参考情報" in prompt

    @pytest.mark.asyncio
    async def test_call_gemini_with_retry_success(self, epic_generator):
        """テスト5: Gemini API呼び出し成功"""
        mock_response = Mock()
        mock_response.text = '{"test": "success"}'

        with patch.object(epic_generator.model, "generate_content", return_value=mock_response):
            response = await epic_generator._call_gemini_with_retry("test prompt")
            assert response.text == '{"test": "success"}'

    @pytest.mark.asyncio
    async def test_call_gemini_with_retry_failure(self, epic_generator):
        """テスト6: Gemini API呼び出し失敗（リトライ）"""
        with patch.object(
            epic_generator.model, "generate_content", side_effect=Exception("API Error")
        ):
            with pytest.raises(Exception) as exc_info:
                await epic_generator._call_gemini_with_retry("test prompt", max_retries=2)
            assert "API" in str(exc_info.value) or "Gemini" in str(exc_info.value)

    def test_extract_json_from_response_valid(self, epic_generator):
        """テスト7: 有効なJSON抽出"""
        response_text = """
```json
[
  {
    "story_name": "テストストーリー",
    "description": "これはテストです",
    "priority": "high"
  }
]
```
"""
        stories = epic_generator._extract_json_from_response_robust(response_text)

        assert isinstance(stories, list)
        assert len(stories) == 1
        assert stories[0]["story_name"] == "テストストーリー"

    def test_extract_json_from_response_without_markdown(self, epic_generator):
        """テスト8: マークダウンなしJSON抽出"""
        response_text = '[{"story_name": "Story1", "description": "Desc1"}]'
        stories = epic_generator._extract_json_from_response_robust(response_text)

        assert isinstance(stories, list)
        assert len(stories) == 1

    def test_format_knowledge_context(self, epic_generator):
        """テスト9: ナレッジコンテキスト整形"""
        search_results = [
            {"title": "事例1", "content": "内容1" * 100},
            {"title": "事例2", "content": "内容2" * 100},
        ]

        context = epic_generator._format_knowledge_context(search_results)

        assert isinstance(context, str)
        assert "事例1" in context
        assert "事例2" in context

    def test_format_knowledge_context_empty(self, epic_generator):
        """テスト10: 空のナレッジコンテキスト"""
        context = epic_generator._format_knowledge_context([])
        assert context == ""


class TestPMAgentV33Epic:
    """PMAgentV33Epicクラスのテスト"""

    @pytest.fixture
    def mock_sheets_manager(self):
        """GoogleSheetsManagerのモック"""
        mock = Mock()
        mock.read_range = Mock(return_value=[["1"], ["2"], ["3"]])
        mock.append_rows = Mock(return_value=True)
        return mock

    @pytest.fixture
    def pm_agent(self, mock_sheets_manager):
        """PMAgentV33Epicインスタンス"""
        with patch("core_agents.pm_agent_v33_epic.SHEETS_AVAILABLE", True):
            with patch.dict("sys.modules", {"google.generativeai": MagicMock()}):
                agent = PMAgentV33Epic(sheets_manager=mock_sheets_manager)
                return agent

    def test_initialization(self, pm_agent):
        """テスト11: PMAgentV33Epic初期化"""
        assert pm_agent is not None
        assert pm_agent.sheets is not None

    def test_convert_to_pm_tasks_format(self, pm_agent):
        """テスト12: pm_tasks形式への変換"""
        stories = [
            {
                "story_name": "Story1",
                "description": "Description1",
                "priority": "high",
                "estimated_time": "2時間",
                "target_lines": 1000,
                "required_role": "autonomous_agent",
                "execution_type": "automated",
                "dependencies": "",
                "parent_goal_id": "epic_001",
            }
        ]

        pm_tasks = pm_agent.convert_to_pm_tasks_format(stories)

        assert isinstance(pm_tasks, list)
        assert len(pm_tasks) == 1
        assert pm_tasks[0]["description"] == "Description1"
        assert pm_tasks[0]["priority"] == "high"

    @pytest.mark.asyncio
    async def test_generate_epic_stories_delegation(self, pm_agent):
        """テスト13: generate_epic_storiesの委譲"""
        with patch.object(
            pm_agent.epic_generator,
            "generate_epic_stories",
            new_callable=AsyncMock,
            return_value=[{"story_name": "Test"}],
        ) as mock_generate:
            result = await pm_agent.generate_epic_stories(
                epic_id="epic_test", epic_description="Test Epic"
            )

            mock_generate.assert_called_once()
            assert len(result) == 1


# カバレッジ測定用
if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--cov=core_agents.pm_agent_v33_epic",
            "--cov-report=term-missing",
            "--cov-report=html:test_reports/pm_agent_v33_epic",
        ]
    )
