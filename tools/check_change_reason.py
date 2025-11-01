#!/usr/bin/env python3
"""変更理由記載チェック"""

import sys
import subprocess


def check_commit_message():
    """コミットメッセージに理由が含まれているか"""

    result = subprocess.run(["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True)

    message = result.stdout

    # 必須キーワード
    required = ["何が起きた", "原因", "狙い"]

    missing = []
    for keyword in required:
        if keyword not in message:
            missing.append(keyword)

    if missing:
        print("⚠️ コミットメッセージに以下が不足:")
        for m in missing:
            print(f"   - {m}")
        print()
        print("テンプレートを使用してください:")
        print("   git config commit.template .gitmessage")
        return False

    print("✅ 変更理由が適切に記載されています")
    return True


if __name__ == "__main__":
    if not check_commit_message():
        sys.exit(1)
