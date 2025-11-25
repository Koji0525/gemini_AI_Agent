#!/usr/bin/env python3
"""
DependencyResolver v2 単体テスト（修正版）

【Phase 3: M3.3テスト】
- テストケース: 16件
- カバレッジ目標: 90%以上
- 期待値修正: モジュール名→ファイル名
"""

import sys
from pathlib import Path

import pytest

# プロジェクトルート設定
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.integration.dependency_resolver_v2 import DependencyResolver


class TestDependencyResolver:
    """DependencyResolverクラスのテスト"""

    @pytest.fixture
    def resolver(self):
        """DependencyResolverインスタンス"""
        return DependencyResolver()

    def test_initialization_success(self, resolver):
        """テスト1: 正常初期化"""
        assert resolver is not None
        assert len(resolver.stdlib_modules) > 0
        assert len(resolver.common_imports) > 0

    def test_detect_undefined_variables_simple(self, resolver):
        """テスト2: 単純な未定義変数検出"""
        code = """
def main():
    path = Path('/tmp')
"""
        undefined = resolver._detect_undefined_variables(code)
        assert "Path" in undefined

    def test_detect_undefined_variables_multiple(self, resolver):
        """テスト3: 複数の未定義変数検出"""
        code = """
def process():
    data = Dict()
    items = List()
    path = Path('/tmp')
"""
        undefined = resolver._detect_undefined_variables(code)
        assert "Dict" in undefined
        assert "List" in undefined
        assert "Path" in undefined

    def test_detect_undefined_variables_with_definitions(self, resolver):
        """テスト4: 定義済み変数は未定義扱いしない"""
        code = """
def my_function():
    pass

my_function()
"""
        undefined = resolver._detect_undefined_variables(code)
        assert "my_function" not in undefined

    def test_infer_required_imports(self, resolver):
        """テスト5: 必要なimport推定"""
        undefined = {"Path", "Dict", "UnknownType"}
        imports = resolver._infer_required_imports(undefined)

        assert "from pathlib import Path" in imports
        assert "from typing import Dict" in imports

    def test_extract_existing_imports(self, resolver):
        """テスト6: 既存import抽出"""
        code = """
import os
import sys
from pathlib import Path

def main():
    pass
"""
        imports = resolver._extract_existing_imports(code)

        assert "import os" in imports
        assert "import sys" in imports
        assert "from pathlib import Path" in imports

    def test_add_imports_simple(self, resolver):
        """テスト7: import追加（単純）"""
        code = """
def main():
    pass
"""
        new_imports = ["import os", "from pathlib import Path"]
        result = resolver._add_imports(code, new_imports)

        assert "import os" in result
        assert "from pathlib import Path" in result

    def test_add_imports_with_shebang(self, resolver):
        """テスト8: shebang付きコードへのimport追加"""
        code = """#!/usr/bin/env python3

def main():
    pass
"""
        new_imports = ["import os"]
        result = resolver._add_imports(code, new_imports)

        assert result.startswith("#!/usr/bin/env python3")
        assert "import os" in result

    def test_resolve_dependencies_adds_missing(self, resolver):
        """テスト9: 不足import自動追加"""
        code = """
def main():
    path = Path('/tmp')
"""
        resolved = resolver.resolve_dependencies(code)

        assert "from pathlib import Path" in resolved

    def test_resolve_dependencies_no_duplicates(self, resolver):
        """テスト10: 既存importを重複追加しない"""
        code = """
from pathlib import Path

def main():
    path = Path('/tmp')
"""
        resolved = resolver.resolve_dependencies(code)

        import_count = resolved.count("from pathlib import Path")
        assert import_count == 1

    def test_build_dependency_graph_simple(self, resolver):
        """テスト11: 依存関係グラフ構築（修正版）"""
        files = {
            "module_a.py": "import module_b",
            "module_b.py": "import module_c",
            "module_c.py": "pass",
        }
        graph = resolver._build_dependency_graph(files)

        # グラフにはファイル名が格納される
        assert "module_b.py" in graph["module_a.py"]
        assert "module_c.py" in graph["module_b.py"]

    def test_detect_circular_dependencies_none(self, resolver):
        """テスト12: 循環依存なし"""
        files = {
            "module_a.py": "import module_b",
            "module_b.py": "import module_c",
            "module_c.py": "pass",
        }
        circular = resolver.detect_circular_dependencies(files)

        assert len(circular) == 0

    def test_detect_circular_dependencies_exists(self, resolver):
        """テスト13: 循環依存あり"""
        files = {"module_a.py": "import module_b", "module_b.py": "import module_a"}
        circular = resolver.detect_circular_dependencies(files)

        # 循環が検出される
        assert len(circular) > 0
        # 循環の内容を確認
        assert any("module_a.py" in cycle and "module_b.py" in cycle for cycle in circular)

    def test_get_builtins(self, resolver):
        """テスト14: 組み込み関数リスト取得"""
        builtins = resolver._get_builtins()

        assert "print" in builtins
        assert "len" in builtins
        assert "range" in builtins

    def test_get_stdlib_modules(self, resolver):
        """テスト15: 標準ライブラリリスト取得"""
        stdlib = resolver._get_stdlib_modules()

        assert "os" in stdlib
        assert "sys" in stdlib
        assert "pathlib" in stdlib

    def test_extract_imports_from_code(self, resolver):
        """テスト16: コードからimport抽出"""
        code = """
import os
import sys
from pathlib import Path
"""
        imports = resolver._extract_imports_from_code(code)

        assert "os" in imports
        assert "sys" in imports
        assert "pathlib" in imports


# カバレッジ測定用
if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--cov=agents.integration.dependency_resolver_v2",
            "--cov-report=term-missing",
        ]
    )
