#!/usr/bin/env python3
"""
非同期テスト自動修正ツール
"""
import re
from pathlib import Path


class AsyncTestFixer:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent

    def find_async_tests(self):
        """非同期テストを検索"""
        test_files = []
        for py_file in self.root_dir.rglob("test_*.py"):
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            # async def があるが @pytest.mark.asyncio がないファイルを検出
            if "async def test_" in content and "@pytest.mark.asyncio" not in content:
                test_files.append(py_file)

        return test_files

    def fix_async_test(self, file_path):
        """単一ファイルを修正"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 既に修正済みかチェック
        if "@pytest.mark.asyncio" in content:
            print(f"✅ 既に修正済み: {file_path}")
            return False

        # import文の追加
        if "import pytest" not in content:
            # 最初のimportの後にpytestを追加
            import_pattern = r"(^import\s+.*?$)"
            content = re.sub(
                import_pattern, r"\1\nimport pytest", content, count=1, flags=re.MULTILINE
            )

        # 非同期テスト関数にデコレータを追加
        content = re.sub(
            r"^(async def test_.*?:)", r"@pytest.mark.asyncio\n\1", content, flags=re.MULTILINE
        )

        # ファイルを保存
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ 修正完了: {file_path}")
        return True

    def run_fixes(self):
        """すべての修正を実行"""
        test_files = self.find_async_tests()

        if not test_files:
            print("✅ 修正が必要な非同期テストはありません")
            return

        print(f"🔧 {len(test_files)} 個の非同期テストを修正します...")

        fixed_count = 0
        for test_file in test_files:
            if self.fix_async_test(test_file):
                fixed_count += 1

        print(f"🎉 {fixed_count}/{len(test_files)} 個のテストを修正完了")


if __name__ == "__main__":
    fixer = AsyncTestFixer()
    fixer.run_fixes()
