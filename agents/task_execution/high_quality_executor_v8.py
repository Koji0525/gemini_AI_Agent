"""
高品質エグゼキューターv8.0 - v7.0完全互換版（Gemini API）
v7.0を継承し、反復改良機能を追加

改善:
- v7.0と完全に同じGemini APIを使用
- 既存システムを完全に保護
- 反復改良ロジックのみを追加
"""

import sys
from pathlib import Path
from typing import Dict

# プロジェクトルート追加
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from agents.task_execution.high_quality_executor_v7 import \
    HighQualityExecutorV7
from agents.task_execution.iterative_refinement_engine import \
    IterativeRefinementEngine


class HighQualityExecutorV8(HighQualityExecutorV7):
    """
    高品質エグゼキューターv8.0（v7.0完全互換 - Gemini API）

    v7.0からの改善:
    - ✅ 反復改良エンジン統合（Gemini API使用）
    - ✅ 最大3回の生成で段階的品質向上
    - ✅ フェーズごとの明確な目標設定
    - ✅ 品質スコア85点以上を目指す
    """

    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """初期化（v7.0と同じシグネチャ）"""
        super().__init__(model_name)

        # ✅ 反復改良エンジン（Gemini API使用）
        self.refinement_engine = IterativeRefinementEngine(model_name=model_name)

        print("✅ HighQualityExecutorV8 初期化完了（Gemini API + 反復改良）")

    def execute_task(
        self, task_data: Dict, goal_description: str = "", required_role: str = "general"
    ) -> Dict:
        """
        タスク実行（v8.0: 反復改良版）

        改善点:
        - 最大3回の生成で段階的に品質を向上
        - フェーズ1: 基本構造（骨組み）
        - フェーズ2: 実装詳細化（完全実装）
        - フェーズ3: エッジケース対応（堅牢性）
        """
        print("\n" + "=" * 80)
        print("🚀 v8.0: 反復改良タスク実行（Gemini API）")
        print("=" * 80)

        task_id = task_data.get("task_id", "unknown")
        task_data.get("description", "")
        task_data.get("execution_type", "implementation")

        # ✅ 反復改良実行
        print(f"\n🔄 反復改良開始: 最大3回生成")
        result = self.refinement_engine.execute_with_refinement(
            task_data=task_data, goal_description=goal_description, max_iterations=3
        )

        # ✅ 結果をv7.0形式に変換
        if result["success"]:
            print(f"\n✅ 反復改良完了")
            print(f"  最終品質スコア: {result.get('final_quality_score', 0)}")
            print(f"  生成回数: {result.get('iterations', 0)}回")
            print(f"  出力ファイル: {result.get('output_path', 'なし')}")

            return {
                "success": True,
                "task_id": task_id,
                "output_path": result.get("output_path"),
                "output_summary": result.get("summary", "反復改良により高品質な成果物を生成"),
                "quality_score": result.get("final_quality_score", 0),
                "elapsed_time": result.get("elapsed_time", 0),
                "retry_count": 0,
                "version": "v8.0_iterative_gemini",
            }
        else:
            print(f"\n❌ 反復改良失敗")
            return {
                "success": False,
                "task_id": task_id,
                "error": result.get("error", "不明なエラー"),
                "output_path": None,
                "retry_count": 0,
            }


def main():
    """テスト実行"""
    print("=" * 80)
    print("🧪 HighQualityExecutorV8 テスト（Gemini API + 反復改良）")
    print("=" * 80)

    executor = HighQualityExecutorV8()

    # テストタスク
    test_task = {
        "task_id": "test_v8_gemini_01",
        "description": "Pythonで簡単な計算機クラスを実装する",
        "execution_type": "implementation",
        "priority": "high",
    }

    result = executor.execute_task(test_task, goal_description="高品質な計算機実装")

    print("\n" + "=" * 80)
    print("📊 実行結果:")
    print("=" * 80)
    print(f"成功: {result['success']}")
    print(f"タスクID: {result['task_id']}")
    print(f"品質スコア: {result.get('quality_score', 0)}")
    print(f"出力パス: {result.get('output_path', 'なし')}")
    print("=" * 80)


if __name__ == "__main__":
    main()
