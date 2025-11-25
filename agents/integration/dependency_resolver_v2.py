"""
DependencyResolverV2 - 依存関係解決エージェント
Version: 2.0
機能: import文自動追加、循環依存検出、未定義変数検出、パッケージ依存管理
"""

import ast
import re
from typing import Any, Dict, List, Set

import networkx as nx


class DependencyResolverV2:
    """依存関係解決エージェント Version 2"""

    def __init__(self):
        self.import_pattern = re.compile(r"^(import|from)\s+([\w\.]+)")
        self.function_call_pattern = re.compile(r"(\w+)\([^)]*\)")
        self.class_instantiation_pattern = re.compile(r"(\w+)\s*\(")
        self.defined_entities: Set[str] = set()
        self.used_entities: Set[str] = set()
        print("✅ DependencyResolverV2 初期化完了")

    def resolve_dependencies(self, code: str) -> Dict[str, Any]:
        """コードの依存関係を解決"""
        print("🔧 依存関係解決開始...")

        try:
            # 依存関係グラフの構築
            dependency_graph = self._build_dependency_graph(code)

            # 循環依存の検出
            circular_dependencies = self._detect_circular_dependencies(dependency_graph)

            # 不足しているimportの検出
            missing_imports = self._detect_missing_imports(code)

            # 未定義変数の検出
            undefined_variables = self._detect_undefined_variables(code)

            # 自動修正の適用
            fixed_code = self._add_missing_imports(code, missing_imports)

            result = {
                "original_code_length": len(code.split("\n")),
                "fixed_code_length": len(fixed_code.split("\n")),
                "circular_dependencies_found": len(circular_dependencies),
                "missing_imports_found": len(missing_imports),
                "undefined_variables_found": len(undefined_variables),
                "circular_dependencies": circular_dependencies,
                "missing_imports": missing_imports,
                "undefined_variables": undefined_variables,
                "fixed_code": fixed_code,
                "resolution_success": True,
            }

            print(f"✅ 依存関係解決完了: {len(missing_imports)}個のimportを追加")
            return result

        except Exception as e:
            print(f"❌ 依存関係解決エラー: {e}")
            return {"resolution_success": False, "error": str(e)}

    def _build_dependency_graph(self, code: str) -> nx.DiGraph:
        """依存関係グラフを構築"""
        graph = nx.DiGraph()

        try:
            # ASTを使用してより正確な解析
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name
                        graph.add_node(module)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module = node.module
                        graph.add_node(module)

                elif isinstance(node, ast.FunctionDef):
                    self.defined_entities.add(node.name)
                    graph.add_node(node.name, type="function")

                elif isinstance(node, ast.ClassDef):
                    self.defined_entities.add(node.name)
                    graph.add_node(node.name, type="class")

                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        self.used_entities.add(node.func.id)
                        graph.add_node(node.func.id, type="function_call")

        except SyntaxError:
            # AST解析が失敗した場合は正規表現でフォールバック
            print("  ⚠️ AST解析失敗、正規表現でフォールバック")
            self._fallback_dependency_analysis(code, graph)

        return graph

    def _fallback_dependency_analysis(self, code: str, graph: nx.DiGraph):
        """フォールバック依存関係分析"""
        lines = code.split("\n")

        for line in lines:
            # import文の解析
            import_match = self.import_pattern.match(line.strip())
            if import_match:
                module = import_match.group(2)
                graph.add_node(module, type="module")

            # 関数定義の解析
            if line.strip().startswith("def "):
                func_name = line.split("def ")[1].split("(")[0].strip()
                self.defined_entities.add(func_name)
                graph.add_node(func_name, type="function")

            # クラス定義の解析
            if line.strip().startswith("class "):
                class_name = line.split("class ")[1].split("(")[0].split(":")[0].strip()
                self.defined_entities.add(class_name)
                graph.add_node(class_name, type="class")

    def _detect_circular_dependencies(self, graph: nx.DiGraph) -> List[List[str]]:
        """循環依存を検出"""
        try:
            cycles = list(nx.simple_cycles(graph))
            return cycles
        except Exception:
            # 循環依存検出が失敗した場合
            return []

    def _detect_missing_imports(self, code: str) -> List[str]:
        """不足しているimportを検出"""
        missing_imports = []

        # 使用されているが定義されていないエンティティを検出
        undefined_entities = self.used_entities - self.defined_entities

        # 標準ライブラリのマッピング
        stdlib_mapping = {
            "json": "import json",
            "os": "import os",
            "sys": "import sys",
            "re": "import re",
            "typing": "import typing",
            "List": "from typing import List",
            "Dict": "from typing import Dict",
            "Any": "from typing import Any",
        }

        for entity in undefined_entities:
            if entity in stdlib_mapping:
                missing_imports.append(stdlib_mapping[entity])

        return missing_imports

    def _detect_undefined_variables(self, code: str) -> List[str]:
        """未定義変数を検出"""
        # 簡易的な未定義変数検出
        undefined_vars = []

        try:
            tree = ast.parse(code)

            defined_vars = set()
            used_vars = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            defined_vars.add(target.id)
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    used_vars.add(node.id)

            undefined_vars = list(used_vars - defined_vars)

        except SyntaxError:
            # AST解析失敗時は空リストを返す
            pass

        return undefined_vars

    def _add_missing_imports(self, code: str, missing_imports: List[str]) -> str:
        """不足しているimportを追加"""
        if not missing_imports:
            return code

        lines = code.split("\n")

        # importセクションの位置を探す
        import_section_end = 0
        for i, line in enumerate(lines):
            if (
                line.strip()
                and not self.import_pattern.match(line.strip())
                and not line.strip().startswith("#")
            ):
                import_section_end = i
                break

        # 重複を避けてimportを追加
        existing_imports = set(lines[:import_section_end])
        new_imports = []

        for imp in missing_imports:
            if imp not in existing_imports:
                new_imports.append(imp)

        # 新しいimportを挿入
        if new_imports:
            lines[import_section_end:import_section_end] = new_imports

        return "\n".join(lines)

    def analyze_package_dependencies(self, code: str) -> List[Dict[str, str]]:
        """パッケージ依存関係を分析"""
        print("🔧 パッケージ依存関係分析中...")

        package_dependencies = []

        # 一般的なパッケージのマッピング
        package_mapping = {
            "fastapi": "FastAPI Webフレームワーク",
            "sqlalchemy": "SQLAlchemy ORM",
            "pydantic": "Pydantic データバリデーション",
            "requests": "Requests HTTPライブラリ",
            "numpy": "NumPy 数値計算",
            "pandas": "Pandas データ分析",
        }

        lines = code.split("\n")
        for line in lines:
            import_match = self.import_pattern.match(line.strip())
            if import_match:
                module = import_match.group(2)
                for pkg, description in package_mapping.items():
                    if pkg in module:
                        package_dependencies.append(
                            {
                                "package": pkg,
                                "description": description,
                                "import_statement": line.strip(),
                            }
                        )
                        break

        return package_dependencies
