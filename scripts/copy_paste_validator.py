#!/usr/bin/env python3
"""
コピペバリデータ - 貼り付け前の構文チェック
"""
import sys
import re
import py_compile
import tempfile
import os


def validate_bash_script(content):
    """Bashスクリプトの構文チェック"""
    issues = []

    # 一般的なBash構文問題のチェック
    if "\\ \\" in content:
        issues.append("❌ 連続したバックスラッシュとスペースを検出")

    if content.count("(") != content.count(")"):
        issues.append("❌ 括弧の数が一致しません")

    if content.count("{") != content.count("}"):
        issues.append("❌ 波括弧の数が一致しません")

    # 不完全なヒアドキュメントをチェック
    heredoc_pattern = r'<<\s*[\'"]?([^\'"]+)[\'"]?'
    heredocs = re.findall(heredoc_pattern, content)
    for marker in heredocs:
        if content.count(marker) < 2:
            issues.append(f"❌ ヒアドキュメント '{marker}' が閉じられていません")

    return issues


def validate_python_syntax(content):
    """Python構文チェック"""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            temp_file = f.name

        py_compile.compile(temp_file, doraise=True)
        os.unlink(temp_file)
        return []
    except SyntaxError as e:
        os.unlink(temp_file)
        return [f"❌ Python構文エラー: {e}"]
    except Exception as e:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        return [f"❌ 検証エラー: {e}"]


def main():
    if len(sys.argv) != 2:
        print("使用方法: python3 copy_paste_validator.py <ファイル名>")
        print("または: cat script.sh | python3 copy_paste_validator.py -")
        sys.exit(1)

    filename = sys.argv[1]

    if filename == "-":
        content = sys.stdin.read()
    else:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

    print("🔍 コピペバリデーション開始...")
    print(f"   文字数: {len(content)}")
    print(f"   行数: {content.count(chr(10)) + 1}")

    all_issues = []

    # Bashスクリプトチェック
    bash_issues = validate_bash_script(content)
    all_issues.extend(bash_issues)

    # Pythonスクリプトチェック（Pythonコードがある場合）
    if "python3" in content or "import " in content:
        python_issues = validate_python_syntax(content)
        all_issues.extend(python_issues)

    # 結果表示
    if all_issues:
        print("\n❌ 検出された問題:")
        for issue in all_issues:
            print(f"   {issue}")
        print("\n💡 修正してから実行してください")
        return 1
    else:
        print("✅ 構文チェック完了 - 問題なし")
        return 0


if __name__ == "__main__":
    sys.exit(main())
