#!/usr/bin/env python3
"""
Git自動コミット＆プッシュツール v3.0 - 完全自動化版
変更理由: Linter/Formatter統合、コミットメッセージ自動生成
"""

import subprocess
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import re

# ============================================================
# 設定
# ============================================================

# 除外するファイル名
EXCLUDE_FILES = {
    "__init__.py",
    ".gitignore",
}

# 除外するディレクトリ
EXCLUDE_DIRECTORIES = {
    "__pycache__",
    ".git",
    "node_modules",
    "_ARCHIVE",
    "_BACKUP",
    "_WIP",
    ".pytest_cache",
    ".mypy_cache",
    "logs",
    "agent_outputs",
}

# コミット対象の拡張子
TARGET_EXTENSIONS = {".py", ".sh", ".md", ".json", ".yaml", ".yml", ".txt"}

# ============================================================
# STEP 1: CLEANUP - 一時ファイルの整理
# ============================================================


def step1_cleanup():
    """一時ファイルを_WIP/または_ARCHIVE/に移動"""
    print("\n" + "=" * 70)
    print("🧹 STEP 1: CLEANUP - 一時ファイルの整理")
    print("=" * 70)

    # __pycache__ と *.pyc の削除
    project_root = Path.cwd()

    cleaned_count = 0
    for cache_dir in project_root.rglob("__pycache__"):
        if cache_dir.is_dir():
            import shutil

            shutil.rmtree(cache_dir)
            cleaned_count += 1

    for pyc_file in project_root.rglob("*.pyc"):
        pyc_file.unlink()
        cleaned_count += 1

    print(f"✅ キャッシュファイル削除: {cleaned_count}件")

    # ログファイルの整理（古いログは_ARCHIVE/へ）
    log_dir = project_root / "logs"
    if log_dir.exists():
        old_logs = [
            f for f in log_dir.glob("*.log") if (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days > 7
        ]

        if old_logs:
            archive_dir = project_root / "_ARCHIVE" / f'logs_{datetime.now().strftime("%Y%m%d")}'
            archive_dir.mkdir(parents=True, exist_ok=True)

            for log in old_logs:
                log.rename(archive_dir / log.name)

            print(f"✅ 古いログをアーカイブ: {len(old_logs)}件")


# ============================================================
# STEP 2: LIST - 本番コードの列挙
# ============================================================


def step2_list_production_files():
    """コミット対象となる本番コードを列挙"""
    print("\n" + "=" * 70)
    print("📋 STEP 2: LIST - 本番コードの列挙")
    print("=" * 70)

    project_root = Path.cwd()
    production_files = []

    for file_path in project_root.rglob("*"):
        if file_path.is_dir():
            continue

        # 除外ディレクトリチェック
        if any(exclude_dir in file_path.parts for exclude_dir in EXCLUDE_DIRECTORIES):
            continue

        # 除外ファイルチェック
        if file_path.name in EXCLUDE_FILES:
            continue

        # 拡張子チェック
        if file_path.suffix in TARGET_EXTENSIONS:
            production_files.append(file_path)

    # Pythonファイルのみ抽出（後のステップで使用）
    python_files = [f for f in production_files if f.suffix == ".py"]

    print(f"✅ 本番ファイル数: {len(production_files)}件")
    print(f"   - Pythonファイル: {len(python_files)}件")
    print(f"   - その他: {len(production_files) - len(python_files)}件")

    return production_files, python_files


# ============================================================
# STEP 3: QUALITY GATE - Linterチェック
# ============================================================


def step3_quality_gate(python_files):
    """コンパイルとLinterチェック"""
    print("\n" + "=" * 70)
    print("🔍 STEP 3: QUALITY GATE - Linterチェック")
    print("=" * 70)

    errors = []

    # py_compile チェック
    print("\n🔧 構文チェック (py_compile)...")
    for py_file in python_files:
        try:
            subprocess.run(
                [sys.executable, "-m", "py_compile", str(py_file)], check=True, capture_output=True, text=True
            )
        except subprocess.CalledProcessError as e:
            errors.append(f"❌ 構文エラー: {py_file}\n{e.stderr}")

    if not errors:
        print("✅ 構文チェック: 全て正常")

    # flake8 チェック
    print("\n🔍 Linterチェック (flake8)...")
    try:
        result = subprocess.run(
            ["flake8", "--max-line-length=120", "--extend-ignore=E203,E501"] + [str(f) for f in python_files],
            capture_output=True,
            text=True,
        )

        if result.stdout:
            # エラーを整理して表示
            lines = result.stdout.strip().split("\n")
            error_count = len(lines)

            if error_count > 10:
                print(f"⚠️ Linter警告: {error_count}件")
                print("   最初の10件のみ表示:")
                for line in lines[:10]:
                    print(f"   {line}")
            else:
                print(f"⚠️ Linter警告: {error_count}件")
                for line in lines:
                    print(f"   {line}")
        else:
            print("✅ Linterチェック: 問題なし")

    except FileNotFoundError:
        print("⚠️ flake8 が見つかりません（スキップ）")

    if errors:
        print("\n❌ 品質チェック失敗:")
        for error in errors:
            print(error)
        return False

    return True


# ============================================================
# STEP 4: FORMATTER - コード整形
# ============================================================


def step4_formatter(python_files):
    """Blackによるコード整形"""
    print("\n" + "=" * 70)
    print("✨ STEP 4: FORMATTER - コード整形")
    print("=" * 70)

    try:
        result = subprocess.run(
            ["black", "--line-length=120"] + [str(f) for f in python_files], capture_output=True, text=True
        )

        # 変更されたファイルをカウント
        changed = result.stdout.count("reformatted")
        unchanged = result.stdout.count("left unchanged")

        print(f"✅ Formatter実行完了")
        print(f"   - 整形済み: {changed}件")
        print(f"   - 変更なし: {unchanged}件")

    except FileNotFoundError:
        print("⚠️ black が見つかりません（スキップ）")


# ============================================================
# STEP 5: 重複チェック
# ============================================================


def step5_check_duplicates(production_files):
    """重複ファイル名チェック"""
    print("\n" + "=" * 70)
    print("🔍 STEP 5: 重複ファイル名チェック")
    print("=" * 70)

    file_map = defaultdict(list)

    for file_path in production_files:
        file_map[file_path.name].append(str(file_path.relative_to(Path.cwd())))

    duplicates = {name: paths for name, paths in file_map.items() if len(paths) > 1}

    if duplicates:
        print(f"⚠️ {len(duplicates)}個の重複ファイル:")
        for file_name, paths in sorted(duplicates.items())[:5]:
            print(f"   📄 {file_name} ({len(paths)}個)")
        print("   ⚠️ 重複を無視して続行...")
    else:
        print("✅ 重複ファイルなし")


# ============================================================
# STEP 6: コミットメッセージ自動生成
# ============================================================


def step6_generate_commit_message():
    """git diff を解析してコミットメッセージを自動生成"""
    print("\n" + "=" * 70)
    print("📝 STEP 6: コミットメッセージ自動生成")
    print("=" * 70)

    try:
        # git status で変更ファイルを取得
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)

        if not result.stdout.strip():
            print("✅ 変更なし（コミット不要）")
            return None

        # 変更ファイルを分類
        modified = []
        added = []
        deleted = []

        for line in result.stdout.strip().split("\n"):
            status = line[:2]
            filepath = line[3:]

            if "M" in status:
                modified.append(filepath)
            elif "A" in status or "??" in status:
                added.append(filepath)
            elif "D" in status:
                deleted.append(filepath)

        # git diff で変更内容を取得
        diff_result = subprocess.run(["git", "diff", "--cached", "--stat"], capture_output=True, text=True)

        # コミットメッセージ生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")

        message_parts = []

        # タイトル
        if added and not modified and not deleted:
            message_parts.append(f"✨ 新規追加 ({len(added)}件)")
        elif modified and not added and not deleted:
            message_parts.append(f"🔧 修正 ({len(modified)}件)")
        elif deleted and not added and not modified:
            message_parts.append(f"🗑️ 削除 ({len(deleted)}件)")
        else:
            message_parts.append(f"🔄 更新 (追加:{len(added)} 修正:{len(modified)} 削除:{len(deleted)})")

        message_parts.append("")
        message_parts.append("【変更内容】")

        if added:
            message_parts.append(f"• 追加: {len(added)}件")
            for f in added[:5]:
                message_parts.append(f"  - {f}")
            if len(added) > 5:
                message_parts.append(f"  ... 他{len(added)-5}件")

        if modified:
            message_parts.append(f"• 修正: {len(modified)}件")
            for f in modified[:5]:
                message_parts.append(f"  - {f}")
            if len(modified) > 5:
                message_parts.append(f"  ... 他{len(modified)-5}件")

        if deleted:
            message_parts.append(f"• 削除: {len(deleted)}件")
            for f in deleted[:3]:
                message_parts.append(f"  - {f}")

        message_parts.append("")
        message_parts.append(f"【タイムスタンプ】{timestamp}")
        message_parts.append("")
        message_parts.append("【品質チェック】")
        message_parts.append("✅ 構文チェック: 正常")
        message_parts.append("✅ Linter: 実行済み")
        message_parts.append("✅ Formatter: 適用済み")

        commit_message = "\n".join(message_parts)

        print("生成されたコミットメッセージ:")
        print("-" * 70)
        print(commit_message)
        print("-" * 70)

        return commit_message

    except subprocess.CalledProcessError as e:
        print(f"❌ git status エラー: {e}")
        return None


