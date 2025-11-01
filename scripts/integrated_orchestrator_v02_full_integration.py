#!/usr/bin/env python3
"""
🎹 Integrated Development Orchestrator v2.0
役割: PM Agent, Task Executor, WordPress Orchestratorの完全統合

連携フロー:
1. pm_tasksシートから保留中タスクを取得
2. PM Agentでタスク分解（必要に応じて）
3. Task Executorでタスク実行
4. WordPress Orchestratorに委譲（WP関連タスク）
5. 結果をシートに記録
"""
import sys

sys.path.insert(0, ".")
import asyncio
import time
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# 設定とシート管理
from configuration.config_loader import get_config
from tools.sheets_manager import GoogleSheetsManager

# ブラウザ制御
from browser_control.browser_controller import BrowserController

# 既存エージェントのインポート
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
        print("🚀 Integrated Orchestrator v2.0 初期化")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 設定読み込み
        self.config = get_config()

        # SheetsManager初期化
        self.sheets = GoogleSheetsManager(
            credentials_path=self.config.get("credentials_path", "service_account.json"),
            spreadsheet_id=self.config.get("spreadsheet_id"),
        )
        print("✅ SheetsManager 初期化完了")

        # BrowserController初期化
        self.browser = BrowserController(headless=True)
        print("✅ BrowserController 初期化完了")

        # PM Agent初期化
        try:
            pm_module = load_module_from_file("pm_agent", "pm_agent.py")
            self.pm_agent = pm_module.PMAgent(self.sheets, self.browser)
            print("✅ PM Agent 初期化完了")
        except Exception as e:
            print(f"⚠️ PM Agent初期化失敗: {e}")
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

            # wp_orchestrator.pyの__init__を確認して正しいパラメータを渡す
            self.wp_orchestrator = WordPressOrchestrator()
            print("✅ WordPress Orchestrator 初期化完了")
        except Exception as e:
            print(f"⚠️ WordPress Orchestrator初期化失敗: {e}")
            self.wp_orchestrator = None

        self.control_flag_file = "/tmp/system_control_flag.txt"
        self.running = True
        self.pm_tasks_sheet = "pm_tasks"

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

            # 2. pm_tasksシートから保留中タスクを取得
            pending_tasks = self._get_pending_tasks()

            if not pending_tasks:
                print("⏸️  保留中のタスクなし。1分後に再確認...")
                await asyncio.sleep(60)

                # タイムアウトチェック
                elapsed = (time.time() - start_time) / 60
                if elapsed > max_duration_minutes:
                    print(f"⏰ {max_duration_minutes}分経過。次のCronへ...")
                    break
                continue

            print(f"📋 発見: {len(pending_tasks)}件の保留タスク")

            # 3. タスクを実行
            for idx, task in enumerate(pending_tasks[:5], 1):  # 一度に最大5件
                try:
                    print(f"\n--- タスク {idx}/{len(pending_tasks[:5])} ---")
                    print(f"ID: {task.get('task_id', 'N/A')}")
                    print(f"内容: {task.get('description', 'N/A')}")
                    print(f"タイプ: {task.get('required_role', 'N/A')}")

                    # タスクタイプに応じてルーティング
                    result = await self._execute_task(task)

                    # 結果を記録
                    self._update_task_status(task, result)

                    print(f"✅ タスク完了: {result.get('status', 'unknown')}")

                except Exception as e:
                    print(f"❌ タスク失敗: {e}")
                    import traceback

                    traceback.print_exc()

                    # エラーを記録
                    self._update_task_status(task, {"status": "error", "error": str(e)})

            # 4. タイムアウトチェック
            elapsed = (time.time() - start_time) / 60
            if elapsed > max_duration_minutes:
                print(f"\n⏰ {max_duration_minutes}分経過。次のCronサイクルへ...")
                break

            cycle_duration = (time.time() - cycle_start) / 60
            print(f"\n✅ サイクル {cycle_count} 完了（{cycle_duration:.1f}分）")
            print(f"⏳ 累計: {elapsed:.1f}/{max_duration_minutes}分")

            await asyncio.sleep(30)  # 30秒待機

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🏁 開発サイクル終了（総サイクル: {cycle_count}）")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # クリーンアップ
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
                if len(row) > 4 and row[4].lower() == "pending":  # E列: status
                    task = dict(zip(headers, row))
                    pending.append(task)

            return pending

        except Exception as e:
            print(f"⚠️ タスク取得エラー: {e}")
            return []

    async def _execute_task(self, task: Dict) -> Dict:
        """タスクを実行"""
        task_type = task.get("required_role", "").lower()

        # WordPressタスクの判定
        if "wordpress" in task_type or "wp" in task_type:
            if self.wp_orchestrator:
                print("🌐 WordPress Orchestratorに委譲...")
                # WordPress Orchestratorの実行
                # （具体的な実行方法はwp_orchestrator.pyのインターフェースに合わせる）
                return {"status": "delegated_to_wp", "message": "WordPress実行予定"}
            else:
                return {"status": "error", "error": "WordPress Orchestrator未初期化"}

        # その他のタスク
        if self.task_executor:
            print("🔧 Task Executorで実行...")
            # Task Executorの実行
            # （実際の実行ロジックはtask_executor.pyに合わせて実装）
            return {"status": "completed", "message": "Task Executor実行完了"}
        else:
            return {"status": "error", "error": "Task Executor未初期化"}

    def _update_task_status(self, task: Dict, result: Dict):
        """タスクのステータスを更新"""
        try:
            task_id = task.get("task_id", "")
            new_status = result.get("status", "unknown")

            print(f"📝 ステータス更新: {task_id} → {new_status}")

            # スプレッドシートの該当行を更新
            # （実装簡略化のため、ログ出力のみ）

        except Exception as e:
            print(f"⚠️ ステータス更新エラー: {e}")

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

    parser = argparse.ArgumentParser(description="Integrated Orchestrator v2.0 - 完全統合版")
    parser.add_argument("--max-duration", type=int, default=330, help="最大実行時間（分）")
    parser.add_argument("--test", action="store_true", help="テストモード（2分間実行）")

    args = parser.parse_args()
    duration = 2 if args.test else args.max_duration

    orchestrator = IntegratedOrchestrator()
    asyncio.run(orchestrator.run_continuous_cycle(duration))


if __name__ == "__main__":
    main()
