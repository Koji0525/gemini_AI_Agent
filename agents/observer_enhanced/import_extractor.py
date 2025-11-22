#!/usr/bin/env python3
"""
Import Extractor for Enhanced Observer System
Extracts import relationships from Python files using AST parsing.
"""

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class ImportRelation:
    """Represents a single import relationship"""

    module: str
    alias: Optional[str] = None
    imported_names: List[str] = None
    import_type: str = "import"  # "import", "from", "relative"
    level: int = 0  # For relative imports
    line_number: int = 0
    file_path: str = ""

    def __post_init__(self):
        if self.imported_names is None:
            self.imported_names = []

    def __repr__(self):
        if self.import_type == "from":
            return f"from {self.module} import {', '.join(self.imported_names)}"
        else:
            alias_str = f" as {self.alias}" if self.alias else ""
            return f"import {self.module}{alias_str}"

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "module": self.module,
            "alias": self.alias,
            "imported_names": self.imported_names,
            "import_type": self.import_type,
            "level": self.level,
            "line_number": self.line_number,
            "file_path": self.file_path,
        }


class ImportExtractor:
    """
    Extracts import relationships from Python files using AST parsing.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self._cache: Dict[Path, List[ImportRelation]] = {}

    def extract_from_file(self, file_path: Path) -> List[ImportRelation]:
        """
        Extract all import statements from a Python file.

        Args:
            file_path: Path to the Python file

        Returns:
            List of ImportRelation objects
        """
        if file_path in self._cache:
            return self._cache[file_path]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()

            imports = self._parse_imports(source_code, str(file_path))
            self._cache[file_path] = imports
            return imports

        except (SyntaxError, UnicodeDecodeError, IOError) as e:
            print(f"Warning: Could not parse {file_path}: {e}")
            return []

    def extract_imports(self, file_path: Path) -> List[ImportRelation]:
        """
        extract_from_fileのエイリアスメソッド
        static_analyzer.pyとの互換性のため
        """
        return self.extract_from_file(file_path)

    def _parse_imports(self, source_code: str, source_file: str) -> List[ImportRelation]:
        """Parse imports from source code using AST"""
        imports = []

        try:
            tree = ast.parse(source_code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(
                            ImportRelation(
                                module=alias.name,
                                alias=alias.asname,
                                import_type="import",
                                line_number=node.lineno,
                                file_path=source_file,
                            )
                        )

                elif isinstance(node, ast.ImportFrom):
                    imported_names = [name.name for name in node.names]
                    imports.append(
                        ImportRelation(
                            module=node.module or "",
                            imported_names=imported_names,
                            import_type="from",
                            level=node.level or 0,
                            line_number=node.lineno,
                            file_path=source_file,
                        )
                    )

        except SyntaxError as e:
            print(f"Syntax error in {source_file}: {e}")

        return imports

    def extract_from_directory(
        self, directory: Path, exclude_dirs: Optional[List[str]] = None
    ) -> Dict[Path, List[ImportRelation]]:
        """
        Extract imports from all Python files in a directory.

        Args:
            directory: Directory to scan
            exclude_dirs: Directories to exclude

        Returns:
            Dictionary mapping file paths to import lists
        """
        if exclude_dirs is None:
            exclude_dirs = ["__pycache__", ".git", "node_modules", "venv"]

        results = {}

        for py_file in directory.rglob("*.py"):
            # Skip excluded directories
            if any(excluded in str(py_file) for excluded in exclude_dirs):
                continue

            imports = self.extract_from_file(py_file)
            if imports:
                results[py_file] = imports

        return results

    def get_imported_modules(self, imports: List[ImportRelation]) -> Set[str]:
        """Get unique module names from import list"""
        return {imp.module for imp in imports if imp.module}

    def get_imports_by_file(
        self, imports_dict: Dict[Path, List[ImportRelation]]
    ) -> Dict[str, List[ImportRelation]]:
        """Convert Path keys to string keys for JSON serialization"""
        return {str(path): imports for path, imports in imports_dict.items()}

    def filter_internal_imports(
        self, imports: List[ImportRelation], project_root: Optional[Path] = None
    ) -> List[ImportRelation]:
        """Filter imports that are internal to the project"""
        root = project_root or self.project_root
        internal_imports = []

        for imp in imports:
            # Check if module path exists in project
            module_path = self._resolve_module_path(imp.module)
            if module_path and root in module_path.parents:
                internal_imports.append(imp)

        return internal_imports

    def filter_external_imports(
        self, imports: List[ImportRelation], project_root: Optional[Path] = None
    ) -> List[ImportRelation]:
        """Filter imports that are external to the project"""
        root = project_root or self.project_root
        external_imports = []

        for imp in imports:
            module_path = self._resolve_module_path(imp.module)
            if not module_path or root not in module_path.parents:
                external_imports.append(imp)

        return external_imports

    def get_dependency_count(
        self, imports_dict: Dict[Path, List[ImportRelation]]
    ) -> Dict[str, int]:
        """Count dependencies between files"""
        dependency_count = {}

        for file_path, imports in imports_dict.items():
            for imp in imports:
                if imp.module not in dependency_count:
                    dependency_count[imp.module] = 0
                dependency_count[imp.module] += 1

        return dependency_count

    def find_circular_imports(
        self, imports_dict: Dict[Path, List[ImportRelation]]
    ) -> List[List[str]]:
        """Find circular import patterns (basic implementation)"""
        # This is a simplified implementation
        # In a real system, you'd use graph algorithms
        circular_imports = []
        import_graph = {}

        # Build import graph
        for file_path, imports in imports_dict.items():
            file_str = str(file_path)
            if file_str not in import_graph:
                import_graph[file_str] = set()

            for imp in imports:
                module_path = self._resolve_module_path(imp.module)
                if module_path:
                    import_graph[file_str].add(str(module_path))

        # Simple cycle detection (for demonstration)
        # In production, use NetworkX or similar
        visited = set()

        def dfs(node, path):
            if node in path:
                cycle_start = path.index(node)
                circular_imports.append(path[cycle_start:] + [node])
                return
            if node in visited:
                return

            visited.add(node)
            path.append(node)

            for neighbor in import_graph.get(node, set()):
                dfs(neighbor, path.copy())

        for node in import_graph:
            dfs(node, [])

        return circular_imports

    def export_to_dict(self, imports: List[ImportRelation]) -> List[Dict]:
        """Export imports to JSON-serializable format"""
        return [imp.to_dict() for imp in imports]

    def _resolve_module_path(self, module: str) -> Optional[Path]:
        """Resolve module name to file path"""
        try:
            # Simple implementation - in production, use importlib
            if module.startswith("."):
                # Relative import
                return None

            # Convert module to path
            module_path = module.replace(".", "/") + ".py"
            possible_paths = [self.project_root / module_path, Path(module_path)]

            for path in possible_paths:
                if path.exists():
                    return path

            return None

        except Exception:
            return None

    def clear_cache(self):
        """Clear the import cache"""
        self._cache.clear()


# ==============================================================================
# 後方互換性のためのエイリアス
# ==============================================================================
# ImportInfoはImportRelationの別名（static_analyzer.pyとの互換性のため）
ImportInfo = ImportRelation


def main():
    """Command line interface for import extraction"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Extract imports from Python files")
    parser.add_argument("path", help="File or directory path")
    parser.add_argument("--output", "-o", help="Output JSON file")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="text")

    args = parser.parse_args()

    extractor = ImportExtractor()
    path = Path(args.path)

    if path.is_file():
        imports = extractor.extract_from_file(path)
        results = {str(path): extractor.export_to_dict(imports)}
    else:
        imports_dict = extractor.extract_from_directory(path)
        results = extractor.get_imports_by_file(imports_dict)
        # Convert to export format
        for file_path, imports in results.items():
            results[file_path] = extractor.export_to_dict(imports)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        if args.format == "json":
            print(json.dumps(results, indent=2))
        else:
            for file_path, imports in results.items():
                print(f"\n{file_path}:")
                for imp in imports:
                    print(f"  {imp}")


if __name__ == "__main__":
    main()
