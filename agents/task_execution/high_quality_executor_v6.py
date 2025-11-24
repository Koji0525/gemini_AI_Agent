"""
高品質タスク実行エンジン v6.0 (最終版)
機能完全性保証版

改善点:
- 各ファイルの最低文字数を強制
- 機能完全性チェック
- タスク要件のカバー率検証
- 不合格時の詳細なリトライ
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from agents.task_execution.completeness_checker import CompletenessChecker
from agents.task_execution.high_quality_executor_v5 import \
    HighQualityExecutorV5


class HighQualityExecutorV6(HighQualityExecutorV5):
    """
    高品質タスク実行エンジン v6.0 (最終版)

    追加機能:
    - 機能完全性チェック
    - タスク達成度の検証
    - より厳格な品質基準
    """

    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """初期化"""
        super().__init__(model_name)

        # 完全性チェッカー追加
        self.completeness_checker = CompletenessChecker()

        print(f"🔍 機能完全性チェック: 有効")

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
        """タスク実行（機能完全性保証版）"""

        # v5の実行
        result = super().execute_task(
            task_id,
            task_description,
            required_role,
            dependencies,
            context,
            retry_count,
            max_retries,
        )

        # 機能完全性チェック
        if result["status"] == "success" and "structured_files" in result:
            # ファイル内容を読み込み
            structured_dir = Path(result["structured_output_dir"])
            files_content = {}

            for filename in result["structured_files"]:
                if filename != "_manifest.json":
                    file_path = structured_dir / filename
                    if file_path.exists():
                        with open(file_path, "r", encoding="utf-8") as f:
                            files_content[filename] = f.read()

            # 完全性チェック
            completeness = self.completeness_checker.check_completeness(
                files_content, task_description
            )

            result["completeness"] = completeness
            result["final_quality_score"] = min(
                result["quality_score"], completeness["quality_score"]
            )

            # 不合格時のリトライ判定
            if not completeness["is_complete"] and retry_count < max_retries:
                print(f"\n⚠️  機能完全性不足 (スコア: {completeness['quality_score']}/100)")
                print(f"🔄 リトライ: {retry_count + 1}/{max_retries}")

                import time

                time.sleep(2)

                return self.execute_task(
                    task_id,
                    task_description,
                    required_role,
                    dependencies,
                    context,
                    retry_count + 1,
                    max_retries,
                )

        return result

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
        """プロンプト生成（v6版・機能完全性重視）"""

        prompt_parts = [
            "# タスク実行プロンプト（機能完全性保証版 v6.0）",
            "",
            "## 🎯 成果物要件（厳格）",
            "",
            "### 数量要件:",
            f"- **最低{minimum_files}個のファイル**",
            "- **各ファイル最低50行以上**（設定ファイル除く）",
            "- **各Pythonファイル最低1000文字以上**",
            "",
            "### 品質要件:",
            "- **完全に動作する実装**（TODO、実装予定は禁止）",
            "- **詳細なドックストリング**（Google形式）",
            "- **エラーハンドリング完備**",
            "- **実用的な実装例**",
            "",
            "### 必須ファイル:",
            "1. **メイン実装** (最低100行、詳細なロジック)",
            "2. **サブモジュール** (機能ごとに分割)",
            "3. **テストコード** (pytest形式、最低30行)",
            "4. **設定ファイル** (yaml/json)",
            "5. **README.md** (詳細な使用方法)",
            "",
            f"## 📋 タスク内容",
            task_description,
            "",
            f"## 👤 ロール: {required_role}",
            "",
            "## 📝 期待されるファイル構成:",
        ]

        for i, filename in enumerate(expected_files, 1):
            prompt_parts.append(f"{i}. `{filename}` - 最低50行以上の実装")

        prompt_parts.extend(
            [
                "",
                "## 📤 出力形式（厳守）:",
                "各ファイルは以下の形式で記述:",
                "",
                "```",
                "## ファイル: example.py",
                "",
                "```python",
                '"""',
                "詳細なモジュール説明",
                "",
                "このモジュールは...",
                "",
                "使用例:",
                "    >>> from example import ExampleClass",
                "    >>> obj = ExampleClass()",
                '"""',
                "",
                "import logging",
                "from typing import Dict, List, Optional",
                "",
                "logger = logging.getLogger(__name__)",
                "",
                "",
                "class ExampleClass:",
                '    """',
                "    クラスの詳細説明",
                "    ",
                "    Args:",
                "        param1: パラメータ1の説明",
                "    ",
                "    Attributes:",
                "        attr1: 属性1の説明",
                '    """',
                "    ",
                "    def __init__(self, param1: str):",
                "        self.attr1 = param1",
                "    ",
                "    def method1(self) -> Dict:",
                '        """メソッドの説明"""',
                "        try:",
                "            # 実装",
                "            result = {}",
                "            return result",
                "        except Exception as e:",
                "            logger.error(f'エラー: {e}')",
                "            raise",
                "```",
                "```",
                "",
                "## ⚠️ 禁止事項:",
                "- 各ファイル50行未満は**絶対NG**",
                "- TODO、実装予定のコメントは**NG**",
                "- 説明だけで実装がないのは**NG**",
                "- エラーハンドリングがないのは**NG**",
                "",
                "## 🚀 実装開始",
                "上記の要件を満たす、完全に動作する実装を生成してください。",
                "**各ファイル最低50行、メイン実装は最低100行が必須です。**",
            ]
        )

        return "\n".join(prompt_parts)


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 v6.0 テスト（機能完全性保証版）")
    print("=" * 60)

    try:
        executor = HighQualityExecutorV6()

        result = executor.execute_task(
            task_id="test_v6_complete",
            task_description=(
                "既存システムの依存関係分析システムを実装。\n"
                "機能:\n"
                "- Pythonファイルのimport文解析\n"
                "- 依存関係グラフの生成\n"
                "- 影響範囲の自動計算\n"
                "- 結果のビジュアライゼーション\n"
                "- 設定ファイル対応\n"
                "- テストカバレッジ80%以上"
            ),
            required_role="engineer",
        )

        print(f"\n{'='*60}")
        print(f"📊 最終結果")
        print(f"{'='*60}")
        print(f"ファイル数: {result.get('file_count', 0)}")
        print(f"品質スコア: {result.get('quality_score', 0)}/100")

        if "completeness" in result:
            comp = result["completeness"]
            print(f"\n機能完全性:")
            print(f"  総合スコア: {comp['quality_score']}/100")
            print(f"  メイン実装: {'✅' if comp['has_main'] else '❌'}")
            print(f"  テスト: {'✅' if comp['has_test'] else '❌'}")
            print(f"  設定: {'✅' if comp['has_config'] else '❌'}")
            print(f"  README: {'✅' if comp['has_readme'] else '❌'}")
            print(f"  タスクカバー率: {comp['task_coverage']*100:.0f}%")
            print(f"  平均ファイルサイズ: {comp['avg_file_size']:.0f}文字")

        print(f"{'='*60}")

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
