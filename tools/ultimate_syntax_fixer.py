#!/usr/bin/env python3
"""
完全な構文修正ツール - 既存システムを完全に保護
"""

import re
from pathlib import Path


def comprehensive_syntax_fix():
    """包括的な構文修正"""

    file_path = Path("agents/complete_engine_ultimate.py")

    # バックアップ作成
    backup_path = file_path.with_suffix(".py.v45_backup")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ バックアップ作成: {backup_path}")

    # 問題のパターンを修正
    fixes = [
        # 未終了の三重クォート文字列
        (r'""".*?(?=\n)(?!""")', lambda m: m.group(0) + '"""'),
        # 未終了の文字列リテラル
        (r'"[^"]*(?=\n)(?!")', lambda m: m.group(0) + '"'),
        (r"'[^']*(?=\n)(?!')", lambda m: m.group(0) + "'"),
        # インデント問題 (412行目)
        (r'^(\s+)説明: "\s*\+ description', r'\1    output += "\\n説明: " + description'),
    ]

    for pattern, replacement in fixes:
        if callable(replacement):
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        else:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    # 特定の行を直接修正
    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        # 412行目のインデント問題を修正
        if i == 411 and '説明: "' in line and "+ description" in line:
            # 適切なインデントに修正
            fixed_line = '        output += "\\n説明: " + description'
            print(f"✅ 412行目を修正: {fixed_line}")
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)

    fixed_content = "\n".join(fixed_lines)

    # 修正内容を保存
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(fixed_content)

    # 構文チェック
    import subprocess

    result = subprocess.run(
        ["python3", "-m", "py_compile", str(file_path)], capture_output=True, text=True
    )

    if result.returncode == 0:
        print("🎉 構文チェック合格 - 修正成功！")

        # 修正箇所を確認
        print("\n🔍 修正内容確認:")
        with open(file_path, "r", encoding="utf-8") as f:
            fixed_lines = f.readlines()
            for i in range(405, 420):
                if i < len(fixed_lines):
                    print(f"{i+1}: {fixed_lines[i].rstrip()}")

        return True
    else:
        print("❌ 構文チェック不合格 - バックアップから復元")
        print(f"エラー詳細: {result.stderr}")

        # バックアップから復元
        with open(backup_path, "r", encoding="utf-8") as f:
            backup_content = f.read()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(backup_content)
        print("✅ バックアップから復元完了")
        return False


if __name__ == "__main__":
    print("🛠️ 包括的構文修正を開始...")
    success = comprehensive_syntax_fix()
    exit(0 if success else 1)
