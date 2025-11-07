#!/usr/bin/env python3
"""
安全なコード挿入ツール
sedの代わりにASTベースで正確な位置にコードを挿入
"""
import ast
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class SafeCodePatcher:
    """構文構造を理解してコードを挿入"""

    def __init__(self, target_file: str):
        self.target_file = Path(target_file)
        with open(self.target_file, "r") as f:
            self.source = f.read()
        self.tree = ast.parse(self.source)
        self.lines = self.source.split("\n")

    def insert_method(
        self, class_name: str, new_method_code: str, after_method: Optional[str] = None
    ) -> bool:
        """
        クラスにメソッドを安全に挿入

        Args:
            class_name: 対象クラス名
            new_method_code: 挿入するメソッドのコード
            after_method: この後に挿入（Noneなら末尾）
        """
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                if after_method:
                    insert_line = self._find_method_end_line(node, after_method)
                else:
                    insert_line = max(
                        item.end_lineno for item in node.body if isinstance(item, ast.FunctionDef)
                    )

                indent = self._detect_indent(node.lineno)
                formatted_method = self._format_with_indent(new_method_code, indent)

                self._create_backup()

                self.lines.insert(insert_line, formatted_method)

                with open(self.target_file, "w") as f:
                    f.write("\n".join(self.lines))

                return True

        return False

    def _find_method_end_line(self, class_node: ast.ClassDef, method_name: str) -> int:
        """メソッドの終了行を取得"""
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef) and item.name == method_name:
                return item.end_lineno
        raise ValueError(f"メソッド {method_name} が見つかりません")

    def _detect_indent(self, line_no: int) -> str:
        """行のインデントを検出"""
        line = self.lines[line_no - 1]
        return line[: len(line) - len(line.lstrip())]

    def _format_with_indent(self, code: str, base_indent: str) -> str:
        """コードを適切なインデントでフォーマット"""
        lines = code.split("\n")
        method_indent = base_indent + "    "
        return "\n".join(method_indent + line for line in lines)

    def _create_backup(self):
        """変更前にバックアップを作成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.target_file.with_suffix(f".{timestamp}.backup")
        with open(backup_path, "w") as f:
            f.write("\n".join(self.lines))
        print(f"📦 バックアップ作成: {backup_path}")

    def verify_syntax(self) -> bool:
        """構文エラーがないか検証"""
        try:
            ast.parse("\n".join(self.lines))
            return True
        except SyntaxError as e:
            print(f"❌ 構文エラー: {e}")
            return False


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("使用法: python3 safe_code_patcher.py <ファイル> <クラス名> <新メソッドコード>")
        sys.exit(1)

    patcher = SafeCodePatcher(sys.argv[1])
    success = patcher.insert_method(sys.argv[2], sys.argv[3])

    if success and patcher.verify_syntax():
        print("✅ メソッド挿入成功")
    else:
        print("❌ 挿入失敗")
