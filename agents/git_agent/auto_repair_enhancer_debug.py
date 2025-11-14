#!/usr/bin/env python3
"""
🔧 自動修復拡張モジュール デバッグ版
"""

import re
from typing import List


class StandardLibraryFixerDebug:
    """標準ライブラリ自動修復クラス - デバッグ版"""

    def __init__(self):
        self.stdlib_modules = {
            "time": "import time",
            "math": "import math",
            "random": "import random",
        }

    def debug_analyze_and_fix(self, file_path: str, error_output: str) -> bool:
        """デバッグ用の分析と修正"""
        print(f"  🔍 デバッグ: ファイル {file_path} を分析")
        print(f"  🔍 デバッグ: エラー出力: {error_output}")

        # F821 undefined name エラーパターンを検出
        f821_pattern = r"F821 undefined name '([^']+)'"
        undefined_names = re.findall(f821_pattern, error_output)
        print(f"  🔍 デバッグ: 未定義名: {undefined_names}")

        for name in undefined_names:
            if name in self.stdlib_modules:
                import_statement = self.stdlib_modules[name]
                print(f"  🔍 デバッグ: {name} に対応するインポート: {import_statement}")
                return self.debug_fix_import(file_path, import_statement)

        return False

    def debug_fix_import(self, file_path: str, import_statement: str) -> bool:
        """デバッグ用のインポート修正"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            print(f"  🔍 デバッグ: 修正前のファイル内容（最初の50行）:")
            lines = content.split("\n")
            for i, line in enumerate(lines[:50]):
                print(f"    {i+1}: {line}")

            # 既にインポートされているかチェック
            if import_statement in content:
                print(f"  🔍 デバッグ: {import_statement} は既に存在します")
                return True

            # インポートセクションを探す
            import_section_end = self._find_import_section_end(lines)
            print(f"  🔍 デバッグ: インポートセクション終了位置: {import_section_end}")

            # インポートを追加
            lines.insert(import_section_end + 1, import_statement)

            # ファイルを保存
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            print(f"  ✅ デバッグ: {import_statement} を追加しました")

            # 修正後の確認
            with open(file_path, "r", encoding="utf-8") as f:
                new_content = f.read()
            print(f"  🔍 デバッグ: 修正後のファイル内容（最初の50行）:")
            new_lines = new_content.split("\n")
            for i, line in enumerate(new_lines[:50]):
                print(f"    {i+1}: {line}")

            return True

        except Exception as e:
            print(f"  ❌ デバッグ: 修正失敗: {e}")
            return False

    def _find_import_section_end(self, lines: List[str]) -> int:
        """インポートセクションの終了位置を検出"""
        last_import_line = -1

        for i, line in enumerate(lines):
            stripped = line.strip()
            if (
                stripped.startswith("import ")
                or stripped.startswith("from ")
                or stripped == ""
                or stripped.startswith("#")
            ):
                last_import_line = i
            else:
                break

        return max(last_import_line, 0)


# デバッグ実行
if __name__ == "__main__":
    fixer = StandardLibraryFixerDebug()
    result = fixer.debug_analyze_and_fix(
        "/workspaces/gemini_AI_Agent/agents/complete_engine_final_v4.py",
        "F821 undefined name 'time'",
    )
    print(f"デバッグ結果: {result}")
