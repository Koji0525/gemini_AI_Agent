#!/usr/bin/env python3
"""
構文チェックスクリプト
修正されたファイルの構文を確認します
"""

import subprocess
import sys


def check_python_syntax(file_path):
    """Pythonファイルの構文をチェック"""
    try:
        result = subprocess.run([sys.executable, "-m", "py_compile", file_path], capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ {file_path}: 構文チェック合格")
            return True
        else:
            print(f"❌ {file_path}: 構文エラー")
            print(f"エラー内容:\n{result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 構文チェック実行エラー: {e}")
        return False


if __name__ == "__main__":
    files_to_check = ["automation/modules/wp_data_populator_v11_comprehensive.py"]

    all_passed = True
    for file_path in files_to_check:
        if not check_python_syntax(file_path):
            all_passed = False

    if all_passed:
        print("\n🎉 すべてのファイルが構文チェックを通過しました")
        sys.exit(0)
    else:
        print("\n❌ 構文エラーがあります")
        sys.exit(1)
