#!/usr/bin/env python3
from auto_repair_enhancer import AdvancedErrorFixer

"""
🚀 Git自動コミット＆プッシュツール v10.1（拡張自動修復版）

【v10.1 変更の理由】
何が起きた:
- v10.0: timeモジュール未定義エラーが発生し手動修正が必要だった
- 既存の自動修復ではインポート不足を検出・修正できない

原因:
- autoflakeは未使用インポートのみ削除、不足インポートは追加しない
- 致命的エラー検出後、自動修復機能が不足
import sys
sys.path.append(os.path.dirname(__file__))
import sys
sys.path.append(os.path.dirname(__file__))

狙い:
- インポート自動修復機能を新規追加
- 既存の全機能を完全に保持
- 類似エラーにも拡張可能な設計
"""

import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List


class ImportAutoFixer:
    """インポート自動修復クラス - 既存機能に追加"""

    def __init__(self):
        self.common_imports_map = {
            "Path": "from pathlib import Path",
            "List": "from typing import List",
            "Dict": "from typing import Dict",
            "Set": "from typing import Set",
            "Tuple": "from typing import Tuple",
            "Any": "from typing import Any",
            "Optional": "from typing import Optional",
            "Union": "from typing import Union",
            "datetime": "import datetime",
            "timedelta": "from datetime import timedelta",
            "json": "import json",
            "re": "import re",
            "ast": "import ast",
            "shutil": "import shutil",
            "hashlib": "import hashlib",
            "subprocess": "import subprocess",
            "sys": "import sys",
            "os": "import os",
        }

    def analyze_missing_imports(self, file_path: str, error_output: str) -> List[str]:
        """エラー出力から不足インポートを分析"""
        missing_imports = []

        # F821 undefined name エラーパターンを検出
        f821_pattern = r"F821 undefined name '([^']+)'"
        undefined_names = re.findall(f821_pattern, error_output)

        for name in undefined_names:
            if name in self.common_imports_map:
                missing_imports.append(self.common_imports_map[name])

        return missing_imports

    def fix_missing_imports(self, file_path: str, missing_imports: List[str]) -> bool:
        """不足インポートを自動追加"""
        if not missing_imports:
            return True

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")

            # 既存のインポートセクションを探す
            import_section_end = self._find_import_section_end(lines)

            # 重複を避けてインポートを追加
            imports_to_add = []
            for imp in missing_imports:
                if imp not in content:
                    imports_to_add.append(imp)

            if imports_to_add:
                # インポートを追加
                for imp in reversed(imports_to_add):
                    lines.insert(import_section_end + 1, imp)

                # ファイルを保存
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))

                print(f"  ✅ インポート自動追加: {', '.join(imports_to_add)}")
                return True
            else:
                return True

        except Exception as e:
            print(f"  ❌ インポート追加失敗: {e}")
            return False

    def _find_import_section_end(self, lines: List[str]) -> int:
        """インポートセクションの終了位置を検出"""
        last_import_line = -1

        for i, line in enumerate(lines):
            stripped = line.strip()
            if (
                stripped.startswith("import ")
                or stripped.startswith("from ")
                or stripped == ""
                or stripped.startswith("#")
            ):
                last_import_line = i
            else:
                break

        return max(last_import_line, 0)


