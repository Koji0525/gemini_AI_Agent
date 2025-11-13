"""
TaskExecutionFlow（品質評価統合版）
"""

import os
import sys

project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.autonomous_engine import AutonomousEngine


class TaskExecutionFlow:
    """タスク実行フロー管理（品質評価統合版）"""

    def __init__(self):
        """初期化"""
        self.engine = AutonomousEngine()
        print("✅ TaskExecutionFlow 初期化完了")

    def run(self, max_tasks: int = 3):
        """実行"""
        return self.engine.auto_execute(max_tasks)


def main():
    """メイン実行"""
    flow = TaskExecutionFlow()
    result = flow.run(max_tasks=3)

    print(f"\n{'='*80}")
    print(f"📊 最終結果")
    print(f"{'='*80}")
    print(f"成功: {result.get('success')}")
    print(f"実行タスク数: {result.get('executed_count', 0)}")
    print(f"成功タスク数: {result.get('success_count', 0)}")
    print(f"平均品質スコア: {result.get('average_quality', 0):.1f}/100")


if __name__ == "__main__":
    main()
