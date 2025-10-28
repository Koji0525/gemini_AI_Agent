#!/usr/bin/env python3
"""
PM Agent 完全自動化システム（Phase 1-4統合版）

Phase 1: アクティブなゴール取得
Phase 2: タスク分解（Gemini）
Phase 3: タスク登録
Phase 4: タスク実行 ← NEW!
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

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


def get_all_active_goals(sheets_manager, spreadsheet_id):
    """アクティブなゴールを取得（空セル対応）"""
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


def get_pending_tasks(sheets_manager, spreadsheet_id, goal_id=None, max_tasks=5):
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

            # pendingで、goal_id指定がある場合はそれに一致するもののみ
            if status == "pending":
                if goal_id is None or str(task_goal_id) == str(goal_id):
                    tasks.append(row_dict)
                    if len(tasks) >= max_tasks:
                        break

    return tasks


async def execute_task_simple(task, browser):
    """シンプルなタスク実行"""
    task_id = task.get("task_id", "Unknown")
    task_name = task.get("task_name", "Unknown")
    description = task.get("description", "")

    print(f"  📝 タスク#{task_id}: {task_name}")

    try:
        # Geminiにタスクを送信
        prompt = f"""以下のタスクを実行してください：

タスク名: {task_name}
説明: {description}

実行結果を簡潔に報告してください。"""

        await browser.send_prompt(prompt)
        await asyncio.sleep(3)  # レスポンス待機

        response = await browser.extract_latest_text_response()

        if response:
            print(f"  ✅ 実行完了")
            return {"success": True, "response": response}
        else:
            print(f"  ⚠️ レスポンスなし")
            return {"success": False, "error": "No response"}

    except Exception as e:
        print(f"  ❌ エラー: {e}")
        return {"success": False, "error": str(e)}


async def main():
    """メイン実行関数"""
    print("=" * 70)
    print("🤖 PM Agent 完全自動化システム（Phase 1-4統合版）")
    print("=" * 70)
    print(f"開始日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    stats = {
        "goals_processed": 0,
        "tasks_generated": 0,
        "tasks_registered": 0,
        "tasks_executed": 0,
        "tasks_succeeded": 0,
        "errors": [],
    }

    browser = None

    try:
        # ============================================================
        # 初期化
        # ============================================================
        config = ConfigLoader()
        spreadsheet_id = config.get("SPREADSHEET_ID")
        service_account_file = config.get("GOOGLE_SERVICE_ACCOUNT_FILE")
        print(f"📊 スプレッドシートID: {spreadsheet_id}")
        print(f"🔑 サービスアカウント: {service_account_file}")
        sheets_manager = GoogleSheetsManager(spreadsheet_id, service_account_file)
        print("✅ Google Sheets接続成功")

        # BrowserController初期化
        print("🌐 BrowserController初期化中...")
        browser = BrowserController()
        await browser.setup_browser()

        # Geminiページに移動
        print("🤖 Geminiページに移動中...")
        await browser.navigate_to_gemini()
        print("✅ Gemini準備完了")
        print()

        # エージェント初期化
        task_breakdown = GeminiTaskBreakdownAgent(sheets_manager, browser)
        task_registration = TaskRegistrationAgent(sheets_manager)
        task_exporter = TaskExportAgent()

        # ============================================================
        # Phase 1: アクティブなゴールを取得
        # ============================================================
        print("【Phase 1】アクティブなゴール取得")
        print("-" * 70)

        active_goals = get_all_active_goals(sheets_manager, spreadsheet_id)

        if not active_goals:
            print("⚠️ アクティブなゴールがありません")
            return

        print(f"✅ {len(active_goals)}個のアクティブなゴールを検出")
        for goal in active_goals:
            goal_id = goal.get("goal_id", "Unknown")
            desc = goal.get("goal_description", "")[:50]
            print(f"  - 目標{goal_id}: {desc}...")
        print()

        # ============================================================
        # Phase 2-3: タスク生成＆登録
        # ============================================================
        for goal in active_goals:
            goal_id = goal["goal_id"]
            goal_title = goal.get("title", f"目標{goal_id}")
            goal_description = goal.get("goal_description", "")

            print("=" * 70)
            print(f"【Phase 2】目標{goal_id}のタスク分解（Gemini使用）")
            print("-" * 70)

            try:
                if not goal_description or goal_description.strip() == "":
                    goal_description = f"{goal_title}を達成するためのタスクを実行する"

                generated_tasks = await task_breakdown.generate_tasks_for_goal(
                    goal_id=goal_id, goal_title=goal_title, goal_description=goal_description
                )

                if not generated_tasks:
                    print(f"⚠️ タスク生成失敗")
                    continue

                print(f"✅ {len(generated_tasks)}個のタスクを生成しました")
                stats["tasks_generated"] += len(generated_tasks)

                export_path = task_exporter.export_tasks(goal_id=goal_id, goal_title=goal_title, tasks=generated_tasks)
                print(f"📄 タスク詳細をエクスポート: {export_path}")

            except Exception as e:
                print(f"❌ タスク生成エラー: {e}")
                continue

            # ============================================================
            # Phase 3: タスク登録
            # ============================================================
            print()
            print(f"【Phase 3】目標{goal_id}のタスク登録")
            print("-" * 70)

            try:
                registered_count = await task_registration.register_tasks(
                    goal_id=goal_id, tasks=generated_tasks, detail_file_path=export_path
                )

                stats["tasks_registered"] += registered_count
                print(f"✅ {registered_count}個のタスクを登録")
                print()
                stats["goals_processed"] += 1

            except Exception as e:
                print(f"❌ タスク登録エラー: {e}")
                continue

        # ============================================================
        # Phase 4: タスク実行
        # ============================================================
        print()
        print("=" * 70)
        print("【Phase 4】タスク実行")
        print("-" * 70)

        # 登録したタスクを取得
        pending_tasks = get_pending_tasks(sheets_manager, spreadsheet_id, max_tasks=5)

        if not pending_tasks:
            print("⚠️ 実行可能なタスクがありません")
        else:
            print(f"✅ {len(pending_tasks)}個のpendingタスクを取得")
            print()

            for i, task in enumerate(pending_tasks, 1):
                print(f"[{i}/{len(pending_tasks)}]")
                result = await execute_task_simple(task, browser)

                stats["tasks_executed"] += 1
                if result.get("success"):
                    stats["tasks_succeeded"] += 1

                print()

        # ============================================================
        # サマリー
        # ============================================================
        print("=" * 70)
        print("📊 実行結果サマリー")
        print("=" * 70)
        print(f"処理したゴール: {stats['goals_processed']}個")
        print(f"生成したタスク: {stats['tasks_generated']}個")
        print(f"登録したタスク: {stats['tasks_registered']}個")
        print(f"実行したタスク: {stats['tasks_executed']}個")
        print(f"成功したタスク: {stats['tasks_succeeded']}個")
        print("=" * 70)

    except Exception as e:
        print(f"❌ システムエラー: {e}")
        import traceback

        traceback.print_exc()

    finally:
        if browser:
            print("\n🧹 ブラウザをクリーンアップ中...")
            await browser.cleanup()
            print("✅ クリーンアップ完了")


if __name__ == "__main__":
    asyncio.run(main())