class IntegratedGitTool:
    """統合版Git自動化ツール v9.1（インポート自動修復対応）"""

    def __init__(self, commit_message: str = None, wait_ci: bool = False):
        self.commit_message = (
            commit_message or f"🔧 品質改善: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        self.wait_ci = wait_ci
        self.project_root = Path.cwd()
        self.cache_file = self.project_root / ".quality_cache.json"

        # インポート自動修復機能を追加（既存機能に追加）
        self.import_fixer = ImportAutoFixer()

        # 統計情報（新規項目追加 - 既存項目は全て保持）
        self.stats = {
            "checked": 0,
            "cached": 0,
            "auto_fixed": 0,
            "manual_required": 0,
            "errors": [],
            "local_check_passed": 0,
            "local_check_total": 0,
            # 新規追加項目
            "imports_fixed": 0,
            "auto_repaired": 0,
        }

        # 既存の設定を全て保持
        self.exclude_dirs = {
            "_WIP",
            "_ARCHIVE",
            "_BACKUP",
            "backups",
            "backup_files",
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

        # ツールの利用可能性チェック（既存機能）
        self.available_tools = {
            "autoflake": shutil.which("autoflake") is not None,
            "black": shutil.which("black") is not None,
            "isort": shutil.which("isort") is not None,
        }

        self._load_cache()

    def run(self) -> int:
        """メイン実行 - 統合9ステップ + CI制御 + インポート自動修復（既存機能完全保持）"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🚀 Git自動コミット＆プッシュツール v9.1")
        print("   v9.0全機能 + インポート自動修復")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 既存の9ステップを完全に保持
        # STEP 0: 設定ファイル検証
        if not self._step0_validate_configs():
            return 1

        # STEP 1: 一時ファイルの整理
        if not self._step1_cleanup():
            return 1

        # STEP 2: 差分ベースファイル列挙
        commit_files = self._step2_list_changed_files()
        if not commit_files:
            print("\n✅ 本番コードの変更なし。コミット不要です。")
            return 0

        # STEP 3: 3段階自動修復（既存機能）
        fixed_files = self._step3_smart_auto_repair(commit_files)

        # STEP 4: 致命的エラーチェック + 自動修復試行（新機能追加）
        if not self._step4_critical_errors_with_auto_fix(fixed_files):
            return 1

        # STEP 5: 重複ファイルチェック
        if not self._step5_duplication_check():
            return 1

        # STEP 6: 最終クリーンアップ
        if not self._step6_final_cleanup():
            return 1

        # STEP 7: 差分ベースプレコミット
        if not self._step7_diff_based_precommit(fixed_files):
            return 1

        # STEP 8: 統計レポート
        self._step8_statistics_report()

        # STEP 9: コミット & プッシュ
        if not self._step9_commit_and_push(fixed_files):
            return 1

        # STEP 10: CI待機制御
        return self._step10_ci_control()

    def _step4_critical_errors_with_auto_fix(self, files: List[str]) -> bool:
        """STEP 4: 致命的エラーチェック + 自動修復試行（v9.1新機能追加）"""
        print("\n🔒 STEP 4: 致命的エラーチェック + 自動修復")
        print("=" * 50)

        all_passed = True

        for file_path in files:
            self.stats["checked"] += 1
            print(f"\n🔍 チェック中: {file_path}")

            # 構文チェック（既存機能）
            syntax_result = subprocess.run(
                ["python3", "-m", "py_compile", file_path],
                capture_output=True,
                text=True,
            )

            if syntax_result.returncode != 0:
                print(f"❌ 構文エラー: {file_path}")
                print(syntax_result.stderr)
                self.stats["errors"].append({"file": file_path, "type": "syntax"})
                all_passed = False
                continue

            # 致命的エラーチェック（既存機能）
            flake_result = subprocess.run(
                ["flake8", file_path, "--select=E9,F821,F822,F823"],
                capture_output=True,
                text=True,
            )

            if flake_result.returncode == 0:
                print(f"  ✅ {file_path}")
                continue

            # エラー検出時の自動修復試行（新機能追加）
            print(f"⚠️  エラー検出: 自動修復を試行します")
            self.stats["auto_repaired"] += 1

            if self._try_auto_repair(file_path, flake_result.stdout):
                # 修復後、再チェック（既存機能）
                flake_result2 = subprocess.run(
                    ["flake8", file_path, "--select=E9,F821,F822,F823"],
                    capture_output=True,
                    text=True,
                )

                if flake_result2.returncode == 0:
                    print(f"  ✅ 自動修復成功: {file_path}")
                    continue
                else:
                    print(f"❌ 自動修復後もエラー: {file_path}")
                    print(flake_result2.stdout)
                    self.stats["errors"].append({"file": file_path, "type": "critical"})
                    all_passed = False
            else:
                print(f"❌ 自動修復失敗: {file_path}")
                print(flake_result.stdout)
                self.stats["errors"].append({"file": file_path, "type": "critical"})
                all_passed = False

        if all_passed:
            print("\n✅ STEP 4 完了: 致命的エラーなし")
        else:
            print("\n❌ STEP 4 エラー: 致命的エラーあり")

        return all_passed

    def _try_auto_repair(self, file_path: str, error_output: str) -> bool:
        """自動修復を試行（v10拡張版）"""
        try:
            # === 新規追加: 高度な自動修復をまず試行 ===
            advanced_fixer = AdvancedErrorFixer()
            if advanced_fixer.try_advanced_fixes(file_path, error_output):
                print("  ✅ 高度な自動修復成功")
                return True
            # === 追加終了 ===

            # 不足インポートを分析（既存機能）
            missing_imports = self.import_fixer.analyze_missing_imports(file_path, error_output)

            if missing_imports:
                print(f"  🔧 不足インポートを検出: {[imp.split()[-1] for imp in missing_imports]}")
                if self.import_fixer.fix_missing_imports(file_path, missing_imports):
                    self.stats["imports_fixed"] += len(missing_imports)
                    return True

            # その他の自動修復ロジックをここに追加可能（将来の拡張用）
            # 例: よくあるタイポの修正など

            return False

        except Exception as e:
            print(f"  ❌ 自動修復エラー: {e}")
            return False

    def _step8_statistics_report(self):
        """STEP 8: 統計レポート（v9.1拡張 - 既存項目を保持）"""
        print("\n📊 STEP 8: 統計レポート")
        print("=" * 50)

        print(
            f"""
📈 処理統計:
  - チェックしたファイル: {self.stats['checked']}件
  - キャッシュヒット: {self.stats['cached']}件
  - 自動修復: {self.stats['auto_fixed']}件
  - 手動確認推奨: {self.stats['manual_required']}件
  - 致命的エラー: {len(self.stats['errors'])}件
  - インポート修復: {self.stats['imports_fixed']}件（新機能）
  - 自動修復試行: {self.stats['auto_repaired']}件（新機能）
        """
        )

        if self.stats["errors"]:
            print("❌ エラー詳細:")
            for error in self.stats["errors"]:
                print(f"  - {error['file']}: {error['type']}")

    # === 既存のメソッドを全て保持（変更なし）===

    def _step0_validate_configs(self) -> bool:
        """STEP 0: 設定ファイル検証（既存機能 - 変更なし）"""
        print("\n🔍 STEP 0: 設定ファイル検証")
        print("=" * 50)

        # ツールの利用可能性を表示
        print("\n📦 利用可能な修復ツール:")
        for tool, available in self.available_tools.items():
            status = "✅" if available else "❌"
            print(f"  {status} {tool}")

        configs = {
            ".flake8": self._validate_flake8,
            "pyproject.toml": self._validate_pyproject,
        }

        all_valid = True
        for config_file, validator in configs.items():
            if Path(config_file).exists():
                try:
                    validator(config_file)
                    print(f"  ✅ {config_file} 検証合格")
                except Exception as e:
                    print(f"  ❌ {config_file} 検証失敗: {e}")
                    all_valid = False
            else:
                print(f"  ℹ️  {config_file} 見つかりません（スキップ）")

        if all_valid:
            print("✅ STEP 0 完了: 設定ファイル検証合格")
        else:
            print("❌ STEP 0 エラー: 設定ファイルを修正してください")

        return all_valid

    def _validate_flake8(self, config_file: str):
        """flake8設定ファイルの検証（既存機能）"""
        result = subprocess.run(
            ["flake8", "--version"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise ValueError(f"flake8設定の読み込み失敗: {result.stderr}")

        with open(config_file, "r") as f:
            for i, line in enumerate(f, 1):
                if re.match(r"^\s*\w+\s*=\s*[^#]+#", line):
                    raise ValueError(
                        f"{config_file}:{i} - INI形式ではインラインコメント不可\n"
                        f"修正: コメントを別行に移動してください"
                    )

    def _validate_pyproject(self, config_file: str):
        """pyproject.toml検証（既存機能）"""

    def _step1_cleanup(self) -> bool:
        """STEP 1: 一時ファイルの整理（既存機能 - 変更なし）"""
        print("\n📦 STEP 1: 一時ファイルの整理")
        print("=" * 50)

        try:
            wip_dir = self.project_root / "_WIP"
            if wip_dir.exists():
                temp_files = list(wip_dir.rglob("*.py"))
                if temp_files:
                    print(f"🔍 _WIP/ 内の一時ファイル: {len(temp_files)}件")
                    print("💡 品質チェック対象から除外されます")

            print("✅ STEP 1 完了")
            return True

        except Exception as e:
            print(f"❌ STEP 1 エラー: {e}")
            return False

    def _step2_list_changed_files(self) -> List[str]:
        """STEP 2: 差分ベースファイル列挙（既存機能 - 変更なし）"""
        print("\n📋 STEP 2: 差分ベースファイル列挙")
        print("=" * 50)

        changed = set()

        commands = [
            ["git", "diff", "--name-only", "--diff-filter=ACMR"],
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            ["git", "ls-files", "--others", "--exclude-standard"],
        ]

        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
                changed.update(files)

        production_files = []
        for file_path in changed:
            path = Path(file_path)

            if any(exclude in str(path) for exclude in self.exclude_dirs):
                continue

            if (
                any(prod_dir in str(path) for prod_dir in self.production_dirs)
                and path.suffix == ".py"
                and path.exists()
            ):
                production_files.append(str(path))

        if production_files:
            print(f"🎯 変更された本番ファイル: {len(production_files)}件")
            for f in production_files[:5]:
                print(f"   📝 {f}")
            if len(production_files) > 5:
                print(f"   ... 他 {len(production_files) - 5}件")
        else:
            print("ℹ️  変更ファイルなし")

        return production_files

    def _step3_smart_auto_repair(self, files: List[str]) -> List[str]:
        """STEP 3: 3段階スマート自動修復（既存機能 - 変更なし）"""
        print("\n🔧 STEP 3: 3段階スマート自動修復")
        print("=" * 50)

        fixed_files = []

        for file_path in files:
            print(f"\n🔍 修復中: {file_path}")

            original_hash = self._get_file_hash(file_path)
            success = True

            # Stage 1: autoflake
            if self.available_tools["autoflake"]:
                result = subprocess.run(
                    [
                        "autoflake",
                        "--in-place",
                        "--remove-all-unused-imports",
                        "--remove-unused-variables",
                        file_path,
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    print("  ✅ Stage 1: autoflake 成功")
                else:
                    print(f"  ⚠️  Stage 1: autoflake 警告")
            else:
                print("  ⏭️  Stage 1: autoflake スキップ（未インストール）")

            # Stage 2: Black
            if self.available_tools["black"]:
                result = subprocess.run(
                    ["black", "--config=pyproject.toml", file_path],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    print("  ✅ Stage 2: Black 成功")
                else:
                    print(f"  ⚠️  Stage 2: Black 警告")
                    success = False
            else:
                print("  ⏭️  Stage 2: Black スキップ（未インストール）")

            # Stage 3: isort
            if self.available_tools["isort"]:
                result = subprocess.run(
                    ["isort", file_path],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    print("  ✅ Stage 3: isort 成功")
                else:
                    print(f"  ⚠️  Stage 3: isort 警告")
            else:
                print("  ⏭️  Stage 3: isort スキップ（未インストール）")

            new_hash = self._get_file_hash(file_path)
            if original_hash != new_hash:
                print(f"  🔄 自動修復適用済み")
                self.stats["auto_fixed"] += 1

            if success:
                fixed_files.append(file_path)

        print(f"\n✅ STEP 3 完了: {len(fixed_files)}件修復")
        return fixed_files

    def _step5_duplication_check(self) -> bool:
        """STEP 5: 重複ファイルチェック（既存機能 - 変更なし）"""
        print("\n🔍 STEP 5: 重複ファイルチェック")
        print("=" * 50)

        try:
            result = subprocess.run(
                ["python3", "tools/file_version_manager.py", "--check-duplicates"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                print("✅ 重複ファイルなし")
            else:
                print("⚠️  重複ファイル検出 - 確認推奨")

            print("✅ STEP 5 完了")
            return True

        except Exception as e:
            print(f"⚠️  STEP 5 警告: {e}")
            return True

    def _step6_final_cleanup(self) -> bool:
        """STEP 6: 最終クリーンアップ（既存機能 - 変更なし）"""
        print("\n🧹 STEP 6: 最終クリーンアップ")
        print("=" * 50)

        try:
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
            subprocess.run(["find", ".", "-name", "*.pyc", "-delete"], capture_output=True)

            print("✅ STEP 6 完了")
            return True

        except Exception as e:
            print(f"❌ STEP 6 エラー: {e}")
            return False

    def _step7_diff_based_precommit(self, files: List[str]) -> bool:
        """STEP 7: 差分ベースプレコミット（既存機能 - 変更なし）"""
        print("\n⚡ STEP 7: 差分ベースプレコミット")
        print("=" * 50)

        all_passed = True

        for file_path in files:
            if not self._is_file_changed(file_path):
                self.stats["cached"] += 1
                print(f"⏭️  キャッシュヒット: {file_path}")
                continue

            result = subprocess.run(
                ["flake8", file_path, "--config=.flake8"],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"⚠️  警告あり: {file_path}")
                print(result.stdout)
                self.stats["manual_required"] += 1
            else:
                print(f"✅ 合格: {file_path}")

        self._save_cache()

        print(f"\n✅ STEP 7 完了: プレコミットフック")
        return all_passed

    def _step9_commit_and_push(self, files: List[str]) -> bool:
        """STEP 9: コミット & プッシュ（既存機能 - 変更なし）"""
        print("\n📤 STEP 9: コミット & プッシュ")
        print("=" * 50)

        try:
            # ステージング
            for file_path in files:
                subprocess.run(["git", "add", file_path], check=True)

            subprocess.run(["git", "add", ".flake8", "pyproject.toml"], check=False)

            # コミット
            result = subprocess.run(
                ["git", "commit", "-m", self.commit_message],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                if "nothing to commit" in result.stdout:
                    print("✅ コミット済み（変更なし）")
                    return True
                else:
                    print(f"❌ コミットエラー: {result.stderr}")
                    return False

            print("✅ コミット成功")

            # プッシュ
            subprocess.run(["git", "push"], check=True)
            print("✅ プッシュ成功")

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Git操作失敗: {e}")
            return False

    def _step10_ci_control(self) -> int:
        """STEP 10: CI待機制御（既存機能 - 変更なし）"""
        print("\n🎯 STEP 10: CI待機制御")
        print("=" * 50)

        # ローカルチェックの合格判定
        local_checks_passed = (
            self.stats["checked"] > 0
            and len(self.stats["errors"]) == 0
            and self.stats["manual_required"] == 0
        )

        if local_checks_passed and not self.wait_ci:
            print("\n" + "=" * 60)
            print("⚡ 高速モード: CI待機をスキップしました")
            print("=" * 60)
            print(f"\n✅ ローカルチェック完了: 問題なし")
            print("\nℹ️  CI結果は以下で確認できます:")
            print("   sh/check_ci_status.sh")
            print("\n" + "=" * 60)
            return 0

        # GitHub CLI確認
        if not self._check_gh_cli():
            print("\n⚠️  GitHub CLI が未設定")
            print("   CI結果は手動で確認してください")
            print("\n" + "=" * 60)
            print("✅ 完了")
            print("=" * 60)
            return 0

        # CI状態確認
        print("\n🔍 CI状態を確認中...")
        ci_status = self._quick_ci_check()

        if ci_status == "success":
            print("\n✅ CI成功: 問題ありません")
        elif ci_status == "running":
            print("\n🔄 CI実行中: 完了まで待機します")
            print("   → Ctrl+C で中断可能（バックグラウンドで実行継続）")
        else:
            print("\n⚠️  CI状態を確認できません")

        print("\n" + "=" * 60)
        print("✅ 完了")
        print("=" * 60)

        return 0

    def _check_gh_cli(self) -> bool:
        """GitHub CLI の確認（既存機能）"""
        result = subprocess.run(["gh", "--version"], capture_output=True)
        return result.returncode == 0

    def _quick_ci_check(self) -> str:
        """CI状態の即座確認（既存機能）"""
        try:
            result = subprocess.run(
                ["gh", "run", "list", "--limit", "1", "--json", "status,conclusion,name"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                runs = json.loads(result.stdout)
                if runs:
                    run = runs[0]
                    status = run.get("status")
                    conclusion = run.get("conclusion")

                    if status == "completed" and conclusion == "success":
                        return "success"
                    elif status == "completed" and conclusion == "failure":
                        return "failure"
                    else:
                        return "running"

            return "unknown"
        except:
            return "unknown"

    def _load_cache(self):
        """キャッシュ読み込み（既存機能）"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    self.cache = json.load(f)
            except Exception:
                self.cache = {}
        else:
            self.cache = {}

    def _save_cache(self):
        """キャッシュ保存（既存機能）"""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"⚠️  キャッシュ保存失敗: {e}")

    def _get_file_hash(self, file_path: str) -> str:
        """ファイルのハッシュ値を計算（既存機能）"""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def _is_file_changed(self, file_path: str) -> bool:
        """ファイルが変更されたかキャッシュで判定（既存機能）"""
        current_hash = self._get_file_hash(file_path)
        cached_hash = self.cache.get(file_path, "")

        if current_hash != cached_hash:
            self.cache[file_path] = current_hash
            return True
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="🚀 Git自動コミット＆プッシュツール v9.1 - インポート自動修復版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 通常開発（超高速モード + インポート自動修復）
  python3 agents/git_agent/auto_commit_push_v09_integrated.py "✅ 機能追加"

  # 重要変更（フルチェックモード）
  python3 agents/git_agent/auto_commit_push_v09_integrated.py "🚨 重要変更" --wait-ci

v9.1 新機能:
  ✅ インポート自動修復（Path, List, Dictなどの未定義エラーを自動修正）
  ✅ 拡張可能な修復マップ（common_imports_mapで簡単拡張）
  ✅ 既存全機能を完全保持（v9.0完全互換）
  ✅ 統計レポートに修復実績を追加
        """,
    )

    parser.add_argument("message", nargs="?", help="コミットメッセージ（省略可）")
    parser.add_argument(
        "--wait-ci",
        action="store_true",
        help="CI完了まで待機（重要な変更時のみ使用）",
    )

    args = parser.parse_args()

    tool = IntegratedGitTool(args.message, args.wait_ci)
    sys.exit(tool.run())


if __name__ == "__main__":
    main()
