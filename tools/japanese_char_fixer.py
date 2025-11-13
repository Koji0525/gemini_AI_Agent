#!/usr/bin/env python3
"""
日本語文字による構文エラー修正ツール
既存システムを完全に保護しながら修正
"""

from pathlib import Path


def fix_japanese_chars():
    """日本語文字による構文エラーを修正"""

    file_path = Path("agents/complete_engine_ultimate.py")

    # バックアップ作成
    backup_path = file_path.with_suffix(".py.japanese_fixed_backup")
    with open(file_path, "r", encoding="utf-8") as f:
        original_content = f.read()

    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(original_content)

    print(f"✅ バックアップ作成: {backup_path}")

    # 問題のパターンを修正
    lines = original_content.split("\n")
    fixed_lines = []
    changes_made = 0

    for i, line in enumerate(lines, 1):
        fixed_line = line

        # 3行目の全角句点を修正
        if i == 3 and "。" in line:
            # 全角句点をピリオドに置換、またはコメントアウト
            if line.strip().startswith("このモジュール"):
                # 日本語の説明文をコメントアウト
                fixed_line = "# " + line
                print(f"✅ 3行目をコメントアウト: {fixed_line}")
                changes_made += 1

        # その他の全角句点を含む行をチェック（コメント以外）
        elif "。" in line and not line.strip().startswith("#"):
            # コード行の場合は修正、コメント行はそのまま
            if not any(keyword in line for keyword in ['"""', "'''", "#"]):
                fixed_line = line.replace("。", ".")  # 全角句点をピリオドに置換
                if fixed_line != line:
                    print(f"✅ {i}行目の全角句点を修正: {fixed_line}")
                    changes_made += 1

        fixed_lines.append(fixed_line)

    fixed_content = "\n".join(fixed_lines)

    # 修正内容を保存
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(fixed_content)

    print(f"📝 修正箇所: {changes_made}箇所")

    # 構文チェック
    import subprocess

    result = subprocess.run(
        ["python3", "-m", "py_compile", str(file_path)], capture_output=True, text=True
    )

    if result.returncode == 0:
        print("🎉 構文チェック合格 - 日本語文字問題を解決！")

        # 修正箇所を確認
        print("\n🔍 修正内容確認:")
        with open(file_path, "r", encoding="utf-8") as f:
            fixed_lines = f.readlines()
            for i in range(0, min(10, len(fixed_lines))):
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
    print("🈲 日本語文字による構文エラー修正を開始...")
    success = fix_japanese_chars()
    exit(0 if success else 1)
