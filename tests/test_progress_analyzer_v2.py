#!/usr/bin/env python3
"""
ProgressAnalyzer v2 単体テスト

【Phase 3: M3.1 T3.1.4】
- テストケース: 15件以上
- カバレッジ目標: 90%以上
- 既存システム保護
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# プロジェクトルート設定
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.integration.progress_analyzer_v2 import ProgressAnalyzer


class TestProgressAnalyzer:
    """ProgressAnalyzerクラスのテスト"""

    @pytest.fixture
    def analyzer(self):
        """ProgressAnalyzerインスタンス（モック）"""
        with patch("agents.integration.progress_analyzer_v2.ACCESSOR_AVAILABLE", True):
            with patch("agents.integration.progress_analyzer_v2.BaseDataAccessor"):
                analyzer = ProgressAnalyzer()
                return analyzer

    @pytest.fixture
    def mock_subtasks(self):
        """モックSub-taskデータ"""
        return [
            {"task_id": "sub_001", "status": "completed", "target_lines": 300},
            {"task_id": "sub_002", "status": "completed", "target_lines": 300},
            {"task_id": "sub_003", "status": "pending", "target_lines": 300},
            {"task_id": "sub_004", "status": "failed", "target_lines": 300},
        ]

    def test_initialization_success(self, analyzer):
        """テスト1: 正常初期化"""
        assert analyzer is not None

    def test_initialization_without_accessor(self):
        """テスト2: Accessor未使用時の初期化"""
        with patch("agents.integration.progress_analyzer_v2.ACCESSOR_AVAILABLE", False):
            analyzer = ProgressAnalyzer()
            assert analyzer is not None
            assert analyzer.accessor is None

    def test_analyze_story_progress_no_subtasks(self, analyzer):
        """テスト3: Sub-taskなしの進捗分析"""
        with patch.object(analyzer, "_get_story_subtasks", return_value=[]):
            result = analyzer.analyze_story_progress("story_001")

            # 必須キーの確認（KeyError防止）
            assert "story_id" in result
            assert "completion_rate" in result
            assert "total_subtasks" in result
            assert "completed_subtasks" in result
            assert "pending_subtasks" in result
            assert "failed_subtasks" in result
            assert "integration_ready" in result
            assert "status" in result
            assert "timestamp" in result
            assert "subtasks" in result

            # 値の確認
            assert result["completion_rate"] == 0.0
            assert result["total_subtasks"] == 0
            assert result["integration_ready"] == False
            assert result["status"] == "no_subtasks"

    def test_analyze_story_progress_with_subtasks(self, analyzer, mock_subtasks):
        """テスト4: Sub-task有りの進捗分析"""
        with patch.object(analyzer, "_get_story_subtasks", return_value=mock_subtasks):
            result = analyzer.analyze_story_progress("story_001")

            # 完了度計算の確認
            assert result["total_subtasks"] == 4
            assert result["completed_subtasks"] == 2
            assert result["pending_subtasks"] == 1
            assert result["failed_subtasks"] == 1
            assert result["completion_rate"] == 0.5  # 2/4
            assert result["integration_ready"] == False  # <80%
            assert result["status"] == "in_progress"

    def test_analyze_story_progress_high_completion(self, analyzer):
        """テスト5: 高完了率の進捗分析"""
        high_completion_subtasks = [
            {"task_id": "sub_001", "status": "completed", "target_lines": 300},
            {"task_id": "sub_002", "status": "completed", "target_lines": 300},
            {"task_id": "sub_003", "status": "completed", "target_lines": 300},
            {"task_id": "sub_004", "status": "completed", "target_lines": 300},
        ]

        with patch.object(analyzer, "_get_story_subtasks", return_value=high_completion_subtasks):
            result = analyzer.analyze_story_progress("story_001")

            assert result["completion_rate"] == 1.0  # 4/4
            assert result["integration_ready"] == True  # >=80%
            assert result["status"] == "completed"

    def test_detect_missing_subtasks_sufficient(self, analyzer):
        """テスト6: 十分なSub-task（不足なし）"""
        story = {"story_id": "story_001", "target_lines": 1000}

        existing_subtasks = [
            {"target_lines": 300},
            {"target_lines": 300},
            {"target_lines": 300},
            {"target_lines": 300},
        ]

        with patch.object(analyzer, "_get_story_subtasks", return_value=existing_subtasks):
            missing = analyzer.detect_missing_subtasks(story)

            assert len(missing) == 0

    def test_detect_missing_subtasks_insufficient(self, analyzer):
        """テスト7: 不足Sub-taskの検出"""
        story = {"story_id": "story_001", "target_lines": 1500}

        existing_subtasks = [
            {"target_lines": 300},
            {"target_lines": 300},
        ]

        with patch.object(analyzer, "_get_story_subtasks", return_value=existing_subtasks):
            missing = analyzer.detect_missing_subtasks(story)

            # 1500 - 600 = 900行不足 → 3個のSub-task
            assert len(missing) == 3
            assert all("subtask_name" in m for m in missing)
            assert all("target_lines" in m for m in missing)

    def test_get_integration_readiness_ready(self, analyzer):
        """テスト8: 統合準備完了の判定"""
        ready_subtasks = [
            {"task_id": "sub_001", "status": "completed", "target_lines": 300},
            {"task_id": "sub_002", "status": "completed", "target_lines": 300},
            {"task_id": "sub_003", "status": "completed", "target_lines": 300},
            {"task_id": "sub_004", "status": "completed", "target_lines": 300},
        ]

        with patch.object(analyzer, "_get_story_subtasks", return_value=ready_subtasks):
            readiness = analyzer.get_integration_readiness("story_001")

            assert "ready_for_integration" in readiness
            assert readiness["ready_for_integration"] == True
            assert all(readiness["checks"].values())

    def test_get_integration_readiness_not_ready(self, analyzer, mock_subtasks):
        """テスト9: 統合準備未完の判定"""
        with patch.object(analyzer, "_get_story_subtasks", return_value=mock_subtasks):
            readiness = analyzer.get_integration_readiness("story_001")

            assert readiness["ready_for_integration"] == False
            assert not readiness["checks"]["completion_rate_ok"]

    def test_determine_status_completed(self, analyzer):
        """テスト10: ステータス判定 - completed"""
        status = analyzer._determine_status(1.0)
        assert status == "completed"

    def test_determine_status_almost_done(self, analyzer):
        """テスト11: ステータス判定 - almost_done"""
        status = analyzer._determine_status(0.85)
        assert status == "almost_done"

    def test_determine_status_in_progress(self, analyzer):
        """テスト12: ステータス判定 - in_progress"""
        status = analyzer._determine_status(0.6)
        assert status == "in_progress"

    def test_determine_status_started(self, analyzer):
        """テスト13: ステータス判定 - started"""
        status = analyzer._determine_status(0.2)
        assert status == "started"

    def test_determine_status_not_started(self, analyzer):
        """テスト14: ステータス判定 - not_started"""
        status = analyzer._determine_status(0.0)
        assert status == "not_started"

    def test_get_recommendation_all_ready(self, analyzer):
        """テスト15: 推奨アクション - 準備完了"""
        checks = {
            "completion_rate_ok": True,
            "no_failed_subtasks": True,
            "all_tests_passed": True,
            "no_lint_errors": True,
        }
        recommendation = analyzer._get_recommendation(checks)
        assert "統合準備完了" in recommendation

    def test_get_recommendation_needs_work(self, analyzer):
        """テスト16: 推奨アクション - 改善必要"""
        checks = {
            "completion_rate_ok": False,
            "no_failed_subtasks": False,
            "all_tests_passed": True,
            "no_lint_errors": True,
        }
        recommendation = analyzer._get_recommendation(checks)
        assert "完了率" in recommendation
        assert "修正" in recommendation

    def test_get_story_subtasks_with_accessor(self, analyzer):
        """テスト17: Sub-task取得（Accessor有効）"""
        mock_tasks = [
            {"task_id": "sub_001", "parent_goal_id": "story_001"},
            {"task_id": "sub_002", "parent_goal_id": "story_001"},
        ]

        with patch.object(analyzer.accessor, "read_sheet_as_dicts", return_value=mock_tasks):
            subtasks = analyzer._get_story_subtasks("story_001")
            assert len(subtasks) == 2

    def test_get_story_subtasks_without_accessor(self):
        """テスト18: Sub-task取得（Accessor無効）"""
        with patch("agents.integration.progress_analyzer_v2.ACCESSOR_AVAILABLE", False):
            analyzer = ProgressAnalyzer()
            subtasks = analyzer._get_story_subtasks("story_001")
            assert subtasks == []


# カバレッジ測定用
if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--cov=agents.integration.progress_analyzer_v2",
            "--cov-report=term-missing",
            "--cov-report=html:test_reports/progress_analyzer_v2",
        ]
    )
