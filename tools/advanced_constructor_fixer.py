#!/usr/bin/env python3
"""
高度なコンストラクタ自動修正ツール - 統一初期化パターンを適用
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import subprocess

from tools.unified_initializer import initializer, get_init_code


class AdvancedConstructorFixer:
    """高度なコンストラクタ修正ツール"""

    def __init__(self):
        self.fixed_files = set()
        self.fix_strategies = self._load_fix_strategies()

    def _load_fix_strategies(self) -> Dict[str, Any]:
        """修正戦略を定義"""
        return {
            "GoogleSheetsManager": {
                "pattern": "GoogleSheetsManager()",
                "fix": "GoogleSheetsManager(spreadsheet_id=os.getenv('SPREADSHEET_ID'))",
                "imports": ["import os"],
            },
            "BrowserController": {
                "pattern": "BrowserController()",
                "fix": "BrowserController(headless=True, timeout=30)",
                "imports": [],
            },
            "TaskExecutor": {
                "pattern": "TaskExecutor()",
                "fix": "TaskExecutor(sheets_manager=sheets_manager, browser_controller=browser_controller)",
                "imports": [],
            },
        }

    def analyze_file(self, file_path: str) -> List[Dict[str, Any]]:
        """ファイルを詳細分析"""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # 構文解析
            try:
                tree = ast.parse(content)
            except SyntaxError:
                return [{"file": file_path, "line": 0, "issue": "構文エラー", "fixable": False}]

            # クラス初期化を検出
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    class_name = node.func.id

                    if class_name in initializer.patterns:
                        pattern = initializer.patterns[class_name]

                        # 現在の引数分析
                        current_args = len(node.args)
                        current_keywords = len(node.keywords) if node.keywords else 0
                        total_current = current_args + current_keywords

                        # 期待される引数
                        expected_total = len(pattern.required_args) + len(pattern.optional_args)

                        if total_current != expected_total:
                            line_no = node.lineno
                            code_snippet = lines[line_no - 1].strip() if line_no <= len(lines) else ""

                            issues.append(
                                {
                                    "file": file_path,
                                    "line": line_no,
                                    "class": class_name,
                                    "issue": f"引数不一致: 期待{expected_total}引数, 実際{total_current}引数",
                                    "expected_args": pattern.required_args + list(pattern.optional_args.keys()),
                                    "current_code": code_snippet,
                                    "suggested_code": get_init_code(class_name),
                                    "fixable": True,
                                }
                            )

            return issues

        except Exception as e:
            print(f"❌ 分析エラー {file_path}: {e}")
            return []

    def apply_advanced_fix(self, file_path: str, issues: List[Dict[str, Any]]) -> bool:
        """高度な修正を適用"""
        if not issues:
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            modified = False

            # 行番号の降順で修正（行番号がずれないように）
            for issue in sorted(issues, key=lambda x: x["line"], reverse=True):
                if issue["fixable"]:
                    line_idx = issue["line"] - 1
                    old_line = lines[line_idx].rstrip()

                    # 新しいコードで置換
                    new_line = old_line.replace(
                        f"{issue['class']}(", f"{issue['suggested_code'].split(' = ')[1]}"  # 変数名を保持
                    )

                    if new_line != old_line:
                        lines[line_idx] = new_line + "\n"
                        print(f"   ✅ 修正: {file_path}:{issue['line']}")
                        print(f"      旧: {old_line}")
                        print(f"      新: {new_line}")
                        modified = True

            if modified:
                # ファイル書き込み
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)

                self.fixed_files.add(file_path)

                # 必要なインポートを追加
                self._add_required_imports(file_path, issues)

            return modified

        except Exception as e:
            print(f"   ❌ 修正失敗 {file_path}: {e}")
            return False

    def _add_required_imports(self, file_path: str, issues: List[Dict[str, Any]]):
        """必要なインポートを追加"""
        required_imports = set()

        for issue in issues:
            class_name = issue["class"]
            pattern = initializer.patterns[class_name]
            module_path = pattern.module_path

            # モジュールインポートを生成
            import_line = f"from {module_path} import {class_name}"
            required_imports.add(import_line)

            # 環境変数が必要な場合
            if "spreadsheet_id" in pattern.required_args:
                required_imports.add("import os")

        if not required_imports:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 既存のインポートをチェック
            existing_imports = set()
            lines = content.split("\n")

            for i, line in enumerate(lines):
                if line.startswith(("import ", "from ")):
                    existing_imports.add(line.strip())

            # 不足しているインポートを追加
            missing_imports = required_imports - existing_imports

            if missing_imports:
                # 最初のインポート行の後に追加
                import_end_index = 0
                for i, line in enumerate(lines):
                    if line.startswith(("import ", "from ")):
                        import_end_index = i

                new_lines = lines[: import_end_index + 1] + list(missing_imports) + lines[import_end_index + 1 :]

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_lines))

                print(f"   📦 インポート追加: {', '.join(missing_imports)}")

        except Exception as e:
            print(f"   ❌ インポート追加失敗: {e}")

    def batch_fix_project(self, root_path: str = ".") -> Dict[str, Any]:
        """プロジェクト全体を一括修正"""
        print("🔧 高度な一括修正を開始")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        results = {"scanned_files": 0, "issues_found": 0, "files_fixed": 0, "details": []}

        root = Path(root_path)

        # プロジェクトファイルをスキャン
        for py_file in root.rglob("*.py"):
            if any(
                ignore in str(py_file) for ignore in [".git", "__pycache__", ".venv", "venv", "_BACKUP", "_ARCHIVE"]
            ):
                continue

            results["scanned_files"] += 1

            issues = self.analyze_file(str(py_file))
            if issues:
                results["issues_found"] += len(issues)

                print(f"📄 {py_file}: {len(issues)}件の問題")

                # 修正適用
                if self.apply_advanced_fix(str(py_file), issues):
                    results["files_fixed"] += 1
                    results["details"].append({"file": str(py_file), "issues": len(issues), "fixed": True})
                else:
                    results["details"].append({"file": str(py_file), "issues": len(issues), "fixed": False})

        return results

    def generate_fix_report(self, results: Dict[str, Any]) -> str:
        """修正レポート生成"""
        report = [
            "📊 高度な自動修正レポート",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"📁 スキャンファイル: {results['scanned_files']}件",
            f"⚠️  検出問題: {results['issues_found']}件",
            f"✅ 修正ファイル: {results['files_fixed']}件",
            "",
        ]

        if results["details"]:
            report.append("📋 詳細結果:")
            for detail in results["details"]:
                status = "✅ 修正済" if detail["fixed"] else "❌ 修正失敗"
                report.append(f"  {status} {detail['file']} ({detail['issues']}件)")

        return "\n".join(report)


def main():
    """メイン実行"""
    fixer = AdvancedConstructorFixer()
    results = fixer.batch_fix_project()

    print()
    print(fixer.generate_fix_report(results))

    if results["files_fixed"] > 0:
        print("🎯 修正完了 - プロジェクトの統一性が向上しました")
        return 0
    else:
        print("ℹ️  修正対象はありませんでした")
        return 0


if __name__ == "__main__":
    sys.exit(main())
