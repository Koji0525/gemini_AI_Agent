"""
品質チェックユーティリティ

タスク実行結果の品質を検証し、不足している場合は再実行を促す。
"""

import re
from typing import Dict, List, Tuple


class QualityChecker:
    """実行結果の品質チェッカー"""

    def __init__(self):
        self.min_total_lines = 500
        self.min_files = 2
        self.min_readme_lines = 100

    def check_output(self, output_text: str) -> Tuple[bool, List[str]]:
        """
        出力の品質をチェック

        Args:
            output_text: タスク実行結果のテキスト

        Returns:
            (合格/不合格, 問題点リスト)
        """
        issues = []

        # ファイル抽出
        files = self._extract_files(output_text)

        if not files:
            issues.append("ファイルが1つも生成されていません")
            return False, issues

        # ファイル数チェック
        if len(files) < self.min_files:
            issues.append(f"ファイル数不足: {len(files)}ファイル（最低{self.min_files}必要）")

        # 総行数チェック
        total_lines = sum(f["lines"] for f in files)
        if total_lines < self.min_total_lines:
            issues.append(f"コード量不足: {total_lines}行（最低{self.min_total_lines}必要）")

        # README.mdチェック
        readme_files = [f for f in files if "README" in f["name"].upper()]
        if not readme_files:
            issues.append("README.mdが見つかりません")
        else:
            readme_lines = readme_files[0]["lines"]
            if readme_lines < self.min_readme_lines:
                issues.append(f"README.md不足: {readme_lines}行（最低{self.min_readme_lines}必要）")

        # 合否判定
        passed = len(issues) == 0

        return passed, issues

    def _extract_files(self, text: str) -> List[Dict]:
        """コードブロックからファイルを抽出"""
        files = []

        # マークダウンコードブロックを検索（正しいエスケープ）
        pattern = r"```(?:python|markdown|yaml|json|txt)?\s*\n#?\s*filename:\s*([^\n]+)\n(.*?)```"
        matches = re.finditer(pattern, text, re.DOTALL)

        for match in matches:
            filename = match.group(1).strip()
            content = match.group(2)
            lines = len(content.split("\n"))

            files.append({"name": filename, "content": content, "lines": lines})

        return files

    def generate_retry_prompt(self, issues: List[str]) -> str:
        """再試行用のプロンプトを生成"""
        prompt = "前回の出力は以下の問題があったため、改善して再生成してください：\n\n"

        for i, issue in enumerate(issues, 1):
            prompt += f"{i}. {issue}\n"

        prompt += "\n必ず以下を満たしてください：\n"
        prompt += f"- 総コード量: {self.min_total_lines}行以上\n"
        prompt += f"- ファイル数: {self.min_files}ファイル以上\n"
        prompt += f"- README.md: {self.min_readme_lines}行以上\n"

        return prompt


# テスト
if __name__ == "__main__":
    checker = QualityChecker()

    # テストケース1: 小規模出力
    test_small = """
`````python
# filename: main.py
def hello():
    print("Hello")
`````
"""
    passed, issues = checker.check_output(test_small)
    print(f"テスト1（小規模）: {'✅ 合格' if passed else '❌ 不合格'}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")
    print()

    # テストケース2: 適切な出力
    test_large = (
        """
`````python
# filename: main.py
"""
        + "\n".join([f"# Line {i}" for i in range(600)])
        + """
`````
`````python
# filename: test_main.py
"""
        + "\n".join([f"# Test line {i}" for i in range(200)])
        + """
`````
`````markdown
# filename: README.md
"""
        + "\n".join([f"# README line {i}" for i in range(150)])
        + """
`````
"""
    )
    passed, issues = checker.check_output(test_large)
    print(f"テスト2（適切）: {'✅ 合格' if passed else '❌ 不合格'}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")
