"""
反復改良エンジン v4.1 - StructuredOutputEngine統合版（修正版）
StructuredOutputEngineV3の正しいメソッド名を使用
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Optional

# プロジェクトルート追加
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# ✅ v7.0と同じインポート
import google.generativeai as genai
from dotenv import load_dotenv

# ✅ v7.0のStructuredOutputEngineを使用
from agents.task_execution.structured_output_engine_v3 import \
    StructuredOutputEngineV3


class IterativeRefinementEngineV2:
    """反復改良エンジン v4.1（StructuredOutputEngine統合版・修正版）"""

    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """初期化"""
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

        # ✅ v7.0のStructuredOutputEngineを使用
        self.structured_engine = StructuredOutputEngineV3(
            base_output_dir=project_root / "agent_outputs" / "structured"
        )

        # フェーズ定義
        self.phases = {
            1: {
                "name": "基本構造",
                "goal": "5ファイル以上の骨組みを生成",
                "target_files": 5,
                "target_length_per_file": 500,
                "focus": "主要モジュール・クラス構造",
            },
            2: {
                "name": "実装詳細化",
                "goal": "各ファイルの完全な実装",
                "target_files": 5,
                "target_length_per_file": 1000,
                "focus": "詳細なロジック、ドキュメント、テスト",
            },
            3: {
                "name": "エッジケース対応",
                "goal": "堅牢性の向上と追加ファイル",
                "target_files": 7,
                "target_length_per_file": 1500,
                "focus": "エラーハンドリング、バリデーション、統合テスト",
            },
        }

        print(f"✅ IterativeRefinementEngineV2 初期化完了（v4.1修正版）")

    def execute_with_refinement(
        self, task_data: Dict, goal_description: str = "", max_iterations: int = 3
    ) -> Dict:
        """反復改良実行"""
        start_time = time.time()

        task_id = task_data.get("task_id", "unknown")
        task_data.get("description", "")

        print(f"\n�� 反復改良開始: {task_id}")
        print(f"  最大反復回数: {max_iterations}")

        current_output_dir = None
        iteration_results = []
        quality_score = 0

        for iteration in range(1, max_iterations + 1):
            phase_info = self.phases.get(iteration, self.phases[3])

            print(f"\n{'='*60}")
            print(f"フェーズ{iteration}: {phase_info['name']}")
            print(f"{'='*60}")

            # 生成実行
            result = self._generate_phase_structured(
                task_data=task_data,
                goal_description=goal_description,
                phase=iteration,
                previous_output_dir=current_output_dir,
            )

            if not result["success"]:
                print(f"❌ フェーズ{iteration}失敗: {result.get('error')}")
                continue

            current_output_dir = result["output_dir"]
            iteration_results.append(result)

            # 品質評価
            quality_score = result.get("quality_score", 0)
            print(f"  品質スコア: {quality_score}/100")
            print(f"  生成ファイル数: {result.get('file_count', 0)}ファイル")

            if quality_score >= 85:
                print(f"✅ 目標品質達成！ フェーズ{iteration}で完了")
                break

        elapsed_time = time.time() - start_time

        if iteration_results:
            final_result = iteration_results[-1]
            return {
                "success": True,
                "output_path": final_result.get("output_dir"),
                "file_count": final_result.get("file_count", 0),
                "final_quality_score": quality_score,
                "iterations": len(iteration_results),
                "elapsed_time": elapsed_time,
                "summary": f'{len(iteration_results)}回の反復改良で{final_result.get("file_count", 0)}ファイル生成',
                "error": None,
            }
        else:
            return {"success": False, "error": "全フェーズ失敗", "iterations": 0}

    def _generate_phase_structured(
        self, task_data: Dict, goal_description: str, phase: int, previous_output_dir: Optional[str]
    ) -> Dict:
        """フェーズごとの生成"""
        phase_info = self.phases.get(phase, self.phases[3])

        # プロンプト作成
        prompt = self._create_prompt(task_data, goal_description, phase_info, phase)

        try:
            print(f"  📡 Gemini API呼び出し中...")
            response = self.model.generate_content(prompt)
            content = response.text
            print(f"  ✅ 生成完了: {len(content)}文字")

            # ✅ v7.0と同じパターンで保存
            task_id = f"{task_data.get('task_id', 'unknown')}_iter{phase}"

            # StructuredOutputEngineV3の正しいメソッド: generate_structured_output
            result = self.structured_engine.generate_structured_output(
                raw_content=content, task_id=task_id
            )

            print(f"  📁 構造化完了: {result.get('file_count', 0)}ファイル")

            return {
                "success": True,
                "output_dir": result.get("output_dir"),
                "file_count": result.get("file_count", 0),
                "quality_score": self._evaluate_quality(result),
                "phase": phase,
                "error": None,
            }

        except Exception as e:
            print(f"  ❌ エラー: {e}")
            import traceback

            traceback.print_exc()
            return {
                "success": False,
                "output_dir": None,
                "file_count": 0,
                "quality_score": 0,
                "phase": phase,
                "error": str(e),
            }

    def _create_prompt(
        self, task_data: Dict, goal_description: str, phase_info: Dict, phase: int
    ) -> str:
        """プロンプト作成"""
        description = task_data.get("description", "")

        return f"""# フェーズ{phase}: {phase_info['name']}

## タスク
{description}

## 目標
- {phase_info['target_files']}ファイル以上
- 各ファイル{phase_info['target_length_per_file']}文字以上
- {phase_info['focus']}

## 出力形式（重要！）
以下の形式で複数ファイルを出力:
```
# ファイル: main.py
<内容>

# ファイル: core.py
<内容>

# ファイル: utils.py
<内容>

# ファイル: config.py
<内容>

# ファイル: README.md
<内容>
```

**注意**: 必ず5ファイル以上、各500文字以上で出力すること。
"""

    def _evaluate_quality(self, result: Dict) -> int:
        """品質評価"""
        file_count = result.get("file_count", 0)
        if file_count >= 5:
            return 90
        elif file_count >= 3:
            return 70
        else:
            return 50


def test_engine():
    """テスト実行"""
    print("=" * 80)
    print("🧪 IterativeRefinementEngineV2 テスト（v4.1修正版）")
    print("=" * 80)

    engine = IterativeRefinementEngineV2()

    test_task = {
        "task_id": "test_iter_v41_01",
        "description": "Pythonで計算機アプリを実装（四則演算・履歴・設定）",
    }

    result = engine.execute_with_refinement(
        task_data=test_task,
        goal_description="高品質なモジュール構造",
        max_iterations=2,  # まず2回でテスト
    )

    print("\n" + "=" * 80)
    print("📊 テスト結果:")
    print("=" * 80)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_engine()
