"""自己進化エージェント（F8）

成功パターンを学習し、システムを進化させます。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from typing import Any, Dict


class SelfEvolutionAgent:
    """自己進化エージェント"""

    def __init__(self):
        """初期化"""
        self.success_patterns = []
        self.failure_patterns = []
        self.performance_history = []
        print("✅ SelfEvolutionAgent 初期化完了")

    def learn_from_success(self, task: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """成功パターンの学習

        Args:
            task: 成功したタスク
            result: 実行結果

        Returns:
            学習成功したらTrue
        """
        try:
            quality_score = result.get("quality_score", 0)

            # 高品質（8点以上）の場合のみ学習
            if quality_score >= 8.0:
                pattern = {
                    "task_type": task.get("execution_type", ""),
                    "description_length": len(task.get("description", "")),
                    "quality_score": quality_score,
                    "elapsed_time": result.get("elapsed_time", 0),
                    "knowledge_used": result.get("knowledge_used", 0),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

                self.success_patterns.append(pattern)
                print(f"✅ 成功パターン学習: スコア{quality_score}")
                return True

            return False

        except Exception as e:
            print(f"❌ 学習エラー: {e}")
            return False

    def learn_from_failure(self, task: Dict[str, Any], error: Exception) -> bool:
        """失敗パターンの学習

        Args:
            task: 失敗したタスク
            error: 発生したエラー

        Returns:
            学習成功したらTrue
        """
        try:
            pattern = {
                "task_type": task.get("execution_type", ""),
                "error_type": type(error).__name__,
                "error_message": str(error)[:200],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            self.failure_patterns.append(pattern)
            print(f"✅ 失敗パターン学習: {pattern['error_type']}")
            return True

        except Exception as e:
            print(f"❌ 学習エラー: {e}")
            return False

    def optimize_performance(self) -> Dict[str, Any]:
        """パフォーマンス最適化

        Returns:
            最適化結果
        """
        if not self.success_patterns:
            return {"optimized": False, "reason": "データ不足"}

        # 平均品質スコア算出
        avg_quality = sum(p["quality_score"] for p in self.success_patterns) / len(
            self.success_patterns
        )

        # 平均実行時間算出
        avg_time = sum(p["elapsed_time"] for p in self.success_patterns) / len(
            self.success_patterns
        )

        print(f"📊 平均品質: {avg_quality:.1f}, 平均時間: {avg_time:.2f}秒")

        return {
            "optimized": True,
            "avg_quality": avg_quality,
            "avg_time": avg_time,
            "patterns_learned": len(self.success_patterns),
        }


if __name__ == "__main__":
    agent = SelfEvolutionAgent()

    # テスト
    test_task = {"task_id": "test_001", "execution_type": "test"}
    test_result = {"quality_score": 9.0, "elapsed_time": 1.5, "knowledge_used": 3}

    agent.learn_from_success(test_task, test_result)
    result = agent.optimize_performance()
    print(f"\n最適化結果: {result}")
