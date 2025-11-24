"""
高品質タスク実行エンジン v5.0
確実に5ファイル以上生成版
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from agents.task_execution.high_quality_executor_v3 import \
    HighQualityExecutorV3
from agents.task_execution.structured_output_engine_v2 import \
    StructuredOutputEngineV2
from agents.task_execution.task_clarifier import TaskClarifier


class HighQualityExecutorV5(HighQualityExecutorV3):
    """
    高品質タスク実行エンジン v5.0

    改善点:
    - 改良版構造化エンジン使用
    - デフォルトファイルで補完
    - 確実に5ファイル以上
    """

    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """初期化"""
        # 親クラスの初期化（v3）
        super(HighQualityExecutorV3, self).__init__(model_name)

        # v2の構造化エンジンに置き換え
        self.structured_engine = StructuredOutputEngineV2(
            base_output_dir=project_root / "agent_outputs" / "structured"
        )

        # タスク具体化エンジン追加
        self.clarifier = TaskClarifier()

        print(f"📁 構造化成果物: {self.structured_engine.base_output_dir}")
        print(f"🎯 タスク具体化: 有効")
        print(f"🔧 最低ファイル数: 5個（自動補完）")

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
        """タスク実行（v5版）"""

        # タスク具体化
        clarified = self.clarifier.clarify(task_description, required_role)

        print(f"\n🎯 タスク具体化:")
        print(f"  タイプ: {clarified['task_type']}")
        print(f"  期待ファイル数: {clarified['minimum_files']}")

        # v3の実行（プロンプト生成はv3のまま）
        result = HighQualityExecutorV3.execute_task(
            self,
            task_id=task_id,
            task_description=clarified["clarified_description"],
            required_role=required_role,
            dependencies=dependencies,
            context={
                **(context or {}),
                "expected_files": clarified["expected_files"],
                "minimum_files": clarified["minimum_files"],
            },
            retry_count=retry_count,
            max_retries=max_retries,
        )

        return result

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
        """タスク実行（改良版構造化対応）"""

        # タスク具体化
        clarified = self.clarifier.clarify(task_description, required_role)
        minimum_files = clarified["minimum_files"]

        print(f"\n🎯 タスク具体化:")
        print(f"  タイプ: {clarified['task_type']}")
        print(f"  最低ファイル数: {minimum_files}")

        # v2の実行（元の処理）
        self.stats["total_executions"] += 1
        from datetime import datetime

        start_time = datetime.now()

        print(f"\n{'='*60}")
        print(f"🚀 タスク実行: {task_id}")
        print(f"{'='*60}")
        print(f"�� リトライ: {retry_count}/{max_retries}")

        try:
            # 依存タスク読み込み
            dep_context = self._load_dependency_outputs(dependencies) if dependencies else {}

            # ナレッジ検索
            knowledge_context = self._search_knowledge(clarified["clarified_description"])

            # プロンプト生成（v4のロジック使用）
            prompt = self._build_high_quality_prompt_v5(
                clarified["clarified_description"],
                required_role,
                dep_context,
                knowledge_context,
                context,
                clarified["expected_files"],
                minimum_files,
            )

            # Gemini実行
            result = self._execute_with_gemini(prompt, task_id)

            # 品質評価
            quality = self._evaluate_quality(result)

            # 構造化（v2エンジン使用・最低ファイル数保証）
            markdown_file = Path(result["file_path"])
            with open(markdown_file, "r", encoding="utf-8") as f:
                markdown_text = f.read()

            # ファイル抽出（minimum_files保証）
            files = self.structured_engine.extract_files_from_markdown(
                markdown_text, task_id, minimum_files=minimum_files
            )

            # 構造化保存
            structured_dir = self.structured_engine.save_structured_output(files, task_id)

            # 統計更新
            self._update_stats(quality)

            # 結果返却
            elapsed = (datetime.now() - start_time).total_seconds()

            return {
                "status": "success",
                "output_file": str(result["file_path"]),
                "output_summary": result["summary"],
                "quality_score": quality["score"],
                "size_bytes": quality["size_bytes"],
                "line_count": quality["line_count"],
                "elapsed_time": elapsed,
                "retry_count": retry_count,
                "structured_output_dir": str(structured_dir),
                "structured_files": list(files.keys()),
                "file_count": len(files),
                "quality_details": quality,
            }

        except Exception as e:
            print(f"\n❌ エラー: {e}")
            import traceback

            traceback.print_exc()

            from datetime import datetime

            elapsed = (datetime.now() - start_time).total_seconds()
            return {
                "status": "failed",
                "error": str(e),
                "elapsed_time": elapsed,
                "retry_count": retry_count,
                "quality_score": 0,
                "file_count": 0,
            }

    def _build_high_quality_prompt_v5(
        self,
        task_description,
        required_role,
        dep_context,
        knowledge_context,
        context,
        expected_files,
        minimum_files,
    ):
        """プロンプト生成（v5版・より明確）"""

        prompt_parts = [
            "# タスク実行（確実な複数ファイル生成版）",
            "",
            "## 🎯 絶対条件",
            f"**{minimum_files}個以上のファイルを生成してください（必須）**",
            "",
            "### 各ファイルは以下の形式で記述:",
            "```",
            "## ファイル: ファイル名.py",
            "",
            "```python",
            "コード内容",
            "```",
            "```",
            "",
            f"## 📋 タスク: {task_description}",
            "",
            "## 📄 生成すべきファイル例:",
        ]

        for i, filename in enumerate(expected_files, 1):
            prompt_parts.append(f"{i}. {filename}")

        prompt_parts.extend(
            [
                "",
                "## 🚀 重要:",
                f"- **{minimum_files}個のファイルは絶対に生成**",
                "- 各ファイルは「## ファイル: xxx」で明記",
                "- テストファイルも必須",
                "- 設定ファイルも必須",
                "",
                "開始してください。",
            ]
        )

        return "\n".join(prompt_parts)


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 v5.0 テスト（確実に5ファイル以上）")
    print("=" * 60)

    try:
        executor = HighQualityExecutorV5()

        result = executor.execute_task(
            task_id="test_v5", task_description="既存システム分析を実装", required_role="engineer"
        )

        print(f"\n📊 最終結果:")
        print(f"  ファイル数: {result.get('file_count', 0)}")
        print(f"  品質スコア: {result.get('quality_score', 0)}/100")

    except Exception as e:
        print(f"\n❌ エラー: {e}")
