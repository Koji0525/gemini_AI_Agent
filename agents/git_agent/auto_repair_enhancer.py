#!/usr/bin/env python3
"""
🔧 自動修復拡張モジュール v1.0
既存の自動コミットツールに追加するだけで、標準ライブラリの自動修復機能を拡張
"""

import re
from typing import List


class StandardLibraryFixer:
    """標準ライブラリ自動修復クラス - 既存機能に追加するだけ"""

    def __init__(self):
        # 標準ライブラリモジュールのマッピング
        self.stdlib_modules = {
            "time": "import time",
            "math": "import math",
            "random": "import random",
            "collections": "import collections",
            "itertools": "import itertools",
            "functools": "import functools",
            "logging": "import logging",
            "argparse": "import argparse",
            "csv": "import csv",
            "pickle": "import pickle",
            "sqlite3": "import sqlite3",
            "threading": "import threading",
            "multiprocessing": "import multiprocessing",
            "asyncio": "import asyncio",
            "unittest": "import unittest",
            "datetime": "import datetime",
        }

        # 使用パターンからモジュールを推測するマップ
        self.usage_patterns = {
            "time": [r"time\.sleep", r"time\.time", r"time\.strftime"],
            "math": [r"math\.sqrt", r"math\.pi", r"math\.cos"],
            "random": [r"random\.randint", r"random\.choice"],
            "os": [r"os\.path", r"os\.getenv", r"os\.listdir"],
            "sys": [r"sys\.argv", r"sys\.exit", r"sys\.path"],
            "json": [r"json\.loads", r"json\.dumps"],
            "re": [r"re\.search", r"re\.match", r"re\.findall"],
            "datetime": [r"datetime\.datetime", r"datetime\.date"],
        }

    def enhance_import_analysis(
        self, file_path: str, error_output: str, current_missing_imports: List[str]
    ) -> List[str]:
        """既存のインポート分析を拡張 - 標準ライブラリを追加"""
        enhanced_imports = current_missing_imports.copy()

        # F821 undefined name エラーパターンを検出
        f821_pattern = r"F821 undefined name '([^']+)'"
        undefined_names = re.findall(f821_pattern, error_output)

        for name in undefined_names:
            # 標準ライブラリモジュールをチェック
            if name in self.stdlib_modules and self.stdlib_modules[name] not in enhanced_imports:
                enhanced_imports.append(self.stdlib_modules[name])
                continue

            # 動的分析: ファイル内の使用パターンから推測
            guessed_import = self._guess_import_from_usage(file_path, name)
            if guessed_import and guessed_import not in enhanced_imports:
                enhanced_imports.append(guessed_import)

        return enhanced_imports

    def _guess_import_from_usage(self, file_path: str, undefined_name: str) -> str:
        """ファイル内の使用パターンからインポートを推測"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 使用パターンからモジュールを推測
            for module, patterns in self.usage_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content):
                        return f"import {module}"

            return ""

        except Exception:
            return ""

    def fix_standard_library_imports(self, file_path: str, missing_imports: List[str]) -> bool:
        """標準ライブラリのインポートを自動追加"""
        if not missing_imports:
            return True

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")

            # 既存のインポートセクションを探す
            import_section_end = self._find_import_section_end(lines)

            # 重複を避けてインポートを追加
            imports_to_add = []
            for imp in missing_imports:
                if imp not in content:
                    imports_to_add.append(imp)

            if imports_to_add:
                # インポートを追加
                for imp in reversed(imports_to_add):
                    lines.insert(import_section_end + 1, imp)

                # ファイルを保存
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))

                print(f"  ✅ 標準ライブラリインポート追加: {', '.join(imports_to_add)}")
                return True
            else:
                return True

        except Exception as e:
            print(f"  ❌ 標準ライブラリインポート追加失敗: {e}")
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


class AdvancedErrorFixer:
    """高度なエラー修正クラス - 既存機能に追加するだけ"""

    def __init__(self):
        self.stdlib_fixer = StandardLibraryFixer()

    def try_advanced_fixes(self, file_path: str, error_output: str) -> bool:
        """高度な自動修正を試行"""
        print("  🔧 高度な自動修復を試行します")

        # インポートエラーの処理
        if self._handle_import_errors(file_path, error_output):
            return True

        return False

    def _handle_import_errors(self, file_path: str, error_output: str) -> bool:
        """インポート関連エラーの処理"""
        # F821 undefined name エラーを処理
        if "F821 undefined name" in error_output:
            # 標準ライブラリのインポートを分析
            enhanced_imports = self.stdlib_fixer.enhance_import_analysis(
                file_path, error_output, []
            )

            if enhanced_imports:
                return self.stdlib_fixer.fix_standard_library_imports(file_path, enhanced_imports)

        return False
