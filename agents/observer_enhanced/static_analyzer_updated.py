"""
静的依存関係解析エンジン（除外設定対応版）

scan_config.pyの除外設定を使用してスキャンを実行します。
"""

import ast
import fnmatch
import json
import logging
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

try:
    import networkx as nx
except ImportError:
    print("Error: networkx is required. Install with: pip install networkx --break-system-packages")
    sys.exit(1)

# scan_configをインポート
try:
    from .scan_config import (EXCLUDE_DIRS, EXCLUDE_FILE_PATTERNS,
                              EXCLUDE_SPECIFIC_DIRS, EXCLUDE_SPECIFIC_FILES)
except ImportError:
    # デフォルト設定
    EXCLUDE_DIRS = {
        "__pycache__",
        ".git",
        "venv",
        "env",
        "node_modules",
        "_BACKUP",
        "_ARCHIVE",
        "_WIP",
        "tests",
        ".pytest_cache",
        ".vscode",
        ".idea",
    }
    EXCLUDE_FILE_PATTERNS = {
        "*_backup_*",
        "*.backup.py",
        "*_old.py",
        "*_deprecated.py",
        "temp_*.py",
    }
    EXCLUDE_SPECIFIC_FILES = {"register_syntax_knowledge.py"}
    EXCLUDE_SPECIFIC_DIRS = {"agents/generated", "core_agents", "final_backup_*"}

# ロガー設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ImportRelation:
    """import関係を表すデータクラス"""

    source_file: str
    target_module: str
    import_type: str
    imported_names: List[str] = field(default_factory=list)
    line_number: int = 0


@dataclass
class FileMetrics:
    """ファイルメトリクス"""

    path: str
    lines: int
    functions: int
    classes: int
    imports: int
    last_modified: str


