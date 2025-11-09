#!/usr/bin/env python3
"""
自動コミット&プッシュツール v10 - テストキャッシュ対応版
テストキャッシュにより、変更されていないファイルのテストをスキップ
"""

import subprocess
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# TestCacheManager をインポート
from tools.test_cache_manager import TestCacheManager


def run_command(cmd, check=True, capture_output=False):
    """コマンドを実行"""
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=check)
            return None
    except subprocess.CalledProcessError as e:
        if capture_output and hasattr(e, "stderr"):
            print(f"❌ エラー: {e.stderr}")
        raise


def get_python_files():
    """Pythonファイルのリストを取得"""
    result = run_command("git diff --cached --name-only --diff-filter=ACM", capture_output=True)
    files = [f for f in result.split("\n") if f.endswith(".py") and f]
    return files


def run_flake8_check(files):
    """Flake8チェック（キャッシュ対応）"""
    print("\n🔍 STEP 4: 致命的エラーチェック")
    print("=" * 50)

    cache = TestCacheManager()

    # テストすべきファイルとスキップするファイルを判定
    to_check, to_skip = cache.get_files_to_test(files)

    if to_skip:
        print(f"⚡ キャッシュヒット: {len(to_skip)}件スキップ")
        for f in to_skip:
            print(f"  ✅ {f} (前回チェック済み)")

    if not to_check:
        print("✅ すべてのファイルがキャッシュ済み - スキップ")
        return True

    print(f"🔍 チェック対象: {len(to_check)}件")

    has_error = False
    for file_path in to_check:
        result = subprocess.run(
            f"python3 -m flake8 {file_path} --select=F821 --show-source",
            shell=True,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(f"  ✅ {file_path}")
            # キャッシュに記録
            cache.update_file_hash(file_path)
            cache.record_test_result(file_path, passed=True)
        else:
            print(f"❌ 致命的エラー: {file_path}")
            print(result.stdout)
            has_error = True
            # エラーもキャッシュに記録
            cache.update_file_hash(file_path)
            cache.record_test_result(file_path, passed=False, error_msg=result.stdout[:200])

    if has_error:
        print("❌ STEP 4 エラー: 致命的エラーあり")
        return False

    print("✅ STEP 4 完了: 致命的エラーなし")
    return True


def run_tests_cached():
    """テスト実行（キャッシュ対応）"""
    print("\n🧪 STEP 5: テスト実行（キャッシュ最適化版）")
    print("=" * 50)

    cache = TestCacheManager()

    # テストファイルのリストを取得
    test_files = [
        "tests/unit/test_knowledge_base_adapter.py",
        "tests/unit/test_observability_manager.py",
        "tests/unit/test_knowledge_manager.py",
        "tests/unit/test_observability_core.py",
    ]

    # 各テストファイルとその依存ファイルをチェック
    to_test, to_skip = cache.get_files_to_test(test_files)

    if to_skip:
        print(f"⚡ キャッシュヒット: {len(to_skip)}件のテストをスキップ")
        for f in to_skip:
            print(f"  ✅ {f} (前回成功)")

    if not to_test:
        print("✅ すべてのテストがキャッシュ済み - スキップ")
        return True

    print(f"🧪 実行対象: {len(to_test)}件")

    # テスト実行
    test_files_str = " ".join(to_test)
    result = subprocess.run(
        f"pytest {test_files_str} -v -q --tb=line", shell=True, capture_output=True, text=True
    )

    # 結果を記録
    for test_file in to_test:
        cache.update_file_hash(test_file)
        cache.record_test_result(test_file, passed=(result.returncode == 0))

    if result.returncode != 0:
        print("❌ テスト失敗:")
        print(result.stdout)
        print(result.stderr)
        return False

    print("✅ すべてのテストが成功")
    return True


def main():
    """メイン処理"""
    print("🚀 自動コミット&プッシュツール v10 (キャッシュ対応)")
    print("=" * 50)

    try:
        # Pythonファイルを取得
        python_files = get_python_files()

        if not python_files:
            print("ℹ️  変更されたPythonファイルがありません")
            return 0

        print(f"📝 変更ファイル数: {len(python_files)}")

        # STEP 4: Flake8チェック（キャッシュ対応）
        if not run_flake8_check(python_files):
            print("\n❌ 致命的エラーがあります。修正してください。")
            return 1

        # STEP 5: テスト実行（キャッシュ対応）
        if not run_tests_cached():
            print("\n❌ テストが失敗しました。修正してください。")
            return 1

        # STEP 9: コミット&プッシュ
        print("\n📤 STEP 9: コミット & プッシュ")
        print("=" * 50)

        # コミット
        run_command('git commit -m "🚀 自動コミット（キャッシュ最適化版）"')
        print("✅ コミット成功")

        # プッシュ
        run_command("git push")
        print("✅ プッシュ成功")

        print("\n🎉 すべての処理が完了しました！")
        return 0

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Git操作失敗: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
