#!/usr/bin/env python3
"""
安全な構文修正ツール
既存システムを破壊しない方法で構文エラーを修正
"""

from pathlib import Path


def fix_syntax_errors():
    """構文エラーを安全に修正"""

    file_path = Path("agents/complete_engine_ultimate.py")

    # バックアップ作成
    backup_path = file_path.with_suffix(".py.backup")
    with open(file_path, "r", encoding="utf-8") as f:
        original_content = f.read()

    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(original_content)

    print(f"✅ バックアップ作成: {backup_path}")

    # 問題の行を修正
    lines = original_content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines, 1):
        fixed_line = line

        # 410行目付近の未終了文字列リテラルを修正
        if i == 410 and '説明: " + description' in line and not line.strip().endswith('"'):
            # 文字列リテラルを適切に閉じる
            fixed_line = line.rstrip() + '"'
            print(f"✅ 410行目を修正: {fixed_line}")

        # その他の未終了文字列リテラルをチェック
        elif '"' in line and line.count('"') % 2 != 0 and not line.rstrip().endswith('"'):
            # 未終了の文字列リテラルを検出
            fixed_line = line.rstrip() + '"'
            print(f"⚠️  {i}行目で未終了文字列を修正: {fixed_line}")

        fixed_lines.append(fixed_line)

    # 修正内容を保存
    fixed_content = "\n".join(fixed_lines)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(fixed_content)

    # 構文チェック
    import subprocess

    result = subprocess.run(
        ["python3", "-m", "py_compile", str(file_path)], capture_output=True, text=True
    )

    if result.returncode == 0:
        print("✅ 構文チェック合格 - 修正成功")
        return True
    else:
        print("❌ 構文チェック不合格 - バックアップから復元")
        print(f"エラー: {result.stderr}")

        # バックアップから復元
        with open(backup_path, "r", encoding="utf-8") as f:
            backup_content = f.read()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(backup_content)
        print("✅ バックアップから復元完了")
        return False


if __name__ == "__main__":
    success = fix_syntax_errors()
    exit(0 if success else 1)
