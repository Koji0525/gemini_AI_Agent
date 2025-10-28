#!/usr/bin/env python3
"""
PM Agent 完全自動化システム（automation.py完全コピー版）

automation.pyから動作確認済みのコードを完全コピーし、
低進捗チェック部分のみを全アクティブゴール取得に変更
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
    """
    アクティブなゴールを取得（空セル対応）
    """
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


async def main():
    """メイン実行関数"""
    print("=" * 70)
    print("🤖 PM Agent 完全自動化システム（Gemini統合版）")
    print("=" * 70)
    print(f"開始日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 統計情報
    stats = {"low_progress_goals": 0, "tasks_generated": 0, "tasks_registered": 0, "errors": []}

    browser = None

    try:
        # ============================================================
        # 初期化（automation.pyから完全コピー）
        # ============================================================

        # Google Sheets接続
        try:
            config = ConfigLoader()
            spreadsheet_id = config.get("SPREADSHEET_ID")
            service_account_file = config.get("GOOGLE_SERVICE_ACCOUNT_FILE")
            print(f"📊 スプレッドシートID: {spreadsheet_id}")
            print(f"🔑 サービスアカウント: {service_account_file}")
            sheets_manager = GoogleSheetsManager(spreadsheet_id, service_account_file)
            print("✅ Google Sheets接続成功")
        except Exception as e:
            print(f"❌ Google Sheets接続エラー: {e}")
            return

        # BrowserController初期化（Gemini連携用）
        print("🌐 BrowserController初期化中...")
        browser = BrowserController()
        await browser.setup_browser()

        # Geminiページに移動
        print("🤖 Geminiページに移動中...")
        await browser.navigate_to_gemini()
        print("✅ Gemini準備完了")
        print()

        # エージェント初期化
        progress_monitor = ProgressMonitorAgent()
        task_breakdown = GeminiTaskBreakdownAgent(sheets_manager, browser)
        task_registration = TaskRegistrationAgent(sheets_manager)
        task_exporter = TaskExportAgent()  # タスク詳細エクスポート

        # ============================================================
        # Phase 1: アクティブなゴールを取得（修正部分）
        # ============================================================
        print("【Phase 1】アクティブなゴール取得")
        print("-" * 70)

        # ✅ 修正: 低進捗チェックをスキップして全アクティブゴールを取得
        low_progress_goals = get_all_active_goals(sheets_manager, spreadsheet_id)

        stats["low_progress_goals"] = len(low_progress_goals)

        if not low_progress_goals:
            print("⚠️ アクティブなゴールがありません")
            return

        print(f"✅ {len(low_progress_goals)}個のアクティブゴールを検出:")
        for goal in low_progress_goals:
            goal_id = goal.get("goal_id", "Unknown")
            status = goal.get("status", "unknown")
            desc = goal.get("goal_description", "")[:50]
            print(f"  - 目標{goal_id}: {desc}... ({status})")
        print()

        # ============================================================
        # Phase 2-3: 各目標に対してタスク生成＆登録
        # （以下はautomation.pyから完全コピー）
        # ============================================================
        for goal in low_progress_goals:
            goal_id = goal["goal_id"]
            goal_title = goal.get("title", f"目標{goal_id}")
            goal_description = goal.get("goal_description", "")

            print("=" * 70)
            print(f"【Phase 2】目標{goal_id}のタスク分解（Gemini使用）")
            print("-" * 70)

            # タスク生成（Gemini使用）
            try:
                # goal_descriptionが空の場合はgoal_titleを使用
                if not goal_description or goal_description.strip() == "":
                    goal_description = f"{goal_title}を達成するためのタスクを実行する"
                    print(f"💡 目標説明が空のため、タイトルから生成: {goal_description}")

                generated_tasks = await task_breakdown.generate_tasks_for_goal(
                    goal_id=goal_id, goal_title=goal_title, goal_description=goal_description
                )

                if not generated_tasks:
                    error_msg = f"目標{goal_id}のタスク生成失敗"
                    print(f"⚠️ {error_msg}")
                    stats["errors"].append(error_msg)
                    continue

                print(f"✅ {len(generated_tasks)}個のタスクを生成しました")
                stats["tasks_generated"] += len(generated_tasks)

                # ============================================================
                # タスク詳細のエクスポート
                # ============================================================
                # ✅ automation.pyの実際の呼び出しをそのままコピー
                export_path = task_exporter.export_tasks(
                    goal_id=goal_id, goal_title=goal_title, tasks=generated_tasks  # ← この引数が必要！
                )
                print(f"📄 タスク詳細をエクスポート: {export_path}")

            except Exception as e:
                error_msg = f"目標{goal_id}のタスク生成失敗: {e}"
                print(f"❌ {error_msg}")
                stats["errors"].append(error_msg)
                import traceback

                traceback.print_exc()
                continue

            # ============================================================
            # Phase 3: タスク登録
            # ============================================================
            print()
            print(f"【Phase 3】目標{goal_id}のタスク登録")
            print("-" * 70)

            try:
                # デバッグ: export_pathの値を確認
                print(f"🔍 export_path = {export_path}")

                # ✅ automation.pyから完全コピー
                registered_count = await task_registration.register_tasks(
                    goal_id=goal_id, tasks=generated_tasks, detail_file_path=export_path
                )

                stats["tasks_registered"] += registered_count
                print(f"✅ {registered_count}個のタスクを登録")
                print()

            except Exception as e:
                error_msg = f"目標{goal_id}のタスク登録失敗: {e}"
                print(f"❌ {error_msg}")
                stats["errors"].append(error_msg)
                continue

    except Exception as e:
        print(f"❌ システムエラー: {e}")
        import traceback

        traceback.print_exc()
        stats["errors"].append(str(e))

    finally:
        # ブラウザクリーンアップ
        if browser:
            print("\n🧹 ブラウザをクリーンアップ中...")
            await browser.cleanup()
            print("✅ クリーンアップ完了")

    # ============================================================
    # サマリー表示
    # ============================================================
    print()
    print("=" * 70)
    print("📊 実行結果サマリー")
    print("=" * 70)
    print(f"処理したゴール: {stats['low_progress_goals']}個")
    print(f"生成したタスク: {stats['tasks_generated']}個")
    print(f"登録したタスク: {stats['tasks_registered']}個")
    print(f"エラー: {len(stats['errors'])}件")

    if stats["errors"]:
        print("\n⚠️ エラー詳細:")
        for err in stats["errors"]:
            print(f"  - {err}")

    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
