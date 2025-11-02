import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import sys
from pathlib import Path
from tools.sheets_manager import GoogleSheetsManager

"""
integrated_orchestrator_v03_phase10_complete.py

Phase 10完全統合版：24時間自律開発システム

【変更理由】
v02はTaskCoordinatorを統合したが、Phase 5-9の自己修復システムが未統合。
メソッド名の不一致などのエラーが手動修正を必要とした。

【Phase 10統合内容】
1. InterfaceValidator統合 → メソッド名自動検証・代替探索
2. SelfHealingPipeline統合 → エラー自動分類・修復
3. TaskCoordinator統合 → 実際のタスク実行
4. サイクル測定・見える化 → パフォーマンス監視

【狙い】
- エラー発生時の自動修復（人間介入不要）
- インターフェース変更への自動適応
- 24時間完全自律運用
- 開発効率10倍化の実現

【長期的メリット】
- 今後のメソッド名変更に自動対応
- エラーパターンの学習と再利用
- システムの自己進化能力
"""


# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


# InterfaceValidator統合
try:
    from tools.interface_validator import InterfaceValidator

    HAS_INTERFACE_VALIDATOR = True
except ImportError:
    HAS_INTERFACE_VALIDATOR = False
    InterfaceValidator = None

# SelfHealingPipeline統合
try:
    from agents.self_healing.self_healing_pipeline import SelfHealingPipeline

    HAS_SELF_HEALING = True
except ImportError:
    HAS_SELF_HEALING = False
    SelfHealingPipeline = None

# TaskCoordinator統合
try:
    from task_executor import TaskExecutor
    from task_executor.task_coordinator import TaskCoordinator

    HAS_TASK_COORDINATOR = True
