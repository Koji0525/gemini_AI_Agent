#!/usr/bin/env python3
"""
PM Agent 完全自動化システム（並列実行対応版）

Phase 1: アクティブなゴール取得
Phase 2: タスク分解（Gemini）- 並列実行
Phase 3: タスク登録
Phase 4: タスク実行 - 並列実行
+ エラーハンドリング強化
+ 並列実行サポート
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
import traceback
from typing import List, Dict, Any

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.pm_agent.progress_monitor_fixed import ProgressMonitorAgent
from agents.pm_agent.task_breakdown_gemini import GeminiTaskBreakdownAgent
from agents.pm_agent.task_registration import TaskRegistrationAgent
from agents.pm_agent.task_exporter import TaskExportAgent
from tools.sheets_manager import GoogleSheetsManager
from browser_control.browser_controller import BrowserController
from configuration.config_loader import ConfigLoader


class ErrorHandler:
    """エラーハンドリング用クラス"""

    def __init__(self):
        self.error_log = []

    def log_error(self, phase: str, error: Exception, context: dict = None):
        """エラーをログに記録"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "traceback": traceback.format_exc(),
        }
        self.error_log.append(error_entry)

        print(f"❌ [{phase}] {type(error).__name__}: {error}")

    def get_summary(self):
        """エラーサマリーを取得"""
        if not self.error_log:
            return "✅ エラーなし"

        summary = f"⚠️ {len(self.error_log)}件のエラー:\n"
        for i, error in enumerate(self.error_log[:5], 1):
            summary += f"  {i}. [{error['phase']}] {error['error_type']}\n"

        if len(self.error_log) > 5:
            summary += f"  ... 他{len(self.error_log) - 5}件\n"

        return summary


async def retry_async(func, max_retries=3, delay=2):
    """非同期関数のリトライ実行"""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  ⏳ リトライ {attempt + 1}/{max_retries - 1}...")
                await asyncio.sleep(delay)
            else:
                raise


def get_all_active_goals(sheets_manager, spreadsheet_id):
    """アクティブなゴールを取得"""
    spreadsheet = sheets_manager.gc.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet("project_goal")
    all_values = worksheet.get_all_values()

    if len(all_values) < 2:
        return []

    headers = all_values[0]
    valid_headers = {}
    for i, header in enumerate(headers):
        if header and header.strip():
            valid_headers[i] = header.strip()

    result = []
    for row_values in all_values[1:]:
        row_dict = {}
        for col_idx, header_name in valid_headers.items():
            if col_idx < len(row_values):
                row_dict[header_name] = row_values[col_idx]
            else:
                row_dict[header_name] = ""
        if any(row_dict.values()):
            goal_id = row_dict.get("goal_id")
            status = row_dict.get("status", "").lower()
            goal_desc = row_dict.get("goal_description", "")
            if goal_id and status in ["planning", "active"] and goal_desc:
                result.append(row_dict)

    return result


def get_pending_tasks(sheets_manager, spreadsheet_id, goal_id=None, max_tasks=10):
    """pendingタスクを取得"""
    spreadsheet = sheets_manager.gc.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet("pm_tasks")
    all_values = worksheet.get_all_values()

    if len(all_values) < 2:
        return []

    headers = all_values[0]
    valid_headers = {}
    for i, header in enumerate(headers):
        if header and header.strip():
            valid_headers[i] = header.strip()

    tasks = []
    for row_values in all_values[1:]:
        row_dict = {}
        for col_idx, header_name in valid_headers.items():
            if col_idx < len(row_values):
                row_dict[header_name] = row_values[col_idx]
            else:
                row_dict[header_name] = ""

        if any(row_dict.values()):
            status = row_dict.get("status", "").lower()
            task_goal_id = row_dict.get("goal_id")

            if status == "pending":
                if goal_id is None or str(task_goal_id) == str(goal_id):
                    tasks.append(row_dict)
                    if len(tasks) >= max_tasks:
                        break

    return tasks


