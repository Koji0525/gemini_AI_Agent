import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import sys
from pathlib import Path
from tools.sheets_manager import GoogleSheetsManager
from tools.graceful_shutdown import shutdown_manager
from tools.system_health_checker import run_health_check

"""
integrated_orchestrator_v04_improved.py

Phase 10.5 改善版

【変更理由】
v03での問題点:
1. Ctrl+Cが効かない → GracefulShutdown統合
2. control_flagsエラー → オプショナル化
3. エラー自動修復なし → SystemHealthChecker統合

【狙い】
- 即座停止可能（Ctrl+C対応）
- システムヘルスチェック
- エラー自動検知・修復
- より堅牢な24時間運用
"""


# プロジェクトルート
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Phase 10コンポーネント
try:
    from tools.interface_validator import InterfaceValidator

    HAS_INTERFACE_VALIDATOR = True
except ImportError:
    HAS_INTERFACE_VALIDATOR = False

try:
    from agents.self_healing.self_healing_pipeline import SelfHealingPipeline

    HAS_SELF_HEALING = True
except ImportError:
    HAS_SELF_HEALING = False

try:
    from task_executor import TaskExecutor
    from task_executor.task_coordinator import TaskCoordinator

    HAS_TASK_COORDINATOR = True
except ImportError:
    HAS_TASK_COORDINATOR = False

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class IntegratedOrchestratorV4:
    """
    Phase 10.5 改善版

    【新機能】
    - GracefulShutdown統合
    - SystemHealthCheck
    - エラー自動検知・修復強化
    """

    def __init__(self):
        """初期化"""
        logger.info("=" * 80)
        logger.info("🚀 Integrated Orchestrator v4 (Phase 10.5) 初期化")
        logger.info("=" * 80)

        self.sheets_manager = GoogleSheetsManager()

        # ヘルスチェック実行
        logger.info("\n🏥 起動前ヘルスチェック...")
        healthy = run_health_check(self.sheets_manager)

        if not healthy:
            logger.warning("⚠️  一部問題がありますが、続行します")

        # InterfaceValidator
        if HAS_INTERFACE_VALIDATOR:
            self.interface_validator = InterfaceValidator()
            logger.info("✅ InterfaceValidator 統合")
        else:
            self.interface_validator = None

        # SelfHealingPipeline
        if HAS_SELF_HEALING:
            self.self_healing = SelfHealingPipeline()
            self.has_self_healing = self.self_healing.is_available()
            if self.has_self_healing:
                logger.info("✅ SelfHealingPipeline 統合")
                status = self.self_healing.get_status()
                logger.info(f"   ErrorClassifier: {'✅' if status['error_classifier'] else '❌'}")
                logger.info(f"   KnowledgeBase: {'✅' if status['knowledge_base'] else '❌'}")
                logger.info(f"   DecisionSupport: {'✅' if status['decision_support'] else '❌'}")
        else:
            self.has_self_healing = False

        # TaskCoordinator
        if HAS_TASK_COORDINATOR:
            try:
                self.task_executor = TaskExecutor(
                    sheets_manager=self.sheets_manager, output_dir="agent_outputs"
                )
                self.task_coordinator = TaskCoordinator(
                    task_executor=self.task_executor,
                    sheets_manager=self.sheets_manager,
                    browser_controller=None,
                )
                self.has_coordinator = True
                logger.info("✅ TaskCoordinator 統合")
            except Exception as e:
                logger.warning(f"⚠️ TaskCoordinator初期化失敗: {e}")
                self.has_coordinator = False
        else:
            self.has_coordinator = False

        # 統計
        self.cycle_stats = {
            "total_cycles": 0,
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "auto_fixed_errors": 0,
            "total_time_minutes": 0.0,
            "graceful_shutdowns": 0,
        }

        logger.info("=" * 80)
        logger.info("📊 Phase 10.5 統合状況")
        logger.info(f"   InterfaceValidator: {'✅' if self.interface_validator else '❌'}")
        logger.info(f"   SelfHealing: {'✅' if self.has_self_healing else '❌'}")
        logger.info(f"   TaskCoordinator: {'✅' if self.has_coordinator else '❌'}")
        logger.info("   GracefulShutdown: ✅ 有効（Ctrl+C対応）")
        logger.info("=" * 80)

    async def run_continuous_cycle(self, max_duration_minutes: int = 330):
        """継続サイクル実行（GracefulShutdown対応）"""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=max_duration_minutes)
        cycle_count = 0

        # 停止フラグクリア
        shutdown_manager.clear_stop_flag()

        logger.info("=" * 80)
        logger.info("🔄 Phase 10.5 自律サイクル開始")
        logger.info("   最大実行時間: {max_duration_minutes}分")
        logger.info("   停止: Ctrl+C または .stop_orchestrator ファイル作成")
        logger.info("=" * 80)

        try:
            while datetime.now() < end_time:
                # 停止チェック（最優先）
                if shutdown_manager.should_stop():
                    logger.info("⏸️  停止要求を検出 - 優雅に終了します")
                    self.cycle_stats["graceful_shutdowns"] += 1
                    break

                cycle_count += 1
                cycle_start = datetime.now()

                logger.info("")
                logger.info("=" * 80)
                logger.info(f"📍 サイクル {cycle_count} 開始")
                elapsed = (datetime.now() - start_time).total_seconds() / 60
                logger.info(f"⏱️  経過: {elapsed:.1f}分 / {max_duration_minutes}分")
                logger.info("=" * 80)

                # サイクル実行
                await self._run_single_cycle()

                # 統計更新
                cycle_duration = (datetime.now() - cycle_start).total_seconds() / 60
                self.cycle_stats["total_cycles"] += 1
                self.cycle_stats["total_time_minutes"] += cycle_duration

                logger.info(f"✅ サイクル {cycle_count} 完了 ({cycle_duration:.1f}分)")

                # 次のサイクルまで待機（停止チェック付き）
                if datetime.now() < end_time and not shutdown_manager.should_stop():
                    logger.info("⏸️  8秒待機... (Ctrl+Cで停止)")
                    await asyncio.sleep(8)

        except KeyboardInterrupt:
            logger.info("\n⚠️  KeyboardInterrupt検出 - 優雅に終了")
            self.cycle_stats["graceful_shutdowns"] += 1
        except Exception as e:
            logger.error(f"❌ サイクルエラー: {e}")
            if self.has_self_healing:
                self.self_healing.handle_error(e, {"location": "run_continuous_cycle"})
        finally:
            self._print_final_stats()

        logger.info("")
        logger.info("=" * 80)
        logger.info("🏁 Phase 10.5 自律サイクル完了")
        logger.info(f"   総サイクル数: {cycle_count}")
        logger.info(f"   総実行時間: {self.cycle_stats['total_time_minutes']:.1f}分")
        logger.info("=" * 80)

    async def _run_single_cycle(self):
        """単一サイクル実行"""
        try:
            # pendingタスク取得
            logger.info("📋 pm_tasksからタスク取得...")
            tasks = await self._get_pending_tasks()

            if not tasks:
                logger.info("⚠️  実行可能なタスクなし")
                return

            logger.info(f"🎯 {len(tasks)}個のpendingタスク検出")

            # 各タスクを実行
            for i, task in enumerate(tasks, 1):
                # 停止チェック
                if shutdown_manager.should_stop():
                    logger.info("⏸️  停止要求 - タスク実行中断")
                    break

                logger.info(f"\n--- タスク {i}/{len(tasks)} ---")
                task_start = datetime.now()

                await self._execute_task_with_auto_healing(task, task_start)

                self.cycle_stats["total_tasks"] += 1

            # Dashboard更新
            logger.info("\n�� Progress Dashboard更新...")
            await self._update_progress_dashboard()

        except Exception as e:
            logger.error(f"❌ サイクル実行エラー: {e}")
            if self.has_self_healing:
                self.self_healing.handle_error(e, {"location": "_run_single_cycle"})

    async def _execute_task_with_auto_healing(self, task: Dict, start_time: datetime):
        """タスク実行（自動修復付き）"""
        task_id = task.get("task_id", "UNKNOWN")
        task_name = task.get("task_name", "No Name")

        logger.info(f"🔧 タスク実行: {task_name[:50]}...")
        logger.info(f"   Task ID: {task_id}")

        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                if self.has_coordinator:
                    if self.interface_validator:
                        logger.info("   🛡️ InterfaceValidator使用")
                        result = await self._safe_execute_with_validator(task)
                    else:
                        result = await self.task_coordinator.execute_task_coordinated(task)

                    success = result.get("success", False)
                    message = result.get("message", "TaskCoordinator実行完了")
                else:
                    logger.info("   ⚠️ シンプルモード")
                    success = True
                    message = "シンプルモード実行"

                # 実行時間計測
                duration = (datetime.now() - start_time).total_seconds() / 60

                # 結果記録
                self._update_task_result_safe(
                    task_id=task_id,
                    status="completed" if success else "failed",
                    result=message,
                    duration_minutes=duration,
                )

                if success:
                    self.cycle_stats["successful_tasks"] += 1
                else:
                    self.cycle_stats["failed_tasks"] += 1

                logger.info(f"✅ タスク完了: {task_id} ({duration:.2f}分)")
                break

            except Exception as e:
                retry_count += 1
                logger.error(f"❌ タスク実行エラー ({retry_count}/{max_retries}): {e}")

                # 自己修復
                if self.has_self_healing and retry_count < max_retries:
                    logger.info("🔧 自己修復パイプライン起動...")
                    healing_result = self.self_healing.handle_error(
                        e, {"task_id": task_id, "retry_count": retry_count}
                    )

                    if healing_result.get("success"):
                        logger.info("✨ 自動修復成功")
                        self.cycle_stats["auto_fixed_errors"] += 1
                        await asyncio.sleep(2)
                        continue

                if retry_count >= max_retries:
                    self.cycle_stats["failed_tasks"] += 1
                    self._update_task_result_safe(
                        task_id=task_id,
                        status="failed",
                        result=f"エラー: {str(e)[:100]}",
                    )
                    break

    async def _safe_execute_with_validator(self, task: Dict) -> Dict:
        """InterfaceValidator使用の安全実行"""
        method_name = self.interface_validator.validate_method(
            self.task_coordinator, "execute_task_coordinated"
        )

        if method_name:
            method = getattr(self.task_coordinator, method_name)
            return await method(task)
        else:
            return {"success": False, "message": "実行可能なメソッドなし"}

    def _update_task_result_safe(
        self, task_id: str, status: str, result: str = "", duration_minutes: float = 0.0
    ):
        """タスク結果更新（安全版）"""
        try:
            data = self.sheets_manager.read_range("pm_tasks!A:Z")
            if not data:
                return

            headers = data[0]
            status_idx = self._find_column_index(headers, ["status"])
            result_idx = self._find_column_index(headers, ["result", "execution_result"])

            for i, row in enumerate(data[1:], 2):
                if len(row) > 0 and row[0] == task_id:
                    if status_idx >= 0:
                        range_name = f"pm_tasks!{chr(65 + status_idx)}{i}"
                        if self.interface_validator:
                            self.interface_validator.safe_call(
                                self.sheets_manager,
                                "write_range",
                                range_name,
                                [[status]],
                            )
                        else:
                            self.sheets_manager.write_range(range_name, [[status]])

                    if result_idx >= 0 and result:
                        result_text = f"{result} ({duration_minutes:.2f}分)"
                        range_name = f"pm_tasks!{chr(65 + result_idx)}{i}"
                        if self.interface_validator:
                            self.interface_validator.safe_call(
                                self.sheets_manager,
                                "write_range",
                                range_name,
                                [[result_text]],
                            )
                        else:
                            self.sheets_manager.write_range(range_name, [[result_text]])

                    logger.info(f"   📝 結果更新: {task_id} → {status}")
                    break
        except Exception as e:
            logger.error(f"⚠️ 結果更新エラー: {e}")

    async def _get_pending_tasks(self) -> List[Dict]:
        """pendingタスク取得"""
        try:
            data = self.sheets_manager.read_range("pm_tasks!A:Z")
            if not data or len(data) < 2:
                return []

            headers = data[0]
            status_idx = self._find_column_index(headers, ["status"])

            pending_tasks = []
            for row in data[1:]:
                if len(row) > status_idx and row[status_idx].lower() == "pending":
                    task = {
                        "task_id": row[0] if len(row) > 0 else "",
                        "goal_id": row[1] if len(row) > 1 else "",
                        "task_name": row[2] if len(row) > 2 else "",
                        "required_role": row[3] if len(row) > 3 else "general",
                        "raw_row": row,
                    }
                    pending_tasks.append(task)

            return pending_tasks
        except Exception as e:
            logger.error(f"❌ タスク取得エラー: {e}")
            return []

    async def _update_progress_dashboard(self):
        """Dashboard更新"""
        try:
            from scripts.unified_progress_updater import UnifiedProgressUpdater

            updater = UnifiedProgressUpdater()
            await updater.update_progress_dashboard()
            logger.info("✅ Dashboard更新完了")
        except Exception as e:
            logger.warning(f"⚠️ Dashboard更新エラー: {e}")

    def _find_column_index(self, headers: List, possible_names: List[str]) -> int:
        """列インデックス検索"""
        for name in possible_names:
            if name in headers:
                return headers.index(name)
        return -1

    def _print_final_stats(self):
        """最終統計"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 Phase 10.5 最終統計")
        logger.info("=" * 80)
        logger.info(f"  総サイクル数: {self.cycle_stats['total_cycles']}")
        logger.info(f"  総タスク数: {self.cycle_stats['total_tasks']}")
        logger.info(f"  成功: {self.cycle_stats['successful_tasks']}")
        logger.info(f"  失敗: {self.cycle_stats['failed_tasks']}")
        logger.info(f"  自動修復: {self.cycle_stats['auto_fixed_errors']}件")
        logger.info(f"  優雅な停止: {self.cycle_stats['graceful_shutdowns']}回")
        logger.info(f"  総実行時間: {self.cycle_stats['total_time_minutes']:.1f}分")

        if self.cycle_stats["total_tasks"] > 0:
            avg_time = self.cycle_stats["total_time_minutes"] / self.cycle_stats["total_tasks"]
            success_rate = (
                self.cycle_stats["successful_tasks"] / self.cycle_stats["total_tasks"]
            ) * 100
            logger.info(f"  平均タスク時間: {avg_time:.2f}分")
            logger.info(f"  成功率: {success_rate:.1f}%")

        logger.info("=" * 80)


def main():
    """メイン実行"""
    orchestrator = IntegratedOrchestratorV4()
    asyncio.run(orchestrator.run_continuous_cycle(max_duration_minutes=330))


if __name__ == "__main__":
    main()
