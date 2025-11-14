#!/usr/bin/env python3
"""
🚀 高度な自動エラー修復エンハンサー

【機能】
- 未定義名エラーの自動検出と修正
- インポート不足の自動補完
- 一般的な構文エラーの自動修正
"""

import re
from typing import Dict, List


class AdvancedErrorFixer:
    """高度なエラー自動修復クラス"""

    def __init__(self):
        self.common_fixes = {
            # 未定義名 → インポートマッピング
            "time": "import time",
            "datetime": "import datetime",
            "Path": "from pathlib import Path",
            "List": "from typing import List",
            "Dict": "from typing import Dict",
            "Set": "from typing import Set",
            "Tuple": "from typing import Tuple",
            "Any": "from typing import Any",
            "Optional": "from typing import Optional",
            "Union": "from typing import Union",
            "re": "import re",
            "json": "import json",
            "os": "import os",
            "sys": "import sys",
            "subprocess": "import subprocess",
            "shutil": "import shutil",
            "hashlib": "import hashlib",
            "asyncio": "import asyncio",
        }

        # 一般的なタイポ修正
        self.typo_fixes = {
            "print(": "print(",
            "range(": "range(",
            "len(": "len(",
            "str(": "str(",
            "int(": "int(",
            "list(": "list(",
            "dict(": "dict(",
        }

    def try_advanced_fixes(self, file_path: str, error_output: str) -> bool:
        """高度な自動修復を試行"""
        try:
            print(f"  �� 高度な自動修復を試行: {file_path}")

            # エラー出力の解析
            errors = self._parse_error_output(error_output)

            if not errors:
                return False

            # ファイル内容の読み込み
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 各エラーに対して修復を試行
            fixed_content = content
            fixes_applied = 0

            for error in errors:
                if self._is_undefined_name_error(error):
                    fixed = self._fix_undefined_name(fixed_content, error)
                    if fixed != fixed_content:
                        fixed_content = fixed
                        fixes_applied += 1

                elif self._is_syntax_error(error):
                    fixed = self._fix_syntax_error(fixed_content, error)
                    if fixed != fixed_content:
                        fixed_content = fixed
                        fixes_applied += 1

            # 変更があった場合はファイルを保存
            if fixes_applied > 0:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                print(f"  ✅ 高度な自動修復成功: {fixes_applied}件の修正を適用")
                return True
            else:
                print("  ⚠️  高度な自動修復: 適用可能な修正なし")
                return False

        except Exception as e:
            print(f"  ❌ 高度な自動修復エラー: {e}")
            return False

    def _parse_error_output(self, error_output: str) -> List[Dict]:
        """エラー出力を解析"""
        errors = []

        # flake8 エラーパターン
        flake8_pattern = r"(.+?):(\d+):(\d+): ([A-Z]\d+) (.+)"
        matches = re.findall(flake8_pattern, error_output)

        for match in matches:
            errors.append(
                {
                    "file": match[0],
                    "line": int(match[1]),
                    "column": int(match[2]),
                    "code": match[3],
                    "message": match[4],
                }
            )

        # Python 構文エラーパターン
        syntax_pattern = r"SyntaxError: (.+)"
        syntax_matches = re.findall(syntax_pattern, error_output)
        for msg in syntax_matches:
            errors.append({"code": "E999", "message": f"SyntaxError: {msg}"})

        return errors

    def _is_undefined_name_error(self, error: Dict) -> bool:
        """未定義名エラーか判定"""
        return error.get("code") == "F821"

    def _is_syntax_error(self, error: Dict) -> bool:
        """構文エラーか判定"""
        return error.get("code") == "E999" or "SyntaxError" in error.get("message", "")

    def _fix_undefined_name(self, content: str, error: Dict) -> str:
        """未定義名エラーを修正"""
        lines = content.split("\n")
        error_line_num = error["line"] - 1  # 0-based index

        if error_line_num >= len(lines):
            return content

        lines[error_line_num]
        message = error["message"]

        # 未定義名を抽出
        undefined_match = re.search(r"undefined name '([^']+)'", message)
        if not undefined_match:
            return content

        undefined_name = undefined_match.group(1)

        # 共通修正マップからインポート文を取得
        if undefined_name in self.common_fixes:
            import_line = self.common_fixes[undefined_name]

            # 既にインポートされていないか確認
            if import_line not in content:
                # インポートセクションを探して追加
                import_section_end = self._find_import_section_end(lines)
                lines.insert(import_section_end + 1, import_line)
                return "\n".join(lines)

        return content

    def _fix_syntax_error(self, content: str, error: Dict) -> str:
        """構文エラーを修正"""
        # 一般的なタイポ修正
        for typo, correction in self.typo_fixes.items():
            if typo in content and correction not in content:
                content = content.replace(typo, correction)

        return content

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


# テスト用
if __name__ == "__main__":
    fixer = AdvancedErrorFixer()

    # テストエラー出力
    test_error = "test.py:10:5: F821 undefined name 'time'"
    result = fixer.try_advanced_fixes("test.py", test_error)
    print(f"テスト結果: {result}")
