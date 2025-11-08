"""
ExecutionAnalyzer - タスク実行履歴分析エージェント

【Phase 3.3: ExecutionAnalyzer連携】
task_execution_logからパフォーマンス分析を実行
"""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ExecutionAnalyzer:
    """タスク実行履歴分析エージェント"""

    def __init__(self, sheets_manager=None):
        self.sheets_manager = sheets_manager
        logger.info("✅ ExecutionAnalyzer初期化完了")

    def analyze_performance(self, task_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        タスク実行履歴からパフォーマンス分析

        Args:
            task_logs: タスク実行ログのリスト

        Returns:
            パフォーマンス分析結果
        """
        if not task_logs:
            return {
                "overall_success_rate": 0.0,
                "average_response_time": 0.0,
                "total_executions": 0,
                "error_rate": 0.0,
                "by_agent": {},
                "by_task_type": {},
            }

        total = len(task_logs)
        success_count = 0
        failed_count = 0
        total_time = 0.0

        agent_stats = defaultdict(lambda: {"total": 0, "success": 0, "failed": 0})
        task_type_stats = defaultdict(lambda: {"total": 0, "success": 0, "failed": 0})

        for log in task_logs:
            status = log.get("status", "").lower()
            agent_id = log.get("agent_id", "unknown")
            task_type = log.get("task_type", "unknown")

            # 成功/失敗カウント
            if status == "success" or status == "completed":
                success_count += 1
                agent_stats[agent_id]["success"] += 1
                task_type_stats[task_type]["success"] += 1
            elif status == "failed" or status == "error":
                failed_count += 1
                agent_stats[agent_id]["failed"] += 1
                task_type_stats[task_type]["failed"] += 1

            agent_stats[agent_id]["total"] += 1
            task_type_stats[task_type]["total"] += 1

            # 実行時間
            if "execution_time" in log:
                try:
                    total_time += float(log["execution_time"])
                except (ValueError, TypeError):
                    pass

        # 集計
        overall_success_rate = success_count / total if total > 0 else 0.0
        error_rate = failed_count / total if total > 0 else 0.0
        average_response_time = total_time / total if total > 0 else 0.0

        # エージェント別統計
        agent_analysis = {}
        for agent_id, stats in agent_stats.items():
            agent_analysis[agent_id] = {
                "total": stats["total"],
                "success_rate": stats["success"] / stats["total"] if stats["total"] > 0 else 0.0,
                "failed": stats["failed"],
            }

        # タスクタイプ別統計
        task_type_analysis = {}
        for task_type, stats in task_type_stats.items():
            task_type_analysis[task_type] = {
                "total": stats["total"],
                "success_rate": stats["success"] / stats["total"] if stats["total"] > 0 else 0.0,
                "failed": stats["failed"],
            }

        return {
            "overall_success_rate": overall_success_rate,
            "average_response_time": average_response_time,
            "total_executions": total,
            "error_rate": error_rate,
            "success_count": success_count,
            "failed_count": failed_count,
            "by_agent": agent_analysis,
            "by_task_type": task_type_analysis,
            "timestamp": datetime.now().isoformat(),
        }

    def get_recent_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """
        最近N時間の分析結果を取得

        Args:
            hours: 分析対象時間（時間）

        Returns:
            分析結果
        """
        # ダミーデータ（実装時にスプレッドシートから取得）
        dummy_logs = [
            {
                "status": "completed",
                "agent_id": "PMAgent",
                "task_type": "planning",
                "execution_time": 2.5,
            },
            {
                "status": "completed",
                "agent_id": "TaskExecutor",
                "task_type": "execution",
                "execution_time": 5.2,
            },
            {
                "status": "failed",
                "agent_id": "TaskExecutor",
                "task_type": "execution",
                "execution_time": 3.1,
            },
            {
                "status": "completed",
                "agent_id": "ReviewAgent",
                "task_type": "review",
                "execution_time": 1.8,
            },
            {
                "status": "completed",
                "agent_id": "PMAgent",
                "task_type": "planning",
                "execution_time": 2.1,
            },
        ]

        return self.analyze_performance(dummy_logs)


if __name__ == "__main__":
    print("🧪 ExecutionAnalyzer テスト")

    analyzer = ExecutionAnalyzer()
    analysis = analyzer.get_recent_analysis()

    print(f"\n📊 分析結果:")
    print(f"  総実行数: {analysis['total_executions']}件")
    print(f"  成功率: {analysis['overall_success_rate']:.1%}")
    print(f"  エラー率: {analysis['error_rate']:.1%}")
    print(f"  平均応答時間: {analysis['average_response_time']:.2f}秒")

    print(f"\n👥 エージェント別:")
    for agent_id, stats in analysis["by_agent"].items():
        print(f"  {agent_id}: 成功率 {stats['success_rate']:.1%} ({stats['total']}件)")
