#!/usr/bin/env python3
"""
コンストラクタ引数不一致チェッカー - 汎用設計

プロジェクト全体のコンストラクタ呼び出しを検証
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class ConstructorChecker(ast.NodeVisitor):
    def __init__(self):
        self.constructors: Dict[str, int] = {}  # クラス名 -> 期待引数数
        self.issues: List[Tuple[str, int, str]] = []  # (ファイル, 行番号, 問題説明)

    def visit_ClassDef(self, node):
        """クラス定義を訪問"""
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                # コンストラクタの引数を記録 (selfを除く)
                args_count = len(item.args.args) - 1
                self.constructors[node.name] = args_count
        self.generic_visit(node)

    def visit_Call(self, node):
        """関数呼び出しを訪問"""
        if isinstance(node.func, ast.Name):
            class_name = node.func.id
            args_count = len(node.args)

            # クラスインスタンス化のチェック
            if class_name in self.constructors:
                expected = self.constructors[class_name]
                if args_count != expected:
                    issue_msg = f"引数不一致: {class_name}() " f"(期待: {expected}引数, 実際: {args_count}引数)"
                    self.issues.append((self.current_file, node.lineno, issue_msg))

        self.generic_visit(node)

    def check_file(self, file_path: Path):
        """単一ファイルをチェック"""
        self.current_file = str(file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            self.visit(tree)

        except SyntaxError as e:
            self.issues.append((str(file_path), e.lineno or 0, f"構文エラー: {e}"))
        except Exception as e:
            self.issues.append((str(file_path), 0, f"解析エラー: {e}"))


def check_project(root_path: str = ".") -> List[Tuple[str, int, str]]:
    """プロジェクト全体をチェック"""
    checker = ConstructorChecker()
    root = Path(root_path)

    # Pythonファイルを再帰的に検索
    for py_file in root.rglob("*.py"):
        # 無視するディレクトリ
        if any(ignore in str(py_file) for ignore in [".git", "__pycache__", ".venv", "venv"]):
            continue

        checker.check_file(py_file)

    return checker.issues


def main():
    """メイン実行関数"""
    print("🔍 コンストラクタ引数チェックを開始...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    issues = check_project()

    if issues:
        print("❌ 以下の問題を検出しました:")
        print()
        for file_path, line_no, message in issues:
            print(f"📄 {file_path}:{line_no}")
            print(f"   ⚠️  {message}")
            print()

        print(f"合計: {len(issues)} 個の問題を検出")
        return 1
    else:
        print("✅ 引数不一致は見つかりませんでした")
        return 0


if __name__ == "__main__":
    sys.exit(main())
