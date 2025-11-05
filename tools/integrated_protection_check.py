#!/usr/bin/env python3
"""
🏥 統合診断＆修復ツール v1.0
目的: プロジェクト全体の保護状態を診断・修復
"""

import os
import sys
from pathlib import Path
import subprocess


class IntegratedProtectionCheck:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed = []

    def check_env_protection(self):
        """1. .env保護状態チェック"""
        env_path = Path(".env")

        if not env_path.exists():
            self.warnings.append(".envファイルが存在しません")
            return

        # パーミッションチェック
        mode = oct(os.stat(env_path).st_mode)[-3:]

        if mode == "444":
            self.passed.append("✅ .envは読み取り専用で保護されています")
        else:
            self.issues.append(f"⚠️  .envが書き込み可能です (mode: {mode})")
            self.issues.append("   修復: python3 tools/env_protector.py protect")

        # バックアップ存在チェック
        backup_dir = Path("_BACKUP/env_backups")
        if backup_dir.exists() and list(backup_dir.glob("*.txt")):
            self.passed.append("✅ .envバックアップが存在します")
        else:
            self.warnings.append("ℹ️  .envバックアップが未作成です")

    def check_git_hooks(self):
        """2. Gitフック設置チェック"""
        hooks_dir = Path(".git/hooks")

        required_hooks = ["pre-commit", "post-checkout"]

        for hook in required_hooks:
            hook_path = hooks_dir / hook

            if hook_path.exists() and os.access(hook_path, os.X_OK):
                self.passed.append(f"✅ {hook}フックが設置されています")
            else:
                self.issues.append(f"❌ {hook}フックが未設置です")
                self.issues.append(f"   修復: tools/setup_protection_hooks.sh")

    def check_critical_files(self):
        """3. 重要ファイルの存在チェック"""
        critical_files = ["requirements.txt", ".gitignore", "README.md"]

        for file in critical_files:
            if Path(file).exists():
                self.passed.append(f"✅ {file}が存在します")
            else:
                self.warnings.append(f"ℹ️  {file}が存在しません")

    def check_tools_availability(self):
        """4. 保護ツールの利用可能性チェック"""
        tools = [
            "tools/env_protector.py",
            "tools/code_impact_analyzer.py",
            "tools/setup_protection_hooks.sh",
        ]

        for tool in tools:
            if Path(tool).exists() and os.access(tool, os.X_OK):
                self.passed.append(f"✅ {Path(tool).name}が利用可能です")
            else:
                self.issues.append(f"❌ {Path(tool).name}が利用できません")

    def run_all_checks(self):
        """全チェック実行"""
        print("=" * 60)
        print("🏥 統合保護診断を開始します")
        print("=" * 60)

        self.check_env_protection()
        self.check_git_hooks()
        self.check_critical_files()
        self.check_tools_availability()

        # レポート表示
        print("\n" + "=" * 60)
        print("📊 診断結果")
        print("=" * 60)

        if self.passed:
            print("\n✅ 正常項目:")
            for item in self.passed:
                print(f"  {item}")

        if self.warnings:
            print("\n⚠️  警告項目:")
            for item in self.warnings:
                print(f"  {item}")

        if self.issues:
            print("\n❌ 問題項目:")
            for item in self.issues:
                print(f"  {item}")

            print("\n🔧 修復オプション:")
            print("  --auto-fix: 自動修復を実行")
            return 1
        else:
            print("\n🎉 すべての保護機能が正常です！")
            return 0

    def auto_fix(self):
        """自動修復実行"""
        print("🔧 自動修復を開始します...\n")

        # .env保護
        if any(".envが書き込み可能" in issue for issue in self.issues):
            subprocess.run(["python3", "tools/env_protector.py", "protect"])

        # Gitフック設置
        if any("フックが未設置" in issue for issue in self.issues):
            subprocess.run(["bash", "tools/setup_protection_hooks.sh"])

        print("\n✅ 自動修復完了")
        print("   診断を再実行してください")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="統合保護診断")
    parser.add_argument("--auto-fix", action="store_true", help="自動修復を実行")

    args = parser.parse_args()

    checker = IntegratedProtectionCheck()

    if args.auto_fix:
        checker.run_all_checks()
        checker.auto_fix()
    else:
        exit_code = checker.run_all_checks()
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
