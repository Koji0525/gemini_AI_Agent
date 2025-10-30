#!/usr/bin/env python3
"""
データ統合パイプラインテスト - 完全版
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.data_integration.pipeline import DataIntegrationPipeline
from tools.data_integration.models import UnifiedLogEntry, SourceType, ContentType
from datetime import datetime


class TestDataIntegrationPipeline:
    """データ統合パイプラインテスト"""

    def test_pipeline_initialization(self):
        """パイプライン初期化テスト - 引数不一致チェック"""
        config = {"sources": {"conversation_logs": {"enabled": False}, "spreadsheet_logs": {"enabled": False}}}

        # 引数不一致がないかテスト
        pipeline = DataIntegrationPipeline(config)
        assert pipeline.config == config
        assert hasattr(pipeline, "sheets_manager")
        assert hasattr(pipeline, "source_registry")
        assert hasattr(pipeline, "pattern_extractor")

    def test_pipeline_invalid_arguments(self):
        """不正な引数でのテスト"""
        with pytest.raises(TypeError):
            # 引数過多でエラーになることを確認
            pipeline = DataIntegrationPipeline({}, "extra_arg")

    @patch("tools.data_integration.pipeline.GoogleSheetsManager")
    def test_pipeline_with_mock_sheets(self, mock_sheets):
        """モックを使用したパイプラインテスト"""
        config = {
            "sources": {"conversation_logs": {"enabled": False}, "spreadsheet_logs": {"enabled": False}},
            "knowledge_base": {"sheet_name": "test_knowledge_base"},
        }

        # モックの設定
        mock_instance = Mock()
        mock_sheets.return_value = mock_instance

        pipeline = DataIntegrationPipeline(config)

        # パイプライン実行（データなし）
        metrics = pipeline.run()

        assert "total_entries" in metrics
        assert "saved_count" in metrics
        assert "patterns_found" in metrics
        assert "timestamp" in metrics

    def test_pattern_extraction_with_sample_data(self):
        """サンプルデータでのパターン抽出テスト"""
        from tools.data_integration.extractors import PatternExtractor

        config = {
            "failure_patterns": {"min_confidence": 0.6, "keywords": ["error", "failed", "エラー"]},
            "fix_recipes": {"min_confidence": 0.7, "success_indicators": ["解決", "修正", "success"]},
            "success_patterns": {"min_confidence": 0.8, "keywords": ["成功", "completed"]},
        }

        extractor = PatternExtractor(config)

        # サンプルエントリを作成
        sample_entries = [
            UnifiedLogEntry(
                timestamp=datetime.now(),
                source_type=SourceType.CONVERSATION,
                source_id="test_1",
                content_type=ContentType.ERROR,
                content="認証エラーが発生しました",
                metadata={},
            ),
            UnifiedLogEntry(
                timestamp=datetime.now(),
                source_type=SourceType.SPREADSHEET,
                source_id="test_2",
                content_type=ContentType.TASK,
                content="問題を解決しました",
                metadata={},
            ),
        ]

        patterns = extractor.extract_all_patterns(sample_entries)

        assert "failure_patterns" in patterns
        assert "fix_recipes" in patterns
        assert "success_patterns" in patterns
        assert isinstance(patterns["failure_patterns"], list)
        assert isinstance(patterns["fix_recipes"], list)
        assert isinstance(patterns["success_patterns"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
