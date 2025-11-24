"""
タスク内容具体化エンジン
曖昧なタスク説明を具体的な実装要件に変換
"""

import re
from typing import Dict, List


class TaskClarifier:
    """タスク内容を具体化するエンジン"""

    # タスクタイプごとのテンプレート
    TASK_TEMPLATES = {
        "analysis": {
            "files": [
                "analyzer.py",
                "report_generator.py",
                "config.yaml",
                "tests/test_analyzer.py",
                "README.md",
            ],
            "requirements": ["データ収集", "分析ロジック", "レポート生成", "可視化"],
        },
        "implementation": {
            "files": [
                "main.py",
                "models.py",
                "utils.py",
                "config.yaml",
                "tests/test_main.py",
                "README.md",
            ],
            "requirements": [
                "コアロジック",
                "データモデル",
                "ユーティリティ",
                "エラーハンドリング",
            ],
        },
        "api": {
            "files": [
                "api.py",
                "models.py",
                "validators.py",
                "config.yaml",
                "tests/test_api.py",
                "README.md",
            ],
            "requirements": [
                "エンドポイント定義",
                "リクエスト検証",
                "レスポンス生成",
                "エラーハンドリング",
            ],
        },
        "test": {
            "files": [
                "test_suite.py",
                "fixtures.py",
                "conftest.py",
                "test_config.yaml",
                "README.md",
            ],
            "requirements": ["テストケース", "テストデータ", "アサーション", "カバレッジ"],
        },
    }

    def clarify(self, task_description: str, required_role: str = "general") -> Dict:
        """
        タスク内容を具体化

        Args:
            task_description: タスクの説明
            required_role: 必要なロール

        Returns:
            具体化された要件
        """
        # タスクタイプの推定
        task_type = self._infer_task_type(task_description, required_role)

        # テンプレート取得
        template = self.TASK_TEMPLATES.get(task_type, self.TASK_TEMPLATES["implementation"])

        # キーワード抽出
        keywords = self._extract_keywords(task_description)

        # ファイル名のカスタマイズ
        customized_files = self._customize_filenames(template["files"], keywords)

        # 具体的な要件生成
        specific_requirements = self._generate_requirements(
            task_description, template["requirements"], keywords
        )

        return {
            "task_type": task_type,
            "original_description": task_description,
            "clarified_description": self._build_clarified_description(
                task_description, specific_requirements
            ),
            "expected_files": customized_files,
            "requirements": specific_requirements,
            "minimum_files": len(customized_files),
            "keywords": keywords,
        }

    def _infer_task_type(self, description: str, role: str) -> str:
        """タスクタイプを推定"""
        description_lower = description.lower()

        if any(kw in description_lower for kw in ["分析", "analyze", "調査", "研究"]):
            return "analysis"
        elif any(kw in description_lower for kw in ["api", "エンドポイント", "rest"]):
            return "api"
        elif any(kw in description_lower for kw in ["テスト", "test", "検証"]):
            return "test"
        else:
            return "implementation"

    def _extract_keywords(self, description: str) -> List[str]:
        """キーワードを抽出"""
        # 主要な名詞を抽出
        keywords = []

        # カタカナ語（例: システム、パイプライン）
        katakana_words = re.findall(r"[ァ-ヴー]+", description)
        keywords.extend([w for w in katakana_words if len(w) >= 3])

        # 英単語（例: ML, API）
        english_words = re.findall(r"\b[A-Za-z]{2,}\b", description)
        keywords.extend(english_words)

        # 重複削除
        return list(set(keywords))[:5]

    def _customize_filenames(self, template_files: List[str], keywords: List[str]) -> List[str]:
        """ファイル名をカスタマイズ"""
        if not keywords:
            return template_files

        # 最初のキーワードを使ってファイル名を調整
        main_keyword = keywords[0].lower().replace("ー", "_")

        customized = []
        for filename in template_files:
            if filename == "main.py":
                customized.append(f"{main_keyword}_main.py")
            elif filename == "analyzer.py":
                customized.append(f"{main_keyword}_analyzer.py")
            else:
                customized.append(filename)

        return customized

    def _generate_requirements(
        self, description: str, template_reqs: List[str], keywords: List[str]
    ) -> List[str]:
        """具体的な要件を生成"""
        requirements = []

        # テンプレート要件をベースに
        for req in template_reqs:
            requirements.append(f"{req}（{', '.join(keywords[:2])}に関連）")

        # 元の説明から追加要件を抽出
        if "300行以上" in description:
            requirements.append("最低300行以上のコード実装")

        if "テスト" in description or "test" in description.lower():
            requirements.append("pytest形式のテストコード（カバレッジ80%以上）")

        return requirements

    def _build_clarified_description(self, original: str, requirements: List[str]) -> str:
        """具体化された説明を生成"""
        clarified_parts = [f"【元のタスク】", original, "", "【具体的な実装要件】"]

        for i, req in enumerate(requirements, 1):
            clarified_parts.append(f"{i}. {req}")

        return "\n".join(clarified_parts)


if __name__ == "__main__":
    clarifier = TaskClarifier()

    # テスト
    test_task = "既存システム分析と影響範囲特定。既存システムのアーキテクチャ、コンポーネント、データフローを詳細に分析"

    result = clarifier.clarify(test_task, "engineer")

    print("=" * 60)
    print("📋 タスク具体化結果")
    print("=" * 60)
    print(f"\nタイプ: {result['task_type']}")
    print(f"\n期待ファイル数: {result['minimum_files']}")
    print(f"\nファイル一覧:")
    for f in result["expected_files"]:
        print(f"  - {f}")
    print(f"\n要件:")
    for r in result["requirements"]:
        print(f"  - {r}")
