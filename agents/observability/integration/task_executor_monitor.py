"""
TaskExecutorMonitor - TaskExecutor連携監視

【Phase 3.2: TaskExecutor連携の拡張】
実行時間計測、品質スコア、エラートレース、リトライの可視化
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.observability.observability_manager import \
    get_observability_manager


class TaskExecutorMonitor:
    """TaskExecutor連携監視"""

    def __init__(self, task_executor=None):
        self.task_executor = task_executor
        self.obs_manager = get_observability_manager()
        print("✅ TaskExecutorMonitor初期化完了")

    def measure_execution_details(self, task_id: str) -> Dict[str, Any]:
        """
        実行時間を詳細計測

        Args:
            task_id: タスクID

        Returns:
            実行時間の詳細情報
        """
        try:
            datetime.now()

            # 各ステップの実行時間を計測（模擬）
            steps = [
                ("preparation", 50),
                ("execution", 200),
                ("validation", 100),
                ("completion", 30),
            ]

            step_details = []
            for step_name, duration_ms in steps:
                step_details.append(
                    {
                        "step": step_name,
                        "duration_ms": duration_ms,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                # 各ステップでトレース記録
                self.obs_manager.record_trace(
                    {
                        "trace_id": f"task-{task_id}-{step_name}",
                        "operation_name": f"task_executor.{step_name}",
                        "status": "success",
                        "duration_ms": duration_ms,
                        "task_id": task_id,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            total_duration = sum(s["duration_ms"] for s in step_details)

            return {
                "task_id": task_id,
                "total_duration_ms": total_duration,
                "step_details": step_details,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"error": str(e)}

    def track_quality_score(self, task_id: str, quality_score: float) -> Dict[str, Any]:
        """
        品質スコアをリアルタイム追跡

        Args:
            task_id: タスクID
            quality_score: 品質スコア（0-1）

        Returns:
            品質スコア情報
        """
        try:
            # 品質スコアをメトリクスとして記録
            self.obs_manager.metrics_exporter.set_gauge(
                "task_quality_score", quality_score, labels={"task_id": task_id}
            )

            # トレース記録
            self.obs_manager.record_trace(
                {
                    "trace_id": f"quality-{task_id}",
                    "operation_name": "task_executor.quality_check",
                    "status": "success" if quality_score >= 0.7 else "warning",
                    "duration_ms": 20,
                    "quality_score": quality_score,
                    "task_id": task_id,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return {
                "task_id": task_id,
                "quality_score": quality_score,
                "threshold": 0.7,
                "passed": quality_score >= 0.7,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"error": str(e)}

    def trace_error_details(self, task_id: str, error: Exception) -> Dict[str, Any]:
        """
        エラー発生時の詳細トレース

        Args:
            task_id: タスクID
            error: 発生したエラー

        Returns:
            エラー詳細情報
        """
        try:
            error_details = {
                "task_id": task_id,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "timestamp": datetime.now().isoformat(),
            }

            # エラートレース記録
            self.obs_manager.record_trace(
                {
                    "trace_id": f"error-{task_id}",
                    "operation_name": "task_executor.error",
                    "status": "error",
                    "duration_ms": 0,
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "task_id": task_id,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return error_details

        except Exception as e:
            return {"error": str(e)}

    def visualize_retry_mechanism(
        self, task_id: str, retry_count: int, max_retries: int
    ) -> Dict[str, Any]:
        """
        リトライメカニズムを可視化

        Args:
            task_id: タスクID
            retry_count: 現在のリトライ回数
            max_retries: 最大リトライ回数

        Returns:
            リトライ状況情報
        """
        try:
            retry_info = {
                "task_id": task_id,
                "retry_count": retry_count,
                "max_retries": max_retries,
                "retry_remaining": max_retries - retry_count,
                "timestamp": datetime.now().isoformat(),
            }

            # リトライトレース記録
            self.obs_manager.record_trace(
                {
                    "trace_id": f"retry-{task_id}-{retry_count}",
                    "operation_name": "task_executor.retry",
                    "status": "in_progress",
                    "duration_ms": 10,
                    "retry_count": retry_count,
                    "max_retries": max_retries,
                    "task_id": task_id,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return retry_info

        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    print("🧪 TaskExecutorMonitor テスト")

    monitor = TaskExecutorMonitor()

    # テスト1: 実行時間計測
    print("\n【テスト1: 実行時間計測】")
    details = monitor.measure_execution_details("task-001")
    print(f"総実行時間: {details.get('total_duration_ms', 0)}ms")
    print(f"ステップ数: {len(details.get('step_details', []))}")

    # テスト2: 品質スコア追跡
    print("\n【テスト2: 品質スコア追跡】")
    quality = monitor.track_quality_score("task-002", 0.85)
    print(f"品質スコア: {quality.get('quality_score', 0)}")
    print(f"合格: {quality.get('passed', False)}")

    # テスト3: リトライ可視化
    print("\n【テスト3: リトライ可視化】")
    retry = monitor.visualize_retry_mechanism("task-003", 2, 5)
    print(f"リトライ残数: {retry.get('retry_remaining', 0)}")
