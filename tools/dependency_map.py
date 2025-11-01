#!/usr/bin/env python3
"""依存関係マップ生成ツール"""

import os
import re
from pathlib import Path
from typing import Dict, Set


class DependencyMapper:
    """依存関係を可視化"""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.dependencies: Dict[str, Set[str]] = {}

    def scan(self):
        """プロジェクト全体をスキャン"""
        for py_file in self.root_dir.rglob("*.py"):
            if any(ex in str(py_file) for ex in ["_ARCHIVE", "_BACKUP", "_WIP", "__pycache__"]):
                continue

            self._scan_file(py_file)

    def _scan_file(self, file_path: Path):
        """1ファイルをスキャン"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # インポート文を抽出
            imports = re.findall(r"from ([\w.]+) import|import ([\w.]+)", content)

            file_key = str(file_path.relative_to(self.root_dir))
            self.dependencies[file_key] = set()

            for imp in imports:
                module = imp[0] or imp[1]
                if module.startswith(("agents", "tools", "config", "browser_control")):
                    self.dependencies[file_key].add(module)

        except Exception:
            pass

    def find_references(self, target_file: str) -> Dict[str, list]:
        """特定ファイルを参照している箇所を検索"""
        target_module = target_file.replace("/", ".").replace(".py", "")

        references = {"direct": [], "indirect": []}

        for file, deps in self.dependencies.items():
            for dep in deps:
                if target_module in dep:
                    references["direct"].append(file)
                elif any(target_module in d for d in deps):
                    references["indirect"].append(file)

        return references

    def visualize(self) -> str:
        """依存関係を可視化"""
        output = ["# 依存関係マップ\n"]

        for file, deps in sorted(self.dependencies.items()):
            if deps:
                output.append(f"\n## {file}")
                output.append(f"参照数: {len(deps)}個")
                for dep in sorted(deps):
                    output.append(f"  - {dep}")

        return "\n".join(output)


if __name__ == "__main__":
    mapper = DependencyMapper()
    mapper.scan()
    print(mapper.visualize())
