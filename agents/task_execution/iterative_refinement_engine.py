"""
反復改良エンジン v3.0 - v7.0完全互換版（Gemini API使用）
v7.0と同じGemini APIを使用して反復改良を実現

設計方針:
- v7.0と同じGemini API (google.generativeai) を使用
- 既存システムを完全に保護
- 反復改良ロジックのみを追加
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict

# プロジェクトルート追加
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# ✅ v7.0と同じインポート
import google.generativeai as genai
from dotenv import load_dotenv


class IterativeRefinementEngine:
    """反復改良エンジン（v7.0完全互換 - Gemini API）"""

    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """
        初期化（v7.0と同じパターン）

        Args:
            model_name: Geminiモデル名
        """
        # ✅ v7.0と同じAPI初期化
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

        # フェーズ定義
        self.phases = {
            1: {
                "name": "基本構造",
                "goal": "骨組みとなるコード構造を生成",
                "target_length": 1500,
                "focus": "主要クラス・関数の定義",
            },
            2: {
                "name": "実装詳細化",
                "goal": "各機能の完全な実装",
                "target_length": 2500,
                "focus": "詳細なロジック、ドキュメント",
            },
            3: {
                "name": "エッジケース対応",
                "goal": "堅牢性の向上",
                "target_length": 3500,
                "focus": "エラーハンドリング、バリデーション",
            },
        }

        print(f"✅ IterativeRefinementEngine 初期化完了（Gemini API: {model_name}）")

    def execute_with_refinement(
        self, task_data: Dict, goal_description: str = "", max_iterations: int = 3
    ) -> Dict:
        """
        反復改良実行

        Returns:
            Dict: 実行結果
        """
        start_time = time.time()

        task_id = task_data.get("task_id", "unknown")
        description = task_data.get("description", "")

        print(f"\n🔄 反復改良開始: {task_id}")
        print(f"  目標: {description}")
        print(f"  最大反復回数: {max_iterations}")

        current_content = ""
        iteration_results = []
        quality_score = 0

        for iteration in range(1, max_iterations + 1):
            phase_info = self.phases.get(iteration, self.phases[3])

            print(f"\n{'='*60}")
            print(f"フェーズ{iteration}: {phase_info['name']}")
            print(f"{'='*60}")
            print(f"目標: {phase_info['goal']}")
            print(f"焦点: {phase_info['focus']}")

            # 生成実行
            result = self._generate_phase(
                task_data=task_data,
                goal_description=goal_description,
                phase=iteration,
                previous_content=current_content,
            )

            if not result["success"]:
                print(f"❌ フェーズ{iteration}失敗")
                continue

            current_content = result["content"]
            iteration_results.append(result)

            # 品質評価
            quality_score = self._evaluate_quality(current_content, phase_info)
            print(f"  品質スコア: {quality_score}/100")

            # 85点以上で早期終了
            if quality_score >= 85:
                print(f"✅ 目標品質達成！ フェーズ{iteration}で完了")
                break

        # 最終成果物を保存
        output_path = self._save_final_output(
            task_id=task_id, content=current_content, iterations=len(iteration_results)
        )

        elapsed_time = time.time() - start_time

        return {
            "success": True,
            "output_path": output_path,
            "final_quality_score": quality_score,
            "iterations": len(iteration_results),
            "elapsed_time": elapsed_time,
            "summary": f"{len(iteration_results)}回の反復改良で品質スコア{quality_score}を達成",
            "error": None,
        }

    def _generate_phase(
        self, task_data: Dict, goal_description: str, phase: int, previous_content: str
    ) -> Dict:
        """フェーズごとの生成（v7.0と同じGemini API呼び出し）"""
        phase_info = self.phases.get(phase, self.phases[3])

        # プロンプト作成
        if phase == 1:
            prompt = self._create_initial_prompt(task_data, goal_description, phase_info)
        else:
            prompt = self._create_refinement_prompt(
                task_data, goal_description, phase_info, previous_content
            )

        # ✅ v7.0と同じGemini API呼び出しパターン
        try:
            print(f"  📡 Gemini API呼び出し中（v7.0と同じパターン）...")

            response = self.model.generate_content(prompt)
            content = response.text

            print(f"  ✅ 生成完了: {len(content)}文字")

            return {"success": True, "content": content, "phase": phase, "error": None}

        except Exception as e:
            print(f"  ❌ 例外発生: {e}")
            return {"success": False, "content": previous_content, "phase": phase, "error": str(e)}

    def _create_initial_prompt(
        self, task_data: Dict, goal_description: str, phase_info: Dict
    ) -> str:
        """初回プロンプト作成"""
        description = task_data.get("description", "")

        return f"""# フェーズ1: {phase_info['name']}

