#!/usr/bin/env python3
"""出力形式検証"""

import sys
import re


def validate_format(text: str) -> bool:
    """R007形式チェック"""

    issues = []

    # 作業番号チェック
    if not re.search(r"# \d+\.", text):
        issues.append("作業番号なし")

    # 区切り線チェック
    if "━━━━" not in text:
        issues.append("区切り線なし")

    # コードブロックチェック
    if "```" in text and text.count("```") % 2 != 0:
        issues.append("コードブロック不完全")

    if issues:
        print("⚠️ 出力形式の問題:")
        for issue in issues:
            print(f"   - {issue}")
        return False

    print("✅ 出力形式OK")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python3 validate_output_format.py <ファイル>")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        content = f.read()

    if not validate_format(content):
        sys.exit(1)
