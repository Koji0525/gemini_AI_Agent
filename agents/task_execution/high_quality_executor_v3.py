"""
高品質タスク実行エンジン v3.0
構造化成果物対応版

改善点:
- 実行可能なファイルセットを生成
- ディレクトリ構造を持つ
- そのまま使える実装
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# v2をベースにインポート
from agents.task_execution.high_quality_executor_v2 import \
    HighQualityExecutorV2
from agents.task_execution.structured_output_engine import \
    StructuredOutputEngine


class HighQualityExecutorV3(HighQualityExecutorV2):
    """
    高品質タスク実行エンジン v3.0

    v2からの変更点:
    - Markdown出力を構造化ファイルセットに変換
    - 実行可能な成果物を生成
    """

    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """初期化"""
        super().__init__(model_name)

        # 構造化エンジン追加
        self.structured_engine = StructuredOutputEngine(
            base_output_dir=project_root / "agent_outputs" / "structured"
        )

        print(f"📁 構造化成果物: {self.structured_engine.base_output_dir}")

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
        """タスク実行（構造化成果物版）"""

        # v2の実行
        result = super().execute_task(
            task_id,
            task_description,
            required_role,
            dependencies,
            context,
            retry_count,
            max_retries,
        )

        if result["status"] in ["success", "needs_improvement"]:
            # Markdown形式の出力を構造化
            try:
                markdown_file = Path(result["output_file"])
                with open(markdown_file, "r", encoding="utf-8") as f:
                    markdown_text = f.read()

                # ファイルセット抽出
                files = self.structured_engine.extract_files_from_markdown(markdown_text, task_id)

                if files:
                    # 構造化保存
                    structured_dir = self.structured_engine.save_structured_output(files, task_id)

                    # 結果に追加
                    result["structured_output_dir"] = str(structured_dir)
                    result["structured_files"] = list(files.keys())
                    result["file_count"] = len(files)

                    print(f"\n📦 構造化成果物:")
                    print(f"  ディレクトリ: {structured_dir}")
                    print(f"  ファイル数: {len(files)}")
                    for filename in files.keys():
                        print(f"    - {filename}")
                else:
                    print(f"\n⚠️ コードブロックが抽出できませんでした")

            except Exception as e:
                print(f"\n⚠️ 構造化エラー: {e}")

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
        """プロンプト生成（構造化出力用に改良）"""

        prompt_parts = [
            "# タスク実行プロンプト（構造化成果物版 v3.0）",
            "",
            "## 🎯 成果物形式（必須）",
            "**実行可能なファイルセット**を生成してください。",
            "",
            "### 必須要件:",
            "1. **複数ファイルに分割**（単一ファイルNG）",
            "2. **実際に動作するコード**（説明だけNG）",
            "3. **ファイル名を明記**（例: `ml_pipeline.py`）",
            "4. **最低300行以上**（全ファイル合計）",
            "5. **そのまま使える実装**",
            "",
            "### 出力例:",
            "```",
            "## ファイル: ml_pipeline.py",
            "```python",
            '"""機械学習パイプライン"""',
            "class MLPipeline:",
            "    ...",
            "```",
            "",
            "## ファイル: config.yaml",
            "```yaml",
            "model:",
            "  type: RandomForest",
            "```",
            "",
            "## ファイル: tests/test_pipeline.py",
            "```python",
            "import pytest",
            "...",
            "```",
            "```",
            "",
            f"## 📋 タスク: {task_description}",
            f"## 👤 ロール: {required_role}",
            "",
        ]

        # リトライ戦略
        if retry_count == 0:
            prompt_parts.append("## 📝 方針: 詳細実装型（初回）")
        elif retry_count == 1:
            prompt_parts.append("## 📝 方針: ファイル分割重視型（2回目）")
        else:
            prompt_parts.append("## 📝 方針: コード量最大化型（3回目）")

        prompt_parts.extend(
            [
                "",
                "## ⚠️ 重要:",
                "- 各ファイルの冒頭に「## ファイル: xxx.py」と明記",
                "- コードブロックは必ず \\`\\`\\`python で開始",
                "- 説明文だけのファイルは作らない",
                "- テストファイルも必ず含める",
                "",
                "## 🚀 開始",
                "上記形式で実行可能なファイルセットを生成してください。",
            ]
        )

        return "\n".join(prompt_parts)


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 HighQualityExecutor v3.0 テスト（構造化成果物）")
    print("=" * 60)

    try:
        executor = HighQualityExecutorV3(model_name="gemini-2.0-flash-exp")

        test_task = {
            "task_id": "test_structured_ml",
            "task_description": (
                "機械学習パイプラインシステムを実装してください。\n"
                "以下のファイルを作成:\n"
                "- ml_pipeline.py: メインの実装\n"
                "- config.yaml: 設定ファイル\n"
                "- tests/test_pipeline.py: テストコード\n"
                "- README.md: 使用方法\n"
                "最低300行以上、実行可能なコードで。"
            ),
            "required_role": "ml_engineer",
        }

        result = executor.execute_task(**test_task)

        if "structured_output_dir" in result:
            print(f"\n✅ 構造化成果物生成成功!")
            print(f"📁 場所: {result['structured_output_dir']}")
            print(f"📄 ファイル数: {result['file_count']}")

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
