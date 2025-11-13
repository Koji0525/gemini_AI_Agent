#!/usr/bin/env python3
"""
🎯 簡易版ASTベースコード修正フレームワーク

最小限の依存で動作するバージョン
"""

import ast
from pathlib import Path
from typing import Any, Dict

import yaml


class SimpleASTModifier:
    """簡易版AST修正ツール"""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込む"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def create_template(self, template_type: str) -> str:
        """設定テンプレートを生成"""
        templates = {
            "imports": """
# インポート追加テンプレート
file: target.py
operations:
  - type: add_imports
    add:
      - "from pathlib import Path"
      - "import logging"
""",
            "method": """
# メソッド修正テンプレート
file: target.py  
operations:
  - type: modify_method
    class: MyClass
    method: my_method
    add_code: |
        \"\"\"改良版メソッド\"\"\"
        # 新しいコードをここに追加
        return result
""",
            "class": """
# クラス追加テンプレート
file: target.py
operations:
  - type: add_class
    name: NewClass
    methods:
      - name: new_method
        body: |
            \"\"\"新しいメソッド\"\"\"
            return "処理結果"
""",
        }
        return templates.get(template_type, "# テンプレートが見つかりません")

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """ファイルを分析"""
        try:
            code = file_path.read_text(encoding="utf-8")
            tree = ast.parse(code)

            return {
                "classes": [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)],
                "functions": [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)],
                "imports": [
                    ast.unparse(n)
                    for n in ast.walk(tree)
                    if isinstance(n, (ast.Import, ast.ImportFrom))
                ],
                "status": "分析完了",
            }
        except Exception as e:
            return {"error": str(e), "status": "分析失敗"}


def main():
    """簡易版デモ"""
    modifier = SimpleASTModifier("dummy.yaml")

    print("🎯 簡易版ASTコード修正ツール")
    print("利用可能なテンプレート: imports, method, class")

    if len(sys.argv) > 1:
        if sys.argv[1] == "analyze" and len(sys.argv) > 2:
            target_file = Path(sys.argv[2])
            if target_file.exists():
                result = modifier.analyze_file(target_file)
                print(f"分析結果: {result}")
            else:
                print("ファイルが見つかりません")
        else:
            template_type = sys.argv[1]
            print(modifier.create_template(template_type))


if __name__ == "__main__":
    import sys

    main()
