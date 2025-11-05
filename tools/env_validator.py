#!/usr/bin/env python3
"""
🔍 環境変数整合性チェックツール
ワンクリックで環境変数の定義と使用状況を確認
"""
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class EnvironmentValidator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.env_file = self.project_root / ".env"
        self.results = {
            "defined_but_unused": [],
            "used_but_undefined": [],
            "properly_used": [],
            "file_issues": [],
        }

    def load_env_variables(self) -> Dict[str, str]:
        """.envファイルから環境変数を読み込み"""
        env_vars = {}
        if not self.env_file.exists():
            self.results["file_issues"].append("❌ .envファイルが存在しません")
            return env_vars

        with open(self.env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()

        return env_vars

    def find_usage_in_python_files(self) -> Dict[str, List[str]]:
        """Pythonファイル内の環境変数使用箇所を検索"""
        usage = {}
        python_files = list(self.project_root.rglob("*.py"))

        for py_file in python_files:
            # 特定のディレクトリを除外
            if any(excluded in str(py_file) for excluded in ["venv", "__pycache__", ".git"]):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # os.getenv パターンを検索
                patterns = [
                    r'os\.getenv\([\'"]([^\'"]+)[\'"]\)',
                    r'os\.environ\.get\([\'"]([^\'"]+)[\'"]\)',
                    r'os\.environ\[[\'"]([^\'"]+)[\'"]\]',
                    r'getenv\([\'"]([^\'"]+)[\'"]\)',
                ]

                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if match not in usage:
                            usage[match] = []
                        usage[match].append(str(py_file.relative_to(self.project_root)))

            except Exception as e:
                print(f"⚠️ ファイル読み込みエラー {py_file}: {e}")

        return usage

    def validate(self) -> bool:
        """環境変数の整合性を検証"""
        print("🔍 環境変数整合性チェックを開始...")
        print("=" * 60)

        # 環境変数を読み込み
        env_vars = self.load_env_variables()
        defined_keys = set(env_vars.keys())

        print(f"📋 .envで定義されている環境変数 ({len(defined_keys)}件):")
        for key in sorted(defined_keys):
            # 機密情報をマスク
            value = env_vars[key]
            if any(sensitive in key.lower() for sensitive in ["key", "pass", "secret", "token"]):
                value = "***" + value[-4:] if len(value) > 4 else "***"
            print(f"  {key}={value}")

        print()

        # 使用状況を検索
        usage = self.find_usage_in_python_files()
        used_keys = set(usage.keys())

        print(f"🔧 コード内で使用されている環境変数 ({len(used_keys)}件):")
        for key in sorted(used_keys):
            files = usage[key][:3]  # 最大3ファイルまで表示
            files_str = ", ".join(files)
            if len(usage[key]) > 3:
                files_str += f" ...他{len(usage[key]) - 3}件"
            print(f"  {key} -> {files_str}")

        print()

        # 整合性チェック
        defined_but_unused = defined_keys - used_keys
        used_but_undefined = used_keys - defined_keys
        properly_used = defined_keys & used_keys

        # 結果を格納
        self.results["defined_but_unused"] = sorted(defined_but_unused)
        self.results["used_but_undefined"] = sorted(used_but_undefined)
        self.results["properly_used"] = sorted(properly_used)

        # 結果を表示
        print("📊 整合性チェック結果:")
        print(f"  ✅ 適切に使用: {len(properly_used)}件")
        print(f"  ⚠️  定義済みだが未使用: {len(defined_but_unused)}件")
        print(f"  ❌ 使用中だが未定義: {len(used_but_undefined)}件")

        if defined_but_unused:
            print(f"\n⚠️  定義済みだが未使用の環境変数:")
            for var in defined_but_unused:
                print(f"    - {var}")

        if used_but_undefined:
            print(f"\n❌ 使用中だが未定義の環境変数:")
            for var in used_but_undefined:
                files = usage[var][:2]
                files_str = ", ".join(files)
                print(f"    - {var} (使用箇所: {files_str})")

        # ファイルの問題を表示
        if self.results["file_issues"]:
            print(f"\n🚨 ファイルの問題:")
            for issue in self.results["file_issues"]:
                print(f"    - {issue}")

        print("=" * 60)

        # 重大な問題がある場合はFalseを返す
        has_critical_issues = len(used_but_undefined) > 0 or len(self.results["file_issues"]) > 0

        if has_critical_issues:
            print("❌ 重大な問題が見つかりました")
            return False
        else:
            print("✅ 環境変数の整合性は良好です")
            return True

    def generate_report(self) -> str:
        """レポートを生成"""
        report = []
        report.append("# 環境変数整合性チェックレポート")
        report.append("")

        report.append("## 概要")
        report.append(f"- 適切に使用: {len(self.results['properly_used'])}件")
        report.append(f"- 定義済みだが未使用: {len(self.results['defined_but_unused'])}件")
        report.append(f"- 使用中だが未定義: {len(self.results['used_but_undefined'])}件")
        report.append("")

        if self.results["defined_but_unused"]:
            report.append("## 定義済みだが未使用の環境変数")
            for var in self.results["defined_but_unused"]:
                report.append(f"- {var}")
            report.append("")

        if self.results["used_but_undefined"]:
            report.append("## 使用中だが未定義の環境変数")
            for var in self.results["used_but_undefined"]:
                report.append(f"- {var}")
            report.append("")

        return "\n".join(report)


def main():
    """メイン実行関数"""
    validator = EnvironmentValidator()
    is_valid = validator.validate()

    # レポートを保存
    report = validator.generate_report()
    with open("environment_validation_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n📄 詳細レポート: environment_validation_report.md")

    # 終了コードを返す（CI/CDで使用可能）
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
