"""
汎用Pythonファイル変更フレームワーク v3.0
- 成功パターン（v21）をベースに設計
- リスト操作で確実に処理
- 設定ファイルで柔軟に対応
- 他のプロジェクトにも横展開可能

使い方:
    python3 tools/code_modifier/python_file_modifier.py \
        --config phase1_integration.yaml
"""

import sys
import yaml
from typing import List, Dict, Optional
from pathlib import Path


class PythonFileModifier:
    """Pythonファイルを確実に変更するフレームワーク"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.lines = f.readlines()
        self.output_lines = []
        print(f"✅ ファイル読み込み: {file_path} ({len(self.lines)}行)")

    def add_imports_after(self, target: str, imports: List[str]) -> "PythonFileModifier":
        """指定行の後にインポートを追加"""
        for i, line in enumerate(self.lines):
            self.output_lines.append(line)

            if target in line:
                for imp in imports:
                    if imp not in "".join(self.lines):
                        self.output_lines.append(imp + "\n")
                        print(f"✅ インポート追加: {imp.split('import')[-1].strip()[:40]}")

        # output_linesが空の場合はエラー
        if not self.output_lines:
            self.output_lines = self.lines.copy()

        return self

    def modify_class_method(
        self,
        class_name: str,
        method_name: str,
        signature_changes: Dict[str, str],
        code_to_add: str,
        add_position: str = "before_next_method",
    ) -> "PythonFileModifier":
        """
        クラスメソッドを変更

        Args:
            class_name: 対象クラス名
            method_name: 対象メソッド名（例: "__init__"）
            signature_changes: シグネチャ変更
                              {'old': 'def __init__(self):',
                               'new': 'def __init__(self, param: Type = None):'}
            code_to_add: 追加するコード（インデントなし）
            add_position: 追加位置（'before_next_method' or 'end_of_method'）
        """
        # まだ処理していない場合はlines、既に処理済みの場合はoutput_lines
        source_lines = self.output_lines if self.output_lines else self.lines
        self.output_lines = []

        class_found = False
        method_found = False
        method_start = -1
        method_end = -1

        for i, line in enumerate(source_lines):
            # クラス発見
            if f"class {class_name}" in line:
                class_found = True
                print(f"✅ クラス発見: {class_name} (行{i+1})")

            # メソッド発見
            if class_found and not method_found and f"def {method_name}(" in line:
                method_found = True
                method_start = i
                print(f"✅ メソッド発見: {method_name} (行{i+1})")

                # シグネチャ変更
                if signature_changes:
                    old_sig = signature_changes["old"]
                    new_sig = signature_changes["new"]

                    if old_sig in line:
                        line = line.replace(old_sig, new_sig)
                        print(f"✅ シグネチャ変更")

            self.output_lines.append(line)

            # メソッドの終わりを探す
            if method_found and method_end == -1:
                # 次のメソッド定義（同じインデントレベル）
                if i > method_start and line.strip().startswith(("def ", "async def ")):
                    # インデントレベルをチェック
                    method_indent = len(source_lines[method_start]) - len(
                        source_lines[method_start].lstrip()
                    )
                    current_indent = len(line) - len(line.lstrip())

                    if current_indent == method_indent:
                        method_end = i
                        print(f"✅ メソッド終了位置: (行{i+1}) {line.strip()[:40]}")

                        # コード追加
                        if code_to_add:
                            self.output_lines.insert(-1, "\n")
                            for code_line in code_to_add.strip().split("\n"):
                                indent = " " * (method_indent + 8)
                                self.output_lines.insert(-1, indent + code_line + "\n")
                            print(f"✅ コード追加完了")

        return self

    def validate(self) -> bool:
        """構文チェック"""
        import ast

        try:
            ast.parse("".join(self.output_lines))
            print("✅ 構文チェック成功")
            return True
        except SyntaxError as e:
            print(f"❌ 構文エラー: {e}")
            print(f"   行{e.lineno}: {e.text}")
            return False

    def save(self, output_path: Optional[str] = None) -> bool:
        """保存"""
        if output_path is None:
            output_path = self.file_path
        else:
            output_path = Path(output_path)

        # バックアップ
        if output_path == self.file_path:
            backup_path = Path(str(self.file_path) + ".backup")
            with open(backup_path, "w", encoding="utf-8") as f:
                f.writelines(self.lines)
            print(f"✅ バックアップ: {backup_path}")

        # 保存
        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(self.output_lines)
        print(f"✅ 保存: {output_path}")

        return True


def load_config(config_path: str) -> Dict:
    """設定ファイル読み込み"""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    if "--config" in sys.argv:
        # 設定ファイルモード
        config_path = sys.argv[sys.argv.index("--config") + 1]
        config = load_config(config_path)

        file_path = config["file"]
        modifier = PythonFileModifier(file_path)

        # インポート追加
        if "imports" in config:
            modifier.add_imports_after(
                target=config["imports"]["after"], imports=config["imports"]["add"]
            )

        # メソッド変更
        if "modify_method" in config:
            for mod in config["modify_method"]:
                modifier.modify_class_method(
                    class_name=mod["class"],
                    method_name=mod["method"],
                    signature_changes=mod.get("signature"),
                    code_to_add=mod.get("add_code", ""),
                )

        # 保存
        if modifier.validate():
            output = config.get("output", file_path)
            modifier.save(output)
        else:
            sys.exit(1)

    else:
        # 対話モード
        print("使い方: python3 python_file_modifier.py --config <設定ファイル>")
        sys.exit(1)


if __name__ == "__main__":
    main()
