#!/usr/bin/env python3
"""
実装詳細分析ツール - 実際の実装を深く理解する
"""
import importlib
import inspect
import sys
from pathlib import Path


class ImplementationAnalyzer:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        # Pythonパスを設定
        sys.path.insert(0, str(self.root_dir))

    def analyze_class_initialization(self, class_path):
        """クラスの初期化プロセスを分析"""
        try:
            module_path, class_name = class_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)

            print(f"🔍 {class_name} の初期化分析:")
            print(f"   モジュール: {module_path}")

            # コンストラクタの分析
            init_method = cls.__init__
            print(f"   __init__ シグネチャ: {inspect.signature(init_method)}")

            # ソースコードの取得（可能な場合）
            try:
                source = inspect.getsource(init_method)
                print(f"   __init__ ソース:")
                for i, line in enumerate(source.split("\n")[:10], 1):
                    print(f"     {i:2d}: {line}")
            except:
                print("   ⚠️  ソースコードを取得できません")

            # メソッドの一覧
            methods = [m for m in dir(cls) if not m.startswith("_") and callable(getattr(cls, m))]
            print(f"   公開メソッド: {', '.join(methods)}")

            return True
        except Exception as e:
            print(f"❌ 分析エラー: {e}")
            return False

    def analyze_method_flow(self, class_path, method_name):
        """特定メソッドの実行フローを分析"""
        try:
            module_path, class_name = class_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            method = getattr(cls, method_name)

            print(f"🔍 {class_name}.{method_name} の実行フロー分析:")

            # メソッドのシグネチャ
            print(f"   シグネチャ: {inspect.signature(method)}")

            # 非同期かどうか
            is_async = inspect.iscoroutinefunction(method)
            print(f"   非同期メソッド: {is_async}")

            # ソースコードの分析（簡易版）
            try:
                source = inspect.getsource(method)
                lines = source.split("\n")
                print(f"   メソッド行数: {len(lines)}")

                # 重要な処理の検出
                key_operations = [
                    ("API呼び出し", ["genai.", "generate_content", "list_models"]),
                    ("環境変数", ["os.getenv", "getenv"]),
                    ("例外処理", ["try:", "except", "raise"]),
                    ("非同期", ["async", "await"]),
                    ("戻り値", ["return {", "return result"]),
                ]

                for op_name, patterns in key_operations:
                    found = any(any(pattern in line for pattern in patterns) for line in lines)
                    print(f"   {op_name}の使用: {'✅' if found else '❌'}")

                # 戻り値の構造を分析
                return_lines = [
                    i
                    for i, line in enumerate(lines)
                    if "return {" in line or "return result" in line
                ]
                if return_lines:
                    print(f"   戻り値定義行: {[l+1 for l in return_lines]}")
                    for line_num in return_lines[:2]:  # 最初の2つのreturn文を表示
                        print(f"      {line_num+1}: {lines[line_num].strip()}")

            except Exception as e:
                print(f"   ⚠️  ソース分析エラー: {e}")

            return True
        except Exception as e:
            print(f"❌ メソッド分析エラー: {e}")
            return False

    def analyze_method_return_value(self, class_path, method_name):
        """メソッドの戻り値構造を詳細分析"""
        try:
            module_path, class_name = class_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            method = getattr(cls, method_name)

            source = inspect.getsource(method)
            lines = source.split("\n")

            print(f"🔍 {class_name}.{method_name} の戻り値分析:")

            # return文を検索
            return_blocks = []
            in_return_block = False
            current_block = []

            for i, line in enumerate(lines):
                if "return {" in line:
                    in_return_block = True
                    current_block = [line]
                elif in_return_block:
                    current_block.append(line)
                    if "}" in line and line.strip().startswith("}"):
                        return_blocks.append((i, current_block))
                        in_return_block = False
                        current_block = []

            for block_num, (line_num, block) in enumerate(return_blocks):
                print(f"   戻り値ブロック {block_num+1} (行 {line_num+1}):")
                for block_line in block:
                    # キーを抽出して表示
                    if ":" in block_line and '"' in block_line:
                        key_part = block_line.split(":")[0].strip()
                        print(f"     - {key_part}")

            return True
        except Exception as e:
            print(f"❌ 戻り値分析エラー: {e}")
            return False


def main():
    analyzer = ImplementationAnalyzer()

    print("📊 CodeGenerationAgent の詳細分析")
    print("=" * 50)

    # CodeGenerationAgent の分析
    analyzer.analyze_class_initialization(
        "agents.code_generation.code_generation_agent.CodeGenerationAgent"
    )
    print()

    analyzer.analyze_method_flow(
        "agents.code_generation.code_generation_agent.CodeGenerationAgent", "generate_code"
    )
    print()

    analyzer.analyze_method_return_value(
        "agents.code_generation.code_generation_agent.CodeGenerationAgent", "generate_code"
    )
    print()

    print("📊 実際の実装を確認")
    print("=" * 50)

    # 実際の実装ファイルを表示
    impl_file = Path("agents/code_generation/code_generation_agent.py")
    if impl_file.exists():
        print(f"📄 実装ファイル: {impl_file}")
        with open(impl_file, "r", encoding="utf-8") as f:
            content = f.read()
            # generate_code メソッドのreturn部分を抽出
            if "def generate_code(" in content:
                start = content.find("def generate_code(")
                end = content.find("def ", start + 1)
                if end == -1:
                    end = len(content)
                method_content = content[start:end]

                # return文を検索
                return_pos = method_content.find("return {")
                if return_pos != -1:
                    return_end = method_content.find("}", return_pos) + 1
                    return_block = method_content[return_pos:return_end]
                    print("🔍 generate_code の戻り値構造:")
                    for line in return_block.split("\n"):
                        if line.strip():
                            print(f"   {line.rstrip()}")


if __name__ == "__main__":
    main()
