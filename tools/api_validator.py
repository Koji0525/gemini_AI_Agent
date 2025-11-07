#!/usr/bin/env python3
"""
API仕様自動検証ツール
実装コードをAST解析し、ラッパークラスとの整合性を検証
"""
import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class APIValidator:
    """Pythonファイルを解析してAPI仕様を検証"""

    def __init__(self, target_file: str):
        self.target_file = Path(target_file)
        self.tree = self._parse_file()
        self.classes: Dict[str, Dict] = {}

    def _parse_file(self) -> ast.Module:
        """ファイルをASTに変換"""
        with open(self.target_file, "r", encoding="utf-8") as f:
            return ast.parse(f.read(), filename=str(self.target_file))

    def extract_class_methods(self, class_name: str) -> Dict[str, Dict]:
        """指定クラスの全メソッドを抽出"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                methods = {}
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods[item.name] = {
                            "args": [arg.arg for arg in item.args.args],
                            "line": item.lineno,
                            "decorators": [
                                d.id if isinstance(d, ast.Name) else "complex"
                                for d in item.decorator_list
                            ],
                        }
                return methods
        return {}

    def validate_wrapper(
        self, wrapper_file: str, required_methods: List[str]
    ) -> Tuple[bool, List[str]]:
        """ラッパークラスが要求するメソッドが実装されているか検証"""
        target_class = self._detect_main_class()
        if not target_class:
            return False, ["ターゲットクラスが見つかりません"]

        actual_methods = self.extract_class_methods(target_class)
        missing = [m for m in required_methods if m not in actual_methods]

        if missing:
            return False, missing

        return len(missing) == 0, missing

    def _detect_main_class(self) -> str:
        """ファイル内の主要クラスを自動検出"""
        classes = [node.name for node in ast.walk(self.tree) if isinstance(node, ast.ClassDef)]
        for cls in classes:
            if cls.endswith("Manager") or cls.endswith("Controller"):
                return cls
        return classes[0] if classes else ""

    def generate_report(self, class_name: str) -> str:
        """検証レポートを生成"""
        methods = self.extract_class_methods(class_name)
        report = f"📊 {class_name} のAPI仕様\n"
        report += "=" * 60 + "\n\n"

        for method, info in sorted(methods.items()):
            report += f"✅ {method}({', '.join(info['args'])})\n"
            report += f"   行: {info['line']}\n"
            if info["decorators"]:
                report += f"   デコレータ: {', '.join(info['decorators'])}\n"
            report += "\n"

        return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用法: python3 api_validator.py <Pythonファイル> [クラス名]")
        sys.exit(1)

    validator = APIValidator(sys.argv[1])
    class_name = sys.argv[2] if len(sys.argv) > 2 else validator._detect_main_class()

    if not class_name:
        print("❌ クラスが見つかりません")
        sys.exit(1)

    print(validator.generate_report(class_name))
