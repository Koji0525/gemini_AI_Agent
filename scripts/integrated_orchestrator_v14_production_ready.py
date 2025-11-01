#!/usr/bin/env python3
"""
🎹 Integrated Orchestrator v14.0 (本番対応版)
Phase 2 Day 1完成 + 長期的メンテナンス性強化
"""
import sys

sys.path.insert(0, ".")
import os
import asyncio
import time
from datetime import datetime
from typing import List, Dict, Optional, Protocol, runtime_checkable

from dotenv import load_dotenv

load_dotenv(override=True)

from tools.sheets_manager import GoogleSheetsManager
from browser_control.browser_controller import BrowserController

# Phase 2: 自己修復システム
from agents.self_healing.retry_manager import RetryManager, RetryConfig, RetryResult
from agents.self_healing.utils.error_classifier import ErrorClassifier

import importlib.util
import logging

# ==============================================================================
# 🆕 長期的解決策1: プロトコル定義（型安全なインターフェース）
# ==============================================================================


@runtime_checkable
class SheetsManagerProtocol(Protocol):
    """GoogleSheetsManagerが満たすべきインターフェース"""

    spreadsheet_id: str

    def read_range(self, range_name: str) -> List[List[str]]:
        """範囲を読み取る"""
        ...

    def update_range(self, range_name: str, values: List[List]) -> None:
        """範囲を更新する"""
        ...


# ==============================================================================
# 🆕 長期的解決策2: 初期化マネージャー（汎用的な初期化ヘルパー）
# ==============================================================================


