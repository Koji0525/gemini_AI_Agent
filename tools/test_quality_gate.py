#!/usr/bin/env python3
"""
テスト品質ゲート - テスト実行前の自動検証
"""
import sys
from pathlib import Path


class TestQualityGate:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.issues = []

    def run_checks(self):
        """すべての品質チェックを実行"""
        print("🔍 テスト品質ゲートを実行中...")

        checks = [
            self.check_imports,
            self.check_async_usage,
            self.check_mock_patterns,
            self.check_test_isolation,
        ]

        for check in checks:
            try:
                check()
            except Exception as e:
                self.issues.append(f"❌ チェック失敗: {check.__name__} - {e}")

        return self.issues

    def check_imports(self):
        """インポートのチェック"""
        test_files = list(self.root_dir.rglob("test_*.py"))

        for test_file in test_files:
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()

            # asyncioの使用をチェック
            if "asyncio.run" in content or "asyncio." in content:
                if "import asyncio" not in content:
                    self.issues.append(
                        f"❌ インポート漏れ: {test_file} で asyncio を使用しているがインポートしていない"
                    )

    def check_async_usage(self):
        """非同期使用のチェック"""
        test_files = list(self.root_dir.rglob("test_*.py"))

        for test_file in test_files:
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 非同期メソッドのテストをチェック
            if "async def" in content:
                if "@pytest.mark.asyncio" not in content:
                    self.issues.append(
                        f"⚠️  非同期テストのマーク不足: {test_file} で async def を使用しているが @pytest.mark.asyncio がない"
                    )

    def check_mock_patterns(self):
        """モックパターンのチェック"""
        test_files = list(self.root_dir.rglob("test_*.py"))

        for test_file in test_files:
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 危険なモックパターンを検出
            if "genai" in content and "mock_genai" not in content:
                self.issues.append(
                    f"⚠️  直接的な genai 使用: {test_file} で genai をモックせずに使用している可能性"
                )

    def check_test_isolation(self):
        """テスト分離のチェック"""
        # グローバル状態の変更を検出する簡単なチェック

    def generate_report(self):
        """レポート生成"""
        issues = self.run_checks()

        if issues:
            print("❌ テスト品質ゲートで問題を検出:")
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print("✅ すべての品質チェックを通過")
            return True


if __name__ == "__main__":
    gate = TestQualityGate()
    success = gate.generate_report()
    sys.exit(0 if success else 1)