async def process_goal(
    goal: Dict[str, Any],
    task_breakdown: GeminiTaskBreakdownAgent,
    task_registration: TaskRegistrationAgent,
    task_exporter: TaskExportAgent,
    error_handler: ErrorHandler,
) -> Dict[str, Any]:
    """
    1つのゴールを処理（タスク分解・登録）
    並列実行可能
    """
    goal_id = goal["goal_id"]
    goal_title = goal.get("title", f"目標{goal_id}")
    goal_description = goal.get("goal_description", "")

    result = {"goal_id": goal_id, "tasks_generated": 0, "tasks_registered": 0, "success": False}

    try:
        print(f"\n🎯 目標{goal_id}を処理中...")

        if not goal_description or goal_description.strip() == "":
            goal_description = f"{goal_title}を達成するためのタスクを実行する"

        # タスク分解
        generated_tasks = await retry_async(
            lambda: task_breakdown.generate_tasks_for_goal(
                goal_id=goal_id, goal_title=goal_title, goal_description=goal_description
            ),
            max_retries=2,
            delay=5,
        )

        if not generated_tasks:
            print(f"⚠️ 目標{goal_id}: タスク生成失敗")
            return result

        result["tasks_generated"] = len(generated_tasks)
        print(f"✅ 目標{goal_id}: {len(generated_tasks)}個のタスクを生成")

        # エクスポート
        export_path = task_exporter.export_tasks(goal_id=goal_id, goal_title=goal_title, tasks=generated_tasks)

        # タスク登録
        registered_count = await task_registration.register_tasks(
            goal_id=goal_id, tasks=generated_tasks, detail_file_path=export_path
        )

        result["tasks_registered"] = registered_count
        result["success"] = True
        print(f"✅ 目標{goal_id}: {registered_count}個のタスクを登録")

    except Exception as e:
        error_handler.log_error(f"Goal {goal_id}", e, {"goal_id": goal_id})
        print(f"❌ 目標{goal_id}: 処理失敗")

    return result


async def execute_task_with_timeout(
    task: Dict[str, Any], browser: BrowserController, timeout: int = 60
) -> Dict[str, Any]:
    """タイムアウト付きタスク実行"""
    task_id = task.get("task_id", "Unknown")
    task_name = task.get("task_name", "Unknown")
    description = task.get("description", "")

    try:
        prompt = f"""以下のタスクを実行してください：

タスク名: {task_name}
説明: {description}

実行結果を簡潔に報告してください。"""

        await asyncio.wait_for(browser.send_prompt(prompt), timeout=timeout)
        await asyncio.sleep(3)

        response = await asyncio.wait_for(browser.extract_latest_text_response(), timeout=timeout)

        if response:
            return {"task_id": task_id, "success": True, "response": response}
        else:
            return {"task_id": task_id, "success": False, "error": "No response"}

    except asyncio.TimeoutError:
        return {"task_id": task_id, "success": False, "error": f"Timeout {timeout}s"}
    except Exception as e:
        return {"task_id": task_id, "success": False, "error": str(e)}


