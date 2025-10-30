#!/usr/bin/env python3
"""
引数不一致自動検知・修正ツール - 汎用設計

Phase 9のSimilaritySearchEngineを活用した自動修正
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
import subprocess


class ConstructorAutoFixer:
    """引数不一致自動修正器"""

    def __init__(self):
        self.issues_found = 0
        self.issues_fixed = 0
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self) -> Dict[str, Any]:
        """過去の修正ナレッジを読み込み"""
        return {
            "argument_mismatch_patterns": [
                {
                    "error_pattern": "takes 2 positional arguments but 3 were given",
                    "cause": "呼び出し側が余分な引数を渡している",
                    "solution": "呼び出し側の余分な引数を削除",
                    "confidence": 0.9,
                },
                {
                    "error_pattern": "takes 1 positional argument but 2 were given",
                    "cause": "呼び出し側が不要な引数を渡している",
                    "solution": "呼び出し側の引数を削除",
                    "confidence": 0.9,
                },
                {
                    "error_pattern": "missing 1 required positional argument",
                    "cause": "呼び出し側が必須引数を渡していない",
                    "solution": "呼び出し側に不足している引数を追加",
                    "confidence": 0.8,
                },
                {
                    "error_pattern": "got an unexpected keyword argument",
                    "cause": "呼び出し側が不正なキーワード引数を使用",
                    "solution": "呼び出し側のキーワード引数を修正または削除",
                    "confidence": 0.85,
                },
            ]
        }

    def analyze_error(self, error_message: str, file_path: str, line_number: int) -> Dict[str, Any]:
        """エラーを分析して修正案を生成"""
        for pattern in self.knowledge_base["argument_mismatch_patterns"]:
            if pattern["error_pattern"] in error_message:
                return {
                    "pattern": pattern["error_pattern"],
                    "cause": pattern["cause"],
                    "solution": pattern["solution"],
                    "confidence": pattern["confidence"],
                    "file": file_path,
                    "line": line_number,
                    "auto_fixable": True,
                }

        return {
            "pattern": "unknown",
            "cause": "未知のエラーパターン",
            "solution": "手動での調査が必要",
            "confidence": 0.0,
            "auto_fixable": False,
        }

    def extract_constructor_info(self, file_path: str, class_name: str) -> Dict[str, Any]:
        """クラスコンストラクタ情報を抽出"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                            # 引数情報を抽出
                            args = [arg.arg for arg in item.args.args]
                            return {
                                "class_name": class_name,
                                "file_path": file_path,
                                "expected_args": args[1:],  # selfを除く
                                "expected_count": len(args) - 1,
                            }

            return {"error": f"クラス {class_name} のコンストラクタが見つかりません"}

        except Exception as e:
            return {"error": f"ファイル解析エラー: {e}"}

    def find_constructor_calls(self, file_path: str, class_name: str) -> List[Dict[str, Any]]:
        """コンストラクタ呼び出しを検出"""
        calls = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id == class_name:
                        calls.append(
                            {
                                "file_path": file_path,
                                "line_number": node.lineno,
                                "actual_args": len(node.args),
                                "code_snippet": lines[node.lineno - 1].strip(),
                            }
                        )

            return calls

        except Exception as e:
            print(f"❌ 呼び出し検出エラー: {e}")
            return []

    def auto_fix_issue(self, issue: Dict[str, Any], constructor_info: Dict[str, Any]) -> bool:
        """問題を自動修正"""
        if not issue["auto_fixable"]:
            return False

        try:
            file_path = issue["file"]
            line_number = issue["line"]

            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # 問題の行を修正
            target_line = lines[line_number - 1]

            if "takes 2 positional arguments but 3 were given" in issue["pattern"]:
                # 余分な引数を削除 (最後の引数を削除)
                if target_line.count("(") == target_line.count(")"):
                    # 単一行の場合は簡単に修正
                    parts = target_line.split("(")
                    if len(parts) > 1:
                        args_part = parts[1].split(")")[0]
                        args = [arg.strip() for arg in args_part.split(",")]
                        if len(args) > constructor_info["expected_count"]:
                            # 余分な引数を削除
                            new_args = args[: constructor_info["expected_count"]]
                            new_line = parts[0] + "(" + ", ".join(new_args) + ")" + parts[1].split(")", 1)[1]
                            lines[line_number - 1] = new_line

                            with open(file_path, "w", encoding="utf-8") as f:
                                f.writelines(lines)

                            print(f"   ✅ 自動修正: {file_path}:{line_number}")
                            return True

            return False

        except Exception as e:
            print(f"   ❌ 自動修正失敗: {e}")
            return False

    def scan_project(self, root_path: str = ".") -> Dict[str, Any]:
        """プロジェクト全体をスキャン"""
        print("🔍 プロジェクトスキャン中...")

        results = {"issues": [], "fixed": [], "summary": {}}

        root = Path(root_path)

        # Pythonファイルをスキャン
        for py_file in root.rglob("*.py"):
            if any(ignore in str(py_file) for ignore in [".git", "__pycache__", ".venv", "venv"]):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # 簡易的な実行テスト
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(py_file)], capture_output=True, text=True, timeout=10
                )

                if result.returncode != 0:
                    # 構文エラーを解析
                    error_lines = result.stderr.split("\n")
                    for line in error_lines:
                        if "line" in line and "File" in line:
                            # エラー行を抽出
                            parts = line.split('", line ')
                            if len(parts) > 1:
                                line_num = int(parts[1].split(",")[0])
                                issue = self.analyze_error(result.stderr, str(py_file), line_num)
                                if issue["auto_fixable"]:
                                    results["issues"].append(issue)

            except Exception as e:
                print(f"❌ スキャンエラー {py_file}: {e}")

        results["summary"]["total_issues"] = len(results["issues"])
        return results

    def run_auto_fix(self):
        """自動修正を実行"""
        print("🤖 引数不一致自動修正を開始")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        scan_results = self.scan_project()

        if not scan_results["issues"]:
            print("✅ 修正対象の問題は見つかりませんでした")
            return

        print(f"📊 検出された問題: {len(scan_results['issues'])}件")
        print()

        for issue in scan_results["issues"]:
            print(f"📄 {issue['file']}:{issue['line']}")
            print(f"   ⚠️  問題: {issue['pattern']}")
            print(f"   🎯 原因: {issue['cause']}")
            print(f"   💡 解決策: {issue['solution']}")
            print(f"   📊 信頼度: {issue['confidence']:.2f}")

            # クラス名を抽出して詳細分析
            if issue["auto_fixable"]:
                # 簡易的な自動修正を試行
                class_name = self._extract_class_name(issue["file"], issue["line"])
                if class_name:
                    constructor_info = self.extract_constructor_info(issue["file"], class_name)
                    if "error" not in constructor_info:
                        if self.auto_fix_issue(issue, constructor_info):
                            self.issues_fixed += 1

            print()

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📊 自動修正結果: {self.issues_fixed}/{len(scan_results['issues'])}件 修正完了")

    def _extract_class_name(self, file_path: str, line_number: int) -> str:
        """エラー行からクラス名を抽出"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            target_line = lines[line_number - 1].strip()

            # 単純なパターンマッチング
            if "=" in target_line and "(" in target_line:
                # variable = ClassName(... のパターン
                parts = target_line.split("=")
                if len(parts) > 1:
                    class_part = parts[1].split("(")[0].strip()
                    if class_part[0].isupper():  # クラス名は大文字始まり
                        return class_part

            return ""

        except:
            return ""


def main():
    """メイン実行"""
    fixer = ConstructorAutoFixer()
    fixer.run_auto_fix()

    if fixer.issues_fixed > 0:
        print("✅ 自動修正完了 - 変更を確認してください")
        return 0
    else:
        print("ℹ️  自動修正対象はありませんでした")
        return 0


if __name__ == "__main__":
    sys.exit(main())
