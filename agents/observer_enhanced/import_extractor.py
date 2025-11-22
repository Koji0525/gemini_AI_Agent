"""
Import文抽出器（修正版）

【責任】
- Pythonファイルからimport文を抽出
- 依存関係の明確化
- AST解析ベース
"""

import ast
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ImportRelation:
    """Import関係を表すデータクラス"""

    module: str
    names: List[str]
    alias: Optional[str] = None
    is_from_import: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """辞書に変換"""
        return asdict(self)


class ImportExtractor:
    """Import文抽出クラス"""

    def __init__(self):
        pass

    def extract_imports(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Import文を抽出（辞書形式で返す）

        Args:
            file_path: Pythonファイルパス

        Returns:
            [
                {
                    'module': 'os',
                    'names': ['path', 'environ'],
                    'alias': None,
                    'is_from_import': True
                },
                ...
            ]
        """
        try:
            path = Path(file_path)

            if not path.exists():
                return []

            with open(path, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(path))

            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    # import xxx
                    for alias in node.names:
                        imports.append(
                            {
                                "module": alias.name,
                                "names": [alias.name],
                                "alias": alias.asname,
                                "is_from_import": False,
                            }
                        )

                elif isinstance(node, ast.ImportFrom):
                    # from xxx import yyy
                    module = node.module or ""
                    names = [alias.name for alias in node.names]

                    imports.append(
                        {"module": module, "names": names, "alias": None, "is_from_import": True}
                    )

            return imports

        except SyntaxError as e:
            # 構文エラーの場合は空リスト
            print(f"Syntax error in {file_path}: {e}")
            return []

        except Exception as e:
            print(f"Error extracting imports from {file_path}: {e}")
            return []

    def get_direct_dependencies(self, file_path: str) -> List[str]:
        """
        直接依存しているモジュール一覧取得

        Args:
            file_path: Pythonファイルパス

        Returns:
            ['os', 'sys', 'pathlib', ...]
        """
        imports = self.extract_imports(file_path)

        modules = set()
        for imp in imports:
            module = imp.get("module", "")
            if module:
                # トップレベルモジュールのみ
                top_module = module.split(".")[0]
                modules.add(top_module)

        return sorted(list(modules))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI実行
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python import_extractor.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    extractor = ImportExtractor()
    imports = extractor.extract_imports(file_path)

    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📝 Import抽出結果: {file_path}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    for i, imp in enumerate(imports, 1):
        print(f"{i}. module: {imp['module']}")
        print(f"   names: {imp['names']}")
        if imp.get("alias"):
            print(f"   alias: {imp['alias']}")
        print()

    print(f"Total: {len(imports)}個のimport文")


def extract_from_file(self, file_path):
    """単一ファイルからimport情報を抽出（テスト用エイリアス）"""
    return self.extract_imports(file_path)


def extract_from_directory(self, directory):
    """ディレクトリ配下の全ファイルからimport情報を抽出"""
    from pathlib import Path

    directory = Path(directory)
    results = {}

    for py_file in directory.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        try:
            imports = self.extract_imports(py_file)
            results[str(py_file)] = imports
        except Exception:
            results[str(py_file)] = []

    return results
