import logging
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from tools.sheets_manager import GoogleSheetsManager
from pm_agent import PMAgent
from task_executor.task_coordinator_v05_self_healing import (
    TaskCoordinatorWithSelfHealing,
)

"""
integrated_orchestrator_v05_final.py

最終統合版オーケストレーター

【変更の理由】
- マッピング対応SheetsManagerを使用
- 自己修復機能統合TaskCoordinatorを使用
- 既存シート構造(project_goal, pm_tasks, task_execution_log)を活用
"""

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


class IntegratedOrchestrator:
    """統合オーケストレーター（最終版）"""

    def __init__(self):
        """初期化"""
        logger.info("=" * 60)
        logger.info("🎹 統合オーケストレーター起動")
        logger.info("=" * 60)

        # Google Sheets初期化（マッピング対応）
        self.sheets_manager = GoogleSheetsManager()

        # PM Agent初期化
        self.pm_agent = PMAgent(self.sheets_manager)

        # Task Coordinator初期化（自己修復機能付き）
        self.task_coordinator = TaskCoordinatorWithSelfHealing(self.sheets_manager)

        logger.info("✅ 全コンポーネント初期化完了")

    async def run_cycle(self):
        """1サイクル実行"""
        logger.info("\n" + "━" * 60)
        logger.info(f"🔄 実行サイクル開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("━" * 60)

        try:
            # STEP 1: 目標分解（project_goalシートから読み取り）
            logger.info("\n📋 STEP 1: 目標分解")
            goals = await self.pm_agent.decompose_active_goals()

            if goals:
                logger.info(f"✅ {len(goals)}個の目標を処理")
            else:
                logger.info("ℹ️ アクティブな目標がありません")

            # STEP 2: タスク実行（pm_tasksシートから読み取り）
            logger.info("\n🎯 STEP 2: タスク実行")
            tasks = await self._get_pending_tasks()

            if not tasks:
                logger.info("ℹ️ 実行可能なタスクがありません")
                return

            logger.info(f"✅ {len(tasks)}個のタスクを実行します")

            for task in tasks[:5]:  # 一度に最大5タスク
                task_id = task.get("task_id", "unknown")
                logger.info(f"\n   🎯 タスク実行: {task_id}")

                result = await self.task_coordinator.execute_task(task)

                # 結果をtask_execution_logに記録
                await self._record_execution(task, result)

                logger.info(f"   ✅ {task_id}: {result.get('status')}")

            logger.info("\n✅ サイクル完了")

        except Exception as e:
            logger.error(f"❌ サイクルエラー: {e}")
            import traceback

            traceback.print_exc()

    async def _get_pending_tasks(self) -> list:
        """保留中のタスクを取得（論理名使用）"""
        try:
            # pm_tasksシートから読み取り（マッピングで自動解決）
            data = self.sheets_manager.read_range("pm_tasks!A2:K100")

            if not data:
                return []

            tasks = []
            for row in data:
                if len(row) > 3 and row[3] == "pending":  # D列: status
                    tasks.append(
                        {
                            "task_id": row[0] if len(row) > 0 else "",
                            "description": row[2] if len(row) > 2 else "",
                            "status": row[3] if len(row) > 3 else "",
                            "execution_type": row[6] if len(row) > 6 else "content",
                        }
                    )

            return tasks

        except Exception as e:
            logger.error(f"❌ タスク取得エラー: {e}")
            return []

    async def _record_execution(self, task: dict, result: dict):
        """実行結果を記録（論理名使用）"""
        try:
            execution_record = [
                [
                    task.get("task_id", ""),
                    datetime.now().isoformat(),
                    result.get("status", "unknown"),
                    str(result)[:200],
                ]
            ]

            # task_execution_logシートに追記（マッピングで自動解決）
            self.sheets_manager.append_rows("task_execution_log", execution_record)

        except Exception as e:
            logger.warning(f"⚠️ 実行記録エラー: {e}")

    async def cleanup(self):
        """クリーンアップ"""
        try:
            await self.task_coordinator.cleanup()
            logger.info("✅ リソースクリーンアップ完了")
        except Exception as e:
            logger.warning(f"⚠️ クリーンアップエラー: {e}")


async def main():
    """メイン実行"""
    orchestrator = None

    try:
        orchestrator = IntegratedOrchestrator()

        # 1サイクル実行
        await orchestrator.run_cycle()

        logger.info("\n" + "=" * 60)
        logger.info("✅ 正常終了")
        logger.info("=" * 60)

        return 0

    except KeyboardInterrupt:
        logger.info("\n⚠️ ユーザーによる中断")
        return 0

    except Exception as e:
        logger.error(f"\n❌ 致命的エラー: {e}")
        import traceback

        traceback.print_exc()
        return 1

    finally:
        if orchestrator:
            await orchestrator.cleanup()


if __name__ == "__main__":
    exit(asyncio.run(main()))
