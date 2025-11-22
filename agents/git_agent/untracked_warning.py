#!/usr/bin/env python3
"""
Untracked ファイル自動追加ツール v2.0

【目的】
auto_commit_push 実行前に Untracked ファイルを検出し、
自動的に git add する

【変更履歴】
v1.0: 警告のみ
v2.0: 自動 git add 機能追加（再発防止）

【使用方法】
python3 agents/git_agent/untracked_warning.py

【推奨運用】
SKIP_AUTO_REPAIR=true python3 agents/git_agent/auto_commit_push_v11_force_push.py
の前に実行、または && で連結
"""

import os
import subprocess
import sys


def get_untracked_files():
    """Untracked ファイルを取得"""
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True
    )

    # 重要なファイル拡張子
    important_extensions = (".py", ".html", ".sh", ".yaml", ".yml", ".json", ".md", ".css", ".js")

    # 除外パターン（機密ファイル、一時ファイル）
    exclude_patterns = (
        "__pycache__",
        ".pyc",
        "node_modules",
        ".env",
        "credentials",
        ".key",
        ".pem",
        ".secret",
        ".db",
        ".sqlite",
        ".log",
    )

    untracked = []
    for f in result.stdout.strip().split("\n"):
        if not f:
            continue
        # 除外パターンに一致しない & 重要な拡張子
        if not any(ex in f for ex in exclude_patterns):
            if f.endswith(important_extensions):
                untracked.append(f)

    return untracked


def check_file_size(file_path, max_size_mb=5):
    """ファイルサイズをチェック（巨大ファイル警告）"""
    try:
        size = os.path.getsize(file_path)
        size_mb = size / (1024 * 1024)
        return size_mb <= max_size_mb, size_mb
    except OSError:
        return True, 0


def auto_add_files(files):
    """ファイルを自動的に git add"""
    added = []
    skipped = []

    for f in files:
        # ファイルサイズチェック
        size_ok, size_mb = check_file_size(f)
        if not size_ok:
            print(f"  ⚠️  スキップ（{size_mb:.1f}MB > 5MB）: {f}")
            skipped.append(f)
            continue

        # git add 実行
        result = subprocess.run(["git", "add", f], capture_output=True, text=True)

        if result.returncode == 0:
            print(f"  ✅ 追加: {f}")
            added.append(f)
        else:
            print(f"  ❌ 失敗: {f} ({result.stderr.strip()})")
            skipped.append(f)

    return added, skipped


def main():
    print("=" * 60)
    print("🔍 Untracked ファイル自動追加ツール v2.0")
    print("=" * 60)

    # Untracked ファイル取得
    untracked = get_untracked_files()

    if not untracked:
        print("\n✅ Untracked ファイルなし（全て追跡済み）")
        print("=" * 60)
        return 0

    print(f"\n📋 検出されたファイル: {len(untracked)}件")
    print("-" * 60)

    # ファイル一覧表示
    for f in untracked:
        print(f"  📄 {f}")

    print("-" * 60)
    print("\n🔧 自動的に git add を実行します...")
    print("-" * 60)

    # 自動追加
    added, skipped = auto_add_files(untracked)

    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 結果サマリー")
    print("=" * 60)
    print(f"  ✅ 追加成功: {len(added)}件")
    if skipped:
        print(f"  ⚠️  スキップ: {len(skipped)}件")
        for f in skipped:
            print(f"      - {f}")

    if added:
        print("\n💡 次のステップ:")
        print(
            "   SKIP_AUTO_REPAIR=true python3 agents/git_agent/auto_commit_push_v11_force_push.py"
        )

    print("=" * 60)

    return 0 if not skipped else 1


if __name__ == "__main__":
    sys.exit(main())
