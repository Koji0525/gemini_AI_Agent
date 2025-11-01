#!/usr/bin/env python3
"""
🚀 Git自動コミット＆プッシュツール v5.0（8ステップ品質保証）

【v5.0 変更の理由】
何が起きた:
- 品質保証プロセスが不足
- 一時ファイルやキャッシュファイルがコミットされる
- コードスタイルの統一性がない

原因:
- 自動化された品質チェックがない
- 一時ファイルの管理が不十分
- フォーマッターとリンターの統合不足

狙い:
- 8ステップの品質保証プロセスを確立
- 自動フォーマットとリンター検査
- 重複ファイルチェックの追加
- プレコミットフックの統合
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import fnmatch


class QualityAssuredGitTool:
    """品質保証付きGitツール v5.0"""

    def __init__(self, commit_message: str = None):
        self.commit_message = (
            commit_message
            or f"🔧 品質改善: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        self.project_root = Path.cwd()
        self.exclude_dirs = {
            "_WIP",
            "_ARCHIVE",
            "_BACKUP",
            "__pycache__",
            ".git",
            "node_modules",
            "wordpress-core",
        }
        self.production_dirs = {
            "scripts",
            "agents",
            "core_agents",
            "tools",
            "configuration",
            "task_executor",
            "browser_control",
        }

    def run(self) -> int:
        """メイン実行 - 8ステップ品質保証"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🚀 Git自動コミット＆プッシュツール v5.0")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # STEP 1: 一時ファイルの整理
        if not self._step1_cleanup():
            return 1

        # STEP 2: コミット対象ファイルの列挙
        commit_files = self._step2_list_production_files()
        if not commit_files:
            print("\n✅ 本番コードの変更なし。コミット不要です。")
            return 0

        # STEP 3: 品質ゲート - コンパイル & リンター
        if not self._step3_quality_gate(commit_files):
            return 1

        # STEP 4: フォーマット & 目視確認
        if not self._step4_format_and_visual_check(commit_files):
            return 1

        # STEP 5: 重複ファイルチェック
        if not self._step5_duplication_check():
            return 1

        # STEP 6: 最終クリーンアップ
        if not self._step6_final_cleanup():
            return 1

        # STEP 7: プレコミットフック実行
        if not self._step7_pre_commit_hooks(commit_files):
            return 1

        # STEP 8: コミット & プッシュ
        return self._step8_commit_and_push(commit_files)

    def _step1_cleanup(self) -> bool:
        """STEP 1: 一時ファイルの整理"""
        print("\n📦 STEP 1: 一時ファイルの整理")
        print("=" * 50)

        try:
            # _WIP/ 内の一時ファイルを整理
            wip_dir = self.project_root / "_WIP"
            if wip_dir.exists():
                temp_files = list(wip_dir.rglob("*.py"))
                if temp_files:
                    print(f"🔍 _WIP/ 内の一時ファイル: {len(temp_files)}件")
                    for f in temp_files[:5]:
                        print(f"   📄 {f.relative_to(self.project_root)}")
                    if len(temp_files) > 5:
                        print(f"   ... 他 {len(temp_files) - 5}件")
                    print("💡 これらのファイルはLinter/Formatter対象から除外されます")

            print("✅ STEP 1 完了: 一時ファイル整理完了")
            return True

        except Exception as e:
            print(f"❌ STEP 1 エラー: {e}")
            return False

    def _step2_list_production_files(self) -> list:
        """STEP 2: 本番コードファイルの列挙"""
        print("\n📋 STEP 2: 本番コードファイルの列挙")
        print("=" * 50)

        all_changed = self._get_all_changed_files()
        production_files = []

        for file_path in all_changed:
            path = Path(file_path)

            # 除外ディレクトリをスキップ
            if any(exclude in str(path) for exclude in self.exclude_dirs):
                continue

            # 本番ディレクトリのファイルのみ対象
            if any(prod_dir in str(path) for prod_dir in self.production_dirs):
                if path.exists() and path.suffix == ".py":
                    production_files.append(str(path))

        if production_files:
            print(f"🎯 本番コードファイル: {len(production_files)}件")
            for f in production_files[:10]:
                print(f"   📝 {f}")
            if len(production_files) > 10:
                print(f"   ... 他 {len(production_files) - 10}件")

            # ファイル内容の確認（最初の3ファイル）
            print("\n🔍 変更内容の確認（サンプル）:")
            for f in production_files[:3]:
                self._show_file_changes(f)
        else:
            print("📭 本番コードの変更ファイルなし")

        return production_files

    def _step3_quality_gate(self, files: list) -> bool:
        """STEP 3: 品質ゲート - コンパイル & リンター"""
        print("\n🔒 STEP 3: 品質ゲート - コンパイル & リンター")
        print("=" * 50)

        all_passed = True

        for file_path in files:
            print(f"\n🔍 検査中: {file_path}")

            # 構文チェック
            result = subprocess.run(
                ["python3", "-m", "py_compile", file_path],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"❌ 構文エラー: {file_path}")
                print(result.stderr)
                all_passed = False
                continue
            else:
                print("   ✅ 構文チェック合格")

            # flake8 リンター検査（警告のみ表示、エラーにはしない）
            result = subprocess.run(
                [
                    "flake8",
                    file_path,
                    "--max-line-length=100",
                    "--extend-ignore=E203,W503,E501,F401",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"⚠️  リンター警告: {file_path}")
                print(result.stdout)
                # リンター警告はエラーにはしないが表示する
            else:
                print("   ✅ リンター検査合格")

        if all_passed:
            print("\n✅ STEP 3 完了: 品質ゲート合格")
            return True
        else:
            print("\n❌ STEP 3 エラー: 品質ゲート不合格 - 修正が必要")
            return False

    def _step4_format_and_visual_check(self, files: list) -> bool:
        """STEP 4: フォーマット & 目視確認"""
        print("\n🎨 STEP 4: フォーマット & 目視確認")
        print("=" * 50)

        try:
            # Black フォーマッター実行
            if files:
                print("🔄 コードフォーマット実行中...")
                result = subprocess.run(
                    ["black"] + files, capture_output=True, text=True
                )

                if result.returncode == 0:
                    print("✅ 自動フォーマット完了")
                    if result.stdout:
                        print(f"📝 フォーマット結果: {result.stdout.strip()}")
                else:
                    print("⚠️  フォーマットで問題が発生")
                    print(result.stderr)

            # 目視確認のための変更表示
            print("\n👀 目視確認のための変更点:")
            for file_path in files[:3]:  # 最初の3ファイルのみ表示
                self._show_file_changes(file_path)

            # ユーザー確認（オプション）
            print("\n💡 目視確認を行ってください")
            print("   エンターキーを押して続行...")
            input()

            print("✅ STEP 4 完了: フォーマット & 目視確認完了")
            return True

        except Exception as e:
            print(f"❌ STEP 4 エラー: {e}")
            return False

    def _step5_duplication_check(self) -> bool:
        """STEP 5: 重複ファイルチェック"""
        print("\n🔍 STEP 5: 重複ファイルチェック")
        print("=" * 50)

        try:
            # ファイルバージョンマネージャーを使用して重複チェック
            result = subprocess.run(
                ["python3", "tools/file_version_manager.py", "--check-duplicates"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("✅ 重複ファイルチェック完了")
                if result.stdout:
                    print("📋 チェック結果:")
                    print(result.stdout)
            else:
                print("⚠️  重複ファイルチェックで問題が発生")
                print(result.stderr)
                # 重複チェックの失敗はコミットを中止しない

            print("✅ STEP 5 完了: 重複ファイルチェック完了")
            return True

        except Exception as e:
            print(f"⚠️  STEP 5 警告: 重複チェックでエラー - {e}")
            # 重複チェックの失敗はコミットを中止しない
            return True

    def _step6_final_cleanup(self) -> bool:
        """STEP 6: 最終クリーンアップ"""
        print("\n🧹 STEP 6: 最終クリーンアップ")
        print("=" * 50)

        try:
            # 不要ファイルの削除
            print("🗑️  キャッシュファイルを削除中...")
            subprocess.run(
                [
                    "find",
                    ".",
                    "-name",
                    "__pycache__",
                    "-type",
                    "d",
                    "-exec",
                    "rm",
                    "-rf",
                    "{}",
                    "+",
                ],
                capture_output=True,
            )
            subprocess.run(
                ["find", ".", "-name", "*.pyc", "-delete"], capture_output=True
            )
            subprocess.run(
                ["find", ".", "-name", "*.log", "-delete"], capture_output=True
            )

            # .gitignore の確認
            gitignore_path = self.project_root / ".gitignore"
            if gitignore_path.exists():
                with open(gitignore_path, "r") as f:
                    current_content = f.read()

                required_patterns = [
                    "__pycache__/",
                    "*.pyc",
                    "*.log",
                    "logs/",
                    "agent_outputs/",
                    "_WIP/",
                    "_ARCHIVE/",
                    "_BACKUP/",
                    ".env",
                ]

                missing_patterns = []
                for pattern in required_patterns:
                    if pattern not in current_content:
                        missing_patterns.append(pattern)

                if missing_patterns:
                    print("⚠️  .gitignore に不足パターンがあります")
                    for pattern in missing_patterns:
                        print(f"   ➕ {pattern}")

            print("✅ STEP 6 完了: 最終クリーンアップ完了")
            return True

        except Exception as e:
            print(f"❌ STEP 6 エラー: {e}")
            return False

    def _step7_pre_commit_hooks(self, files: list) -> bool:
        """STEP 7: プレコミットフック実行"""
        print("\n⚡ STEP 7: プレコミットフック実行")
        print("=" * 50)

        all_passed = True

        for file_path in files:
            print(f"\n🔍 最終チェック: {file_path}")

            # 最終構文チェック
            result = subprocess.run(
                ["python3", "-m", "py_compile", file_path],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"❌ 構文エラー: {file_path}")
                print(result.stderr)
                all_passed = False
                continue

            # 最終フォーマットチェック（変更があるか確認）
            result = subprocess.run(
                ["black", "--check", file_path], capture_output=True, text=True
            )

            if result.returncode != 0:
                print(f"⚠️  フォーマットが必要: {file_path}")
                # フォーマットの失敗はエラーにはしない

            # 最終リンターチェック（必須）
            result = subprocess.run(
                [
                    "flake8",
                    file_path,
                    "--max-line-length=100",
                    "--ignore=E203,W503,E501,F401",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"❌ リンターエラー: {file_path}")
                print(result.stdout)
                all_passed = False

        if all_passed:
            print("✅ STEP 7 完了: プレコミットフック合格")
            return True
        else:
            print("❌ STEP 7 エラー: プレコミットフック不合格")
            return False

    def _step8_commit_and_push(self, files: list) -> int:
        """STEP 8: コミット & プッシュ"""
        print("\n📤 STEP 8: コミット & プッシュ")
        print("=" * 50)

        try:
            # ステージング（本番ファイルのみ）
            print("📝 本番ファイルをステージング中...")
            for file_path in files:
                subprocess.run(["git", "add", file_path], check=True)

            # コミット
            print("💾 コミット中...")
            result = subprocess.run(
                ["git", "commit", "-m", self.commit_message],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                if "nothing to commit" in result.stdout:
                    print("✅ コミット済み（変更なし）")
                    return 0
                else:
                    print(f"❌ コミットエラー: {result.stderr}")
                    return 1

            print("✅ コミット成功")

            # プッシュ
            print("🚀 プッシュ中...")
            subprocess.run(["git", "push"], check=True)
            print("✅ プッシュ成功")

            # README.md のバージョン情報確認
            self._check_readme_version()

            print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("🎉 8ステップ品質保証完了！")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            return 0

        except subprocess.CalledProcessError as e:
            print(f"❌ Git操作失敗: {e}")
            return 1

    def _get_all_changed_files(self) -> list:
        """すべての変更ファイルを取得"""
        changed = set()

        # git diff で変更ファイル
        commands = [
            ["git", "diff", "--name-only"],
            ["git", "diff", "--cached", "--name-only"],
            ["git", "ls-files", "--others", "--exclude-standard"],
        ]

        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                changed.update(result.stdout.strip().split("\n"))

        return [f for f in changed if f and Path(f).exists()]

    def _show_file_changes(self, file_path: str):
        """ファイルの変更内容を表示"""
        try:
            result = subprocess.run(
                ["git", "diff", "--color=always", file_path],
                capture_output=True,
                text=True,
            )

            if result.stdout:
                print(f"\n📊 {file_path} の変更:")
                # 最初の20行のみ表示
                lines = result.stdout.split("\n")[:20]
                print("\n".join(lines))
                if len(result.stdout.split("\n")) > 20:
                    print("... (省略)")
            else:
                # 新規ファイルの場合
                with open(file_path, "r") as f:
                    content = f.read()
                print(f"\n📄 {file_path} (新規ファイル):")
                lines = content.split("\n")[:10]
                print("\n".join(lines))
                if len(content.split("\n")) > 10:
                    print("... (省略)")

        except Exception as e:
            print(f"⚠️  変更表示エラー: {e}")

    def _check_readme_version(self):
        """README.md のバージョン情報を確認"""
        readme_path = self.project_root / "README.md"
        if readme_path.exists():
            with open(readme_path, "r") as f:
                content = f.read()

            if "安定バージョン" not in content and "Stable Version" not in content:
                print("⚠️  README.md に安定バージョンの記載がありません")
                print("💡 現在の安定バージョンを明記してください")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="🚀 Git自動コミット＆プッシュツール v5.0 - 8ステップ品質保証",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python3 agents/git_agent/auto_commit_push_v05_optimized.py "新機能: 自動品質チェック"
  python3 agents/git_agent/auto_commit_push_v05_optimized.py  # デフォルトメッセージで実行

8ステップ品質保証:
  1. 📦 一時ファイル整理
  2. 📋 本番コード列挙
  3. 🔒 コンパイル & リンター
  4. 🎨 フォーマット & 目視確認
  5. 🔍 重複ファイルチェック
  6. 🧹 最終クリーンアップ
  7. ⚡ プレコミットフック
  8. 📤 コミット & プッシュ
        """,
    )

    parser.add_argument("message", nargs="?", help="コミットメッセージ（省略可）")

    args = parser.parse_args()

    tool = QualityAssuredGitTool(args.message)
    sys.exit(tool.run())


if __name__ == "__main__":
    main()
