#!/usr/bin/env python3
"""
IntegrationTester v2 単体テスト

【Phase 3: M3.4テスト】
- テストケース: 15件以上
- カバレッジ目標: 90%以上
"""

import sys
from pathlib import Path

import pytest

# プロジェクトルート設定
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.integration.integration_tester_v2 import IntegrationTester


class TestIntegrationTester:
    """IntegrationTesterクラスのテスト"""

    @pytest.fixture
    def tester(self):
        """IntegrationTesterインスタンス（モック）"""
        from unittest.mock import patch

        with patch("agents.integration.integration_tester_v2.ACCESSOR_AVAILABLE", False):
            tester = IntegrationTester()
            return tester

    @pytest.fixture
    def valid_code(self):
        """有効なコード"""
        return {
            "main.py": """
import os

def main():
    print("Hello, World!")

if __name__ == '__main__':
    main()
"""
        }

    @pytest.fixture
    def invalid_code(self):
        """無効なコード（構文エラー）"""
        return {
            "error.py": """
def broken_function()
    print("Missing colon")
"""
        }

    def test_initialization_success(self, tester):
        """テスト1: 正常初期化"""
        assert tester is not None

    def test_check_syntax_valid(self, tester, valid_code):
        """テスト2: 構文チェック（正常）"""
        results = tester._check_syntax(valid_code)

        assert len(results) == 1
        assert results[0]["valid"] == True
        assert results[0]["message"] == "OK"

    def test_check_syntax_invalid(self, tester, invalid_code):
        """テスト3: 構文チェック（エラー）"""
        results = tester._check_syntax(invalid_code)

        assert len(results) == 1
        assert results[0]["valid"] == False
        assert "line" in results[0]

    def test_check_lint_no_issues(self, tester, valid_code):
        """テスト4: Lintチェック（問題なし）"""
        results = tester._check_lint(valid_code)

        assert len(results) == 1
        assert len(results[0]["issues"]) == 0

    def test_check_lint_line_too_long(self, tester):
        """テスト5: Lintチェック（行が長い）"""
        long_line_code = {"long.py": 'x = "' + "a" * 130 + '"  # This line is too long'}
        results = tester._check_lint(long_line_code)

        assert len(results) == 1
        assert len(results[0]["issues"]) > 0
        assert results[0]["issues"][0]["type"] == "line_too_long"

    def test_verify_imports_valid(self, tester, valid_code):
        """テスト6: import検証（正常）"""
        results = tester._verify_imports(valid_code)

        assert len(results) == 1
        assert results[0]["valid"] == True
        assert "os" in results[0]["imports"]

    def test_verify_imports_invalid(self, tester, invalid_code):
        """テスト7: import検証（エラー）"""
        results = tester._verify_imports(invalid_code)

        assert len(results) == 1
        assert results[0]["valid"] == False

    def test_test_integrated_code_success(self, tester, valid_code):
        """テスト8: 統合コードテスト（成功）"""
        result = tester.test_integrated_code("story_test", valid_code)

        assert result["test_passed"] == True
        assert result["total_errors"] == 0
        assert "syntax_check" in result
        assert "lint_check" in result
        assert "import_check" in result

    def test_test_integrated_code_failure(self, tester, invalid_code):
        """テスト9: 統合コードテスト（失敗）"""
        result = tester.test_integrated_code("story_test", invalid_code)

        assert result["test_passed"] == False
        assert result["total_errors"] > 0

    def test_generate_fix_suggestions_syntax_error(self, tester, invalid_code):
        """テスト10: 修正提案生成（構文エラー）"""
        test_result = tester.test_integrated_code("story_test", invalid_code)
        suggestions = tester.generate_fix_suggestions(test_result)

        assert len(suggestions) > 0
        assert any(s["type"] == "syntax_error" for s in suggestions)

    def test_generate_fix_suggestions_empty(self, tester, valid_code):
        """テスト11: 修正提案生成（問題なし）"""
        test_result = tester.test_integrated_code("story_test", valid_code)
        suggestions = tester.generate_fix_suggestions(test_result)

        # 問題がないので提案も0件
        assert len(suggestions) == 0

    def test_suggest_syntax_fix_invalid_syntax(self, tester):
        """テスト12: 構文エラー修正提案"""
        error = {"message": "invalid syntax"}
        suggestion = tester._suggest_syntax_fix(error)

        assert "構文エラー" in suggestion

    def test_suggest_syntax_fix_indent(self, tester):
        """テスト13: インデントエラー修正提案"""
        error = {"message": "unexpected indent"}
        suggestion = tester._suggest_syntax_fix(error)

        assert "インデント" in suggestion

    def test_suggest_lint_fix_line_too_long(self, tester):
        """テスト14: Lint問題修正提案"""
        issue = {"type": "line_too_long", "message": "Line too long"}
        suggestion = tester._suggest_lint_fix(issue)

        assert "行を分割" in suggestion

    def test_suggest_import_fix(self, tester):
        """テスト15: import問題修正提案"""
        error = {"message": "Module not found"}
        suggestion = tester._suggest_import_fix(error)

        assert "import" in suggestion


# カバレッジ測定用
if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--cov=agents.integration.integration_tester_v2",
            "--cov-report=term-missing",
        ]
    )
