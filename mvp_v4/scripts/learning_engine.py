"""
Learning Engine v4.0
実行ログからパターンを抽出して学習
"""

import json
import os
from datetime import datetime
from typing import List, Dict
from collections import defaultdict


class LearningEngine:
    """学習エンジン"""

    def __init__(self, log_dir: str = "mvp_v4/logs"):
        """
        初期化

        Args:
            log_dir: ログディレクトリ
        """
        self.log_dir = log_dir
        self.learned_patterns = []

    def analyze_execution_logs(self, log_file: str) -> Dict:
        """
        実行ログを分析してパターン抽出

        Args:
            log_file: ログファイルパス

        Returns:
            分析結果
        """
        print(f"\n📊 実行ログ分析中: {log_file}")

        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)

        # タスクタイプ別に集計
        task_stats = defaultdict(
            lambda: {
                "total": 0,
                "completed": 0,
                "failed": 0,
                "total_time": 0,
                "retry_count": 0,
                "knowledge_used": 0,
            }
        )

        for log in logs:
            task_type = log.get("task_type", "unknown")
            stats = task_stats[task_type]

            stats["total"] += 1
            if log["status"] == "completed":
                stats["completed"] += 1
            else:
                stats["failed"] += 1

            stats["total_time"] += log.get("elapsed_time", 0)
            stats["retry_count"] += log.get("retry_count", 0)
            if log.get("knowledge_used"):
                stats["knowledge_used"] += 1

        # パターン抽出
        patterns = []
        for task_type, stats in task_stats.items():
            if stats["total"] == 0:
                continue

            success_rate = stats["completed"] / stats["total"]
            avg_time = stats["total_time"] / stats["total"]
            knowledge_effectiveness = (
                (stats["knowledge_used"] / stats["total"]) if stats["total"] > 0 else 0
            )

            pattern = {
                "task_type": task_type,
                "success_rate": round(success_rate, 3),
                "avg_execution_time": round(avg_time, 2),
                "avg_retry_count": round(stats["retry_count"] / stats["total"], 1),
                "knowledge_effectiveness": round(knowledge_effectiveness, 3),
                "sample_count": stats["total"],
                "learned_at": datetime.now().isoformat(),
            }

            patterns.append(pattern)

            print(f"\n✅ パターン抽出: {task_type}")
            print(f"   成功率: {success_rate*100:.1f}%")
            print(f"   平均実行時間: {avg_time:.2f}秒")
            print(f"   ナレッジ有効性: {knowledge_effectiveness*100:.1f}%")

        self.learned_patterns.extend(patterns)

        return {"patterns_count": len(patterns), "patterns": patterns}

    def save_learned_patterns(self, filepath: str = "mvp_v4/knowledge/learned/patterns.json"):
        """学習したパターンを保存"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.learned_patterns, f, indent=2, ensure_ascii=False)

        print(f"\n💾 学習パターン保存: {filepath}")
        print(f"   パターン数: {len(self.learned_patterns)}件")

    def generate_improvement_suggestions(self) -> List[Dict]:
        """改善提案を生成"""
        suggestions = []

        for pattern in self.learned_patterns:
            # 成功率が低い場合
            if pattern["success_rate"] < 0.9:
                suggestions.append(
                    {
                        "task_type": pattern["task_type"],
                        "issue": "成功率が低い",
                        "current_rate": f"{pattern['success_rate']*100:.1f}%",
                        "suggestion": "より詳細なナレッジの追加が必要",
                        "priority": "high",
                    }
                )

            # リトライが多い場合
            if pattern["avg_retry_count"] > 1.0:
                suggestions.append(
                    {
                        "task_type": pattern["task_type"],
                        "issue": "リトライが多い",
                        "current_count": pattern["avg_retry_count"],
                        "suggestion": "エラー修正レシピの改善が必要",
                        "priority": "medium",
                    }
                )

            # ナレッジ有効性が低い場合
            if pattern["knowledge_effectiveness"] < 0.8:
                suggestions.append(
                    {
                        "task_type": pattern["task_type"],
                        "issue": "ナレッジ活用率が低い",
                        "current_rate": f"{pattern['knowledge_effectiveness']*100:.1f}%",
                        "suggestion": "ナレッジ検索精度の改善が必要",
                        "priority": "medium",
                    }
                )

        return suggestions


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧪 Learning Engine テスト")
    print("=" * 70)

    # 学習エンジン初期化
    learner = LearningEngine()

    # ログ分析
    log_file = "mvp_v4/logs/execution/task_log.json"
    if os.path.exists(log_file):
        result = learner.analyze_execution_logs(log_file)

        # パターン保存
        learner.save_learned_patterns()

        # 改善提案
        suggestions = learner.generate_improvement_suggestions()

        if suggestions:
            print("\n" + "=" * 70)
            print("💡 改善提案")
            print("=" * 70)

            for i, suggestion in enumerate(suggestions, 1):
                print(f"\n{i}. タスクタイプ: {suggestion['task_type']}")
                print(f"   問題: {suggestion['issue']}")
                print(f"   提案: {suggestion['suggestion']}")
                print(f"   優先度: {suggestion['priority']}")

        print("\n✅ 学習完了")
    else:
        print(f"⚠️ ログファイルが見つかりません: {log_file}")
        print("   先にタスク実行エンジンを実行してください")
