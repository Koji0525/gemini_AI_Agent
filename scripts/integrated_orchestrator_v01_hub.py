#!/usr/bin/env python3
"""
🎹 Integrated Development Orchestrator v1.1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
役割: 全エージェントの統合制御ハブ

【v1.1 変更の理由】
何が起きた:
- ModuleNotFoundError: task_executor のインポートエラー
- task_executor/__init__.py が古いパスを参照

原因:
- task_executor パッケージの __init__.py が存在
- プロジェクトルートの task_executor.py を直接インポートできない

狙い:
- sys.path で明示的にプロジェクトルートを追加
- importlib で動的にモジュールをロード
- インポートエラーを完全回避

【統合フロー】
GitHub Actions (6時間ごと)
    ↓
IntegratedOrchestrator.run_continuous_cycle()
    ↓
    ├─→ 1. pm_task_queue から pending タスク取得
    ├─→ 2. task_executor.execute_single_task() 実行
    └─→ 3. 進捗をスプレッドシートに記録

【使用例】
    # 2分間のテスト実行
    python3 scripts/integrated_orchestrator_v01_hub.py --max-duration 2

    # 5.5時間の本番実行（GitHub Actions用）
    python3 scripts/integrated_orchestrator_v01_hub.py --max-duration 330
"""
import sys
import os

# プロジェクトルートを sys.path の最優先に追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import importlib.util


