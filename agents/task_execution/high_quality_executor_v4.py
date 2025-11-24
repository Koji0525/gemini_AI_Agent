"""
高品質タスク実行エンジン v4.0
品質強化版

改善点:
- タスク内容の自動具体化
- 最低ファイル数の強制（5個以上）
- 成果物の妥当性検証
- より詳細なプロンプト
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from agents.task_execution.high_quality_executor_v3 import \
    HighQualityExecutorV3
from agents.task_execution.task_clarifier import TaskClarifier


class HighQualityExecutorV4(HighQualityExecutorV3):
    """
    高品質タスク実行エンジン v4.0

    v3からの変更点:
    - タスク内容の自動具体化
    - ファイル数の品質基準追加
    - より厳格な成果物検証
    """

    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """初期化"""
        super().__init__(model_name)

        # タスク具体化エンジン追加
        self.clarifier = TaskClarifier()

        print(f"🎯 タスク具体化エンジン: 有効")

    def execute_task(
        self,
        task_id,
        task_description,
        required_role="general",
        dependencies=None,
        context=None,
        retry_count=0,
        max_retries=3,
    ):
        """タスク実行（品質強化版）"""

        # 1. タスク内容の具体化
        clarified = self.clarifier.clarify(task_description, required_role)

        print(f"\n🎯 タスク具体化:")
        print(f"  タイプ: {clarified['task_type']}")
        print(f"  期待ファイル数: {clarified['minimum_files']}")
        print(f"  キーワード: {', '.join(clarified['keywords'][:3])}")

        # 2. 具体化された説明で実行
        result = super().execute_task(
            task_id=task_id,
            task_description=clarified["clarified_description"],
            required_role=required_role,
            dependencies=dependencies,
            context={
                **(context or {}),
                "expected_files": clarified["expected_files"],
                "requirements": clarified["requirements"],
            },
            retry_count=retry_count,
            max_retries=max_retries,
        )

        # 3. ファイル数の検証
        if "file_count" in result:
            if result["file_count"] < clarified["minimum_files"]:
                print(f"\n⚠️ ファイル数不足: {result['file_count']}/{clarified['minimum_files']}")

                # リトライ判定
                if retry_count < max_retries:
                    print(f"🔄 ファイル数不足によるリトライ: {retry_count + 1}/{max_retries}")
                    import time

                    time.sleep(2)

                    return self.execute_task(
                        task_id=task_id,
                        task_description=task_description,
                        required_role=required_role,
                        dependencies=dependencies,
                        context=context,
                        retry_count=retry_count + 1,
                        max_retries=max_retries,
                    )

        return result

    def _build_high_quality_prompt(
        self,
        task_description,
        required_role,
        dep_context,
        knowledge_context,
        additional_context,
        retry_count,
    ):
        """プロンプト生成（品質強化版）"""

        # 期待ファイルリスト
        expected_files = additional_context.get("expected_files", []) if additional_context else []
        requirements = additional_context.get("requirements", []) if additional_context else []

        prompt_parts = [
            "# タスク実行プロンプト（品質強化版 v4.0）",
            "",
            "## 🎯 成果物要件（厳格）",
            "",
            "### 必須条件:",
            f"1. **最低{len(expected_files) if expected_files else 5}個以上のファイル**を生成",
            "2. **各ファイルは独立して実行可能**なコード",
            "3. **テストファイル必須**（tests/ ディレクトリ）",
            "4. **設定ファイル必須**（config.yaml または .env）",
            "5. **README.md 必須**（詳細な使用方法）",
            "6. **全ファイル合計で300行以上**",
            "",
            "### 生成すべきファイル:",
        ]

        if expected_files:
            for i, filename in enumerate(expected_files, 1):
                prompt_parts.append(f"{i}. `{filename}`")
        else:
            prompt_parts.extend(
                [
                    "1. `main.py` - メイン実装",
                    "2. `models.py` - データモデル",
                    "3. `utils.py` - ユーティリティ",
                    "4. `config.yaml` - 設定ファイル",
                    "5. `tests/test_main.py` - テストコード",
                    "6. `README.md` - ドキュメント",
                ]
            )

        prompt_parts.extend(
            [
                "",
                "### 出力形式（厳守）:",
                "各ファイルは必ず以下の形式で記述してください:",
                "",
                "```",
                "## ファイル: ファイル名",
                "",
                "```言語名",
                "ファイル内容",
                "```",
                "```",
                "",
                "### 例:",
                "```",
                "## ファイル: ml_pipeline.py",
                "",
                "```python",
                '"""機械学習パイプライン"""',
                "import pandas as pd",
                "",
                "class MLPipeline:",
                "    def __init__(self):",
                "        pass",
                "```",
                "",
                "## ファイル: config.yaml",
                "",
                "```yaml",
                "model:",
                "  type: RandomForest",
                "  n_estimators: 100",
                "```",
                "```",
                "",
                f"## 📋 タスク内容",
                task_description,
                "",
                f"## 👤 ロール: {required_role}",
                "",
            ]
        )

        # 具体的な要件
        if requirements:
            prompt_parts.append("## 📝 実装要件:")
            for i, req in enumerate(requirements, 1):
                prompt_parts.append(f"{i}. {req}")
            prompt_parts.append("")

        # リトライ戦略
        if retry_count == 0:
            prompt_parts.extend(
                [
                    "## 🎯 方針（初回）: 完全性重視",
                    "- すべてのファイルを確実に生成",
                    "- 各ファイルに詳細なコメント",
                    "- 実行可能なコードを優先",
                ]
            )
        elif retry_count == 1:
            prompt_parts.extend(
                [
                    "## 🎯 方針（2回目）: ファイル数重視",
                    "- **前回ファイル数が不足していました**",
                    f"- **最低{len(expected_files) if expected_files else 5}個以上必須**",
                    "- テストファイルも必ず含める",
                    "- 設定ファイルも必ず含める",
                ]
            )
        else:
            prompt_parts.extend(
                [
                    "## 🎯 方針（3回目）: 最大化",
                    "- **ファイル数を最大化**",
                    "- **コード量を最大化**",
                    f"- **{len(expected_files) if expected_files else 5}個以上は絶対条件**",
                ]
            )

        prompt_parts.extend(
            [
                "",
                "## ⚠️ 禁止事項:",
                "- ファイル数が5個未満は絶対NG",
                "- テストファイルがないのはNG",
                "- 設定ファイルがないのはNG",
                "- README.mdがないのはNG",
                "- 説明だけのファイルはNG",
                "",
                "## 🚀 開始",
                "上記の要件を満たす完全なファイルセットを生成してください。",
                f"**最低{len(expected_files) if expected_files else 5}個以上のファイルは必須です。**",
            ]
        )

        return "\n".join(prompt_parts)

    def _evaluate_quality(self, result):
        """品質評価（ファイル数も考慮）"""
        quality = super()._evaluate_quality(result)

        # ファイル数ボーナス（追加で最大10点）
        # この時点ではファイル数は不明なので、後で調整する必要がある

        return quality


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 HighQualityExecutor v4.0 テスト（品質強化版）")
    print("=" * 60)

    try:
        executor = HighQualityExecutorV4(model_name="gemini-2.0-flash-exp")

        test_task = {
            "task_id": "test_quality_v4",
            "task_description": "既存システム分析システムを実装。既存コードの依存関係分析、影響範囲特定、テストカバレッジ測定を行う。",
            "required_role": "engineer",
        }

        result = executor.execute_task(**test_task)

        if "file_count" in result:
            print(f"\n📊 最終結果:")
            print(f"  ファイル数: {result['file_count']}")
            print(f"  品質スコア: {result['quality_score']}/100")
            print(f"  行数: {result['line_count']}")

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
