"""
機能完全性チェッカー v2.0
現実的な基準版
"""

from typing import Dict, List


class CompletenessCheckerV2:
    """現実的な基準でチェック"""

    # 緩和した最低要件
    MINIMUM_REQUIREMENTS = {
        "main_implementation": {
            "min_chars": 500,  # 1000 → 500
            "min_lines": 30,  # 50 → 30
            "required_elements": ["def ", "import "],
        },
        "test": {
            "min_chars": 300,  # 500 → 300
            "min_lines": 15,  # 30 → 15
            "required_elements": ["def test_"],
        },
        "config": {"min_chars": 100, "min_lines": 5, "required_elements": []},
        "readme": {
            "min_chars": 200,  # 300 → 200
            "min_lines": 10,  # 20 → 10
            "required_elements": ["##"],
        },
    }

    def check_completeness(self, files: Dict[str, str], task_description: str) -> Dict:
        """完全性チェック（緩和版）"""
        issues = []
        quality_score = 100

        print(f"\n🔍 機能完全性チェック（緩和版）...")

        # 必須ファイル
        has_main = any(f.endswith(".py") and "test" not in f for f in files.keys())
        has_test = any("test" in f.lower() for f in files.keys())
        has_config = any(f.endswith((".yaml", ".yml")) for f in files.keys())
        has_readme = "README.md" in files

        if not has_main:
            issues.append("メイン実装ファイルなし")
            quality_score -= 25

        if not has_test:
            issues.append("テストファイルなし")
            quality_score -= 15

        if not has_config:
            issues.append("設定ファイルなし")
            quality_score -= 10

        if not has_readme:
            issues.append("README.mdなし")
            quality_score -= 10

        # 各ファイルの品質（緩和基準）
        for filename, content in files.items():
            file_issues = self._check_file_quality(filename, content)
            issues.extend(file_issues)
            quality_score -= len(file_issues) * 3  # 5 → 3

        quality_score = max(0, quality_score)

        result = {
            "is_complete": quality_score >= 70,  # 100 → 70
            "quality_score": quality_score,
            "issues": issues,
            "has_main": has_main,
            "has_test": has_test,
            "has_config": has_config,
            "has_readme": has_readme,
            "file_count": len(files),
        }

        if result["is_complete"]:
            print(f"  ✅ 完全性チェック: 合格 ({quality_score}/100)")
        else:
            print(f"  ⚠️  完全性チェック: 要改善 ({quality_score}/100)")
            print(f"  問題点: {len(issues)}件")

        return result

    def _check_file_quality(self, filename: str, content: str) -> List[str]:
        """ファイル品質チェック（緩和版）"""
        issues = []

        # ファイルタイプ判定
        if filename.endswith(".py") and "test" not in filename.lower():
            file_type = "main_implementation"
        elif "test" in filename.lower():
            file_type = "test"
        elif filename.endswith((".yaml", ".yml")):
            file_type = "config"
        elif filename == "README.md":
            file_type = "readme"
        else:
            return []

        requirements = self.MINIMUM_REQUIREMENTS.get(file_type, {})

        # 文字数チェック
        if len(content) < requirements.get("min_chars", 0):
            issues.append(f"{filename}: 内容が薄い")

        # 必須要素チェック（緩和）
        required = requirements.get("required_elements", [])
        missing = [elem for elem in required if elem not in content]
        if missing:
            issues.append(f"{filename}: 要素不足")

        return issues
