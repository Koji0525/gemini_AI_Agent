"""人間連携エージェント（F9）

人間との連携を管理します。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from typing import Any, Dict


class HumanCollaborationAgent:
    """人間連携エージェント"""

    def __init__(self):
        """初期化"""
        self.questions = []
        self.reports = []
        print("✅ HumanCollaborationAgent 初期化完了")

    def detect_uncertainty(self, task: Dict[str, Any]) -> bool:
        """不明点検出

        Args:
            task: タスク

        Returns:
            不明点があればTrue
        """
        # 簡易実装：複雑なタスクは不明点ありと判定
        description = task.get("description", "")

        if len(description) > 200:
            return True
        if "?" in description:
            return True

        return False

    def generate_question(self, task: Dict[str, Any]) -> str:
        """質問生成

        Args:
            task: タスク

        Returns:
            質問文
        """
        task_id = task.get("task_id", "UNKNOWN")
        description = task.get("description", "")[:100]

        question = f"タスク{task_id}について：{description}... の実装方針を確認したいです。"

        self.questions.append(
            {
                "task_id": task_id,
                "question": question,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "answered": False,
            }
        )

        print(f"❓ 質問生成: {question[:80]}...")
        return question

    def send_progress_report(self, stats: Dict[str, Any]) -> bool:
        """進捗報告送信

        Args:
            stats: 統計情報

        Returns:
            送信成功したらTrue
        """
        try:
            report = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_tasks": stats.get("total_tasks", 0),
                "completed_tasks": stats.get("completed_tasks", 0),
                "pending_tasks": stats.get("pending_tasks", 0),
                "avg_quality": stats.get("avg_quality", 0),
            }

            self.reports.append(report)

            print(f"📊 進捗報告:")
            print(f"  完了: {report['completed_tasks']}/{report['total_tasks']}タスク")
            print(f"  平均品質: {report['avg_quality']:.1f}/10")

            return True

        except Exception as e:
            print(f"❌ 報告送信エラー: {e}")
            return False


if __name__ == "__main__":
    agent = HumanCollaborationAgent()

    # テスト
    test_task = {"task_id": "test_001", "description": "複雑なタスクの説明が長い" * 20}

    if agent.detect_uncertainty(test_task):
        question = agent.generate_question(test_task)

    stats = {"total_tasks": 103, "completed_tasks": 95, "pending_tasks": 8, "avg_quality": 8.5}
    agent.send_progress_report(stats)
