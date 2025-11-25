#!/usr/bin/env python3
"""
EpicOrchestrator テストスイート

Phase 4で実装したEpicOrchestrator機能の検証
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestEpicOrchestrator:
    """EpicOrchestratorクラスのテスト"""

    def test_import_success(self):
        """インポートが成功すること"""
        from agents.epic_orchestrator import EpicOrchestrator

        assert EpicOrchestrator is not None

    def test_initialization(self):
        """初期化が正常に行われること"""
        from agents.epic_orchestrator import EpicOrchestrator

        mock_sheets = Mock()
        mock_knowledge = Mock()

        orchestrator = EpicOrchestrator(
            sheets_manager=mock_sheets, knowledge_wrapper=mock_knowledge, api_key="test_key"
        )

        assert orchestrator is not None
        assert hasattr(orchestrator, "pm_agent")
        assert hasattr(orchestrator, "task_executor")

    def test_has_phase1_integration(self):
        """Phase 1（PMAgentV33Epic）が統合されていること"""
        from agents.epic_orchestrator import EpicOrchestrator

        mock_sheets = Mock()
        mock_knowledge = Mock()

        orchestrator = EpicOrchestrator(
            sheets_manager=mock_sheets, knowledge_wrapper=mock_knowledge, api_key="test_key"
        )

        assert hasattr(orchestrator, "pm_agent")
        assert orchestrator.pm_agent is not None

    def test_has_phase2_integration(self):
        """Phase 2（TaskExecutorV4）が統合されていること"""
        from agents.epic_orchestrator import EpicOrchestrator

        mock_sheets = Mock()
        mock_knowledge = Mock()

        orchestrator = EpicOrchestrator(
            sheets_manager=mock_sheets, knowledge_wrapper=mock_knowledge, api_key="test_key"
        )

        assert hasattr(orchestrator, "task_executor")
        assert orchestrator.task_executor is not None

    def test_has_phase3_integrations(self):
        """Phase 3（F11-F14）が統合されていること"""
        from agents.epic_orchestrator import EpicOrchestrator

        mock_sheets = Mock()
        mock_knowledge = Mock()

        orchestrator = EpicOrchestrator(
            sheets_manager=mock_sheets, knowledge_wrapper=mock_knowledge, api_key="test_key"
        )

        assert hasattr(orchestrator, "progress_analyzer")
        assert hasattr(orchestrator, "code_integrator")
        assert hasattr(orchestrator, "dependency_resolver")
        assert hasattr(orchestrator, "integration_tester")

    def test_execute_epic_flow_dry_run(self):
        """Epic実行フロー（ドライラン）が動作すること"""
        from agents.epic_orchestrator import EpicOrchestrator

        mock_sheets = Mock()
        mock_knowledge = Mock()

        orchestrator = EpicOrchestrator(
            sheets_manager=mock_sheets, knowledge_wrapper=mock_knowledge, api_key="test_key"
        )

        # ドライラン実行
        with patch.object(orchestrator, "_get_epic_data") as mock_get:
            mock_get.return_value = {"goal_id": "test_001", "goal_description": "テストEpic"}

            with patch.object(orchestrator, "_get_existing_stories") as mock_stories:
                mock_stories.return_value = []

                result = orchestrator.execute_epic_flow(epic_id="test_001", dry_run=True)

                assert result is not None
                assert "status" in result
                assert "epic_id" in result

    def test_execute_epic_flow_result_structure(self):
        """実行結果の構造が正しいこと"""
        from agents.epic_orchestrator import EpicOrchestrator

        mock_sheets = Mock()
        mock_knowledge = Mock()

        orchestrator = EpicOrchestrator(
            sheets_manager=mock_sheets, knowledge_wrapper=mock_knowledge, api_key="test_key"
        )

        with patch.object(orchestrator, "_get_epic_data") as mock_get:
            mock_get.return_value = {"goal_id": "test_001", "goal_description": "テストEpic"}

            with patch.object(orchestrator, "_get_existing_stories") as mock_stories:
                mock_stories.return_value = []

                result = orchestrator.execute_epic_flow(epic_id="test_001", dry_run=True)

                # 必須キーの確認
                assert "epic_id" in result
                assert "status" in result
                assert "stories_completed" in result
                assert "stories_total" in result
                assert "errors" in result
                assert "execution_time" in result


# ==
# 開発ログ
# ==
"""
何が起きた:
Phase 4（EpicOrchestrator）の実装とテストを作成

狙い:
1. Epic→Story→Sub-taskの全体制御
2. Phase 1-3の統合
3. 既存システムとの後方互換性
4. 段階的な実装とテスト
"""
