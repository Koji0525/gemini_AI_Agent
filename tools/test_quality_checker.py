#!/usr/bin/env python3
"""
テスト品質チェッカー
"""
import ast
from pathlib import Path


class TestQualityChecker:
    def __init__(self):
        self.root_dir = Path(".")

    def check_test_imports(self, test_file):
        """テストファイルのインポートをチェック"""
        issues = []

        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module = node.module
                    for alias in node.names:
                        # モックのインポートをチェック
                        if alias.name in ["patch", "Mock", "MagicMock"]:
                            if module != "unittest.mock":
                                issues.append(f"❌ 誤ったモックインポート: {module}.{alias.name}")

        except Exception as e:
            issues.append(f"❌ 構文解析エラー: {e}")

        return issues

    def validate_test_structure(self):
        """テスト構造を検証"""
        test_files = list(self.root_dir.rglob("test_*.py"))
        results = {}

        for test_file in test_files:
            issues = self.check_test_imports(test_file)
            if issues:
                results[str(test_file)] = issues

        return results


def main():
    checker = TestQualityChecker()
    results = checker.validate_test_structure()

    if results:
        print("❌ テスト品質の問題を発見:")
        for file, issues in results.items():
            print(f"\n📄 {file}:")
            for issue in issues:
                print(f"  {issue}")
    else:
        print("✅ すべてのテストファイルが品質基準を満たしています")


if __name__ == "__main__":
    main()