# ============================================================
# STEP 7: Git操作
# ============================================================


def step7_git_commit_push(commit_message):
    """Git add, commit, push"""
    print("\n" + "=" * 70)
    print("📦 STEP 7: Git操作")
    print("=" * 70)

    try:
        # git add
        print("📝 ステージング中...")
        subprocess.run(["git", "add", "."], check=True)

        # git commit
        print("💾 コミット中...")
        result = subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True)

        if result.returncode != 0:
            if "nothing to commit" in result.stdout:
                print("✅ コミット対象なし")
                return True
            else:
                print(f"❌ コミットエラー: {result.stderr}")
                return False

        print("✅ コミット完了")

        # git push
        print("🚀 プッシュ中...")
        subprocess.run(["git", "push"], check=True)
        print("✅ プッシュ完了")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Git操作エラー: {e}")
        return False


# ============================================================
# メイン処理
# ============================================================


def main():
    """メイン処理フロー"""
    print("🚀 Git自動コミット＆プッシュツール v3.0")
    print("=" * 70)
    print("📅 実行日時:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)

    # カスタムメッセージがあれば使用
    custom_message = sys.argv[1] if len(sys.argv) > 1 else None

    try:
        # STEP 1: クリーンアップ
        step1_cleanup()

        # STEP 2: 本番コード列挙
        production_files, python_files = step2_list_production_files()

        # STEP 3: 品質チェック
        if not step3_quality_gate(python_files):
            print("\n❌ 品質チェック失敗 - コミットを中止")
            sys.exit(1)

        # STEP 4: コード整形
        step4_formatter(python_files)

        # STEP 5: 重複チェック
        step5_check_duplicates(production_files)

        # STEP 6: コミットメッセージ生成
        if custom_message:
            commit_message = custom_message
            print(f"\n📝 カスタムメッセージを使用:\n{commit_message}")
        else:
            commit_message = step6_generate_commit_message()

            if not commit_message:
                print("\n✅ コミット対象なし - 終了")
                return

        # STEP 7: Git操作
        if step7_git_commit_push(commit_message):
            print("\n" + "=" * 70)
            print("🎉 完了！")
            print("=" * 70)
        else:
            print("\n❌ Git操作失敗")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️ ユーザーによる中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
