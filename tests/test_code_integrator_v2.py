#!/usr/bin/env python3
"""
CodeIntegrator v2 単体テスト

【Phase 3: M3.2テスト】
- テストケース: 15件以上
- カバレッジ目標: 90%以上
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# プロジェクトルート設定
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.integration.code_integrator_v2 import CodeIntegrator


class TestCodeIntegrator:
    """CodeIntegratorクラスのテスト"""

    @pytest.fixture
    def integrator(self, tmp_path):
        """CodeIntegratorインスタンス（モック）"""
        with patch("agents.integration.code_integrator_v2.ACCESSOR_AVAILABLE", False):
            integrator = CodeIntegrator(output_dir=tmp_path)
            return integrator

    @pytest.fixture
    def sample_files(self):
        """サンプルファイル"""
        return [
            {
                "subtask_id": "sub_001",
                "file_name": "api.py",
                "content": "import os\nimport sys\n\nclass API:\n    pass",
                "size": 100,
            },
            {
                "subtask_id": "sub_002",
                "file_name": "models.py",
                "content": "from typing import Dict\n\nclass Model:\n    pass",
                "size": 50,
            },
            {
                "subtask_id": "sub_003",
                "file_name": "README.md",
                "content": "# README\n\nThis is a test.",
                "size": 30,
            },
        ]

    def test_initialization_success(self, integrator):
        """テスト1: 正常初期化"""
        assert integrator is not None
        assert integrator.output_dir.exists()

    def test_categorize_files_python(self, integrator, sample_files):
        """テスト2: Pythonファイルの分類"""
        categorized = integrator._categorize_files(sample_files)

        assert "python" in categorized
        assert len(categorized["python"]) == 2
        assert categorized["python"][0]["file_name"] == "api.py"

    def test_categorize_files_markdown(self, integrator, sample_files):
        """テスト3: Markdownファイルの分類"""
        categorized = integrator._categorize_files(sample_files)

        assert "markdown" in categorized
        assert len(categorized["markdown"]) == 1
        assert categorized["markdown"][0]["file_name"] == "README.md"

    def test_categorize_files_empty(self, integrator):
        """テスト4: 空のファイルリスト"""
        categorized = integrator._categorize_files([])
        assert categorized == {}

    def test_extract_imports_simple(self, integrator):
        """テスト5: 単純なimport抽出"""
        code = """
import os
import sys
from pathlib import Path
"""
        imports = integrator._extract_imports(code)

        assert len(imports) == 3
        assert "import os" in imports
        assert "import sys" in imports
        assert "from pathlib import Path" in imports

    def test_extract_imports_duplicates(self, integrator):
        """テスト6: 重複import抽出"""
        code = """
import os
import os
import sys
"""
        imports = integrator._extract_imports(code)

        # setなので重複は自動削除される
        assert len(imports) == 2
        assert "import os" in imports

    def test_extract_classes(self, integrator):
        """テスト7: クラス定義抽出"""
        code = """
class MyClass:
    def __init__(self):
        pass

class AnotherClass:
    pass
"""
        classes = integrator._extract_classes(code)

        assert len(classes) == 2
        assert "MyClass" in classes
        assert "AnotherClass" in classes

    def test_extract_functions(self, integrator):
        """テスト8: 関数定義抽出"""
        code = """
def my_function():
    return True

def another_function(x, y):
    return x + y
"""
        functions = integrator._extract_functions(code)

        assert len(functions) == 2
        assert "my_function" in functions
        assert "another_function" in functions

    def test_integrate_python_files_single(self, integrator):
        """テスト9: 単一Pythonファイル統合"""
        python_files = [{"file_name": "api.py", "content": "import os\n\nclass API:\n    pass"}]

        integrated = integrator._integrate_python_files(python_files)

        assert "api.py" in integrated
        assert "import os" in integrated["api.py"]

    def test_integrate_python_files_multiple(self, integrator):
        """テスト10: 複数Pythonファイル統合（重複あり）"""
        python_files = [
            {"file_name": "api.py", "content": "import os\n\nclass API:\n    pass"},
            {"file_name": "api.py", "content": "import sys\n\nclass API:\n    pass"},
        ]

        integrated = integrator._integrate_python_files(python_files)

        assert "api.py" in integrated
        # マージされている
        assert len(integrated["api.py"]) > 0

    def test_merge_markdown(self, integrator):
        """テスト11: Markdownファイルマージ"""
        md_files = [
            {"subtask_id": "sub_001", "content": "# Section 1\n\nContent 1"},
            {"subtask_id": "sub_002", "content": "# Section 2\n\nContent 2"},
        ]

        merged = integrator._merge_markdown(md_files)

        assert "統合ドキュメント" in merged
        assert "sub_001" in merged
        assert "sub_002" in merged

    def test_resolve_imports(self, integrator):
        """テスト12: import文調整"""
        code = """
import os
import sys
from pathlib import Path

def main():
    pass
"""
        adjusted = integrator.resolve_imports(code)

        assert "import os" in adjusted
        assert "def main():" in adjusted

    def test_resolve_imports_duplicates(self, integrator):
        """テスト13: 重複import削除"""
        code = """
import os
import os
import sys
import sys

def main():
    pass
"""
        adjusted = integrator.resolve_imports(code)

        # 重複が削除されている
        import_count = adjusted.count("import os")
        assert import_count == 1

    def test_save_integrated_files(self, integrator, tmp_path):
        """テスト14: 統合ファイル保存"""
        python_files = {"api.py": "import os\n\nclass API:\n    pass"}
        other_files = {"README.md": "# README\n\nTest"}

        output_files = integrator._save_integrated_files("story_test", python_files, other_files)

        assert len(output_files) == 2
        assert all(f.exists() for f in output_files)

    def test_integrate_subtasks_mock(self, integrator):
        """テスト15: Sub-task統合（モック）"""
        with patch.object(integrator, "_collect_subtask_outputs", return_value=[]):
            result = integrator.integrate_subtasks("story_test", ["sub_001", "sub_002"])

            assert "story_id" in result
            assert "integration_success" in result


# カバレッジ測定用
if __name__ == "__main__":
    pytest.main(
        [__file__, "-v", "--cov=agents.integration.code_integrator_v2", "--cov-report=term-missing"]
    )
