#!/usr/bin/env python3
"""
コード探索ツール - 実際の実装構造を調査
"""
import ast
import importlib
import inspect
from pathlib import Path


class CodeExplorer:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)

    def find_class_definitions(self, class_name):
        """指定したクラス名の定義を検索"""
        results = []
        for py_file in self.root_dir.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and class_name in node.name:
                        results.append(
                            {"file": str(py_file), "class_name": node.name, "line": node.lineno}
                        )
            except Exception as e:
                print(f"❌ {py_file} の解析中にエラー: {e}")

        return results

    def get_module_structure(self, module_path):
        """モジュールの構造を取得"""
        try:
            spec = importlib.util.spec_from_file_location("module", module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            structure = {"classes": [], "functions": [], "attributes": []}

            for name in dir(module):
                if not name.startswith("_"):
                    obj = getattr(module, name)
                    if inspect.isclass(obj):
                        structure["classes"].append(name)
                    elif inspect.isfunction(obj):
                        structure["functions"].append(name)
                    else:
                        structure["attributes"].append(name)

            return structure
        except Exception as e:
            return f"エラー: {e}"

    def explore_agent_structure(self):
        """エージェントの構造を探索"""
        agents_dir = self.root_dir / "agents"
        results = {}

        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir():
                agent_name = agent_dir.name
                results[agent_name] = {}

                for py_file in agent_dir.rglob("*.py"):
                    structure = self.get_module_structure(py_file)
                    results[agent_name][py_file.name] = structure

        return results


def main():
    explorer = CodeExplorer()

    print("🔍 Gemini関連のクラスを検索中...")
    gemini_classes = explorer.find_class_definitions("Gemini")
    print("📋 検索結果:")
    for result in gemini_classes:
        print(f"  - {result['class_name']} in {result['file']}:{result['line']}")

    print("\n🔍 エージェント構造を探索中...")
    agent_structure = explorer.explore_agent_structure()

    print("📋 エージェント構造:")
    for agent, files in agent_structure.items():
        print(f"\n🤖 {agent}:")
        for file, structure in files.items():
            print(f"  📄 {file}:")
            if isinstance(structure, dict):
                if structure["classes"]:
                    print(f"    🏛️  クラス: {', '.join(structure['classes'])}")
                if structure["functions"]:
                    print(f"    🔧 関数: {', '.join(structure['functions'])}")


if __name__ == "__main__":
    main()
