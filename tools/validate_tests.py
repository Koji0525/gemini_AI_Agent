#!/usr/bin/env python3
"""
テスト検証ツール
"""
import subprocess
import sys


def validate_tests():
    """テストの検証を実行"""

    print("🧪 テスト検証を開始...")

    # 1. 構文チェック
    print("1. 構文チェック...")
    result = subprocess.run(
        ["python3", "-m", "py_compile", "tests/test_data_integration.py"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("❌ 構文エラー:", result.stderr)
        return False
    print("✅ 構文チェック完了")

    # 2. テスト実行
    print("2. テスト実行...")
    result = subprocess.run(
        ["python3", "-m", "pytest", "tests/test_data_integration.py", "-v"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("❌ テスト失敗:", result.stdout)
        return False
    print("✅ テスト実行完了")

    # 3. カバレッジチェック
    print("3. カバレッジチェック...")
    result = subprocess.run(
        [
            "python3",
            "-m",
            "pytest",
            "tests/test_data_integration.py",
            "--cov=tools.data_integration",
        ],
        capture_output=True,
        text=True,
    )
    print("📊 カバレッジレポート:")
    print(result.stdout)

    print("🎉 すべての検証が完了しました")
    return True


if __name__ == "__main__":
    success = validate_tests()
    sys.exit(0 if success else 1)
