#!/usr/bin/env python3
"""
PM Agent 完全自動化システム（automation.pyベース・全ゴール対応版）

動作確認済みのautomation.pyをベースに、
低進捗チェックをスキップして全アクティブゴールを処理する版
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


def get_sheet_data_robust(sheets_manager, spreadsheet_id, sheet_name):
    """空セル対応のデータ取得"""
    spreadsheet = sheets_manager.gc.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet(sheet_name)
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
            result.append(row_dict)

    return result


async def main():
    """メイン実行関数"""
    print("=" * 70)
    print("🤖 PM Agent 完全自動化システム（全ゴール対応版）")
    print("=" * 70)
    print(f"開始日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    stats = {"goals_processed": 0, "tasks_generated": 0, "tasks_registered": 0, "errors": []}

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
        print("�� Geminiページに移動中...")
        await browser.navigate_to_gemini()
        print("✅ Gemini準備完了")
        print()

        # エージェント初期化
        task_breakdown = GeminiTaskBreakdownAgent(sheets_manager, browser)
        task_registration = TaskRegistrationAgent(sheets_manager)
        task_exporter = TaskExportAgent()

        # ============================================================
        # Phase 1: アクティブなゴールを取得（低進捗チェックなし）
        # ============================================================
        print("【Phase 1】アクティブなゴール取得")
        print("-" * 70)

        # 空セル対応でデータ取得
        all_goals_data = get_sheet_data_robust(sheets_manager, spreadsheet_id, "project_goal")

        # planning または active なゴールをフィルタ
        active_goals = []
        for row in all_goals_data:
            goal_id = row.get("goal_id")
            status = row.get("status", "").lower()
            goal_desc = row.get("goal_description", "")

            if goal_id and status in ["planning", "active"] and goal_desc:
                active_goals.append(
                    {
                        "goal_id": goal_id,
                        "title": row.get("title", f"ゴール{goal_id}"),
                        "description": goal_desc,
                        "status": status,
                    }
                )

        if not active_goals:
            print("⚠️ アクティブなゴールがありません")
            return

        print(f"✅ {len(active_goals)}個のアクティブなゴールを発見")
        for goal in active_goals:
            print(f"  - 目標{goal['goal_id']}: {goal['description'][:50]}...")
        print()

        # ============================================================
        # Phase 2-3: 各目標に対してタスク生成＆登録
        # ============================================================
        for goal in active_goals:
            goal_id = goal["goal_id"]
            goal_title = goal.get("title", f"目標{goal_id}")
            goal_description = goal.get("description", "")

            print("=" * 70)
            print(f"【Phase 2】目標{goal_id}のタスク分解（Gemini使用）")
            print("-" * 70)

            # タスク生成（Gemini使用）
            try:
                generated_tasks = await task_breakdown.generate_tasks_for_goal(
                    goal_id=goal_id, goal_title=goal_title, goal_description=goal_description
                )

                if not generated_tasks:
                    print(f"⚠️ タスク生成失敗: 目標{goal_id}")
                    stats["errors"].append(f"タスク生成失敗: 目標{goal_id}")
                    continue

                print(f"✅ {len(generated_tasks)}個のタスクを生成しました")
                stats["tasks_generated"] += len(generated_tasks)

                # タスク詳細のエクスポート
                export_path = task_exporter.export_tasks_to_file(goal_id=goal_id, tasks=generated_tasks)
                print(f"📄 タスク詳細をエクスポート: {export_path}")

            except Exception as e:
                print(f"❌ タスク生成エラー: {e}")
                stats["errors"].append(f"タスク生成エラー: {e}")
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

                if registered_count > 0:
                    print(f"✅ {registered_count}個のタスクを登録しました")
                    stats["tasks_registered"] += registered_count
                else:
                    print(f"⚠️ タスク登録: 0件（重複の可能性）")

            except Exception as e:
                print(f"❌ タスク登録エラー: {e}")
                stats["errors"].append(f"タスク登録エラー: {e}")
                continue

            stats["goals_processed"] += 1
            print()

        # ============================================================
        # 統計情報表示
        # ============================================================
        print("=" * 70)
        print("📊 実行統計")
        print("-" * 70)
        print(f"  処理したゴール数: {stats['goals_processed']}")
        print(f"  生成したタスク数: {stats['tasks_generated']}")
        print(f"  登録したタスク数: {stats['tasks_registered']}")
        if stats["errors"]:
            print(f"  エラー数: {len(stats['errors'])}")
            for err in stats["errors"][:5]:
                print(f"    - {err}")
        print("=" * 70)
        print()

        # ============================================================
        # Phase 4: 次のステップ案内
        # ============================================================
        print("【Phase 4】タスク実行準備")
        print("-" * 70)
        print("📝 タスクが pm_tasks シートに登録されました")
        print()
        print("🚀 次のステップ:")
        print("  1. タスク実行スクリプトを使用:")
        print("     python3 scripts/task_executor.py")
        print()
        print("  2. または integrated_executor を使用:")
        print("     python3 agents/integrated_executor.py [goal_id]")

    except Exception as e:
        print(f"❌ システムエラー: {e}")
        import traceback

        traceback.print_exc()

    finally:
        if browser:
            print("🧹 ブラウザをクリーンアップ中...")
            await browser.cleanup()
            print("✅ クリーンアップ完了")


if __name__ == "__main__":
    asyncio.run(main())
