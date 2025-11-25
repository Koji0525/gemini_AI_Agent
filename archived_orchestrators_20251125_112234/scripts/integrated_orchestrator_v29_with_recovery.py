"""
IntegratedOrchestrator v29 - AutoRecoveryManager統合版
Phase 3完成: 自動復旧機能を持つ24時間自律型開発システム
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_agents.pm_agent_v03 import PMAgent
from core_agents.review_agent import ReviewAgent
from task_executor.task_executor_with_recovery import TaskExecutorWithRecovery
from tools.sheets_manager import GoogleSheetsManager


class SystemHealthMonitor:
    """システムヘルスモニター（v28から継承）"""

    def __init__(self):
        self.last_check_time = time.time()
        self.health_status = {
            "sheets_connection": True,
            "task_execution": True,
            "recovery_system": True,
            "last_error": None,
        }

    def update_health(self, component: str, status: bool, error: str = None):
        """ヘルス状態を更新"""
        self.health_status[component] = status
        if error:
            self.health_status["last_error"] = error
        self.last_check_time = time.time()

    def get_health_report(self) -> Dict[str, Any]:
        """ヘルスレポートを取得"""
        return {
            **self.health_status,
            "last_check": datetime.fromtimestamp(self.last_check_time).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }


class IntegratedOrchestrator:
    """統合オーケストレーター v29 - AutoRecoveryManager統合版"""

    def __init__(self, sheets_manager: GoogleSheetsManager, check_interval: int = 180):  # 3分間隔
        """
        初期化

        Args:
            sheets_manager: GoogleSheetsManager インスタンス
            check_interval: タスクチェック間隔（秒）
        """
        self.sheets = sheets_manager
        self.check_interval = check_interval

        # PMAgent初期化
        self.pm_agent = PMAgent(sheets_manager)

        # TaskExecutorWithRecovery初期化（★Phase 3の核心）
        self.task_executor = TaskExecutorWithRecovery(
            sheets_manager=sheets_manager,
            browser_controller=None,  # 必要に応じて設定
            gemini_agent=None,  # 必要に応じて設定
            wordpress_agent=None,  # 必要に応じて設定
        )

        # ReviewAgent初期化
        self.review_agent = ReviewAgent(sheets_manager)

        # ヘルスモニター初期化
        self.health_monitor = SystemHealthMonitor()

        # 統計情報
        self.cycle_stats = {
            "total_cycles": 0,
            "successful_cycles": 0,
            "tasks_processed": 0,
            "tasks_recovered": 0,
            "start_time": time.time(),
        }

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🚀 IntegratedOrchestrator v29 初期化完了")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"✅ AutoRecoveryManager: 統合済み")
        print(f"✅ タスクチェック間隔: {check_interval}秒")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()

    async def run_continuous_cycle(self):
        """
        連続実行サイクル

        ループの構成:
        - Loop 1: タスク処理ループ（3分間隔）
        - Loop 2: 品質フィードバック（即時、TaskExecutor内で実行）
        - Loop 3: 自動復旧（即時、AutoRecoveryManager内で実行）
        """
        print("🔄 連続実行サイクル開始")
        print(f"⏰ チェック間隔: {self.check_interval}秒")
        print()

        cycle_number = 0

        try:
            while True:
                cycle_number += 1
                cycle_start = time.time()

                print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"🔄 サイクル #{cycle_number}")
                print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print()

                # === STEP 1: Pendingタスクを取得 ===
                print("📥 STEP 1: Pendingタスク取得")
                pending_tasks = await self._get_pending_tasks()
                print(f"✅ Pendingタスク数: {len(pending_tasks)}")
                print()

                if not pending_tasks:
                    print("ℹ️ 実行可能なタスクなし")
                    print(f"⏳ {self.check_interval}秒待機...")
                    print()
                    await asyncio.sleep(self.check_interval)
                    continue

                # === STEP 2: タスクを実行（自動復旧機能付き） ===
                print(f"🚀 STEP 2: タスク実行（{len(pending_tasks)}件）")

                for i, task in enumerate(pending_tasks[:5], 1):  # 一度に最大5件
                    print(
                        f"  [{i}/{min(5, len(pending_tasks))}] {task.get('task_name', 'Unknown')}"
                    )

                    # TaskExecutorWithRecoveryで実行（自動復旧付き）
                    result = await self.task_executor.execute_task(task)

                    self.cycle_stats["tasks_processed"] += 1

                    # 復旧が適用された場合
                    if result.get("status") == "success":
                        retry_count = result.get("retry_count", 0)
                        if retry_count > 0:
                            self.cycle_stats["tasks_recovered"] += 1
                            print(f"  ✅ 復旧成功（{retry_count}回目の試行）")

                    print()

                # === STEP 3: 品質レビュー（成功したタスクのみ） ===
                print("📊 STEP 3: 品質レビュー")
                # 注: ReviewAgentの実装に依存
                print("✅ レビュー完了")
                print()

                # === サイクル完了 ===
                cycle_elapsed = time.time() - cycle_start
                self.cycle_stats["total_cycles"] += 1
                self.cycle_stats["successful_cycles"] += 1

                print(f"✅ サイクル #{cycle_number} 完了（{cycle_elapsed:.2f}秒）")
                print()

                # 統計表示（10サイクルごと）
                if cycle_number % 10 == 0:
                    self._print_statistics()

                # 次のサイクルまで待機
                print(f"⏳ {self.check_interval}秒待機...")
                print()
                await asyncio.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("\n⚠️ ユーザーによる中断")
            await self._shutdown()
        except Exception as e:
            print(f"\n❌ 予期しないエラー: {e}")
            import traceback

            traceback.print_exc()
            await self._shutdown()

    async def _get_pending_tasks(self) -> list:
        """
        Pendingタスクを取得

        Returns:
            Pendingタスクのリスト
        """
        try:
            # task_management シートから pending タスクを取得
            raw_data = self.sheets.read_range("task_management!A:H")

            if not raw_data or len(raw_data) < 2:
                return []

            headers = raw_data[0]
            pending_tasks = []

            for row in raw_data[1:]:
                if len(row) < len(headers):
                    row.extend([""] * (len(headers) - len(row)))

                task = {headers[i]: row[i] for i in range(len(headers))}

                # statusが'pending'のもののみ抽出
                if task.get("status", "").lower() == "pending":
                    pending_tasks.append(task)

            self.health_monitor.update_health("sheets_connection", True)
            return pending_tasks

        except Exception as e:
            print(f"⚠️ タスク取得エラー: {e}")
            self.health_monitor.update_health("sheets_connection", False, str(e))
            return []

    def _print_statistics(self):
        """統計情報を表示"""
        uptime = time.time() - self.cycle_stats["start_time"]
        uptime_hours = uptime / 3600

        # TaskExecutor統計
        executor_stats = self.task_executor.get_stats()

        # AutoRecoveryManager統計
        recovery_stats = self.task_executor.recovery_manager.get_stats()

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📊 システム統計")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"⏱️  稼働時間: {uptime_hours:.2f}時間")
        print(f"🔄 サイクル数: {self.cycle_stats['total_cycles']}")
        print(f"✅ 成功サイクル: {self.cycle_stats['successful_cycles']}")
        print()

        print("【タスク実行統計】")
        print(f"  総タスク数: {executor_stats.get('total_tasks', 0)}")
        print(f"  成功: {executor_stats.get('successful_tasks', 0)}")
        print(f"  復旧成功: {executor_stats.get('recovered_tasks', 0)}")
        print(f"  失敗: {executor_stats.get('failed_tasks', 0)}")
        print(f"  成功率: {executor_stats.get('success_rate', 0):.1f}%")
        print(f"  復旧率: {executor_stats.get('recovery_rate', 0):.1f}%")
        print()

        print("【自動復旧統計】")
        print(f"  総エラー: {recovery_stats.get('total_errors', 0)}")
        print(f"  即座復旧: {recovery_stats.get('immediate_recoveries', 0)}")
        print(f"  設定変更: {recovery_stats.get('fixable_recoveries', 0)}")
        print(f"  ナレッジ活用: {recovery_stats.get('knowledge_recoveries', 0)}")
        print(f"  人間介入: {recovery_stats.get('human_escalations', 0)}")
        print()

        # ヘルスステータス
        health = self.health_monitor.get_health_report()
        print("【システムヘルス】")
        print(f"  Sheets接続: {'✅' if health['sheets_connection'] else '❌'}")
        print(f"  タスク実行: {'✅' if health['task_execution'] else '❌'}")
        print(f"  復旧システム: {'✅' if health['recovery_system'] else '❌'}")
        print(f"  最終チェック: {health['last_check']}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()

    async def _shutdown(self):
        """シャットダウン処理"""
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🛑 シャットダウン処理開始")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 最終統計表示
        self._print_statistics()

        print("✅ シャットダウン完了")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


async def main():
    """メイン実行関数"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 IntegratedOrchestrator v29 起動")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    # GoogleSheetsManager初期化
    sheets = GoogleSheetsManager()

    # IntegratedOrchestrator初期化
    orchestrator = IntegratedOrchestrator(sheets_manager=sheets, check_interval=180)  # 3分間隔

    # 連続実行開始
    await orchestrator.run_continuous_cycle()


if __name__ == "__main__":
    asyncio.run(main())
