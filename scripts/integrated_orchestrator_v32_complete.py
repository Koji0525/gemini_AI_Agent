"""
統合オーケストレーター v32: 3つのループ完全統合版
既存の phase2_6hour_test.py をベースに拡張
"""

import asyncio
import sys
import os
from datetime import datetime

# プロジェクトルートをPYTHONPATHに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.sheets_manager import GoogleSheetsManager
from tools.safe_sheets_wrapper import SafeSheetsWrapper
from core_agents.pm_agent import PMAgent
from task_executor.task_executor_main import TaskExecutor
from agents.observability.observability_manager import ObservabilityManager


class IntegratedOrchestrator:
    """3つのループを統合したオーケストレーター"""

    def __init__(self):
        print("1️⃣ コンポーネント初期化中...")

        # 基本コンポーネント
        self.sheets = GoogleSheetsManager()
        self.safe_sheets = SafeSheetsWrapper(self.sheets)

        # Loop 1: タスク処理
        self.pm_agent = PMAgent(sheets_manager=self.sheets)
        self.task_executor = TaskExecutor(sheets_manager=self.sheets)

        # 監視
        self.observability = ObservabilityManager()

        print("✅ 初期化完了\n")

    async def execute_loop1(self):
        """Loop 1: タスク処理（3分間隔）"""
        print("🔄 Loop 1: タスク処理開始")

        try:
            # 1. pending タスク取得
            pending_tasks = self.task_executor.get_pending_tasks()

            if not pending_tasks:
                print("📋 pending タスクなし")
                return

            # 2. タスク実行（最大5件）
            for task in pending_tasks[:5]:
                result = await self.task_executor.execute_task(task)
                print(f"  ✅ タスク完了: {task['title']} ({result['elapsed_time']:.2f}秒)")

            print("✅ Loop 1 完了\n")

        except Exception as e:
            print(f"❌ Loop 1 エラー: {e}\n")

    async def run_continuous(self, max_hours: int = 24):
        """連続稼働"""
        print(f"🚀 {max_hours}時間連続稼働開始\n")

        start_time = datetime.now()
        cycle = 0

        while True:
            cycle += 1
            elapsed = (datetime.now() - start_time).total_seconds() / 3600

            if elapsed >= max_hours:
                print(f"⏰ {max_hours}時間経過 - 稼働終了")
                break

            print(f"━━━ サイクル {cycle} (経過: {elapsed:.2f}時間) ━━━")

            # Loop 1: タスク処理
            await self.execute_loop1()

            # 3分待機
            print("⏸️  次のサイクルまで3分待機...")
            await asyncio.sleep(180)

        print(f"\n✅ 連続稼働完了: {cycle}サイクル")


async def main():
    orchestrator = IntegratedOrchestrator()
    await orchestrator.run_continuous(max_hours=24)


if __name__ == "__main__":
    asyncio.run(main())