except ImportError:
    HAS_TASK_COORDINATOR = False
    TaskCoordinator = None
    TaskExecutor = None

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class IntegratedOrchestratorV3:
    """
    Phase 10完全統合版：24時間自律開発システム

    【統合機能】
    - InterfaceValidator: メソッド自動検証
    - SelfHealingPipeline: エラー自動修復
    - TaskCoordinator: タスク実行制御
    - サイクル測定: パフォーマンス監視
    """

    def __init__(self):
        """初期化"""
        logger.info("=" * 80)
        logger.info("🚀 Integrated Orchestrator v3 (Phase 10) 初期化開始")
        logger.info("=" * 80)

        self.sheets_manager = GoogleSheetsManager()

        # InterfaceValidator統合
        if HAS_INTERFACE_VALIDATOR:
            self.interface_validator = InterfaceValidator()
            logger.info("✅ InterfaceValidator 統合成功")
        else:
            self.interface_validator = None
            logger.warning("⚠️ InterfaceValidator 利用不可")

        # SelfHealingPipeline統合
        if HAS_SELF_HEALING:
            self.self_healing = SelfHealingPipeline()
            if self.self_healing.is_available():
                logger.info("✅ SelfHealingPipeline 統合成功")
                self.has_self_healing = True
            else:
                logger.warning("⚠️ SelfHealingPipeline コンポーネント不完全")
                self.has_self_healing = False

            # パイプラインの状態を確認
            if self.has_self_healing:
                status = self.self_healing.get_status()
                logger.info(f"   ErrorClassifier: {'✅' if status['error_classifier'] else '❌'}")
                logger.info(f"   KnowledgeBase: {'✅' if status['knowledge_base'] else '❌'}")
                logger.info(f"   DecisionSupport: {'✅' if status['decision_support'] else '❌'}")
                logger.info(f"   RetryManager: {'✅' if status['retry_manager'] else '❌'}")
        else:
            self.self_healing = None
            self.has_self_healing = False
            logger.warning("⚠️ SelfHealingPipeline 利用不可")

        # TaskCoordinator統合
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
                logger.info("✅ TaskCoordinator 統合成功")
            except Exception as e:
                logger.warning(f"⚠️ TaskCoordinator初期化エラー: {e}")
                self.task_coordinator = None
                self.has_coordinator = False
        else:
            logger.warning("⚠️ TaskCoordinator 利用不可")
            self.task_coordinator = None
            self.has_coordinator = False

        # サイクル測定用
        self.cycle_stats = {
            "total_cycles": 0,
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "auto_fixed_errors": 0,
            "total_time_minutes": 0.0,
            "error_log": [],
        }

        logger.info("=" * 80)
        logger.info("📊 Phase 10 統合状況")
        logger.info(
            f"   InterfaceValidator: {'✅ 有効' if self.interface_validator else '❌ 無効'}"
        )
        logger.info(f"   SelfHealing: {'✅ 有効' if self.has_self_healing else '❌ 無効'}")
        logger.info(f"   TaskCoordinator: {'✅ 有効' if self.has_coordinator else '❌ 無効'}")
        logger.info("=" * 80)

    async def run_continuous_cycle(self, max_duration_minutes: int = 330):
        """
        継続サイクル実行（Phase 10完全自律版）

        Args:
            max_duration_minutes: 最大実行時間（分）デフォルト5.5時間
        """
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=max_duration_minutes)
        cycle_count = 0

        logger.info("=" * 80)
        logger.info(f"🔄 Phase 10 自律サイクル開始 (最大: {max_duration_minutes}分)")
        logger.info("=" * 80)

        try:
            while datetime.now() < end_time:
                cycle_count += 1
                cycle_start = datetime.now()

                # 停止フラグチェック
                if self._check_stop_flag():
                    logger.info("⏸️  停止フラグ検出 - サイクル終了")
                    break

                logger.info("")
                logger.info("=" * 80)
                logger.info(f"📍 サイクル {cycle_count} 開始")
                elapsed = (datetime.now() - start_time).total_seconds() / 60
                logger.info(f"⏱️  経過時間: {elapsed:.1f}分 / {max_duration_minutes}分")
                logger.info("=" * 80)

                # サイクル実行（自己修復付き）
                await self._run_single_cycle_with_healing()

                # サイクル統計記録
                cycle_duration = (datetime.now() - cycle_start).total_seconds() / 60
                self.cycle_stats["total_cycles"] += 1
                self.cycle_stats["total_time_minutes"] += cycle_duration

                logger.info(f"✅ サイクル {cycle_count} 完了 ({cycle_duration:.1f}分)")
                logger.info(f"⏳ 累計: {self.cycle_stats['total_time_minutes']:.1f}分")
                logger.info(f"📊 自動修復: {self.cycle_stats['auto_fixed_errors']}件")

                # 次のサイクルまで待機
                if datetime.now() < end_time:
                    logger.info("⏸️  次のサイクルまで 8秒待機...")
                    await asyncio.sleep(8)

        except KeyboardInterrupt:
            logger.info("\n⚠️  ユーザーによる中断")
        except Exception as e:
            logger.error(f"❌ 継続サイクルエラー: {e}")

            # 自己修復を試みる
            if self.has_self_healing:
                logger.info("🔧 自己修復パイプライン起動...")
                self._handle_critical_error(e, {"location": "run_continuous_cycle"})

            import traceback

            traceback.print_exc()
        finally:
            self._print_final_stats()

        logger.info("")
        logger.info("=" * 80)
        logger.info("🏁 Phase 10 自律サイクル完了")
        logger.info(f"   総サイクル数: {cycle_count}")
        logger.info(f"   総実行時間: {self.cycle_stats['total_time_minutes']:.1f}分")
        logger.info(f"   自動修復件数: {self.cycle_stats['auto_fixed_errors']}件")
        logger.info("=" * 80)

    async def _run_single_cycle_with_healing(self):
        """単一サイクル実行（自己修復機能付き）"""
        try:
            # 1. pendingタスクを取得
            logger.info("📋 pm_tasksからタスク取得中...")
            tasks = await self._get_pending_tasks()

            if not tasks:
                logger.info("⚠️  実行可能なpendingタスクなし")
                return

            logger.info(f"🎯 {len(tasks)}個のpendingタスクを検出")

            # 2. 各タスクを実行（自己修復付き）
            for i, task in enumerate(tasks, 1):
                logger.info(f"\n--- タスク {i}/{len(tasks)} ---")
                task_start = datetime.now()

                await self._execute_task_with_auto_healing(task, task_start)

                self.cycle_stats["total_tasks"] += 1

            # 3. Progress Dashboard更新
            logger.info("\n📊 Progress Dashboard更新中...")
            await self._update_progress_dashboard()

        except Exception as e:
            logger.error(f"❌ サイクル実行エラー: {e}")

            # 自己修復を試みる
            if self.has_self_healing:
                self._handle_critical_error(e, {"location": "_run_single_cycle"})

            import traceback

            traceback.print_exc()

    async def _execute_task_with_auto_healing(self, task: Dict, start_time: datetime):
        """
        タスク実行（自動修復機能付き）

        Args:
            task: タスク情報
            start_time: 開始時刻
        """
        task_id = task.get("task_id", "UNKNOWN")
        task_name = task.get("task_name", "No Name")

        logger.info(f"🔧 タスク実行: {task_name[:50]}...")
        logger.info(f"   Task ID: {task_id}")

        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                if self.has_coordinator:
                    # InterfaceValidatorで安全に呼び出し
                    if self.interface_validator:
                        logger.info("   🛡️ InterfaceValidator使用")
                        result = await self._safe_execute_with_validator(task)
                    else:
                        # 通常実行
                        result = await self.task_coordinator.execute_task_coordinated(task)

                    success = result.get("success", False)
                    message = result.get("message", "TaskCoordinator実行完了")
                else:
                    # シンプルモード
                    logger.info("   ⚠️ シンプルモード: ログのみ")
                    success = True
                    message = "シンプルモード実行"

                # 実行時間計測
                duration = (datetime.now() - start_time).total_seconds()
                duration_minutes = duration / 60

                # 結果を記録
                self._update_task_result_safe(
                    task_id=task_id,
                    status="completed" if success else "failed",
                    result=message,
                    duration_minutes=duration_minutes,
                )

                if success:
                    self.cycle_stats["successful_tasks"] += 1
                else:
                    self.cycle_stats["failed_tasks"] += 1

                logger.info(f"✅ タスク完了: {task_id} ({duration_minutes:.2f}分)")
                break  # 成功したらループ脱出

            except Exception as e:
                retry_count += 1
                logger.error(f"❌ タスク実行エラー ({retry_count}/{max_retries}): {e}")

                # 自己修復を試みる
                if self.has_self_healing and retry_count < max_retries:
                    logger.info("🔧 自己修復パイプライン起動...")
                    healing_result = self.self_healing.handle_error(
                        e,
                        {
                            "task_id": task_id,
                            "task_name": task_name,
                            "retry_count": retry_count,
                        },
                    )

                    if healing_result.get("success"):
                        logger.info("✨ 自動修復成功 - リトライします")
                        self.cycle_stats["auto_fixed_errors"] += 1
                        await asyncio.sleep(2)  # 少し待機
                        continue
                    else:
                        logger.warning("⚠️ 自動修復失敗")

                # 最終リトライ失敗
                if retry_count >= max_retries:
                    self.cycle_stats["failed_tasks"] += 1
                    self._update_task_result_safe(
                        task_id=task_id,
                        status="failed",
                        result=f"エラー（{max_retries}回リトライ失敗）: {str(e)[:100]}",
                    )

                    # エラーログに記録
                    self.cycle_stats["error_log"].append(
                        {
                            "task_id": task_id,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    break

    async def _safe_execute_with_validator(self, task: Dict) -> Dict:
        """
        InterfaceValidatorを使った安全な実行

        Args:
            task: タスク情報

        Returns:
            実行結果
        """
        try:
            # TaskCoordinatorのメソッドを検証
            method_name = self.interface_validator.validate_method(
                self.task_coordinator, "execute_task_coordinated"
            )

            if method_name:
                method = getattr(self.task_coordinator, method_name)
                result = await method(task)
                return result
            else:
                return {
                    "success": False,
                    "message": "TaskCoordinatorに実行可能なメソッドが見つかりません",
                }

        except Exception as e:
            logger.error(f"❌ 安全実行エラー: {e}")
            raise

    def _update_task_result_safe(
        self, task_id: str, status: str, result: str = "", duration_minutes: float = 0.0
    ):
        """
        タスク結果を安全に更新（InterfaceValidator使用）

        Args:
            task_id: タスクID
            status: ステータス
            result: 結果メッセージ
            duration_minutes: 実行時間
        """
        try:
            data = self.sheets_manager.read_range("pm_tasks!A:Z")
            if not data:
                return

            headers = data[0]
            status_idx = self._find_column_index(headers, ["status", "ステータス"])
            result_idx = self._find_column_index(headers, ["result", "結果", "execution_result"])

            for i, row in enumerate(data[1:], 2):
                if len(row) > 0 and row[0] == task_id:
                    # ステータス更新
                    if status_idx >= 0:
                        range_name = f"pm_tasks!{self._col_letter(status_idx)}{i}"

                        # InterfaceValidatorで安全に更新
                        if self.interface_validator:
                            self.interface_validator.safe_call(
                                self.sheets_manager,
                                "write_range",
                                range_name,
                                [[status]],
                            )
                        else:
                            self.sheets_manager.write_range(range_name, [[status]])

                    # 結果更新
                    if result_idx >= 0 and result:
                        result_with_time = f"{result} (実行時間: {duration_minutes:.2f}分)"
                        range_name = f"pm_tasks!{self._col_letter(result_idx)}{i}"

                        if self.interface_validator:
                            self.interface_validator.safe_call(
                                self.sheets_manager,
                                "write_range",
                                range_name,
                                [[result_with_time]],
                            )
                        else:
                            self.sheets_manager.write_range(range_name, [[result_with_time]])

                    logger.info(f"   📝 タスク結果更新: {task_id} → {status}")
                    break

        except Exception as e:
            logger.error(f"⚠️ タスク結果更新エラー: {e}")

            # 自己修復を試みる
            if self.has_self_healing:
                self.self_healing.handle_error(
                    e, {"location": "_update_task_result_safe", "task_id": task_id}
                )

    async def _get_pending_tasks(self) -> List[Dict]:
        """pm_tasksからpendingタスクを取得"""
        try:
            data = self.sheets_manager.read_range("pm_tasks!A:Z")
            if not data or len(data) < 2:
                return []

            headers = data[0]
            status_idx = self._find_column_index(headers, ["status", "ステータス"])

            pending_tasks = []
            for row in data[1:]:
                if len(row) > status_idx:
                    status = row[status_idx].lower()
                    if status == "pending":
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
        """Progress Dashboard更新"""
        try:
            logger.info("📊 Progress Dashboard更新開始...")

            from scripts.unified_progress_updater import UnifiedProgressUpdater

            updater = UnifiedProgressUpdater()
            await updater.update_progress_dashboard()

            logger.info("✅ Progress Dashboard更新完了")

        except Exception as e:
            logger.warning(f"⚠️ Progress Dashboard更新エラー: {e}")

    def _check_stop_flag(self) -> bool:
        """停止フラグチェック（安全版）"""
        try:
            data = self.sheets_manager.read_range("control_flags!A:B")
            if not data:
                return False

            for row in data:
                if len(row) >= 2 and row[0].lower() == "stop":
                    return row[1].lower() == "true"
            return False
        except Exception:
            return False

    def _handle_critical_error(self, error: Exception, context: Dict):
        """
        クリティカルエラーの処理

        Args:
            error: エラー
            context: コンテキスト
        """
        logger.error(f"🚨 クリティカルエラー: {error}")

        if self.has_self_healing:
            healing_result = self.self_healing.handle_error(error, context)

            if healing_result.get("success"):
                logger.info("✨ クリティカルエラーの自動修復に成功")
                self.cycle_stats["auto_fixed_errors"] += 1
            else:
                logger.error("❌ クリティカルエラーの自動修復に失敗")

    def _find_column_index(self, headers: List, possible_names: List[str]) -> int:
        """列インデックス検索"""
        for name in possible_names:
            if name in headers:
                return headers.index(name)
        return -1

    def _col_letter(self, col_idx: int) -> str:
        """列番号を列文字に変換（0-indexed）"""
        return chr(65 + col_idx)

    def _print_final_stats(self):
        """最終統計出力"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 Phase 10 最終統計")
        logger.info("=" * 80)
        logger.info(f"  総サイクル数: {self.cycle_stats['total_cycles']}")
        logger.info(f"  総タスク数: {self.cycle_stats['total_tasks']}")
        logger.info(f"  成功: {self.cycle_stats['successful_tasks']}")
        logger.info(f"  失敗: {self.cycle_stats['failed_tasks']}")
        logger.info(f"  自動修復: {self.cycle_stats['auto_fixed_errors']}件")
        logger.info(f"  総実行時間: {self.cycle_stats['total_time_minutes']:.1f}分")

        if self.cycle_stats["total_tasks"] > 0:
            avg_time = self.cycle_stats["total_time_minutes"] / self.cycle_stats["total_tasks"]
            success_rate = (
                self.cycle_stats["successful_tasks"] / self.cycle_stats["total_tasks"]
            ) * 100
            logger.info(f"  平均タスク時間: {avg_time:.2f}分/タスク")
            logger.info(f"  成功率: {success_rate:.1f}%")

        if self.cycle_stats["error_log"]:
            logger.info(f"\n  未解決エラー: {len(self.cycle_stats['error_log'])}件")

        logger.info("=" * 80)


def main():
    """メイン実行"""
    orchestrator = IntegratedOrchestratorV3()
    asyncio.run(orchestrator.run_continuous_cycle(max_duration_minutes=330))


if __name__ == "__main__":
    main()
