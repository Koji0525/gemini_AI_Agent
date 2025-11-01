#!/usr/bin/env python3
"""
🎯 統合開発コマンド - dev

【目的】
既存の優れたツールを統合し、開発効率を10倍向上させる

【統合ツール】
1. File Version Manager - ファイル作成のゲートキーパー
2. Auto Commit Push Agent - Git操作の自動化
3. Enterprise Path Resolver - ファイル発見の専門家
4. プロジェクト構造可視化 - 全体像の把握

【変更の理由】
何が起きた:
- pm_agent.py, task_executor.py の場所が不明
- 既存ツールは優秀だが、統合されていない

原因:
- ツールがバラバラで、使い方を覚える必要がある
- プロジェクト全体を俯瞰する手段がない

狙い:
- 統一インターフェースで全ツールを使えるように
- 開発者が迷わず、瞬時に必要な情報を取得

【使用例】
    # ファイル検索
    python3 tools/dev.py find pm_agent.py
    python3 tools/dev.py find task_executor

    # プロジェクト構造表示
    python3 tools/dev.py structure
    python3 tools/dev.py structure --detail

    # ファイル作成
    python3 tools/dev.py create goal_processor v02

    # 重複チェック
    python3 tools/dev.py duplicates

    # Git操作
    python3 tools/dev.py commit "Phase 2 Day 3 完了"

    # 統計情報
    python3 tools/dev.py stats
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
from pathlib import Path
from typing import List, Dict
import subprocess
import json


class DevCommand:
    """統合開発コマンド"""

    def __init__(self):
        self.root = Path(".").resolve()
        self.ignore_dirs = {
            "__pycache__",
            ".git",
            "node_modules",
            ".venv",
            "venv",
            ".pytest_cache",
            ".mypy_cache",
            "dist",
            "build",
            "*.egg-info",
            "_BACKUP",
            "_ARCHIVE",
        }

    def find(self, pattern: str, exact: bool = False) -> List[Path]:
        """
        ファイル検索（Enterprise Path Resolver の簡易版）

        Args:
            pattern: 検索パターン
            exact: 完全一致モード
        """
        print(f"\n🔍 ファイル検索: '{pattern}'")
        print(f"   検索モード: {'完全一致' if exact else '部分一致'}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        results = []

        # .py ファイルを検索
        for path in self.root.rglob("*.py"):
            # 無視ディレクトリをスキップ
            if any(ignore in str(path) for ignore in self.ignore_dirs):
                continue

            if exact:
                if path.name == pattern or path.name == f"{pattern}.py":
                    results.append(path)
            else:
                if pattern.lower() in path.name.lower():
                    results.append(path)

        if results:
            print(f"\n✅ {len(results)} 件見つかりました:\n")

            # バージョン付きファイルとベースファイルを分類
            base_files = []
            versioned_files = []

            for path in results:
                rel_path = path.relative_to(self.root)
                if "_v" in path.name or "v0" in path.name:
                    versioned_files.append(rel_path)
                else:
                    base_files.append(rel_path)

            # ベースファイルを優先表示
            if base_files:
                print("📌 本番ファイル:")
                for path in sorted(base_files):
                    abs_path = self.root / path
                    size = abs_path.stat().st_size
                    lines = self._count_lines(abs_path)
                    print(f"   • {path}")
                    print(f"     サイズ: {size:,} bytes | 行数: {lines:,}")

            if versioned_files:
                print("\n📦 バージョン付きファイル:")
                for path in sorted(versioned_files, reverse=True):
                    abs_path = self.root / path
                    size = abs_path.stat().st_size
                    lines = self._count_lines(abs_path)
                    print(f"   • {path}")
                    print(f"     サイズ: {size:,} bytes | 行数: {lines:,}")
        else:
            print(f"\n❌ ファイルが見つかりませんでした")
            self._suggest_similar(pattern)

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        return results

    def structure(self, detail: bool = False):
        """プロジェクト構造を表示"""
        print("\n📂 プロジェクト構造")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 主要ディレクトリの統計
        dirs_to_check = [
            "scripts",
            "core_agents",
            "agents",
            "tools",
            "configuration",
            "task_executor",
            "browser_control",
        ]

        print("\n📊 主要ディレクトリ:\n")

        for dir_name in dirs_to_check:
            dir_path = self.root / dir_name
            if dir_path.exists():
                py_files = list(dir_path.rglob("*.py"))
                py_files = [f for f in py_files if not any(ignore in str(f) for ignore in self.ignore_dirs)]

                total_lines = sum(self._count_lines(f) for f in py_files)

                print(f"   📁 {dir_name}/")
                print(f"      ファイル数: {len(py_files)}")
                print(f"      総行数: {total_lines:,}")

                if detail and py_files:
                    print(f"      主要ファイル:")
                    for f in sorted(py_files)[:5]:
                        rel = f.relative_to(dir_path)
                        lines = self._count_lines(f)
                        print(f"        - {rel} ({lines:,} 行)")
                print()

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def create(self, base: str, feature: str, target_dir: str = None):
        """
        新しいファイルを作成（File Version Manager を使用）

        Args:
            base: ベースファイル名
            feature: 機能名
            target_dir: 配置先ディレクトリ
        """
        print(f"\n🔧 ファイル作成: {base}_{feature}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        cmd = ["python3", "tools/file_version_manager.py", "--quick", base, feature]
        if target_dir:
            cmd.extend(["--target-dir", target_dir])

        result = subprocess.run(cmd, capture_output=False)

        if result.returncode == 0:
            print("\n✅ ファイル作成完了")
        else:
            print("\n❌ ファイル作成失敗")

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def duplicates(self):
        """重複ファイルチェック（File Version Manager を使用）"""
        print("\n🔍 重複ファイルチェック")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        subprocess.run(["python3", "tools/file_version_manager.py", "--check-duplicates"])

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def commit(self, message: str):
        """Git コミット・プッシュ（Auto Commit Push Agent を使用）"""
        print(f"\n📤 Git コミット・プッシュ: '{message}'")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        subprocess.run(["python3", "agents/git_agent/auto_commit_push_v03_improve.py", message])

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def stats(self):
        """プロジェクト統計"""
        print("\n📊 プロジェクト統計")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 全Pythonファイルを収集
        all_py_files = []
        for path in self.root.rglob("*.py"):
            if not any(ignore in str(path) for ignore in self.ignore_dirs):
                all_py_files.append(path)

        total_lines = sum(self._count_lines(f) for f in all_py_files)
        total_size = sum(f.stat().st_size for f in all_py_files)

        print(f"\n   総ファイル数: {len(all_py_files):,}")
        print(f"   総行数: {total_lines:,}")
        print(f"   総サイズ: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")

        # カテゴリ別統計
        categories = {
            "エージェント": ["agents/", "core_agents/"],
            "スクリプト": ["scripts/"],
            "ツール": ["tools/"],
            "タスク実行": ["task_executor/"],
            "設定": ["configuration/"],
            "ブラウザ制御": ["browser_control/"],
        }

        print("\n📂 カテゴリ別統計:\n")
        for category, paths in categories.items():
            cat_files = [f for f in all_py_files if any(p in str(f) for p in paths)]
            if cat_files:
                cat_lines = sum(self._count_lines(f) for f in cat_files)
                print(f"   {category}:")
                print(f"      ファイル数: {len(cat_files)}")
                print(f"      行数: {cat_lines:,}")

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def _count_lines(self, path: Path) -> int:
        """ファイルの行数をカウント"""
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return len(f.readlines())
        except:
            return 0

    def _suggest_similar(self, pattern: str):
        """類似ファイルを提案"""
        print("\n💡 類似ファイルを検索中...")

        # 部分一致で再検索
        similar = []
        for path in self.root.rglob("*.py"):
            if any(ignore in str(path) for ignore in self.ignore_dirs):
                continue

            # パターンの一部でも含まれていればヒット
            if any(part in path.name.lower() for part in pattern.lower().split("_")):
                similar.append(path)

        if similar:
            print(f"\n   類似ファイル:\n")
            for path in sorted(similar)[:10]:
                rel_path = path.relative_to(self.root)
                print(f"      • {rel_path}")
        else:
            print("   類似ファイルも見つかりませんでした")


def main():
    parser = argparse.ArgumentParser(
        description="🎯 統合開発コマンド - すべてのツールを統合",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # ファイル検索
  python3 tools/dev.py find pm_agent
  python3 tools/dev.py find task_executor --exact
  
  # プロジェクト構造
  python3 tools/dev.py structure
  python3 tools/dev.py structure --detail
  
  # ファイル作成
  python3 tools/dev.py create goal_processor v02
  python3 tools/dev.py create new_agent feature --target-dir scripts
  
  # 重複チェック
  python3 tools/dev.py duplicates
  
  # Git操作
  python3 tools/dev.py commit "Phase 2 完了"
  
  # 統計情報
  python3 tools/dev.py stats
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="コマンド")

    # find コマンド
    find_parser = subparsers.add_parser("find", help="ファイル検索")
    find_parser.add_argument("pattern", help="検索パターン")
    find_parser.add_argument("--exact", action="store_true", help="完全一致モード")

    # structure コマンド
    structure_parser = subparsers.add_parser("structure", help="プロジェクト構造表示")
    structure_parser.add_argument("--detail", action="store_true", help="詳細表示")

    # create コマンド
    create_parser = subparsers.add_parser("create", help="ファイル作成")
    create_parser.add_argument("base", help="ベースファイル名")
    create_parser.add_argument("feature", help="機能名")
    create_parser.add_argument("--target-dir", help="配置先ディレクトリ")

    # duplicates コマンド
    subparsers.add_parser("duplicates", help="重複ファイルチェック")

    # commit コマンド
    commit_parser = subparsers.add_parser("commit", help="Git コミット・プッシュ")
    commit_parser.add_argument("message", help="コミットメッセージ")

    # stats コマンド
    subparsers.add_parser("stats", help="プロジェクト統計")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    dev = DevCommand()

    try:
        if args.command == "find":
            dev.find(args.pattern, args.exact)

        elif args.command == "structure":
            dev.structure(args.detail)

        elif args.command == "create":
            dev.create(args.base, args.feature, args.target_dir)

        elif args.command == "duplicates":
            dev.duplicates()

        elif args.command == "commit":
            dev.commit(args.message)

        elif args.command == "stats":
            dev.stats()

        return 0

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
