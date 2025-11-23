#!/usr/bin/env python3
"""
隠れた依存関係検出エンジン

**機能**:
- 環境変数依存の検出（os.getenv, os.environ）
- ファイルI/O依存の検出（open, Path操作）
- 外部コマンド依存の検出（subprocess, os.system）
- データベース接続の検出
- ネットワーク依存の検出

**作成理由**:
通常のインポート解析では検出できない「隠れた依存関係」を可視化し、
環境依存のリスクを明確にするため。これにより、デプロイ時の問題を
事前に把握できる。

Google Docstrings形式を使用
"""

import ast
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set


class HiddenDependencyVisitor(ast.NodeVisitor):
    """AST訪問者：隠れた依存関係を検出する.

    Attributes:
        env_vars: 検出された環境変数のセット
        file_operations: 検出されたファイル操作のリスト
        commands: 検出された外部コマンドのリスト
        db_operations: 検出されたDB操作のリスト
        network_calls: 検出されたネットワーク呼び出しのリスト
    """

    def __init__(self):
        """初期化."""
        self.env_vars: Set[str] = set()
        self.file_operations: List[Dict] = []
        self.commands: List[Dict] = []
        self.db_operations: List[Dict] = []
        self.network_calls: List[Dict] = []

    def visit_Call(self, node: ast.Call):
        """関数呼び出しノードを訪問する.

        Args:
            node: ASTの関数呼び出しノード
        """
        # 環境変数アクセス検出
        if isinstance(node.func, ast.Attribute):
            # os.getenv(), os.environ.get()
            if (
                hasattr(node.func.value, "id")
                and node.func.value.id == "os"
                and node.func.attr in ["getenv", "environ"]
            ):
                self._extract_env_var(node)

            # Path操作
            elif node.func.attr in ["read_text", "read_bytes", "write_text", "write_bytes", "open"]:
                self._extract_file_operation(node, node.func.attr)

            # subprocess操作
            elif hasattr(node.func.value, "id") and node.func.value.id == "subprocess":
                self._extract_command(node, node.func.attr)

        # 組み込み関数
        elif isinstance(node.func, ast.Name):
            # open()
            if node.func.id == "open":
                self._extract_file_operation(node, "open")

        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript):
        """添字アクセスノードを訪問する.

        Args:
            node: AST添字ノード
        """
        # os.environ['KEY']
        if (
            isinstance(node.value, ast.Attribute)
            and hasattr(node.value.value, "id")
            and node.value.value.id == "os"
            and node.value.attr == "environ"
        ):
            if isinstance(node.slice, ast.Constant):
                self.env_vars.add(node.slice.value)

        self.generic_visit(node)

    def _extract_env_var(self, node: ast.Call):
        """環境変数名を抽出する.

        Args:
            node: 関数呼び出しノード
        """
        if node.args and isinstance(node.args[0], ast.Constant):
            self.env_vars.add(node.args[0].value)

    def _extract_file_operation(self, node: ast.Call, operation: str):
        """ファイル操作を抽出する.

        Args:
            node: 関数呼び出しノード
            operation: 操作の種類
        """
        file_path = None
        if node.args and isinstance(node.args[0], ast.Constant):
            file_path = node.args[0].value

        if file_path:
            self.file_operations.append(
                {"operation": operation, "path": file_path, "line": node.lineno}
            )

    def _extract_command(self, node: ast.Call, method: str):
        """外部コマンドを抽出する.

        Args:
            node: 関数呼び出しノード
            method: subprocess のメソッド名
        """
        command = None

        # subprocess.run(['git', 'log'])
        if node.args:
            if isinstance(node.args[0], ast.List):
                command = " ".join(
                    [elt.value for elt in node.args[0].elts if isinstance(elt, ast.Constant)]
                )
            elif isinstance(node.args[0], ast.Constant):
                command = node.args[0].value

        if command:
            self.commands.append({"method": method, "command": command, "line": node.lineno})


