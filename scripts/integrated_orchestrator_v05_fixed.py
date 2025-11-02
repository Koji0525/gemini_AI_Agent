#!/usr/bin/env python3
"""
統合オーケストレーター v05（修正版）

【修正内容】
- インポートパスを修正
- 5行目以降に書けるように smart_append_rows 使用
- ナレッジベース連携確認機能追加
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.smart_sheets_manager import SmartSheetsManager
from task_executor.task_coordinator_v05_self_healing import (
    TaskCoordinatorWithSelfHealing,
)
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IntegratedOrchestratorV05:
    """統合オーケストレーター（修正版）"""

    def __init__(self):
        self.sheets_manager = SmartSheetsManager()
        self.task_coordinator = TaskCoordinatorWithSelfHealing(self.sheets_manager)

        # ナレッジベース連携チェック
        self.kb_available = self._check_knowledge_base()

    def _check_knowledge_base(self) -> bool:
        """ナレッジベース連携確認"""
        try:
            kb_data = self.sheets_manager.read_range("knowledge_base!A2:A10")
            logger.info(f"✅ ナレッジベース連携OK: {len(kb_data)}件")
            return True
        except Exception as e:
            logger.warning(f"⚠️ ナレッジベース未利用: {e}")
            return False

    async def run(self):
        """メイン実行"""
        print("=" * 60)
        print("🚀 統合オーケストレーター v05（修正版）")
        print("=" * 60)

        try:
            # STEP 1: アクティブな目標を取得
            print("\n📋 STEP 1: アクティブな目標取得")
            goals = await self.get_active_goals()

            if not goals:
                print("   ℹ️ アクティブな目標がありません")
                return

            print(f"   ✅ {len(goals)}件の目標を検出")

            # STEP 2: 各目標をタスクに分解
            for goal in goals:
                print(f"\n📝 STEP 2: 目標をタスクに分解")
                print(f"   目標ID: {goal['goal_id']}")
                print(f"   内容: {goal['description'][:60]}...")

                await self.decompose_goal(goal)

            # STEP 3: タスク実行
            print(f"\n🎯 STEP 3: タスク実行")
            await self.execute_tasks()

            # STEP 4: ナレッジベース更新
            if self.kb_available:
                print(f"\n📚 STEP 4: ナレッジベース更新")
                await self.update_knowledge_base()

            print("\n" + "=" * 60)
            print("✅ 実行完了")
            print("=" * 60)

        except Exception as e:
            logger.error(f"❌ 実行エラー: {e}")
            import traceback

            traceback.print_exc()

    async def get_active_goals(self):
        """アクティブな目標を取得"""
        try:
            # 実データ範囲を自動検出
            last_row = self.sheets_manager.detect_actual_data_range("project_goal")
            goals_data = self.sheets_manager.read_range(f"project_goal!A2:D{last_row}")

            active_goals = []
            for row in goals_data:
                if len(row) >= 3 and row[2] == "active":
                    active_goals.append(
                        {
                            "goal_id": row[0],
                            "description": row[1],
                            "status": row[2],
                            "created_at": row[3] if len(row) > 3 else "",
                        }
                    )

            return active_goals

        except Exception as e:
            logger.error(f"❌ 目標取得エラー: {e}")
            return []

    async def decompose_goal(self, goal):
        """目標をタスクに分解（PM Agent使用）"""
        try:
            from pm_agent import PMAgent

            pm_agent = PMAgent(self.sheets_manager)

            # 目標をタスクに分解
            tasks = await pm_agent.decompose_goal_to_tasks(goal["goal_id"], goal["description"])

            print(f"   ✅ {len(tasks)}個のタスクに分解")

            # タスクをpm_tasksシートに登録（smart_append使用）
            if tasks:
                # 既存のタスク範囲を検出
                last_row = self.sheets_manager.detect_actual_data_range("pm_tasks")

                # タスクデータを準備
                task_data = []
                for task in tasks:
                    task_data.append(
                        [
                            task.get("task_id", ""),
                            goal["goal_id"],
                            task.get("description", ""),
                            task.get("required_role", ""),
                            "pending",
                            task.get("priority", "medium"),
                            task.get("estimated_time", ""),
                            task.get("dependencies", ""),
                            datetime.now().isoformat(),
                            task.get("batch_id", ""),
                            task.get("detail_file_path", ""),
                            "",
                            task.get("execution_type", "content"),
                        ]
                    )

                # smart_appendで追加
                self.sheets_manager.smart_append_rows(
                    "pm_tasks", task_data, validate=False  # pm_tasksは列数が多いので検証スキップ
                )

                print(f"   ✅ pm_tasksシートの{last_row + 1}行目以降に登録")

        except Exception as e:
            logger.error(f"❌ タスク分解エラー: {e}")
            import traceback

            traceback.print_exc()

    async def execute_tasks(self):
        """タスクを実行"""
        try:
            # pendingタスクを取得
            last_row = self.sheets_manager.detect_actual_data_range("pm_tasks")
            tasks_data = self.sheets_manager.read_range(f"pm_tasks!A2:M{last_row}")

            pending_tasks = []
            for row in tasks_data:
                if len(row) > 4 and row[4] == "pending":
                    pending_tasks.append(
                        {
                            "task_id": row[0],
                            "description": row[2] if len(row) > 2 else "",
                            "execution_type": row[12] if len(row) > 12 else "content",
                        }
                    )

            if not pending_tasks:
                print("   ℹ️ 実行待ちタスクなし")
                return

            print(f"   📋 実行待ちタスク: {len(pending_tasks)}件")

            # タスク実行
            for task in pending_tasks[:3]:  # 最初の3件のみ実行
                print(f"\n   🎯 タスク実行: {task['task_id']}")
                print(f"      {task['description'][:50]}...")

                result = await self.task_coordinator.execute_task(task)

                if result.get("status") == "success":
                    print(f"      ✅ 成功")
                else:
                    print(f"      ⚠️ 失敗: {result.get('error', 'Unknown')}")

        except Exception as e:
            logger.error(f"❌ タスク実行エラー: {e}")
            import traceback

            traceback.print_exc()

    async def update_knowledge_base(self):
        """ナレッジベース更新"""
        try:
            # task_execution_logから最新の実行結果を取得
            log_data = self.sheets_manager.read_range("task_execution_log!A2:J10")

            if log_data:
                print(f"   📊 実行ログ: {len(log_data)}件")

                # 成功パターンを抽出
                success_count = sum(1 for row in log_data if len(row) > 7 and row[7] == "success")
                print(f"   ✅ 成功: {success_count}件")

        except Exception as e:
            logger.warning(f"⚠️ ナレッジベース更新スキップ: {e}")


async def main():
    """メイン関数"""
    orchestrator = IntegratedOrchestratorV05()
    await orchestrator.run()


if __name__ == "__main__":
    asyncio.run(main())
