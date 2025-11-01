#!/usr/bin/env python3
"""誤解を招くエラーメッセージを検出"""

import re
from pathlib import Path


def check_file(file_path):
    """ファイルをチェック"""
    with open(file_path, "r") as f:
        lines = f.readlines()

    issues = []

    for i, line in enumerate(lines, 1):
        # 汎用すぎるエラーメッセージ
        if re.search(r'raise Exception\(["\'].*失敗.*["\']\)', line):
            issues.append({"line": i, "type": "汎用エラー", "message": line.strip()})

    return issues


if __name__ == "__main__":
    py_files = Path(".").rglob("*.py")

    for file in py_files:
        if any(ex in str(file) for ex in ["_ARCHIVE", "_BACKUP", "__pycache__"]):
            continue

        issues = check_file(file)

        if issues:
            print(f"\n⚠️ {file}")
            for issue in issues:
                print(f"   行{issue['line']}: {issue['type']}")
                print(f"   → {issue['message']}")
