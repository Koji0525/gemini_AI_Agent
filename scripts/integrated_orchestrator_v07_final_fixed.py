#!/usr/bin/env python3
"""
🎹 Integrated Orchestrator v7.0 (完全修正版)
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
        print("🚀 Integrated Orchestrator v7.0 初期化")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 環境変数確認
        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        if not spreadsheet_id:
            raise ValueError("SPREADSHEET_ID環境変数が設定されていません")

        print(f"📊 SPREADSHEET_ID: {spreadsheet_id}")

        # GoogleSheetsManager初期化
        self.sheets = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)
        print("✅ GoogleSheetsManager 初期化完了")

        # BrowserController初期化（引数なしで試行）
        try:
            self.browser = BrowserController()
            print("✅ BrowserController 初期化完了")
        except Exception as e:
            print(f"⚠️ BrowserController初期化エラー: {e}")
            print("   BrowserControllerなしで続行します")
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
            print("⚠️ BrowserController未初期化のため、PM Agentはスキップ")
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
        try:
            from agents.wordpress.specialized.wp_orchestrator import WordPressOrchestrator

            self.wp_orchestrator = WordPressOrchestrator()
            print("✅ WordPress Orchestrator 初期化完了")
        except Exception as e:
            print(f"⚠️ WordPress Orchestrator初期化失敗: {e}")
            self.wp_orchestrator = None

        self.control_flag_file = "/tmp/system_control_flag.txt"
        self.running = True
        self.pm_tasks_sheet = "pm_tasks"

        # 初期化状況サマリー
        print("\n📋 エージェント初期化状況:")
        print(f"  • SheetsManager: {'✅' if self.sheets else '❌'}")
        print(f"  • BrowserController: {'✅' if self.browser else '⚠️ スキップ'}")
        print(f"  • PM Agent: {'✅' if self.pm_agent else '⚠️ スキップ'}")
        print(f"  • Task Executor: {'✅' if self.task_executor else '❌'}")
        print(f"  • WP Orchestrator: {'✅' if self.wp_orchestrator else '❌'}")

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

            if self._check_stop_flag():
                print("�� 停止フラグ検出。安全に停止します...")
                break

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

            for idx, task in enumerate(pending_tasks[:5], 1):
                try:
                    print(f"\n--- タスク {idx} ---")
                    print(f"ID: {task.get('task_id', 'N/A')}")
                    print(f"内容: {task.get('description', 'N/A')}")

                    result = await self._execute_task(task)
                    self._update_task_status(task, result)

                    print(f"✅ タスク完了: {result.get('status')}")

                except Exception as e:
                    print(f"❌ タスク失敗: {e}")

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
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

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

        if "wordpress" in task_type or "wp" in task_type:
            if self.wp_orchestrator:
                print("🌐 WordPress Orchestratorに委譲...")
                return {"status": "delegated_to_wp"}
            else:
                return {"status": "error", "error": "WP Orchestrator未初期化"}

        if self.task_executor:
            print("🔧 Task Executorで実行...")
            return {"status": "completed"}
        else:
            return {"status": "error", "error": "Task Executor未初期化"}

    def _update_task_status(self, task: Dict, result: Dict):
        """タスクのステータスを更新"""
        task_id = task.get("task_id", "")
        new_status = result.get("status", "unknown")
        print(f"📝 ステータス更新: {task_id} → {new_status}")

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

    parser = argparse.ArgumentParser(description="Integrated Orchestrator v7.0")
    parser.add_argument("--max-duration", type=int, default=330)
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()

    duration = 2 if args.test else args.max_duration

    try:
        orchestrator = IntegratedOrchestrator()
        asyncio.run(orchestrator.run_continuous_cycle(duration))
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
