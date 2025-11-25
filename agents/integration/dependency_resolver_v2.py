#!/usr/bin/env python3
"""
DependencyResolver v2 - 依存関係解決エージェント（修正版）

【Phase 3: M3.3実装】
- テストエラー修正: モジュール名とファイル名のマッピング
"""

import ast
import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set

# プロジェクトルート設定
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# ロギング設定
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)


class DependencyResolver:
    """依存関係解決エージェント"""

    def __init__(self):
        """初期化"""
        self.stdlib_modules = self._get_stdlib_modules()

        self.common_imports = {
            "Path": "from pathlib import Path",
            "datetime": "from datetime import datetime",
            "defaultdict": "from collections import defaultdict",
            "Dict": "from typing import Dict",
            "List": "from typing import List",
            "Optional": "from typing import Optional",
            "Any": "from typing import Any",
            "Tuple": "from typing import Tuple",
            "Set": "from typing import Set",
        }

        logger.info("✅ DependencyResolver 初期化完了")

    def resolve_dependencies(self, code: str, available_modules: Optional[List[str]] = None) -> str:
        """依存関係を自動解決"""
        logger.info("🔧 依存関係解決開始...")

        try:
            undefined_vars = self._detect_undefined_variables(code)
            logger.info(f"   未定義変数: {len(undefined_vars)}個")

            required_imports = self._infer_required_imports(undefined_vars)
            logger.info(f"   必要なimport: {len(required_imports)}件")

            existing_imports = self._extract_existing_imports(code)
            logger.info(f"   既存import: {len(existing_imports)}件")

            missing_imports = [imp for imp in required_imports if imp not in existing_imports]

            if missing_imports:
                logger.info(f"   追加import: {len(missing_imports)}件")
                resolved_code = self._add_imports(code, missing_imports)
            else:
                logger.info("   追加import: 0件（すべて存在）")
                resolved_code = code

            logger.info("✅ 依存関係解決完了")
            return resolved_code

        except Exception as e:
            logger.error(f"❌ 依存関係解決エラー: {e}")
            import traceback

            traceback.print_exc()
            return code

    def detect_circular_dependencies(self, files: Dict[str, str]) -> List[List[str]]:
        """循環依存を検出"""
        logger.info("🔍 循環依存検出開始...")

        try:
            dependencies = self._build_dependency_graph(files)
            circular = self._find_cycles(dependencies)

            if circular:
                logger.warning(f"⚠️ {len(circular)}個の循環依存を検出")
                for cycle in circular:
                    logger.warning(f"   循環: {' -> '.join(cycle)}")
            else:
                logger.info("✅ 循環依存なし")

            return circular

        except Exception as e:
            logger.error(f"❌ 循環依存検出エラー: {e}")
            return []

    def _detect_undefined_variables(self, code: str) -> Set[str]:
        """未定義変数を検出"""
        undefined = set()

        try:
            tree = ast.parse(code)

            defined = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    defined.add(node.name)
                elif isinstance(node, ast.ClassDef):
                    defined.add(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            defined.add(target.id)

            used = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    used.add(node.id)

            undefined = used - defined - self._get_builtins()

        except SyntaxError:
            logger.warning("⚠️ 構文エラーにより未定義変数検出をスキップ")

        return undefined

    def _infer_required_imports(self, undefined_vars: Set[str]) -> List[str]:
        """未定義変数から必要なimportを推定"""
        required_imports = []

        for var in undefined_vars:
            if var in self.common_imports:
                import_stmt = self.common_imports[var]
                if import_stmt not in required_imports:
                    required_imports.append(import_stmt)

        return required_imports

    def _extract_existing_imports(self, code: str) -> List[str]:
        """既存のimport文を抽出"""
        imports = []

        for line in code.split("\n"):
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                imports.append(line)

        return imports

    def _add_imports(self, code: str, imports: List[str]) -> str:
        """import文を追加"""
        lines = code.split("\n")
        insert_pos = 0

        # shebangをスキップ
        if lines and lines[0].startswith("#!"):
            insert_pos = 1

        # docstringをスキップ
        if len(lines) > insert_pos:
            if lines[insert_pos].strip().startswith('"""') or lines[insert_pos].strip().startswith(
                "'''"
            ):
                for i in range(insert_pos + 1, len(lines)):
                    if '"""' in lines[i] or "'''" in lines[i]:
                        insert_pos = i + 1
                        break

        # 既存のimport文の後に追加
        for i in range(insert_pos, len(lines)):
            line = lines[i].strip()
            if not (line.startswith("import ") or line.startswith("from ") or line == ""):
                insert_pos = i
                break

        for imp in sorted(imports):
            lines.insert(insert_pos, imp)
            insert_pos += 1

        return "\n".join(lines)

    def _build_dependency_graph(self, files: Dict[str, str]) -> Dict[str, List[str]]:
        """
        依存関係グラフを構築（修正版）

        【修正内容】
        モジュール名（module_a）とファイル名（module_a.py）を
        適切にマッピングする
        """
        graph = defaultdict(list)

        # ファイル名からモジュール名へのマッピング
        file_to_module = {}
        for file_name in files.keys():
            # module_a.py -> module_a
            module_name = file_name.replace(".py", "")
            file_to_module[file_name] = module_name

        for file_name, code in files.items():
            # このファイルがimportしているモジュール名を抽出
            imported_modules = self._extract_imports_from_code(code)

            for imported_module in imported_modules:
                # imported_module（例: module_b）を
                # ファイル名（例: module_b.py）に変換
                for fname, mname in file_to_module.items():
                    if mname == imported_module:
                        graph[file_name].append(fname)
                        break

        return dict(graph)

    def _extract_imports_from_code(self, code: str) -> List[str]:
        """コードからimportされているモジュール名を抽出"""
        imported_modules = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_modules.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imported_modules.append(node.module)

        except SyntaxError:
            logger.warning("⚠️ 構文エラーによりimport抽出をスキップ")

        return imported_modules

    def _find_cycles(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """グラフから循環を検出（DFS）"""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path[:])
                elif neighbor in rec_stack:
                    # 循環を検出
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in cycles:
                        cycles.append(cycle)

            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def _get_stdlib_modules(self) -> Set[str]:
        """標準ライブラリのリストを取得"""
        return {
            "os",
            "sys",
            "time",
            "datetime",
            "json",
            "csv",
            "re",
            "pathlib",
            "typing",
            "collections",
            "itertools",
            "functools",
            "math",
            "random",
            "logging",
            "unittest",
            "asyncio",
            "threading",
            "multiprocessing",
            "subprocess",
            "argparse",
            "configparser",
            "io",
            "tempfile",
            "shutil",
            "glob",
            "urllib",
            "http",
            "socket",
            "email",
            "smtplib",
            "sqlite3",
            "pickle",
            "gzip",
            "zipfile",
            "tarfile",
            "hashlib",
            "hmac",
            "secrets",
            "base64",
            "binascii",
            "struct",
            "array",
            "queue",
            "heapq",
            "bisect",
            "copy",
            "pprint",
            "enum",
            "dataclasses",
            "abc",
        }

    def _get_builtins(self) -> Set[str]:
        """組み込み変数・関数のリストを取得"""
        return {
            "abs",
            "all",
            "any",
            "ascii",
            "bin",
            "bool",
            "bytes",
            "chr",
            "dict",
            "dir",
            "divmod",
            "enumerate",
            "filter",
            "float",
            "format",
            "frozenset",
            "getattr",
            "hasattr",
            "hash",
            "hex",
            "id",
            "input",
            "int",
            "isinstance",
            "issubclass",
            "iter",
            "len",
            "list",
            "map",
            "max",
            "min",
            "next",
            "object",
            "oct",
            "open",
            "ord",
            "pow",
            "print",
            "range",
            "repr",
            "reversed",
            "round",
            "set",
            "setattr",
            "slice",
            "sorted",
            "str",
            "sum",
            "tuple",
            "type",
            "zip",
            "True",
            "False",
            "None",
            "Exception",
            "ValueError",
            "TypeError",
            "KeyError",
            "IndexError",
            "RuntimeError",
            "NotImplementedError",
            "AttributeError",
        }


# テスト用
def test_dependency_resolver():
    """Phase 3 M3.3 テスト実行"""
    print("=" * 60)
    print("Phase 3: DependencyResolver (F13) テスト実行（修正版）")
    print("=" * 60)
    print()

    try:
        resolver = DependencyResolver()
        print()

        # テスト1: 未定義変数検出
        print("🧪 テスト1: 未定義変数検出")
        test_code1 = """
def main():
    path = Path('/tmp')
    data = Dict()
"""
        undefined = resolver._detect_undefined_variables(test_code1)
        print(f"   未定義変数: {undefined}")
        print()

        # テスト2: 依存関係解決
        print("🧪 テスト2: 依存関係解決")
        resolved = resolver.resolve_dependencies(test_code1)
        print(f"   解決後のコード長: {len(resolved)}文字")
        print(f"   import追加確認: {'from pathlib import Path' in resolved}")
        print()

        # テスト3: 循環依存検出
        print("🧪 テスト3: 循環依存検出")
        test_files = {
            "module_a.py": "import module_b\n\nclass A: pass",
            "module_b.py": "import module_a\n\nclass B: pass",
        }
        circular = resolver.detect_circular_dependencies(test_files)
        print(f"   循環依存: {len(circular)}件")
        if circular:
            for cycle in circular:
                print(f"     循環: {' -> '.join(cycle)}")
        print()

        print("=" * 60)
        print("Phase 3 M3.3 テスト完了 ✅")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(test_dependency_resolver())