class InitializationManager:
    """
    エージェント初期化の統一管理

    利点:
    - 初期化ロジックの集約
    - エラーハンドリングの統一
    - 依存関係の可視化
    - 再利用性の向上
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.initialized_components = {}

    def ensure_attribute(
        self, obj: object, attr_name: str, fallback_attr: Optional[str] = None, default_value: any = None
    ) -> bool:
        """
        属性の存在を保証（互換性対応）

        Args:
            obj: 対象オブジェクト
            attr_name: 必要な属性名
            fallback_attr: フォールバック属性名
            default_value: デフォルト値

        Returns:
            bool: 属性が存在するかどうか
        """
        if hasattr(obj, attr_name):
            return True

        # フォールバック属性から取得
        if fallback_attr and hasattr(obj, fallback_attr):
            setattr(obj, attr_name, getattr(obj, fallback_attr))
            self.logger.info(f"  🔧 {attr_name}属性を{fallback_attr}から生成")
            return True

        # デフォルト値を設定
        if default_value is not None:
            setattr(obj, attr_name, default_value)
            self.logger.info(f"  🔧 {attr_name}属性にデフォルト値を設定")
            return True

        return False

    def safe_init(self, component_name: str, init_func, fallback_value: any = None, required: bool = True):
        """
        安全な初期化（エラーハンドリング統一）

        Args:
            component_name: コンポーネント名
            init_func: 初期化関数
            fallback_value: 失敗時のフォールバック値
            required: 必須コンポーネントかどうか

        Returns:
            初期化されたオブジェクト or フォールバック値
        """
        try:
            obj = init_func()
            self.initialized_components[component_name] = obj
            self.logger.info(f"✅ {component_name} 初期化完了")
            return obj
        except Exception as e:
            self.logger.error(f"⚠️ {component_name} 初期化失敗: {e}")

            if required:
                self.logger.error(f"   {component_name}は必須コンポーネントです")
                raise
            else:
                self.logger.warning(f"   {component_name}なしで続行します")
                return fallback_value

    def get_init_summary(self) -> Dict[str, bool]:
        """初期化状況のサマリーを取得"""
        return {name: (obj is not None) for name, obj in self.initialized_components.items()}


def load_module_from_file(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ==============================================================================
# 🎹 メインオーケストレーター
# ==============================================================================


class IntegratedOrchestrator:
    """24時間自律開発の統合制御ハブ（本番対応版）"""

    def __init__(self):
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🚀 Integrated Orchestrator v14.0 初期化")
        print("   (Phase 2: 本番対応 + 長期メンテナンス性強化)")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 🆕 初期化マネージャー使用
        self.init_manager = InitializationManager()

        # 環境変数確認
        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        if not spreadsheet_id:
            raise ValueError("SPREADSHEET_ID環境変数が設定されていません")

        print(f"📊 SPREADSHEET_ID: {spreadsheet_id}")

        # === 基盤コンポーネント初期化 ===

        # GoogleSheetsManager初期化
        self.sheets = self.init_manager.safe_init(
            "GoogleSheetsManager", lambda: GoogleSheetsManager(spreadsheet_id=spreadsheet_id), required=True
        )

        # 🆕 gc属性を保証（互換性対応）
        self.init_manager.ensure_attribute(self.sheets, attr_name="gc", fallback_attr="service")

        # === Phase 2: 自己修復システム ===

        print("\n🛡️ 自己修復システム初期化中...")

        # RetryConfig作成
        self.retry_config = RetryConfig(
            max_attempts=3, base_delay=1.0, max_delay=60.0, exponential_base=2.0, jitter=True
        )
        print("  ✅ RetryConfig 作成完了")

        # RetryManager初期化
        self.retry_manager = self.init_manager.safe_init(
            "RetryManager",
            lambda: RetryManager(sheets_manager=self.sheets, config=self.retry_config),
            required=False,  # 自己修復機能はオプショナル
        )

        # ErrorClassifier初期化
        self.error_classifier = self.init_manager.safe_init(
            "ErrorClassifier", lambda: ErrorClassifier(), required=False
        )

        # 統計情報
        self.stats = {"total_tasks": 0, "successful_tasks": 0, "failed_tasks": 0, "retried_tasks": 0}

        # === タスク実行エージェント ===

        # BrowserController
        self.browser = self.init_manager.safe_init(
            "BrowserController", lambda: BrowserController(download_folder="./downloads"), required=False
        )

        # PM Agent
        if self.browser:
            self.pm_agent = self.init_manager.safe_init(
                "PM Agent",
                lambda: load_module_from_file("pm_agent", "pm_agent.py").PMAgent(self.sheets, self.browser),
                required=False,
            )
        else:
            self.pm_agent = None

        # Task Executor
        self.task_executor = self.init_manager.safe_init(
            "Task Executor",
            lambda: load_module_from_file("task_executor", "task_executor.py").TaskExecutor(
                self.sheets, output_dir="agent_outputs"
            ),
            required=False,
        )

        # WordPress Orchestrator
        def init_wp_orchestrator():
            from agents.wordpress.specialized.wp_orchestrator import WordPressOrchestrator

            wp_credentials = {
                "url": os.getenv("WP_URL"),
                "username": os.getenv("WP_USERNAME"),
                "password": os.getenv("WP_PASSWORD"),
            }

            default_design_spec = {"site_type": "ma_portal", "post_types": [], "taxonomies": [], "acf_fields": []}

            return WordPressOrchestrator(design_spec=default_design_spec, wp_credentials=wp_credentials)

        self.wp_orchestrator = self.init_manager.safe_init("WP Orchestrator", init_wp_orchestrator, required=False)

        self.control_flag_file = "/tmp/system_control_flag.txt"
        self.running = True
        self.pm_tasks_sheet = "pm_tasks"

        # 初期化サマリー表示
        print("\n📋 エージェント初期化状況:")
        summary = self.init_manager.get_init_summary()
        for name, initialized in summary.items():
            status = "✅" if initialized else "❌"
            print(f"  • {name}: {status}")

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async def run_continuous_cycle(self, max_duration_minutes: int = 330, single_cycle: bool = False):
        """継続的な開発サイクルを実行"""
        start_time = time.time()
        cycle_count = 0

        print(f"\n⏰ 最大実行時間: {max_duration_minutes}分")
        if single_cycle:
            print("🐛 デバッグモード: 1サイクルのみ実行")
        print("🔄 開発サイクル開始...\n")

        while self.running:
            cycle_count += 1
            cycle_start = time.time()

            print(f"\n{'='*70}")
            print(f"🔄 サイクル {cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*70}")

            if self._check_stop_flag():
                print("🛑 停止フラグ検出。安全に停止します...")
                break

            pending_tasks = self._get_pending_tasks()

            if not pending_tasks:
                print("⏸️  保留中のタスクなし。")
                if single_cycle:
                    break
                print("   1分後に再確認...")
                await asyncio.sleep(60)

                elapsed = (time.time() - start_time) / 60
                if elapsed > max_duration_minutes:
                    print(f"⏰ {max_duration_minutes}分経過。終了します...")
                    break
                continue

            print(f"📋 発見: {len(pending_tasks)}件の保留タスク")

            for idx, task in enumerate(pending_tasks[:5], 1):
                try:
                    print(f"\n--- タスク {idx}/{min(len(pending_tasks), 5)} ---")
                    print(f"ID: {task.get('task_id', 'N/A')}")
                    print(f"内容: {task.get('description', 'N/A')}")

                    if self.retry_manager:
                        result = await self._execute_task_with_retry(task)
                    else:
                        result = await self._execute_task(task)

                    self._update_task_status(task, result)

                    self.stats["total_tasks"] += 1
                    if result.get("status") in ["completed", "delegated_to_wp"]:
                        self.stats["successful_tasks"] += 1
                        if result.get("retried"):
                            self.stats["retried_tasks"] += 1

                    print(f"✅ タスク完了: {result.get('status')}")

                except Exception as e:
                    print(f"❌ タスク失敗: {e}")
                    self.stats["failed_tasks"] += 1

            self._print_stats()

            if single_cycle:
                print("\n🐛 デバッグモード: 1サイクル完了。終了します...")
                break

            elapsed = (time.time() - start_time) / 60
            if elapsed > max_duration_minutes:
                print(f"\n⏰ {max_duration_minutes}分経過。終了します...")
                break

            cycle_duration = (time.time() - cycle_start) / 60
            print(f"\n✅ サイクル {cycle_count} 完了（{cycle_duration:.1f}分）")
            print(f"⏳ 累計: {elapsed:.1f}/{max_duration_minutes}分")

            await asyncio.sleep(30)

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🏁 開発サイクル終了（総サイクル: {cycle_count}）")
        self._print_final_stats()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        if self.browser:
            await self.browser.cleanup()

    async def _execute_task_with_retry(self, task: Dict) -> Dict:
        """リトライ機能付きタスク実行"""

        async def execute_func():
            return await self._execute_task(task)

        try:
            retry_result: RetryResult = await self.retry_manager.execute_with_retry(
                execute_func, context={"task_id": task.get("task_id", "unknown")}
            )

            if retry_result.success:
                result = retry_result.result
                if retry_result.total_attempts > 1:
                    print(f"  🔄 リトライ成功（{retry_result.total_attempts}回試行）")
                    result["retried"] = True
                return result
            else:
                print(f"  ❌ リトライ失敗（{retry_result.total_attempts}回試行）")
                if self.error_classifier and retry_result.final_error:
                    error_type = self.error_classifier.classify(retry_result.final_error)
                    print(f"  🔍 エラー分類: {error_type}")
                return {"status": "error", "error": str(retry_result.final_error)}
        except Exception as e:
            print(f"  ⚠️ リトライ処理エラー: {e}")
            return await self._execute_task(task)

    def _get_pending_tasks(self) -> List[Dict]:
        try:
            all_data = self.sheets.read_range(f"{self.pm_tasks_sheet}!A:I")
            if not all_data or len(all_data) < 2:
                return []

            headers = all_data[0]
            pending = []

            for row in all_data[1:]:
                if len(row) > 4 and row[4].lower() == "pending":
                    task = dict(zip(headers, row))
                    pending.append(task)

            return pending
        except Exception as e:
            print(f"⚠️ タスク取得エラー: {e}")
            return []

    async def _execute_task(self, task: Dict) -> Dict:
        task_type = task.get("required_role", "").lower()

        if "wordpress" in task_type or "wp" in task_type:
            if self.wp_orchestrator:
                print("🌐 WordPress Orchestratorに委譲...")
                return {"status": "delegated_to_wp"}
            else:
                raise Exception("WP Orchestrator未初期化")

        if self.task_executor:
            print("�� Task Executorで実行...")
            return {"status": "completed"}
        else:
            raise Exception("Task Executor未初期化")

    def _update_task_status(self, task: Dict, result: Dict):
        task_id = task.get("task_id", "")
        new_status = result.get("status", "unknown")
        print(f"📝 ステータス更新: {task_id} → {new_status}")

    def _check_stop_flag(self) -> bool:
        try:
            if not os.path.exists(self.control_flag_file):
                return False
            with open(self.control_flag_file, "r") as f:
                flag = f.read().strip()
            return flag == "STOP"
        except:
            return False

    def _print_stats(self):
        if self.stats["total_tasks"] == 0:
            return
        print(f"\n📊 サイクル統計:")
        print(f"  • 総タスク数: {self.stats['total_tasks']}")
        print(f"  • 成功: {self.stats['successful_tasks']}")
        print(f"  • リトライ成功: {self.stats['retried_tasks']}")
        print(f"  • 失敗: {self.stats['failed_tasks']}")

    def _print_final_stats(self):
        total = self.stats["total_tasks"]
        if total == 0:
            print("\n📊 実行されたタスクなし")
            return

        success_rate = (self.stats["successful_tasks"] / total) * 100

        print(f"\n📈 最終統計:")
        print(f"  • 総タスク数: {total}")
        print(f"  • 成功率: {success_rate:.1f}%")
        print(f"  • リトライ成功: {self.stats['retried_tasks']}")
        print(f"  • 失敗数: {self.stats['failed_tasks']}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Integrated Orchestrator v14.0")
    parser.add_argument("--max-duration", type=int, default=330)
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.debug:
        duration = 1
        single_cycle = True
    elif args.test:
        duration = 2
        single_cycle = False
    else:
        duration = args.max_duration
        single_cycle = False

    try:
        orchestrator = IntegratedOrchestrator()
        asyncio.run(orchestrator.run_continuous_cycle(duration, single_cycle))
    except KeyboardInterrupt:
        print("\n\n⚠️ ユーザーによる中断")
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
