"""
汎用Pythonファイル変更フレームワーク v2.0
- v21の成功パターンを完全移植
- インデント計算を修正
"""

import sys
import yaml
from typing import List, Dict, Optional
from pathlib import Path


class PythonFileModifier:
    """v21の成功ロジックをベースにした確実なファイル変更"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.lines = f.readlines()
        print(f"✅ ファイル読み込み: {file_path} ({len(self.lines)}行)")

    def apply_phase1_integration(
        self, class_name: str, imports_config: Dict, method_config: Dict
    ) -> List[str]:
        """
        Phase 1統合を適用（v21の成功ロジック）

        Returns:
            変更後の行リスト
        """
        output_lines = []

        # ステップ1: インポート追加
        import_added = False
        for i, line in enumerate(self.lines):
            output_lines.append(line)

            # dotenvの次に追加
            if not import_added and imports_config["after"] in line:
                for imp in imports_config["add"]:
                    if imp not in "".join(self.lines):
                        output_lines.append(imp + "\n")
                        print(f"✅ インポート追加: {imp.split('import')[-1].strip()[:40]}")
                import_added = True

        # ステップ2: クラスと__init__を探す
        final_output = []
        class_found = False
        init_found = False

        for i, line in enumerate(output_lines):
            final_output.append(line)

            # クラス発見
            if f"class {class_name}:" in line:
                class_found = True
                print(f"✅ クラス発見: {class_name} (行{i+1})")

                # __init__を探す
                for j in range(i + 1, len(output_lines)):
                    final_output.append(output_lines[j])

                    # __init__発見
                    if "    def __init__(self):" in output_lines[j]:
                        init_found = True
                        print(f"✅ __init__発見 (行{j+1})")

                        # シグネチャ変更
                        sig_changes = method_config["signature"]
                        final_output[-1] = final_output[-1].replace(
                            sig_changes["old"], sig_changes["new"]
                        )
                        print(f"✅ シグネチャ変更")

                        # __init__の中身をコピー（次のasync defまで）
                        init_start = j + 1
                        init_end = -1

                        for k in range(init_start, len(output_lines)):
                            if output_lines[k].startswith("    async def "):
                                init_end = k
                                print(
                                    f"✅ __init__終了位置 (行{k+1}): {output_lines[k].strip()[:40]}"
                                )
                                break

                        if init_end == -1:
                            print("❌ __init__の終了位置が見つかりません")
                            return []

                        # __init__の中身をコピー
                        for k in range(init_start, init_end):
                            final_output.append(output_lines[k])

                        # Phase 1コード追加
                        final_output.append("\n")
                        for code_line in method_config["add_code"].strip().split("\n"):
                            final_output.append("        " + code_line + "\n")
                        print(f"✅ Phase 1コード追加")

                        # 残りをコピー
                        for k in range(init_end, len(output_lines)):
                            final_output.append(output_lines[k])

                        return final_output

        if not class_found:
            print(f"❌ クラス {class_name} が見つかりません")
        if not init_found:
            print(f"❌ __init__が見つかりません")

        return []

    def save(self, output_lines: List[str], output_path: Optional[str] = None) -> bool:
        """保存"""
        if not output_lines:
            print("❌ 保存するデータがありません")
            return False

        # 構文チェック
        import ast

        try:
            ast.parse("".join(output_lines))
            print("✅ 構文チェック成功")
        except SyntaxError as e:
            print(f"❌ 構文エラー: {e}")
            print(f"   行{e.lineno}: {e.text}")
            return False

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
            f.writelines(output_lines)
        print(f"✅ 保存: {output_path}")

        return True


def main():
    if "--config" not in sys.argv:
        print("使い方: python3 python_file_modifier_v2.py --config <設定ファイル>")
        sys.exit(1)

    config_path = sys.argv[sys.argv.index("--config") + 1]
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    file_path = config["file"]
    output_path = config.get("output", file_path)

    modifier = PythonFileModifier(file_path)

    # Phase 1統合を適用
    output_lines = modifier.apply_phase1_integration(
        class_name="IntegratedOrchestrator",
        imports_config=config["imports"],
        method_config=config["modify_method"][0],
    )

    if output_lines:
        if modifier.save(output_lines, output_path):
            print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("✅ Phase 1統合完了")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        else:
            sys.exit(1)
    else:
        print("❌ 処理失敗")
        sys.exit(1)


if __name__ == "__main__":
    main()
