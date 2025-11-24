#!/usr/bin/env python3
"""
TaskExecutor v4 Sub-task 単体テスト

【Phase 2: M2.2 T2.2.1】
- テストケース: 15件以上
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

from agents.task_executor_v4_subtask import (SubTaskDecomposer,
                                             SubTaskMemoryManager,
                                             TaskExecutorV4SubTask)


class TestSubTaskDecomposer:
    """SubTaskDecomposerクラスのテスト"""

    @pytest.fixture
    def mock_api_key(self, monkeypatch):
        """GEMINI_API_KEYをモック"""
        monkeypatch.setenv("GEMINI_API_KEY", "test_api_key_12345")
        return "test_api_key_12345"

    @pytest.fixture
    def decomposer(self, mock_api_key):
        """SubTaskDecomposerインスタンス"""
        with patch("google.generativeai.configure"):
            with patch("google.generativeai.GenerativeModel"):
                decomposer = SubTaskDecomposer(api_key=mock_api_key)
                return decomposer

    def test_initialization_success(self, decomposer):
        """テスト1: 正常初期化"""
        assert decomposer is not None
        assert decomposer.api_key == "test_api_key_12345"

    def test_initialization_without_api_key(self, monkeypatch):
        """テスト2: API KEY未設定時のエラー"""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        with patch("google.generativeai.configure"):
            with pytest.raises(ValueError) as exc_info:
                SubTaskDecomposer(api_key=None)
            assert "GEMINI_API_KEY" in str(exc_info.value)

    def test_create_subtask_breakdown_prompt(self, decomposer):
        """テスト3: Sub-task分解プロンプト生成"""
        prompt = decomposer._create_subtask_breakdown_prompt(
            story_description="テストStory", num_subtasks=4, target_lines=300
        )

        assert isinstance(prompt, str)
        assert len(prompt) > 500
        assert "テストStory" in prompt
        assert "4個" in prompt
        assert "JSON" in prompt

    @pytest.mark.asyncio
    async def test_call_gemini_with_retry_success(self, decomposer):
        """テスト4: Gemini API呼び出し成功"""
        mock_response = Mock()
        mock_response.text = '{"test": "success"}'

        with patch.object(decomposer.model, "generate_content", return_value=mock_response):
            response = await decomposer._call_gemini_with_retry("test prompt")
            assert response.text == '{"test": "success"}'

    @pytest.mark.asyncio
    async def test_call_gemini_with_retry_failure(self, decomposer):
        """テスト5: Gemini API呼び出し失敗（リトライ）"""
        with patch.object(decomposer.model, "generate_content", side_effect=Exception("API Error")):
            with pytest.raises(Exception):
                await decomposer._call_gemini_with_retry("test prompt", max_retries=2)

    def test_extract_json_from_response_valid(self, decomposer):
        """テスト6: 有効なJSON抽出"""
        response_text = """
```json
[
  {
    "subtask_name": "テストサブタスク",
    "description": "これはテストです",
    "target_lines": 300
  }
]
```
"""
        subtasks = decomposer._extract_json_from_response_robust(response_text)

        assert isinstance(subtasks, list)
        assert len(subtasks) == 1
        assert subtasks[0]["subtask_name"] == "テストサブタスク"

    def test_extract_json_from_response_without_markdown(self, decomposer):
        """テスト7: マークダウンなしJSON抽出"""
        response_text = '[{"subtask_name": "Sub1", "description": "Desc1", "target_lines": 300}]'
        subtasks = decomposer._extract_json_from_response_robust(response_text)

        assert isinstance(subtasks, list)
        assert len(subtasks) == 1

    def test_parse_partial_json(self, decomposer):
        """テスト8: 部分的JSON解析"""
        text = '{"subtask_name": "Sub1", "description": "Desc1"} {"subtask_name": "Sub2", "description": "Desc2"}'
        subtasks = decomposer._parse_partial_json(text)

        assert isinstance(subtasks, list)
        assert len(subtasks) >= 1


class TestSubTaskMemoryManager:
    """SubTaskMemoryManagerクラスのテスト"""

    @pytest.fixture
    def memory_manager(self):
        """SubTaskMemoryManagerインスタンス"""
        return SubTaskMemoryManager()

    def test_initialization(self, memory_manager):
        """テスト9: 初期化"""
        assert memory_manager is not None
        assert len(memory_manager.subtask_results) == 0

    def test_save_subtask_result(self, memory_manager):
        """テスト10: Sub-task結果保存"""
        memory_manager.save_subtask_result(
            story_id="story_001", subtask_id="sub_001", result={"status": "success"}
        )

        results = memory_manager.get_story_results("story_001")
        assert len(results) == 1
        assert results[0]["subtask_id"] == "sub_001"

    def test_get_story_results_empty(self, memory_manager):
        """テスト11: 空のStory結果取得"""
        results = memory_manager.get_story_results("story_999")
        assert results == []

    def test_get_all_results(self, memory_manager):
        """テスト12: すべての結果取得"""
        memory_manager.save_subtask_result("story_001", "sub_001", {"status": "success"})
        memory_manager.save_subtask_result("story_002", "sub_002", {"status": "success"})

        all_results = memory_manager.get_all_results()
        assert len(all_results) == 2
        assert "story_001" in all_results
        assert "story_002" in all_results

    def test_clear_story_results(self, memory_manager):
        """テスト13: Story結果削除"""
        memory_manager.save_subtask_result("story_001", "sub_001", {"status": "success"})
        memory_manager.clear_story_results("story_001")

        results = memory_manager.get_story_results("story_001")
        assert results == []


class TestTaskExecutorV4SubTask:
    """TaskExecutorV4SubTaskクラスのテスト"""

    @pytest.fixture
    def mock_executor(self):
        """TaskExecutorV4SubTaskインスタンス（モック）"""
        with patch("agents.task_executor_v4_subtask.EXECUTOR_AVAILABLE", True):
            with patch("agents.task_executor_v4_subtask.HighQualityExecutorV6"):
                with patch.dict("sys.modules", {"google.generativeai": MagicMock()}):
                    executor = TaskExecutorV4SubTask()
                    return executor

    def test_initialization(self, mock_executor):
        """テスト14: 初期化"""
        assert mock_executor is not None
        assert mock_executor.decomposer is not None
        assert mock_executor.memory is not None

    @pytest.mark.asyncio
    async def test_execute_story_with_subtasks(self, mock_executor):
        """テスト15: Story→Sub-task実行"""
        # decomposerをモック
        mock_subtasks = [
            {
                "subtask_id": "sub_001",
                "subtask_name": "Test Sub-task",
                "description": "Test description",
                "target_lines": 300,
            }
        ]

        with patch.object(
            mock_executor.decomposer,
            "decompose_story_to_subtasks",
            new_callable=AsyncMock,
            return_value=mock_subtasks,
        ):
            # base_executorをモック
            with patch.object(
                mock_executor.base_executor, "execute_task", return_value={"status": "success"}
            ):
                result = await mock_executor.execute_story_with_subtasks(
                    story_id="story_test", story_description="Test story"
                )

                assert result["story_id"] == "story_test"
                assert result["total_subtasks"] == 1
                assert result["success_rate"] == 1.0


# カバレッジ測定用
if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--cov=agents.task_executor_v4_subtask",
            "--cov-report=term-missing",
            "--cov-report=html:test_reports/task_executor_v4_subtask",
        ]
    )
