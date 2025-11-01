#!/usr/bin/env python3
"""
プログラム実行前に自動的にキャッシュクリーンアップを実行するラッパースクリプト
"""
import os
import sys
import subprocess


def clean_cache():
    """キャッシュをクリーンアップ"""
    print("�� 自動キャッシュクリーンアップ実行...")

    # clean_cache.sh が存在する場合はそれを使用
    if os.path.exists("./scripts/clean_cache.sh"):
        subprocess.run(["./scripts/clean_cache.sh"], check=False)
    else:
        # 直接キャッシュ削除を実行
        subprocess.run(["find", ".", "-name", "*.pyc", "-delete"], check=False)
        subprocess.run(
            ["find", ".", "-name", "__pycache__", "-type", "d", "-exec", "rm", "-rf", "{}", "+"],
            check=False,
            stderr=subprocess.DEVNULL,
        )
        print("✅ 基本キャッシュクリーンアップ完了")


def main():
    # キャッシュクリーンアップ実行
    clean_cache()

    # 元のプログラムを実行
    if len(sys.argv) > 1:
        original_program = sys.argv[1:]
        print(f"🚀 プログラム実行: {' '.join(original_program)}")
        os.execvp(original_program[0], original_program)
    else:
        print("❌ 実行するプログラムを指定してください")
        sys.exit(1)


if __name__ == "__main__":
    main()