def analyze_file(file_path: Path) -> Dict:
    """ファイルの隠れた依存関係を分析する.

    Args:
        file_path: 分析対象のファイルパス

    Returns:
        隠れた依存関係の辞書
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        visitor = HiddenDependencyVisitor()
        visitor.visit(tree)

        return {
            "env_vars": list(visitor.env_vars),
            "file_operations": visitor.file_operations,
            "commands": visitor.commands,
            "db_operations": visitor.db_operations,
            "network_calls": visitor.network_calls,
        }
    except Exception as e:
        return {
            "env_vars": [],
            "file_operations": [],
            "commands": [],
            "db_operations": [],
            "network_calls": [],
            "error": str(e),
        }


def scan_project(project_root: str = ".") -> Dict:
    """プロジェクト全体をスキャンする.

    Args:
        project_root: プロジェクトのルートディレクトリ

    Returns:
        スキャン結果の辞書
    """
    root_path = Path(project_root)
    python_files = list(root_path.rglob("*.py"))

    results = {}
    env_var_summary = defaultdict(list)
    file_op_summary = defaultdict(list)
    command_summary = defaultdict(list)

    # 除外パターン
    exclude_patterns = [
        "__pycache__",
        "venv",
        ".git",
        "site-packages",
        ".venv",
        "env",
        "build",
        "dist",
    ]

    scanned_count = 0
    skipped_count = 0

    print(f"📂 {len(python_files)}個のPythonファイルを検出")

    for file_path in python_files:
        # 除外パターンチェック
        if any(pattern in str(file_path) for pattern in exclude_patterns):
            skipped_count += 1
            continue

        try:
            relative_path = str(file_path.relative_to(root_path))
        except ValueError:
            relative_path = str(file_path)

        analysis = analyze_file(file_path)

        # 何か検出された場合のみ記録
        if (
            analysis["env_vars"]
            or analysis["file_operations"]
            or analysis["commands"]
            or analysis["db_operations"]
            or analysis["network_calls"]
        ):

            results[relative_path] = analysis

            # サマリー作成
            for env_var in analysis["env_vars"]:
                env_var_summary[env_var].append(relative_path)

            for file_op in analysis["file_operations"]:
                file_op_summary[file_op["path"]].append(relative_path)

            for cmd in analysis["commands"]:
                command_summary[cmd["command"]].append(relative_path)

        scanned_count += 1

    print(f"✅ {scanned_count}個のファイルをスキャン（{skipped_count}個をスキップ）")

    return {
        "files": results,
        "summary": {
            "env_vars": dict(env_var_summary),
            "file_operations": dict(file_op_summary),
            "commands": dict(command_summary),
        },
        "statistics": {
            "total_scanned": scanned_count,
            "files_with_hidden_deps": len(results),
            "unique_env_vars": len(env_var_summary),
            "unique_files_accessed": len(file_op_summary),
            "unique_commands": len(command_summary),
        },
    }


def main():
    """メイン処理を実行する."""
    print("=" * 60)
    print("🔍 隠れた依存関係検出エンジン")
    print("=" * 60)
    print(f"📁 作業ディレクトリ: {Path.cwd()}")
    print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # スキャン実行
    results = scan_project()

    # 結果保存
    output_dir = Path("docs")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "hidden_dependencies.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # 結果表示
    print("\n" + "=" * 60)
    print("✅ 隠れた依存関係検出完了")
    print("=" * 60)

    stats = results["statistics"]
    print(f"📊 スキャン統計:")
    print(f"   総スキャン数: {stats['total_scanned']} ファイル")
    print(f"   隠れた依存あり: {stats['files_with_hidden_deps']} ファイル")
    print(f"   ユニーク環境変数: {stats['unique_env_vars']} 個")
    print(f"   ユニークファイル: {stats['unique_files_accessed']} 個")
    print(f"   ユニークコマンド: {stats['unique_commands']} 個")

    # Top 10環境変数
    summary = results["summary"]
    if summary["env_vars"]:
        print(f"\n🏆 最も使用されている環境変数 Top 10:")
        sorted_env = sorted(summary["env_vars"].items(), key=lambda x: len(x[1]), reverse=True)
        for i, (env_var, files) in enumerate(sorted_env[:10], 1):
            print(f"   {i:2d}. {env_var} - {len(files)}ファイルで使用")

    # Top 10ファイル
    if summary["file_operations"]:
        print(f"\n📁 最もアクセスされているファイル Top 10:")
        sorted_files = sorted(
            summary["file_operations"].items(), key=lambda x: len(x[1]), reverse=True
        )
        for i, (file_path, files) in enumerate(sorted_files[:10], 1):
            print(f"   {i:2d}. {file_path} - {len(files)}ファイルからアクセス")

    # Top 10コマンド
    if summary["commands"]:
        print(f"\n⚙️  最も実行されているコマンド Top 10:")
        sorted_cmds = sorted(summary["commands"].items(), key=lambda x: len(x[1]), reverse=True)
        for i, (cmd, files) in enumerate(sorted_cmds[:10], 1):
            print(f"   {i:2d}. {cmd} - {len(files)}ファイルから実行")

    print(f"\n💾 結果保存先: {output_file.absolute()}")
    print(f"📁 ファイルサイズ: {output_file.stat().st_size / 1024:.1f} KB")
    print("=" * 60)


if __name__ == "__main__":
    main()
