#!/usr/bin/env python3
"""
AIコードレビューツール
定期的なコード品質チェックを自動化
"""

import subprocess
from pathlib import Path


def run_code_quality_checks():
    """コード品質チェックを実行"""

    checks = [
        ("構文チェック", ["python", "-m", "py_compile"]),
        ("型チェック", ["mypy", "--ignore-missing-imports"]),
        ("スタイルチェック", ["flake8"]),
        ("フォーマットチェック", ["black", "--check"]),
        ("インポート整理チェック", ["isort", "--check-only"]),
    ]

    print("🔍 AIコードレビュー実行中...")
    print("=" * 60)

    all_passed = True
    python_files = list(Path(".").rglob("*.py"))

    for check_name, command in checks:
        print(f"\n📋 {check_name}:")
        failed_files = []

        for file_path in python_files:
            if "venv" in str(file_path) or "__pycache__" in str(file_path):
                continue

            full_command = command + [str(file_path)]
            try:
                result = subprocess.run(full_command, capture_output=True, text=True, timeout=30)

                if result.returncode != 0:
                    failed_files.append((file_path, result.stderr))

            except subprocess.TimeoutExpired:
                print(f"   ⏰ {file_path}: タイムアウト")
            except Exception as e:
                print(f"   ❌ {file_path}: エラー - {e}")

        if failed_files:
            print(f"   ❌ {len(failed_files)}ファイルに問題")
            for file_path, error in failed_files[:3]:  # 最初の3件のみ表示
                print(f"      - {file_path}: {error.split(chr(10))[0]}")
            all_passed = False
        else:
            print("   ✅ すべてのファイルが合格")

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 すべてのコード品質チェックが合格しました！")
    else:
        print("⚠️ 一部のチェックで問題が見つかりました")

    return all_passed


if __name__ == "__main__":
    run_code_quality_checks()