class StaticDependencyAnalyzer:
    """静的依存関係解析エンジン（除外設定対応版）"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            current = Path(__file__).resolve()
            while current.parent != current:
                if (current / "requirements.txt").exists() or (current / ".git").exists():
                    project_root = current
                    break
                current = current.parent
            else:
                project_root = Path.cwd()

        self.project_root = Path(project_root)
        self.graph = nx.DiGraph()
        self.file_metrics: Dict[str, FileMetrics] = {}
        self.import_relations: List[ImportRelation] = []

        logger.info(f"Initialized StaticDependencyAnalyzer with root: {self.project_root}")

    def _should_exclude_file(self, file_path: Path) -> bool:
        """ファイルを除外すべきかチェック"""
        relative_path = str(file_path.relative_to(self.project_root))
        filename = file_path.name

        # 特定ファイル名で除外
        if filename in EXCLUDE_SPECIFIC_FILES:
            return True

        # ファイルパターンで除外
        for pattern in EXCLUDE_FILE_PATTERNS:
            if fnmatch.fnmatch(filename, pattern):
                return True

        # 特定ディレクトリパスで除外
        for exclude_dir in EXCLUDE_SPECIFIC_DIRS:
            if fnmatch.fnmatch(relative_path, f"{exclude_dir}/*") or relative_path.startswith(
                exclude_dir
            ):
                return True

        return False

    def scan_project(self, exclude_dirs: Optional[Set[str]] = None) -> nx.DiGraph:
        """プロジェクト全体をスキャン（除外設定適用）"""
        if exclude_dirs is None:
            exclude_dirs = EXCLUDE_DIRS

        logger.info("Starting project scan with exclusion rules...")
        start_time = time.time()

        python_files = self._find_python_files(exclude_dirs)
        logger.info(f"Found {len(python_files)} Python files (after exclusion)")

        for file_path in python_files:
            if self._should_exclude_file(file_path):
                continue

            try:
                self._analyze_file(file_path)
            except Exception as e:
                logger.debug(f"Failed to analyze {file_path}: {e}")

        self._build_graph()

        elapsed = time.time() - start_time
        logger.info(f"Scan completed in {elapsed:.2f} seconds")
        logger.info(
            f"Graph: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges"
        )

        return self.graph

    def _find_python_files(self, exclude_dirs: Set[str]) -> List[Path]:
        """Pythonファイルを再帰的に検索"""
        python_files = []

        for path in self.project_root.rglob("*.py"):
            if any(excluded in path.parts for excluded in exclude_dirs):
                continue
            python_files.append(path)

        return python_files

    def _analyze_file(self, file_path: Path) -> None:
        """1ファイルを解析"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logger.debug(f"Cannot read {file_path}: {e}")
            return

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.debug(f"Syntax error in {file_path}: {e}")
            return

        imports = self._extract_imports(tree, file_path)
        self.import_relations.extend(imports)

        metrics = self._collect_metrics(tree, file_path, content)
        relative_path = str(file_path.relative_to(self.project_root))
        self.file_metrics[relative_path] = metrics

    def _extract_imports(self, tree: ast.AST, file_path: Path) -> List[ImportRelation]:
        """AST木からimport文を抽出"""
        imports = []
        relative_path = str(file_path.relative_to(self.project_root))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        ImportRelation(
                            source_file=relative_path,
                            target_module=alias.name,
                            import_type="import",
                            imported_names=[alias.asname if alias.asname else alias.name],
                            line_number=node.lineno,
                        )
                    )

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_names = [alias.name for alias in node.names]
                    imports.append(
                        ImportRelation(
                            source_file=relative_path,
                            target_module=node.module,
                            import_type="from_import",
                            imported_names=imported_names,
                            line_number=node.lineno,
                        )
                    )

        return imports

    def _collect_metrics(self, tree: ast.AST, file_path: Path, content: str) -> FileMetrics:
        """ファイルメトリクスを収集"""
        lines = len(content.splitlines())
        functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
        imports = sum(
            1 for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
        )

        try:
            last_modified = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        except Exception:
            last_modified = "unknown"

        relative_path = str(file_path.relative_to(self.project_root))

        return FileMetrics(
            path=relative_path,
            lines=lines,
            functions=functions,
            classes=classes,
            imports=imports,
            last_modified=last_modified,
        )

    def _build_graph(self) -> None:
        """依存関係グラフを構築"""
        for file_path, metrics in self.file_metrics.items():
            self.graph.add_node(
                file_path,
                lines=metrics.lines,
                functions=metrics.functions,
                classes=metrics.classes,
                imports=metrics.imports,
                last_modified=metrics.last_modified,
                type="file",
            )

        for relation in self.import_relations:
            target_file = self._resolve_module_path(relation.target_module)

            if target_file and target_file in self.file_metrics:
                self.graph.add_edge(
                    relation.source_file,
                    target_file,
                    import_type=relation.import_type,
                    imported_names=relation.imported_names,
                    line_number=relation.line_number,
                )

    def _resolve_module_path(self, module_name: str) -> Optional[str]:
        """モジュール名をファイルパスに変換"""
        potential_path = module_name.replace(".", "/") + ".py"
        full_path = self.project_root / potential_path

        if full_path.exists():
            try:
                return str(full_path.relative_to(self.project_root))
            except ValueError:
                return None

        potential_init = module_name.replace(".", "/") + "/__init__.py"
        full_init_path = self.project_root / potential_init

        if full_init_path.exists():
            try:
                return str(full_init_path.relative_to(self.project_root))
            except ValueError:
                return None

        return None

    def detect_circular_dependencies(self) -> List[List[str]]:
        """循環依存を検出"""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            if cycles:
                logger.info(f"Found {len(cycles)} circular dependencies")
            return cycles
        except Exception as e:
            logger.error(f"Error detecting cycles: {e}")
            return []

    def get_dependencies(self, file_path: str) -> Set[str]:
        """特定ファイルの依存先を取得"""
        if file_path not in self.graph:
            return set()
        return set(self.graph.successors(file_path))

    def get_dependents(self, file_path: str) -> Set[str]:
        """特定ファイルに依存しているファイルを取得"""
        if file_path not in self.graph:
            return set()
        return set(self.graph.predecessors(file_path))

    def export_graph(self, output_path: Path) -> None:
        """グラフをJSON形式でエクスポート"""
        data = {
            "nodes": [],
            "edges": [],
            "metrics": {
                "total_files": self.graph.number_of_nodes(),
                "total_dependencies": self.graph.number_of_edges(),
                "circular_dependencies": len(self.detect_circular_dependencies()),
                "generated_at": datetime.now().isoformat(),
            },
        }

        for node, attrs in self.graph.nodes(data=True):
            data["nodes"].append({"id": node, **attrs})

        for source, target, attrs in self.graph.edges(data=True):
            data["edges"].append({"source": source, "target": target, **attrs})

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Graph exported to {output_path}")


def main():
    """メイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description="Static Dependency Analyzer")
    parser.add_argument("--scan-all", action="store_true", help="Scan entire project")
    parser.add_argument(
        "--output", type=str, default="logs/dependency_graph.json", help="Output file path"
    )

    args = parser.parse_args()

    if args.scan_all:
        analyzer = StaticDependencyAnalyzer()
        analyzer.scan_project()

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        analyzer.export_graph(output_path)

        cycles = analyzer.detect_circular_dependencies()
        if cycles:
            print("\n⚠️  Circular dependencies detected:")
            for i, cycle in enumerate(cycles, 1):
                print(f"{i}. {' -> '.join(cycle)}")
        else:
            print("\n✅ No circular dependencies found")


if __name__ == "__main__":
    main()
