#!/usr/bin/env python3
"""
🔍 コード変更影響分析ツール v1.0
目的: コード変更時の機能削除を検出
"""

import ast
import difflib
from pathlib import Path
from typing import List, Dict, Set
import json


class CodeImpactAnalyzer:
    def __init__(self):
        self.results = {
            "deleted_functions": [],
            "deleted_classes": [],
            "deleted_imports": [],
            "modified_functions": [],
            "risk_level": "low",
        }

    def analyze_python_file(self, old_content: str, new_content: str) -> Dict:
        """Pythonファイルの変更を分析"""
        old_ast = self._parse_safe(old_content)
        new_ast = self._parse_safe(new_content)

        if old_ast and new_ast:
            old_funcs = self._extract_functions(old_ast)
            new_funcs = self._extract_functions(new_ast)

            deleted_funcs = old_funcs - new_funcs
            if deleted_funcs:
                self.results["deleted_functions"] = list(deleted_funcs)
                self.results["risk_level"] = "high"

            old_classes = self._extract_classes(old_ast)
            new_classes = self._extract_classes(new_ast)

            deleted_classes = old_classes - new_classes
            if deleted_classes:
                self.results["deleted_classes"] = list(deleted_classes)
                self.results["risk_level"] = "critical"

            old_imports = self._extract_imports(old_ast)
            new_imports = self._extract_imports(new_ast)

            deleted_imports = old_imports - new_imports
            if deleted_imports:
                self.results["deleted_imports"] = list(deleted_imports)

        # 行数の大幅な削減を検出
        old_lines = len(old_content.split("\n"))
        new_lines = len(new_content.split("\n"))

        if old_lines > 100 and new_lines < old_lines * 0.7:
            self.results["risk_level"] = "critical"
            self.results["warning"] = f"行数が{old_lines}行から{new_lines}行に大幅削減"

        return self.results

    def _parse_safe(self, content: str):
        """安全にASTをパース"""
        try:
            return ast.parse(content)
        except SyntaxError:
            return None

    def _extract_functions(self, tree) -> Set[str]:
        """関数名を抽出"""
        functions = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.add(node.name)
        return functions

    def _extract_classes(self, tree) -> Set[str]:
        """クラス名を抽出"""
        classes = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.add(node.name)
        return classes

    def _extract_imports(self, tree) -> Set[str]:
        """import文を抽出"""
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        return imports

    def generate_report(self) -> str:
        """レポート生成"""
        report = []
        report.append("=" * 60)
        report.append("🔍 コード変更影響分析レポート")
        report.append("=" * 60)

        if self.results["risk_level"] == "critical":
            report.append("⛔ リスクレベル: CRITICAL")
            report.append("   → この変更は承認が必要です")
        elif self.results["risk_level"] == "high":
            report.append("⚠️  リスクレベル: HIGH")
            report.append("   → 慎重なレビューが必要です")
        else:
            report.append("✅ リスクレベル: LOW")

        if self.results.get("warning"):
            report.append(f"\n⚠️  警告: {self.results['warning']}")

        if self.results["deleted_functions"]:
            report.append(f"\n🔴 削除される関数 ({len(self.results['deleted_functions'])}個):")
            for func in self.results["deleted_functions"]:
                report.append(f"   - {func}")

        if self.results["deleted_classes"]:
            report.append(f"\n🔴 削除されるクラス ({len(self.results['deleted_classes'])}個):")
            for cls in self.results["deleted_classes"]:
                report.append(f"   - {cls}")

        if self.results["deleted_imports"]:
            report.append(f"\n🟡 削除されるimport ({len(self.results['deleted_imports'])}個):")
            for imp in self.results["deleted_imports"]:
                report.append(f"   - {imp}")

        report.append("=" * 60)
        return "\n".join(report)


def analyze_file_change(old_file: Path, new_file: Path):
    """ファイル変更を分析"""
    analyzer = CodeImpactAnalyzer()

    with open(old_file, "r", encoding="utf-8") as f:
        old_content = f.read()

    with open(new_file, "r", encoding="utf-8") as f:
        new_content = f.read()

    analyzer.analyze_python_file(old_content, new_content)
    print(analyzer.generate_report())

    return analyzer.results["risk_level"] in ["high", "critical"]


def main():
    import argparse

    parser = argparse.ArgumentParser(description="コード変更影響分析")
    parser.add_argument("old_file", help="変更前のファイル")
    parser.add_argument("new_file", help="変更後のファイル")
    parser.add_argument("--json", action="store_true", help="JSON形式で出力")

    args = parser.parse_args()

    analyzer = CodeImpactAnalyzer()

    with open(args.old_file, "r") as f:
        old_content = f.read()
    with open(args.new_file, "r") as f:
        new_content = f.read()

    results = analyzer.analyze_python_file(old_content, new_content)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(analyzer.generate_report())


if __name__ == "__main__":
    main()
