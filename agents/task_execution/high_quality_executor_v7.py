"""
高品質タスク実行エンジン v7.0 (安定版)
日本語対応 + ゴミファイル除去 + 現実的な基準
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from agents.task_execution.completeness_checker_v2 import CompletenessCheckerV2
from agents.task_execution.high_quality_executor_v5 import \
    HighQualityExecutorV5
from agents.task_execution.structured_output_engine_v3 import \
    StructuredOutputEngineV3


class HighQualityExecutorV7(HighQualityExecutorV5):
    """
    高品質タスク実行エンジン v7.0 (安定版)

    改善点:
    - ゴミファイル除去
    - 日本語README自動生成
    - 現実的な品質基準
    - 安定した高スコア
    """

    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """初期化"""
        super(HighQualityExecutorV5, self).__init__(model_name)

        # v3エンジン（安定版）
        self.structured_engine = StructuredOutputEngineV3(
            base_output_dir=project_root / "agent_outputs" / "structured"
        )

        # v2チェッカー（緩和版）
        self.completeness_checker = CompletenessCheckerV2()

        # タスク具体化
        from agents.task_execution.task_clarifier import TaskClarifier

        self.clarifier = TaskClarifier()

        print(f"📁 構造化成果物: {self.structured_engine.base_output_dir}")
        print(f"🎯 タスク具体化: 有効")
        print(f"🔍 品質基準: 現実的（安定版）")
        print(f"🇯🇵 README: 日本語自動生成")
        print(f"🗑️  ゴミファイル: 自動除去")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 v7.0 (安定版) テスト")
    print("=" * 60)

    try:
        executor = HighQualityExecutorV7()

        result = executor.execute_task(
            task_id="test_v7_stable",
            task_description="既存システム分析ツールを実装",
            required_role="engineer",
        )

        print(f"\n{'='*60}")
        print(f"📊 最終結果")
        print(f"{'='*60}")
        print(f"ファイル数: {result.get('file_count', 0)}")
        print(f"品質スコア: {result.get('quality_score', 0)}/100")

        if "completeness" in result:
            comp = result["completeness"]
            print(f"\n機能完全性: {comp['quality_score']}/100")
            print(f"  問題点: {len(comp['issues'])}件")

        print(f"{'='*60}")

    except Exception as e:
        print(f"\n❌ エラー: {e}")
