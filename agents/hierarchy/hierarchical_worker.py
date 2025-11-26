#!/usr/bin/env python3
"""
階層型Worker
既存TaskExecutorをメッセージ駆動で動作させるWrapper

Google Docstring形式
"""
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.hierarchy.messaging import (HierarchicalMessenger, MessageBus,
                                        MessageType)

logger = logging.getLogger(__name__)


class HierarchicalWorker:
    """
    階層型Worker
    既存TaskExecutorをラップしてメッセージ駆動で実行

    Attributes:
        worker_id (str): Worker ID
        team_leader_id (str): 所属TeamLeader ID
        task_executor: 既存TaskExecutor（保護）
        messenger (HierarchicalMessenger): メッセンジャー
        running (bool): 実行中フラグ
    """

    def __init__(
        self,
        worker_id: str,
        team_leader_id: str,
        task_executor,
        message_bus: Optional[MessageBus] = None,
    ):
        """
        初期化

        Args:
            worker_id (str): Worker ID
            team_leader_id (str): TeamLeader ID
            task_executor: 既存TaskExecutor
            message_bus (MessageBus, optional): メッセージバス
        """
        self.worker_id = worker_id
        self.team_leader_id = team_leader_id
        self.task_executor = task_executor  # 既存を保護
        self.messenger = HierarchicalMessenger(message_bus)
        self.running = False

        logger.info(f"HierarchicalWorker初期化: {worker_id} (TeamLeader: {team_leader_id})")

    def start(self, poll_interval: int = 10):
        """
        Worker開始（メッセージ受信ループ）

        Args:
            poll_interval (int): ポーリング間隔（秒）
        """
        self.running = True
        logger.info(f"Worker開始: {self.worker_id}")

        try:
            while self.running:
                # メッセージ受信
                messages = self.messenger.message_bus.receive(
                    self.worker_id, MessageType.TASK_ASSIGNMENT
                )

                for message in messages:
                    self._handle_task_assignment(message)
                    # 既読処理
                    self.messenger.message_bus.mark_as_read(self.worker_id, message.message_id)

                # ポーリング待機
                time.sleep(poll_interval)

        except KeyboardInterrupt:
            logger.info(f"Worker停止: {self.worker_id}")
        except Exception as e:
            logger.error(f"Worker異常終了: {e}")
            raise

    def stop(self):
        """Worker停止"""
        self.running = False
        logger.info(f"Worker停止要求: {self.worker_id}")

    def _handle_task_assignment(self, message):
        """
        タスク割り当てメッセージを処理

        Args:
            message (Message): タスク割り当てメッセージ
        """
        task_id = message.content.get("task_id")
        task_details = message.content.get("task_details")

        logger.info(f"タスク受信: {task_id}")

        try:
            # 開始報告
            self._report_progress(task_id, 0, "started")

            # 既存TaskExecutorに委譲
            result = self.task_executor.execute(task_details)

            # 完了報告
            quality_score = result.get("quality_score", None)
            self._report_progress(task_id, 100, "completed", quality_score)

            logger.info(f"タスク完了: {task_id} (品質: {quality_score})")

        except Exception as e:
            logger.error(f"タスク実行失敗: {task_id} - {e}")
            # 失敗報告
            self._report_progress(task_id, -1, "failed")

    def _report_progress(
        self,
        task_id: str,
        progress: int,
        status: str = "in_progress",
        quality_score: Optional[int] = None,
    ):
        """
        進捗報告

        Args:
            task_id (str): タスクID
            progress (int): 進捗率 0-100（失敗時は-1）
            status (str): ステータス
            quality_score (int, optional): 品質スコア
        """
        self.messenger.worker_to_team_leader(
            worker_id=self.worker_id,
            team_leader_id=self.team_leader_id,
            task_id=task_id,
            progress=progress,
            quality_score=quality_score,
        )
        logger.debug(f"進捗報告: {task_id} ({progress}%)")

    def execute_once(self, task_details: Dict) -> Dict:
        """
        単発実行（テスト用）

        Args:
            task_details (Dict): タスク詳細

        Returns:
            Dict: 実行結果
        """
        logger.info(f"単発実行: {self.worker_id}")
        return self.task_executor.execute(task_details)


# モックTaskExecutor（テスト用）
class MockTaskExecutor:
    """モックTaskExecutor（テスト用）"""

    def execute(self, task_details: Dict) -> Dict:
        """タスク実行（モック）"""
        import random

        time.sleep(1)  # 実行をシミュレート

        return {
            "status": "completed",
            "output": f"Task output: {task_details.get('description', 'N/A')}",
            "quality_score": random.randint(70, 95),
        }


# テスト実行
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HierarchicalWorker テスト")
    print("=" * 60)

    # メッセージバス
    bus = MessageBus()
    messenger = HierarchicalMessenger(bus)

    # MockTaskExecutor
    mock_executor = MockTaskExecutor()

    # Worker初期化
    worker = HierarchicalWorker(
        worker_id="worker_test_01",
        team_leader_id="team_leader_test",
        task_executor=mock_executor,
        message_bus=bus,
    )

    # 1. 単発実行テスト
    print("\n[1/3] 単発実行テスト")
    result = worker.execute_once({"description": "テストタスク"})
    print(f"   結果: {result['status']}")
    print(f"   品質: {result['quality_score']}")

    # 2. メッセージ駆動テスト
    print("\n[2/3] メッセージ駆動テスト")

    # TeamLeaderからタスク割り当て
    messenger.team_leader_to_worker(
        team_leader_id="team_leader_test",
        worker_id="worker_test_01",
        task_id="task_test_001",
        task_details={"description": "メッセージ駆動タスク"},
    )
    print("   タスク割り当て送信完了")

    # Workerがメッセージ受信・処理（1回だけ）
    messages = bus.receive("worker_test_01", MessageType.TASK_ASSIGNMENT)
    print(f"   受信メッセージ数: {len(messages)}")

    if messages:
        worker._handle_task_assignment(messages[0])
        bus.mark_as_read("worker_test_01", messages[0].message_id)

    # 3. 進捗報告確認
    print("\n[3/3] 進捗報告確認")
    reports = bus.receive("team_leader_test", MessageType.PROGRESS_REPORT)
    print(f"   報告数: {len(reports)}")

    for i, report in enumerate(reports[:3], 1):
        content = report.content
        print(f"   報告{i}: task_id={content['task_id']}, progress={content['progress']}%")

    print("\n✅ HierarchicalWorker テスト完了")
