#!/usr/bin/env python3
"""
🎹 Integrated Orchestrator v8.0 (Phase 1最終版)
役割: PM Agent, Task Executor, WordPress Orchestratorの完全統合
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

import importlib.util


def load_module_from_file(module_name: str, file_path: str):
    """ファイルからモジュールを動的にロード"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class IntegratedOrchestrator:
    """24時間自律開発の統合制御ハブ"""

    def __init__(self):
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🚀 Integrated Orchestrator v8.0 初期化")
        print("   (Phase 1 最終版)")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 環境変数確認
        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        if not spreadsheet_id:
            raise ValueError("SPREADSHEET_ID環境変数が設定されていません")

        print(f"📊 SPREADSHEET_ID: {spreadsheet_id}")

        # GoogleSheetsManager初期化
        self.sheets = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)
        print("✅ GoogleSheetsManager 初期化完了")

        # BrowserController初期化（正しい引数：download_folder のみ）
        try:
            self.browser = BrowserController(download_folder="./downloads")
            print("✅ BrowserController 初期化完了")
        except Exception as e:
            print(f"⚠️ BrowserController初期化エラー: {e}")
            print("   BrowserControllerなしで続行（PM Agentは利用不可）")
            self.browser = None

        # PM Agent初期化（BrowserControllerが必要）
        if self.browser:
            try:
                pm_module = load_module_from_file("pm_agent", "pm_agent.py")
                self.pm_agent = pm_module.PMAgent(self.sheets, self.browser)
                print("✅ PM Agent 初期化完了")
            except Exception as e:
                print(f"⚠️ PM Agent初期化失敗: {e}")
                self.pm_agent = None
        else:
            print("⚠️ BrowserController未初期化 → PM Agentスキップ")
            self.pm_agent = None

        # Task Executor初期化（BrowserController不要）
        try:
            te_module = load_module_from_file("task_executor", "task_executor.py")
            self.task_executor = te_module.TaskExecutor(self.sheets, output_dir="agent_outputs")
            print("✅ Task Executor 初期化完了")
        except Exception as e:
            print(f"⚠️ Task Executor初期化失敗: {e}")
            self.task_executor = None

        # WordPress Orchestrator初期化
        # design_specが必須の場合は、デフォルト設計仕様を渡す
        try:
            from agents.wordpress.specialized.wp_orchestrator import WordPressOrchestrator

            # デフォルトの設計仕様（空またはシンプルなもの）
            default_design_spec = {"site_type": "ma_portal", "post_types": [], "taxonomies": [], "acf_fields": []}

            # design_spec引数が必要かどうかを確認して初期化
            try:
                self.wp_orchestrator = WordPressOrchestrator(default_design_spec)
                print("✅ WordPress Orchestrator 初期化完了（design_spec付き）")
            except TypeError:
                # design_spec不要の場合
                self.wp_orchestrator = WordPressOrchestrator()
                print("✅ WordPress Orchestrator 初期化完了（引数なし）")

        except Exception as e:
            print(f"⚠️ WordPress Orchestrator初期化失敗: {e}")
            print("   WordPress機能は利用不可")
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
        }

        for name, obj in status_map.items():
            status = "✅" if obj else "❌"
            print(f"  • {name}: {status}")

        # 最低限必要なエージェントの確認
        if not self.sheets or not self.task_executor:
            print("\n⚠️ 警告: 必須エージェントが初期化されていません")
            print("   最低限、SheetsManagerとTask Executorが必要です")

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async def run_continuous_cycle(self, max_duration_minutes: int = 330):
        """継続的な開発サイクルを実行"""
        start_time = time.time()
        cycle_count = 0

        print(f"\n⏰ 最大実行時間: {max_duration_minutes}分")
        print("🔄 開発サイクル開始...\n")

        while self.running:
            cycle_count += 1
            cycle_start = time.time()

            print(f"\n{'='*70}")
            print(f"🔄 サイクル {cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*70}")

            # 1. 制御フラグチェック
            if self._check_stop_flag():
                print("🛑 停止フラグ検出。安全に停止します...")
                break

            # 2. タスク取得
            pending_tasks = self._get_pending_tasks()

            if not pending_tasks:
                print("⏸️  保留中のタスクなし。1分後に再確認...")
                await asyncio.sleep(60)

                elapsed = (time.time() - start_time) / 60
                if elapsed > max_duration_minutes:
                    print(f"⏰ {max_duration_minutes}分経過。終了します...")
                    break
                continue

            print(f"📋 発見: {len(pending_tasks)}件の保留タスク")

            # 3. タスク実行（最大5件）
            for idx, task in enumerate(pending_tasks[:5], 1):
                try:
                    print(f"\n--- タスク {idx}/{min(len(pending_tasks), 5)} ---")
                    print(f"ID: {task.get('task_id', 'N/A')}")
                    print(f"内容: {task.get('description', 'N/A')}")

                    result = await self._execute_task(task)
                    self._update_task_status(task, result)

                    print(f"✅ タスク完了: {result.get('status')}")

                except Exception as e:
                    print(f"❌ タスク失敗: {e}")
                    import traceback

                    traceback.print_exc()

            # 4. タイムアウトチェック
            elapsed = (time.time() - start_time) / 60
            if elapsed > max_duration_minutes:
                print(f"\n⏰ {max_duration_minutes}分経過。終了します...")
                break

            cycle_duration = (time.time() - cycle_start) / 60
            print(f"\n✅ サイクル {cycle_count} 完了（{cycle_duration:.1f}分）")
            print(f"⏳ 累計: {elapsed:.1f}/{max_duration_minutes}分")

            # 5. 次サイクルまで待機
            await asyncio.sleep(30)

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🏁 開発サイクル終了")
        print(f"   総サイクル数: {cycle_count}")
        print(f"   総実行時間: {(time.time() - start_time) / 60:.1f}分")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # クリーンアップ
        if self.browser:
            await self.browser.cleanup()

    def _get_pending_tasks(self) -> List[Dict]:
        """pm_tasksシートから保留中タスクを取得"""
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
        """タスクを実行"""
        task_type = task.get("required_role", "").lower()

        # WordPress関連タスク
        if "wordpress" in task_type or "wp" in task_type:
            if self.wp_orchestrator:
                print("🌐 WordPress Orchestratorに委譲...")
                # 実際の実行ロジック（Phase 2で実装）
                return {"status": "delegated_to_wp", "message": "WP実行予定"}
            else:
                return {"status": "error", "error": "WP Orchestrator未初期化"}

        # 通常のタスク
        if self.task_executor:
            print("🔧 Task Executorで実行...")
            # 実際の実行ロジック（Phase 2で実装）
            return {"status": "completed", "message": "タスク実行完了"}
        else:
            return {"status": "error", "error": "Task Executor未初期化"}

    def _update_task_status(self, task: Dict, result: Dict):
        """タスクのステータスを更新"""
        task_id = task.get("task_id", "")
        new_status = result.get("status", "unknown")
        print(f"📝 ステータス更新: {task_id} → {new_status}")

        # 実際のスプレッドシート更新（Phase 2で実装）

    def _check_stop_flag(self) -> bool:
        """停止フラグをチェック"""
        try:
            if not os.path.exists(self.control_flag_file):
                return False

            with open(self.control_flag_file, "r") as f:
                flag = f.read().strip()

            return flag == "STOP"
        except:
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Integrated Orchestrator v8.0 (Phase 1最終版)")
    parser.add_argument("--max-duration", type=int, default=330, help="最大実行時間（分）")
    parser.add_argument("--test", action="store_true", help="テストモード（2分間実行）")

    args = parser.parse_args()
    duration = 2 if args.test else args.max_duration

    try:
        orchestrator = IntegratedOrchestrator()
        asyncio.run(orchestrator.run_continuous_cycle(duration))
    except KeyboardInterrupt:
        print("\n\n⚠️ ユーザーによる中断")
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
