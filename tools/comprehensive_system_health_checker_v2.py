#!/usr/bin/env python3
"""
システム健全性チェッカー v2.0
全てのコンポーネントを統合的にチェック
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict


class ComprehensiveSystemHealthChecker:
    """システム健全性チェッカー"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {"status": "unknown", "checks": {}, "errors": [], "warnings": []}

    def check_python_syntax(self) -> Dict[str, Any]:
        """全Pythonファイルの構文チェック"""
        print("🐍 Python構文チェック中...")
        errors = []

        for py_file in self.project_root.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    compile(f.read(), py_file, "exec")
            except SyntaxError as e:
                errors.append(f"{py_file}: Line {e.lineno} - {e.msg}")

        return {"passed": len(errors) == 0, "errors": errors}

    def check_required_files(self) -> Dict[str, Any]:
        """必須ファイルの存在確認"""
        print("📁 必須ファイルチェック中...")
        required = [".env", "requirements.txt", "README.md"]

        missing = [f for f in required if not (self.project_root / f).exists()]

        return {"passed": len(missing) == 0, "missing": missing}

    def check_env_variables(self) -> Dict[str, Any]:
        """環境変数チェック"""
        print("🔐 環境変数チェック中...")
        required_vars = ["GEMINI_API_KEY", "SPREADSHEET_ID"]

        missing = [var for var in required_vars if not os.getenv(var)]

        return {"passed": len(missing) == 0, "missing": missing}

    def run_all_checks(self) -> Dict[str, Any]:
        """全チェック実行"""
        print("🏥 システム健全性チェック開始\n")

        checks = {
            "python_syntax": self.check_python_syntax(),
            "required_files": self.check_required_files(),
            "env_variables": self.check_env_variables(),
        }

        self.results["checks"] = checks

        # 総合判定
        all_passed = all(check["passed"] for check in checks.values())
        self.results["status"] = "healthy" if all_passed else "unhealthy"

        # エラー集計
        for check_name, check_result in checks.items():
            if not check_result["passed"]:
                if "errors" in check_result:
                    self.results["errors"].extend(check_result["errors"])
                if "missing" in check_result:
                    self.results["warnings"].append(f"{check_name}: {check_result['missing']}")

        return self.results

    def print_results(self):
        """結果表示"""
        print("\n" + "=" * 60)
        print(f"📊 総合結果: {self.results['status'].upper()}")
        print("=" * 60)

        for check_name, check_result in self.results["checks"].items():
            status = "✅" if check_result["passed"] else "❌"
            print(f"{status} {check_name}")

        if self.results["errors"]:
            print("\n❌ エラー:")
            for error in self.results["errors"]:
                print(f"  - {error}")

        if self.results["warnings"]:
            print("\n⚠️  警告:")
            for warning in self.results["warnings"]:
                print(f"  - {warning}")


def main():
    checker = ComprehensiveSystemHealthChecker()
    results = checker.run_all_checks()
    checker.print_results()

    # 終了コード
    sys.exit(0 if results["status"] == "healthy" else 1)


if __name__ == "__main__":
    main()