## タスク概要
- タスクID: {task_data.get('task_id', 'unknown')}
- 説明: {description}
- ゴール: {goal_description}

## このフェーズの目標
{phase_info['goal']}

## 焦点
{phase_info['focus']}

## 要件
1. {description}を実装するPythonコードを生成
2. 基本的なクラス構造・関数定義を含める
3. 主要な機能の骨組みを作る
4. ドキュメント文字列（Googleスタイル）を含める
5. 目標文字数: {phase_info['target_length']}文字以上

## 出力形式
- Pythonコードのみを出力
- コードブロック（```python）は不要
- 実行可能なコードであること
"""

    def _create_refinement_prompt(
        self, task_data: Dict, goal_description: str, phase_info: Dict, previous_content: str
    ) -> str:
        """改良プロンプト作成"""
        return f"""# フェーズ{phase_info.get('phase', 2)}: {phase_info['name']}

## 前回の成果物
```python
{previous_content}
```

## このフェーズの目標
{phase_info['goal']}

## 焦点
{phase_info['focus']}

## 改良要件
1. 前回のコードをベースに**大幅に拡張**
2. {phase_info['focus']}に重点を置く
3. コメント・ドキュメント（Googleスタイル）を充実させる
4. 目標文字数: {phase_info['target_length']}文字以上
5. **前回より必ず長く、詳細に**

## 出力形式
- 改良後の完全なPythonコード
- コードブロック（```python）は不要
- 実行可能なコードであること
"""

    def _evaluate_quality(self, content: str, phase_info: Dict) -> int:
        """品質評価"""
        score = 0

        # 長さ評価（40点）
        length = len(content)
        target = phase_info["target_length"]

        if length >= target:
            score += 40
        else:
            score += int(40 * (length / target))

        # 構造評価（30点）
        has_class = "class " in content
        has_function = "def " in content
        has_docstring = '"""' in content or "'''" in content

        if has_class:
            score += 10
        if has_function:
            score += 10
        if has_docstring:
            score += 10

        # コメント評価（15点）
        comment_count = content.count("#")
        score += min(15, comment_count)

        # エラーハンドリング評価（15点）
        has_try = "try:" in content
        has_except = "except" in content
        has_validation = "if not" in content or "assert" in content

        if has_try and has_except:
            score += 8
        if has_validation:
            score += 7

        return min(100, score)

    def _save_final_output(self, task_id: str, content: str, iterations: int) -> str:
        """最終成果物を保存"""
        output_dir = Path("/workspaces/gemini_AI_Agent/agent_outputs/implementation")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{task_id}_v8_iter{iterations}.py"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"\n💾 最終成果物保存: {output_path}")

        return str(output_path)


def test_engine():
    """テスト実行"""
    print("=" * 80)
    print("🧪 IterativeRefinementEngine テスト（Gemini API）")
    print("=" * 80)

    engine = IterativeRefinementEngine()

    test_task = {
        "task_id": "test_engine_gemini_01",
        "description": "Pythonで四則演算ができる計算機クラスを実装",
    }

    result = engine.execute_with_refinement(
        task_data=test_task, goal_description="シンプルで使いやすい計算機", max_iterations=3
    )

    print("\n" + "=" * 80)
    print("📊 テスト結果:")
    print("=" * 80)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_engine()
