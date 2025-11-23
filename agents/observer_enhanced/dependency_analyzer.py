"""
Dependency Analyzer - 全システム依存関係解析（エラー修正版）
Phase 5: システム可視化
"""

import ast
import logging
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("observer_enhanced.dependency_analyzer")


class DependencyAnalyzer:
    """プロジェクト全体の依存関係解析"""

    def __init__(self, project_root: str = "/workspaces/gemini_AI_Agent"):
        """初期化"""
        self.project_root = Path(project_root)
        self.logger = logger

        # 依存関係グラフ
        self.nodes: List[Dict] = []
        self.edges: List[Dict] = []

        # ファイル情報
        self.files: Dict[str, Dict] = {}

        # 除外ディレクトリ
        self.exclude_dirs = {
            "__pycache__",
            ".git",
            "node_modules",
            "venv",
            ".pytest_cache",
            ".mypy_cache",
            "_BACKUP",
            "git_cleanup_backup_20251104_200146",  # バックアップディレクトリ除外
        }

        # 除外ファイル
        self.exclude_files = {".pyc", ".pyo", ".pyd", ".so", ".dll"}

        self.logger.info("Initialized DependencyAnalyzer")

    def scan_project(self) -> Dict:
        """プロジェクト全体をスキャン"""
        self.logger.info("Starting project scan...")

        # ファイル収集
        self._collect_files()

        # 依存関係解析
        self._analyze_dependencies()

        # グラフ構築
        self._build_graph()

        result = {
            "nodes": self.nodes,
            "edges": self.edges,
            "stats": self._calculate_stats(),
            "scan_time": None,
        }

        self.logger.info(f"Scan complete: {len(self.nodes)} nodes, {len(self.edges)} edges")

        return result

    def _collect_files(self):
        """プロジェクト内の全ファイルを収集（エラーハンドリング強化版）"""
        for root, dirs, files in os.walk(self.project_root):
            # rootがNoneまたは不正な場合はスキップ
            if root is None:
                self.logger.warning(f"Skipping invalid root: {root}")
                continue

            # 除外ディレクトリをスキップ
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                # ファイル名がNoneまたは不正な場合はスキップ
                if file is None or not isinstance(file, str):
                    self.logger.warning(f"Skipping invalid file: {file}")
                    continue

                # 除外ファイルをスキップ
                if any(file.endswith(ext) for ext in self.exclude_files):
                    continue

                try:
                    file_path = Path(root) / file

                    # パスが存在しない場合はスキップ
                    if not file_path.exists():
                        self.logger.warning(f"Skipping non-existent path: {file_path}")
                        continue

                    rel_path = file_path.relative_to(self.project_root)

                    # ファイル情報を記録
                    file_ext = file_path.suffix
                    self.files[str(rel_path)] = {
                        "path": str(rel_path),
                        "name": file,
                        "ext": file_ext,
                        "size": file_path.stat().st_size,
                        "type": self._get_file_type(file_ext),
                        "imports": [],
                        "imported_by": [],
                    }

                except Exception as e:
                    self.logger.warning(f"Error processing file {file} in {root}: {e}")
                    continue

    def _get_file_type(self, ext: str) -> str:
        """ファイルタイプを判定"""
        type_map = {
            ".py": "python",
            ".sh": "shell",
            ".md": "markdown",
            ".txt": "text",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".html": "html",
            ".js": "javascript",
            ".css": "css",
        }
        return type_map.get(ext, "other")

    def _analyze_dependencies(self):
        """依存関係を解析"""
        for file_path, file_info in self.files.items():
            if file_info["type"] == "python":
                self._analyze_python_file(file_path)
            elif file_info["type"] == "shell":
                self._analyze_shell_file(file_path)

    def _analyze_python_file(self, file_path: str):
        """Pythonファイルの依存関係解析"""
        full_path = self.project_root / file_path

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._add_import(file_path, alias.name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._add_import(file_path, node.module)

        except Exception as e:
            self.logger.debug(f"Failed to parse {file_path}: {e}")

    def _analyze_shell_file(self, file_path: str):
        """シェルスクリプトの依存関係解析"""
        full_path = self.project_root / file_path

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            python_pattern = r"python3?\s+([^\s]+\.py)"
            matches = re.findall(python_pattern, content)

            for match in matches:
                self._add_import(file_path, match)

            bash_pattern = r"bash\s+([^\s]+\.sh)"
            matches = re.findall(bash_pattern, content)

            for match in matches:
                self._add_import(file_path, match)

        except Exception as e:
            self.logger.debug(f"Failed to parse {file_path}: {e}")

    def _add_import(self, from_file: str, to_module: str):
        """インポート関係を記録"""
        to_file = self._resolve_module_path(to_module)

        if to_file and to_file in self.files:
            if to_file not in self.files[from_file]["imports"]:
                self.files[from_file]["imports"].append(to_file)
            if from_file not in self.files[to_file]["imported_by"]:
                self.files[to_file]["imported_by"].append(from_file)

    def _resolve_module_path(self, module_name: str) -> str:
        """モジュール名からファイルパスを解決"""
        if module_name in self.files:
            return module_name

        module_path = module_name.replace(".", "/")

        candidates = [f"{module_path}.py", f"{module_path}/__init__.py"]

        for candidate in candidates:
            if candidate in self.files:
                return candidate

        return None

    def _build_graph(self):
        """グラフデータを構築"""
        for file_path, file_info in self.files.items():
            category = self._categorize_file(file_path)

            self.nodes.append(
                {
                    "id": file_path,
                    "label": file_info["name"],
                    "type": file_info["type"],
                    "category": category,
                    "size": file_info["size"],
                    "imports_count": len(file_info["imports"]),
                    "imported_by_count": len(file_info["imported_by"]),
                }
            )

        for file_path, file_info in self.files.items():
            for imported_file in file_info["imports"]:
                self.edges.append({"source": file_path, "target": imported_file, "type": "imports"})

    def _categorize_file(self, file_path: str) -> str:
        """ファイルをカテゴリ分類"""
        path_str = str(file_path)

        if path_str.startswith("agents/"):
            return "agent"
        elif path_str.startswith("tools/"):
            return "tool"
        elif path_str.startswith("tests/"):
            return "test"
        elif path_str.startswith("sh/"):
            return "script"
        elif path_str.startswith("MD/"):
            return "doc"
        else:
            return "other"

    def _calculate_stats(self) -> Dict:
        """統計情報を計算"""
        stats = {
            "total_files": len(self.files),
            "by_type": defaultdict(int),
            "by_category": defaultdict(int),
            "total_dependencies": len(self.edges),
            "top_imported": [],
            "top_importers": [],
        }

        for file_info in self.files.values():
            stats["by_type"][file_info["type"]] += 1

        for node in self.nodes:
            stats["by_category"][node["category"]] += 1

        sorted_by_imported = sorted(
            self.files.items(), key=lambda x: len(x[1]["imported_by"]), reverse=True
        )[:10]

        stats["top_imported"] = [
            {"file": path, "count": len(info["imported_by"])} for path, info in sorted_by_imported
        ]

        sorted_by_imports = sorted(
            self.files.items(), key=lambda x: len(x[1]["imports"]), reverse=True
        )[:10]

        stats["top_importers"] = [
            {"file": path, "count": len(info["imports"])} for path, info in sorted_by_imports
        ]

        return dict(stats)

    def find_impact(self, file_path: str) -> Dict:
        """ファイル変更時の影響範囲を分析"""
        if file_path not in self.files:
            return {"error": "File not found"}

        directly_affected = self.files[file_path]["imported_by"]
        all_affected = self._recursive_impact(file_path, set())

        return {
            "file": file_path,
            "directly_affected": directly_affected,
            "all_affected": list(all_affected),
            "impact_count": len(all_affected),
        }

    def _recursive_impact(self, file_path: str, visited: Set[str]) -> Set[str]:
        """再帰的に影響範囲を探索"""
        if file_path in visited:
            return visited

        visited.add(file_path)

        if file_path in self.files:
            for importer in self.files[file_path]["imported_by"]:
                self._recursive_impact(importer, visited)

        return visited

    def detect_duplicates(self) -> Dict:
        """重複ファイルを検出"""
        duplicates = {}
        base_names = defaultdict(list)

        version_pattern = re.compile(r"_v\d{2,3}(_|\.)")

        for file_path in self.files.keys():
            base_name = version_pattern.sub("_", file_path)
            base_names[base_name].append(file_path)

        for base_name, files in base_names.items():
            if len(files) > 1:
                duplicates[base_name] = {
                    "files": sorted(files),
                    "count": len(files),
                    "latest": self._find_latest_version(files),
                }

        return duplicates

    def _find_latest_version(self, files: List[str]) -> str:
        """最新バージョンを特定"""
        version_pattern = re.compile(r"_v(\d{2,3})(_|\.)")

        versions = []
        for file in files:
            match = version_pattern.search(file)
            if match:
                version_num = int(match.group(1))
                versions.append((version_num, file))
            else:
                versions.append((0, file))

        if versions:
            return max(versions, key=lambda x: x[0])[1]
        return files[0]

    def detect_unused_files(self) -> List[Dict]:
        """未使用ファイルを検出"""
        unused = []

        for file_path, file_info in self.files.items():
            if file_info["type"] not in ["python", "shell"]:
                continue

            if len(file_info["imported_by"]) == 0:
                is_entry_point = self._is_entry_point(file_path)

                if not is_entry_point:
                    unused.append(
                        {
                            "file": file_path,
                            "type": file_info["type"],
                            "size": file_info["size"],
                            "imports_count": len(file_info["imports"]),
                        }
                    )

        return unused

    def _is_entry_point(self, file_path: str) -> bool:
        """エントリーポイント判定"""
        full_path = self.project_root / file_path

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "if __name__ == '__main__':" in content or 'if __name__ == "__main__":' in content:
                return True

            if content.startswith("#!/bin/bash") or content.startswith("#!/bin/sh"):
                return True

        except Exception:
            pass

        return False

    def suggest_reusable_tools(self) -> List[Dict]:
        """汎用的に使えるツールを推奨"""
        reusable = []

        for file_path, file_info in self.files.items():
            if not file_path.startswith("tools/"):
                continue

            if len(file_info["imported_by"]) <= 1 and file_info["size"] > 1000:
                reusable.append(
                    {
                        "file": file_path,
                        "size": file_info["size"],
                        "imported_by_count": len(file_info["imported_by"]),
                        "description": "汎用ツールとして再利用可能",
                    }
                )

        return sorted(reusable, key=lambda x: x["size"], reverse=True)

    def analyze_version_history(self) -> Dict:
        """バージョン管理されたファイルを分析"""
        version_pattern = re.compile(r"(.+)_v(\d{2,3})(_|\.)")
        version_groups = defaultdict(list)

        for file_path in self.files.keys():
            match = version_pattern.search(file_path)
            if match:
                base_name = match.group(1)
                version_num = int(match.group(2))
                version_groups[base_name].append({"file": file_path, "version": version_num})

        for base_name in version_groups:
            version_groups[base_name] = sorted(
                version_groups[base_name], key=lambda x: x["version"], reverse=True
            )

        return dict(version_groups)

    def get_comprehensive_report(self) -> Dict:
        """包括的な分析レポート"""
        return {
            "duplicates": self.detect_duplicates(),
            "unused_files": self.detect_unused_files(),
            "reusable_tools": self.suggest_reusable_tools(),
            "version_history": self.analyze_version_history(),
            "stats": self._calculate_stats(),
        }