# 動的にモジュールをロード（インポートエラー回避）
def load_module_from_path(module_name: str, file_path: str):
    """指定パスからモジュールを動的ロード"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# PMAgent を動的ロード
pm_agent_path = os.path.join(project_root, "pm_agent.py")
pm_agent_module = load_module_from_path("pm_agent_module", pm_agent_path)
PMAgent = pm_agent_module.PMAgent

# TaskExecutor を動的ロード
task_executor_path = os.path.join(project_root, "task_executor.py")
task_executor_module = load_module_from_path("task_executor_module", task_executor_path)
TaskExecutor = task_executor_module.TaskExecutor

# 通常のインポート（これは問題ない）
from tools.sheets_manager import GoogleSheetsManager
from browser_control.browser_controller import BrowserController


class IntegratedOrchestrator:
    """24時間自律開発の統合制御ハブ"""

    def __init__(self):
        """
        初期化

        【設計原則】運用ルール 8 に従い、リソースを自ら初期化せず注入
        """
        print("🔧 Integrated Orchestrator 初期化中...")

        # 環境変数から設定を取得
        self.spreadsheet_id = os.getenv("SPREADSHEET_ID", "1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s")

        # GoogleSheetsManager を初期化
        self.sheets = GoogleSheetsManager(self.spreadsheet_id)

        # BrowserController を初期化
        self.browser = BrowserController()

        # PMAgent を初期化（リソース注入）
        self.pm_agent = PMAgent(sheets_manager=self.sheets, browser_controller=self.browser)

        # TaskExecutor を初期化（リソース注入）
        self.task_executor = TaskExecutor(sheets_manager=self.sheets, output_dir="agent_outputs")

        # 制御フラグファイル（人間からの停止指示）
        self.control_flag_file = Path("/tmp/system_control_flag.txt")

        self.running = True

        print("✅ Integrated Orchestrator 初期化完了")

    async def run_continuous_cycle(self, max_duration_minutes: int = 330):
        """
        継続的な開発サイクルを実行

        Args:
            max_duration_minutes: 最大実行時間（分）
        """
        start_time = time.time()
        cycle_count = 0

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🚀 24時間自律開発システム 起動")
        print(f"⏰ 最大実行時間: {max_duration_minutes}分")
        print(f"📅 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        try:
            # ブラウザ初期化
            print("🌐 ブラウザ初期化中...")
            await self.browser.initialize()
            print("✅ ブラウザ初期化完了")

            while self.running:
                cycle_count += 1
                cycle_start = time.time()

                print(f"\n{'='*60}")
                print(f"🔄 サイクル {cycle_count} 開始")
                print(f"{'='*60}")

                # 1. 制御フラグチェック（人間からの停止指示）
                if self._check_stop_flag():
                    print("🛑 停止フラグ検出。システムを安全に停止します...")
                    break

                # 2. pm_task_queue から pending タスクを取得
                tasks = await self._get_pending_tasks()

                if not tasks:
                    print("⏸️  保留中のタスクなし。1分後に再確認...")
                    await asyncio.sleep(60)
                    continue

                print(f"📋 実行タスク数: {len(tasks)}")

                # 3. タスクを実行
                for idx, task in enumerate(tasks, 1):
                    print(f"\n--- タスク {idx}/{len(tasks)} ---")
                    print(f"目標ID: {task.get('目標ID', 'N/A')}")
                    print(f"内容: {task.get('目標内容', 'N/A')[:50]}...")

                    try:
                        # TaskExecutor で実行
                        success = await self.task_executor.execute_single_task(browser=self.browser, task=task)

                        if success:
                            print(f"✅ タスク完了")
                            await self._update_task_status(task, "completed")
                        else:
                            print(f"⚠️ タスク失敗（詳細はログ参照）")
                            await self._update_task_status(task, "failed")

                    except Exception as e:
                        print(f"❌ タスク実行エラー: {e}")
                        await self._log_error(task, str(e))
                        await self._update_task_status(task, "error")

                # 4. タイムアウトチェック
                elapsed = (time.time() - start_time) / 60
                if elapsed > max_duration_minutes:
                    print(f"\n⏰ {max_duration_minutes}分経過。次のCronサイクルへ引き継ぎ...")
                    break

                cycle_duration = (time.time() - cycle_start) / 60
                print(f"\n✅ サイクル {cycle_count} 完了（所要時間: {cycle_duration:.1f}分）")
                print(f"⏳ 累計実行時間: {elapsed:.1f}分 / {max_duration_minutes}分")

                # 5. 次サイクルまで待機
                await asyncio.sleep(60)

        finally:
            # ブラウザクリーンアップ
            print("\n🧹 ブラウザクリーンアップ中...")
            await self.browser.cleanup()
            print("✅ クリーンアップ完了")

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🏁 開発サイクル終了（総サイクル数: {cycle_count}）")
        print(f"📅 終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async def _get_pending_tasks(self) -> List[Dict]:
        """pm_task_queue から pending タスクを取得"""
        try:
            print("📋 pm_task_queue から pending タスク取得中...")

            sheet = self.sheets.gc.open_by_key(self.spreadsheet_id)

            try:
                queue_sheet = sheet.worksheet("pm_task_queue")
            except:
                print("⚠️ pm_task_queue シートが見つかりません")
                return []

            all_values = queue_sheet.get_all_values()

            if len(all_values) < 2:
                print("⚠️ pm_task_queue にデータがありません")
                return []

            headers = all_values[0]
            pending_tasks = []

            for row in all_values[1:]:
                if len(row) > 5 and row[5] == "pending":  # F列: ステータス
                    task = dict(zip(headers, row))
                    pending_tasks.append(task)

            print(f"✅ {len(pending_tasks)} 件の pending タスク発見")
            return pending_tasks[:5]  # 一度に最大5タスク

        except Exception as e:
            print(f"⚠️ タスク取得エラー: {e}")
            import traceback

            traceback.print_exc()
            return []

    async def _update_task_status(self, task: Dict, status: str):
        """タスクのステータスを更新"""
        try:
            goal_id = task.get("目標ID", "")
            print(f"📝 ステータス更新: {goal_id} → {status}")

            # Google Sheets のステータス列を更新
            sheet = self.sheets.gc.open_by_key(self.spreadsheet_id)
            queue_sheet = sheet.worksheet("pm_task_queue")

            # 該当行を検索して更新
            all_values = queue_sheet.get_all_values()
            for idx, row in enumerate(all_values[1:], start=2):
                if len(row) > 1 and row[1] == goal_id:  # B列: 目標ID
                    queue_sheet.update_cell(idx, 6, status)  # F列: ステータス
                    break

        except Exception as e:
            print(f"⚠️ ステータス更新エラー: {e}")

    async def _log_error(self, task: Dict, error: str):
        """エラーをログに記録"""
        timestamp = datetime.now().isoformat()
        task_id = task.get("目標ID", "unknown")

        print(f"📝 エラーログ記録: {task_id} → {error}")

        # エラーログファイルに記録
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"error_log_{datetime.now().strftime('%Y%m%d')}.txt"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} | {task_id} | {error}\n")

    def _check_stop_flag(self) -> bool:
        """人間からの停止フラグをチェック"""
        try:
            if not self.control_flag_file.exists():
                return False

            with open(self.control_flag_file, "r") as f:
                flag = f.read().strip()

            return flag == "STOP"
        except:
            return False


def main():
    """コマンドライン実行のエントリーポイント"""
    parser = argparse.ArgumentParser(
        description="🎹 Integrated Development Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 2分間のテスト実行
  python3 scripts/integrated_orchestrator_v01_hub.py --max-duration 2
  
  # 5.5時間の本番実行（GitHub Actions用）
  python3 scripts/integrated_orchestrator_v01_hub.py --max-duration 330
  
  # 停止フラグを設定（別ターミナルで）
  echo "STOP" > /tmp/system_control_flag.txt
        """,
    )

    parser.add_argument("--max-duration", type=int, default=330, help="最大実行時間（分、デフォルト: 330分=5.5時間）")

    args = parser.parse_args()

    try:
        orchestrator = IntegratedOrchestrator()
        asyncio.run(orchestrator.run_continuous_cycle(args.max_duration))
        return 0

    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによる中断")
        return 130

    except Exception as e:
        print(f"\n💥 予期しないエラー: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
