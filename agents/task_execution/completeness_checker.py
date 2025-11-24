"""
機能完全性チェッカー
生成された成果物が実際に目標を達成できるかを検証
"""

import re
from typing import Dict, List


class CompletenessChecker:
    """成果物の機能完全性を検証"""

    # ファイルタイプごとの最低要件
    MINIMUM_REQUIREMENTS = {
        "main_implementation": {
            "min_chars": 1000,
            "min_lines": 50,
            "required_elements": ["class ", "def ", "import ", '"""'],
        },
        "test": {
            "min_chars": 500,
            "min_lines": 30,
            "required_elements": ["def test_", "assert ", "import pytest"],
        },
        "config": {"min_chars": 200, "min_lines": 10, "required_elements": []},
        "readme": {
            "min_chars": 300,
            "min_lines": 20,
            "required_elements": ["##", "使用方法", "インストール"],
        },
    }

    def check_completeness(self, files: Dict[str, str], task_description: str) -> Dict:
        """
        成果物の完全性をチェック

        Args:
            files: {ファイル名: 内容} の辞書
            task_description: 元のタスク説明

        Returns:
            チェック結果
        """
        issues = []
        quality_score = 100

        print(f"\n🔍 機能完全性チェック開始...")

        # 1. 必須ファイルの存在チェック
        has_main = any(f.endswith(".py") and "test" not in f for f in files.keys())
        has_test = any("test" in f.lower() for f in files.keys())
        has_config = any(f.endswith((".yaml", ".yml", ".json", ".env")) for f in files.keys())
        has_readme = any(f.lower() == "readme.md" for f in files.keys())

        if not has_main:
            issues.append("メイン実装ファイルがありません")
            quality_score -= 30

        if not has_test:
            issues.append("テストファイルがありません")
            quality_score -= 20

        if not has_config:
            issues.append("設定ファイルがありません")
            quality_score -= 10

        if not has_readme:
            issues.append("README.mdがありません")
            quality_score -= 10

        # 2. 各ファイルの品質チェック
        for filename, content in files.items():
            file_issues = self._check_file_quality(filename, content)
            if file_issues:
                issues.extend(file_issues)
                quality_score -= len(file_issues) * 5

        # 3. タスク要件の達成度チェック
        task_coverage = self._check_task_coverage(files, task_description)
        if task_coverage < 0.7:
            issues.append(f"タスク要件のカバー率が低い: {task_coverage*100:.0f}%")
            quality_score -= 20

        # 4. 実装の深さチェック
        avg_file_size = sum(len(c) for c in files.values()) / len(files) if files else 0
        if avg_file_size < 800:
            issues.append(f"ファイルの平均サイズが小さい: {avg_file_size:.0f}文字")
            quality_score -= 15

        quality_score = max(0, quality_score)

        result = {
            "is_complete": len(issues) == 0,
            "quality_score": quality_score,
            "issues": issues,
            "has_main": has_main,
            "has_test": has_test,
            "has_config": has_config,
            "has_readme": has_readme,
            "task_coverage": task_coverage,
            "avg_file_size": avg_file_size,
        }

        # 結果表示
        if result["is_complete"]:
            print(f"  ✅ 完全性チェック: 合格 ({quality_score}/100)")
        else:
            print(f"  ⚠️  完全性チェック: 改善の余地あり ({quality_score}/100)")
            for issue in issues:
                print(f"    - {issue}")

        return result

    def _check_file_quality(self, filename: str, content: str) -> List[str]:
        """個別ファイルの品質チェック"""
        issues = []

        # ファイルタイプの判定
        if filename.endswith(".py") and "test" not in filename.lower():
            file_type = "main_implementation"
        elif "test" in filename.lower():
            file_type = "test"
        elif filename.endswith((".yaml", ".yml", ".json")):
            file_type = "config"
        elif filename.lower() == "readme.md":
            file_type = "readme"
        else:
            return []  # その他のファイルはスキップ

        requirements = self.MINIMUM_REQUIREMENTS.get(file_type, {})

        # 文字数チェック
        min_chars = requirements.get("min_chars", 0)
        if len(content) < min_chars:
            issues.append(f"{filename}: 文字数不足 ({len(content)}/{min_chars})")

        # 行数チェック
        min_lines = requirements.get("min_lines", 0)
        line_count = len(content.split("\n"))
        if line_count < min_lines:
            issues.append(f"{filename}: 行数不足 ({line_count}/{min_lines})")

        # 必須要素チェック
        required_elements = requirements.get("required_elements", [])
        for element in required_elements:
            if element not in content:
                issues.append(f"{filename}: 必須要素不足 ({element})")

        return issues

    def _check_task_coverage(self, files: Dict[str, str], task_description: str) -> float:
        """タスク要件のカバー率を計算"""
        # タスク説明からキーワードを抽出
        keywords = self._extract_task_keywords(task_description)

        if not keywords:
            return 1.0  # キーワードがない場合は100%とする

        # 全ファイルの内容を結合
        all_content = "\n".join(files.values()).lower()

        # キーワードのカバー率
        covered = sum(1 for kw in keywords if kw.lower() in all_content)
        coverage = covered / len(keywords)

        return coverage

    def _extract_task_keywords(self, description: str) -> List[str]:
        """タスク説明から重要なキーワードを抽出"""
        # 主要な名詞を抽出（簡易版）
        keywords = []

        # カタカナ語
        katakana = re.findall(r"[ァ-ヴー]{3,}", description)
        keywords.extend(katakana)

        # 英単語
        english = re.findall(r"\b[A-Za-z]{3,}\b", description)
        keywords.extend(english)

        # 重複削除
        return list(set(keywords))[:10]


if __name__ == "__main__":
    checker = CompletenessChecker()

    # テスト
    test_files = {
        "main.py": "def test(): pass",  # 小さすぎる
        "config.yaml": "key: value",
    }

    result = checker.check_completeness(test_files, "機械学習パイプラインを実装")
    print(f"\nスコア: {result['quality_score']}/100")
    print(f"問題点: {len(result['issues'])}件")