async def execute_tasks_parallel(
    tasks: List[Dict[str, Any]], browser: BrowserController, max_concurrent: int = 3
) -> List[Dict[str, Any]]:
    """
    タスクを並列実行（同時実行数制限付き）
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def execute_with_semaphore(task):
        async with semaphore:
            task_id = task.get("task_id", "Unknown")
            print(f"  🔄 タスク#{task_id} 開始")
            result = await retry_async(
                lambda: execute_task_with_timeout(task, browser, timeout=60), max_retries=2, delay=3
            )
            status = "✅" if result.get("success") else "❌"
            print(f"  {status} タスク#{task_id} 完了")
            return result

    # 並列実行
    results = await asyncio.gather(*[execute_with_semaphore(task) for task in tasks], return_exceptions=True)

    # Exception を result に変換
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append(
                {"task_id": tasks[i].get("task_id", "Unknown"), "success": False, "error": str(result)}
            )
        else:
            processed_results.append(result)

    return processed_results


async def main():
    """メイン実行関数"""
    print("=" * 70)
    print("🤖 PM Agent 完全自動化システム（並列実行対応版）")
    print("=" * 70)
    print(f"開始日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    stats = {
        "goals_processed": 0,
        "tasks_generated": 0,
        "tasks_registered": 0,
        "tasks_executed": 0,
        "tasks_succeeded": 0,
        "tasks_failed": 0,
    }

    error_handler = ErrorHandler()
    browser = None

    try:
        # ============================================================
        # 初期化
        # ============================================================
        print("【初期化】")
        print("-" * 70)

        config = ConfigLoader()
        spreadsheet_id = config.get("SPREADSHEET_ID")
        service_account_file = config.get("GOOGLE_SERVICE_ACCOUNT_FILE")

        sheets_manager = GoogleSheetsManager(spreadsheet_id, service_account_file)
        print("✅ Google Sheets接続成功")

        browser = BrowserController()
        await retry_async(lambda: browser.setup_browser(), max_retries=3, delay=5)
        await retry_async(lambda: browser.navigate_to_gemini(), max_retries=3, delay=5)
        print("✅ Gemini準備完了")
        print()

        # エージェント初期化
        task_breakdown = GeminiTaskBreakdownAgent(sheets_manager, browser)
        task_registration = TaskRegistrationAgent(sheets_manager)
        task_exporter = TaskExportAgent()

        # ============================================================
        # Phase 1: アクティブなゴール取得
        # ============================================================
        print("【Phase 1】アクティブなゴール取得")
        print("-" * 70)

        active_goals = get_all_active_goals(sheets_manager, spreadsheet_id)

        if not active_goals:
            print("⚠️ アクティブなゴールがありません")
            return

        print(f"✅ {len(active_goals)}個のアクティブなゴールを検出")
        print()

        # ============================================================
        # Phase 2-3: タスク生成＆登録（並列実行）
        # ============================================================
        print("【Phase 2-3】タスク生成＆登録（並列実行）")
        print("-" * 70)
        print(f"📊 {len(active_goals)}個のゴールを並列処理します")

        # 並列実行（最大3ゴール同時）
        goal_results = await asyncio.gather(
            *[
                process_goal(goal, task_breakdown, task_registration, task_exporter, error_handler)
                for goal in active_goals[:3]  # 最大3個まで
            ],
            return_exceptions=True,
        )

        # 結果集計
        for result in goal_results:
            if isinstance(result, Exception):
                continue
            if result.get("success"):
                stats["goals_processed"] += 1
                stats["tasks_generated"] += result.get("tasks_generated", 0)
                stats["tasks_registered"] += result.get("tasks_registered", 0)

        print()
        print(f"✅ Phase 2-3 完了: {stats['goals_processed']}個のゴールを処理")

        # ============================================================
        # Phase 4: タスク実行（並列実行）
        # ============================================================
        print()
        print("【Phase 4】タスク実行（並列実行）")
        print("-" * 70)

        pending_tasks = get_pending_tasks(sheets_manager, spreadsheet_id, max_tasks=6)

        if not pending_tasks:
            print("⚠️ 実行可能なタスクがありません")
        else:
            print(f"✅ {len(pending_tasks)}個のpendingタスクを取得")
            print(f"📊 並列実行（最大3タスク同時）")
            print()

            # 並列実行
            task_results = await execute_tasks_parallel(pending_tasks, browser, max_concurrent=3)

            # 結果集計
            for result in task_results:
                stats["tasks_executed"] += 1
                if result.get("success"):
                    stats["tasks_succeeded"] += 1
                else:
                    stats["tasks_failed"] += 1

        # ============================================================
        # サマリー
        # ============================================================
        print()
        print("=" * 70)
        print("📊 実行結果サマリー")
        print("=" * 70)
        print(f"処理したゴール: {stats['goals_processed']}個")
        print(f"生成したタスク: {stats['tasks_generated']}個")
        print(f"登録したタスク: {stats['tasks_registered']}個")
        print(f"実行したタスク: {stats['tasks_executed']}個")
        print(f"  成功: {stats['tasks_succeeded']}個")
        print(f"  失敗: {stats['tasks_failed']}個")
        print()
        print(error_handler.get_summary())
        print("=" * 70)

    except Exception as e:
        error_handler.log_error("System", e)
        print(f"❌ システムエラー: {e}")
        traceback.print_exc()

    finally:
        if browser:
            print("\n🧹 ブラウザをクリーンアップ中...")
            try:
                await browser.cleanup()
                print("✅ クリーンアップ完了")
            except Exception as e:
                print(f"⚠️ クリーンアップエラー: {e}")


if __name__ == "__main__":
    asyncio.run(main())
