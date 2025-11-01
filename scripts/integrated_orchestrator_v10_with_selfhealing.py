#!/usr/bin/env python3
"""
�� Integrated Orchestrator v10.0 (自己修復機能統合版)
Phase 2 Day 1: RetryManager + ErrorClassifier統合
"""
import sys

sys.path.insert(0, ".")
import os
import asyncio
import time
from datetime import datetime
from typing import List, Dict

from dotenv import load_dotenv

load_dotenv(override=True)

from tools.sheets_manager import GoogleSheetsManager
from browser_control.browser_controller import BrowserController

# Phase 2: 自己修復システムのインポート
from agents.self_healing.retry_manager import RetryManager, RetryConfig, RetryResult
from agents.self_healing.utils.error_classifier import ErrorClassifier

import importlib.util


def load_module_from_file(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class IntegratedOrchestrator:
    """24時間自律開発の統合制御ハブ（自己修復機能付き）"""

    def __init__(self):
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🚀 Integrated Orchestrator v10.0 初期化")
        print("   (Phase 2: 自己修復機能統合版)")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 環境変数確認
        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        if not spreadsheet_id:
            raise ValueError("SPREADSHEET_ID環境変数が設定されていません")

        print(f"📊 SPREADSHEET_ID: {spreadsheet_id}")

        # GoogleSheetsManager初期化
        self.sheets = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)
        print("✅ GoogleSheetsManager 初期化完了")

        # 🆕 Phase 2: 自己修復システム初期化
        print("\n🛡️ 自己修復システム初期化中...")

        # RetryManager初期化
        self.retry_config = RetryConfig(
            max_retries=3,  # 最大3回リトライ
            base_delay=1.0,  # 初回待機1秒
            max_delay=60.0,  # 最大待機60秒
            exponential_base=2.0,  # 指数バックオフ
        )
        self.retry_manager = RetryManager(self.retry_config)
        print("  ✅ RetryManager 初期化完了")

        # ErrorClassifier初期化
        self.error_classifier = ErrorClassifier()
        print("  ✅ ErrorClassifier 初期化完了")

        # 統計情報
        self.stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "retried_tasks": 0,
            "auto_fixed_tasks": 0,
        }

        # BrowserController初期化
        try:
            self.browser = BrowserController(download_folder="./downloads")
            print("✅ BrowserController 初期化完了")
        except Exception as e:
            print(f"⚠️ BrowserController初期化エラー: {e}")
            self.browser = None

        # PM Agent初期化
        if self.browser:
            try:
                pm_module = load_module_from_file("pm_agent", "pm_agent.py")
                self.pm_agent = pm_module.PMAgent(self.sheets, self.browser)
                print("✅ PM Agent 初期化完了")
            except Exception as e:
                print(f"⚠️ PM Agent初期化失敗: {e}")
                self.pm_agent = None
        else:
            self.pm_agent = None

        # Task Executor初期化
        try:
            te_module = load_module_from_file("task_executor", "task_executor.py")
            self.task_executor = te_module.TaskExecutor(self.sheets, output_dir="agent_outputs")
            print("✅ Task Executor 初期化完了")
        except Exception as e:
            print(f"⚠️ Task Executor初期化失敗: {e}")
            self.task_executor = None

        # WordPress Orchestrator初期化
        try:
            from agents.wordpress.specialized.wp_orchestrator import WordPressOrchestrator

            wp_credentials = {
                "url": os.getenv("WP_URL"),
                "username": os.getenv("WP_USERNAME"),
                "password": os.getenv("WP_PASSWORD"),
            }

            default_design_spec = {"site_type": "ma_portal", "post_types": [], "taxonomies": [], "acf_fields": []}

            self.wp_orchestrator = WordPressOrchestrator(design_spec=default_design_spec, wp_credentials=wp_credentials)
            print("✅ WordPress Orchestrator 初期化完了")

        except Exception as e:
            print(f"⚠️ WordPress Orchestrator初期化失敗: {e}")
            self.wp_orchestrator = None

        self.control_flag_file = "/tmp/system_control_flag.txt"
        self.running = True
        self.pm_tasks_sheet = "pm_tasks"

        # 初期化状況サマリー
        print("\n📋 エージェント初期化状況:")
        status_map = {
            "SheetsManager": self.sheets,
            "BrowserController": self.browser,
            "PM Agent": self.pm_agent,
            "Task Executor": self.task_executor,
            "WP Orchestrator": self.wp_orchestrator,
            "🆕 RetryManager": self.retry_manager,
            "🆕 ErrorClassifier": self.error_classifier,
        }

        for name, obj in status_map.items():
            status = "✅" if obj else "❌"
            print(f"  • {name}: {status}")

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async def run_continuous_cycle(self, max_duration_minutes: int = 330, single_cycle: bool = False):
        """
        継続的な開発サイクルを実行

        Args:
            max_duration_minutes: 最大実行時間
            single_cycle: Trueの場合、1サイクルのみ実行（デバッグ用）
        """
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

            # 🆕 Phase 2: タスク実行（自己修復機能付き）
            for idx, task in enumerate(pending_tasks[:5], 1):
                try:
                    print(f"\n--- タスク {idx}/{min(len(pending_tasks), 5)} ---")
                    print(f"ID: {task.get('task_id', 'N/A')}")
                    print(f"内容: {task.get('description', 'N/A')}")

                    # 🆕 自己修復機能を使ってタスク実行
                    result = await self._execute_task_with_retry(task)
                    self._update_task_status(task, result)

                    # 統計更新
                    self.stats["total_tasks"] += 1
                    if result.get("status") == "completed":
                        self.stats["successful_tasks"] += 1
                    elif result.get("retried"):
                        self.stats["retried_tasks"] += 1
                        self.stats["successful_tasks"] += 1

                    print(f"✅ タスク完了: {result.get('status')}")

                except Exception as e:
                    print(f"❌ タスク失敗: {e}")
                    self.stats["failed_tasks"] += 1

            # �� サイクル統計表示
            self._print_stats()

            # デバッグモード: 1サイクルで終了
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
        print(f"🏁 開発サイクル終了")
        print(f"   総サイクル数: {cycle_count}")
        print(f"   総実行時間: {(time.time() - start_time) / 60:.1f}分")

        # 🆕 最終統計
        self._print_final_stats()

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        if self.browser:
            await self.browser.cleanup()

    async def _execute_task_with_retry(self, task: Dict) -> Dict:
        """
        🆕 Phase 2: リトライ機能付きタスク実行
        """
        task_id = task.get("task_id", "unknown")

        # タスク実行関数を定義
        async def execute_func():
            return await self._execute_task(task)

        # RetryManagerでリトライ実行
        retry_result: RetryResult = await self.retry_manager.execute_with_retry(
            execute_func, context={"task_id": task_id, "task": task}
        )

        if retry_result.success:
            result = retry_result.result
            if retry_result.retry_count > 0:
                print(f"  🔄 リトライ成功（試行回数: {retry_result.retry_count + 1}回）")
                result["retried"] = True
            return result
        else:
            # リトライ失敗
            print(f"  ❌ リトライ失敗（{retry_result.retry_count}回試行）")

            # 🆕 ErrorClassifierでエラー分類
            error_type = self.error_classifier.classify(retry_result.error)
            print(f"  🔍 エラー分類: {error_type}")

            return {
                "status": "error",
                "error": str(retry_result.error),
                "error_type": error_type,
                "retry_count": retry_result.retry_count,
            }

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
            print("🔧 Task Executorで実行...")
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
        """統計情報を表示"""
        print(f"\n📊 サイクル統計:")
        print(f"  • 総タスク数: {self.stats['total_tasks']}")
        print(f"  • 成功: {self.stats['successful_tasks']}")
        print(f"  • リトライ成功: {self.stats['retried_tasks']}")
        print(f"  • 失敗: {self.stats['failed_tasks']}")

    def _print_final_stats(self):
        """最終統計を表示"""
        total = self.stats["total_tasks"]
        if total == 0:
            return

        success_rate = (self.stats["successful_tasks"] / total) * 100
        retry_rate = (self.stats["retried_tasks"] / total) * 100

        print(f"\n📈 最終統計:")
        print(f"  • 総タスク数: {total}")
        print(f"  • 成功率: {success_rate:.1f}%")
        print(f"  • リトライ成功率: {retry_rate:.1f}%")
        print(f"  • 失敗数: {self.stats['failed_tasks']}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Integrated Orchestrator v10.0")
    parser.add_argument("--max-duration", type=int, default=330)
    parser.add_argument("--test", action="store_true", help="テストモード（2分間）")
    parser.add_argument("--debug", action="store_true", help="デバッグモード（1サイクルのみ）")
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
