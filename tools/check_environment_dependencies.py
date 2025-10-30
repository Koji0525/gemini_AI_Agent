#!/usr/bin/env python3
"""環境依存コード検出ツール（R012）"""

import sys
import re
from pathlib import Path


def check_file(file_path):
    """ファイル内の環境依存コードを検出"""

    with open(file_path, "r") as f:
        lines = f.readlines()

    issues = []

    for i, line in enumerate(lines, 1):
        # DISPLAY設定
        if "DISPLAY=" in line and "os.environ" not in line:
            issues.append(
                {
                    "line": i,
                    "type": "DISPLAY設定",
                    "message": "Pythonコード内でDISPLAY設定（シェルスクリプトに分離推奨）",
                    "code": line.strip(),
                }
            )

        # Geminiセレクタ
        if re.search(r"(Locator|contenteditable|data-test-id)", line):
            if "BrowserController" not in Path(file_path).read_text():
                issues.append(
                    {
                        "line": i,
                        "type": "UIセレクタ",
                        "message": "BrowserController外でUIセレクタ使用",
                        "code": line.strip(),
                    }
                )

        # 直接的なブラウザ操作
        if re.search(r"page\.(click|fill|goto)", line):
            if "browser_controller" not in file_path.lower():
                issues.append(
                    {
                        "line": i,
                        "type": "ブラウザ直接操作",
                        "message": "BrowserController経由推奨",
                        "code": line.strip(),
                    }
                )

    return issues


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python3 check_environment_dependencies.py <ファイル>")
        sys.exit(1)

    file_path = sys.argv[1]
    issues = check_file(file_path)

    if issues:
        print(f"\n⚠️ {file_path} で環境依存コードを検出:\n")
        for issue in issues:
            print(f"行{issue['line']}: {issue['type']}")
            print(f"  {issue['message']}")
            print(f"  コード: {issue['code']}")
            print()
    else:
        print(f"✅ {file_path}: 環境依存コードなし")
