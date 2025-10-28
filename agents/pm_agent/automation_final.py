#!/usr/bin/env python3
"""
最終版automation.py - 環境変数問題を解決
"""

import asyncio
import sys
import os
from datetime import datetime

# まず環境変数を確実に設定
_current_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_current_dir))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# 環境変数を設定
os.environ.setdefault("SPREADSHEET_ID", "1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_FILE", "configuration/service_account.json")

from tools.sheets_manager import GoogleSheetsManager
from browser_control.browser_controller import BrowserController
from configuration.config_loader import ConfigLoader

# ここでインポート（環境変数設定後）
from agents.pm_agent.progress_monitor_fixed import ProgressMonitorAgent
from agents.pm_agent.task_breakdown_gemini import GeminiTaskBreakdownAgent
from agents.pm_agent.task_registration import TaskRegistrationAgent
from agents.pm_agent.task_exporter import TaskExportAgent


async def main():
    """メイン実行関数"""
    print("=" * 70)
    print("🤖 PM Agent 完全自動化システム（最終版）")
    print("=" * 70)
    print(f"開始日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    browser = None
    try:
        # ============================================================
        # 環境設定の確認
        # ============================================================
        print("🔧 環境設定を確認...")
        config = ConfigLoader()
        spreadsheet_id = config.get("SPREADSHEET_ID")
        service_account_file = config.get("GOOGLE_SERVICE_ACCOUNT_FILE")

        print(f"📊 スプレッドシートID: {spreadsheet_id}")
        print(f"🔑 サービスアカウント: {service_account_file}")

        if not service_account_file or not os.path.exists(service_account_file):
            print(f"❌ サービスアカウントファイルが見つかりません: {service_account_file}")
            # 代替パスを探す
            alternative_paths = [
                "service_account.json",
                "../service_account.json",
                "configuration/service_account.json",
                "../configuration/service_account.json",
            ]
            for path in alternative_paths:
                if os.path.exists(path):
                    service_account_file = path
                    print(f"✅ 代替パスを使用: {service_account_file}")
                    break
            else:
                print("❌ サービスアカウントファイルが見つかりませんでした")
                return False

        # ============================================================
        # Google Sheets接続
        # ============================================================
        print("🔗 Google Sheetsに接続中...")
        sheets_manager = GoogleSheetsManager(spreadsheet_id, service_account_file)
        print("✅ Google Sheets接続成功")

        # ============================================================
        # ブラウザ初期化
        # ============================================================
        print("🌐 ブラウザを初期化中...")
        browser = BrowserController()
        await browser.setup_browser()

        # Gemini接続確認
        print("🤖 Geminiに接続中...")
        await browser.page.goto("https://gemini.google.com/", wait_until="networkidle")
        print("✅ Gemini準備完了")

        # ============================================================
        # 【Phase 1】進捗監視
        # ============================================================
        print()
        print("【Phase 1】進捗監視")
        print("-" * 50)

        progress_monitor = ProgressMonitorAgent()
        low_progress_goals = await progress_monitor.get_goals_progress()

        if not low_progress_goals:
            print("✅ すべての目標が順調に進行しています")
            return True

        print(f"⚠️  {len(low_progress_goals)}個の低進捗目標を検出:")
        for goal in low_progress_goals:
            print(f"  - 目標{goal['goal_id']}: {goal['progress_rate']:.1f}%")

        # ============================================================
        # 【Phase 2】タスク分解（Gemini使用）
        # ============================================================
        print()
        print("【Phase 2】目標のタスク分解（Gemini使用）")
        print("-" * 50)

        task_breakdown_agent = GeminiTaskBreakdownAgent(browser)
        task_exporter = TaskExportAgent()

        processed_goals = 0
        for goal in low_progress_goals:
            goal_id = goal["goal_id"]
            goal_title = goal.get("goal_name", f"目標{goal_id}")

            print(f"🎯 目標{goal_id}のタスク分解を開始...")

            # タスク分解実行
            formatted_tasks = await task_breakdown_agent.breakdown_goal(
                goal_title=goal_title, goal_description=goal.get("description", ""), max_tasks=5, goal_id=goal_id
            )

            if not formatted_tasks:
                print(f"❌ 目標{goal_id}のタスク分解に失敗")
                continue

            print(f"✅ {len(formatted_tasks)}個のタスクを生成")

            # ============================================================
            # 【Phase 3】タスク登録
            # ============================================================
            print()
            print("【Phase 3】目標{}のタスク登録".format(goal_id))
            print("-" * 50)

            try:
                export_path = task_exporter.export_tasks(formatted_tasks, goal_id=goal_id, goal_title=goal_title)
                print(f"📄 詳細ファイル: {export_path}")

                # タスクをSheetsに登録
                task_registration_agent = TaskRegistrationAgent()
                registered_count = task_registration_agent.register_tasks_to_sheets(
                    formatted_tasks, sheets_manager=sheets_manager, detail_file_path=export_path
                )

                print(f"📊 {registered_count}個のタスクをSheetsに登録")
                processed_goals += 1

            except Exception as e:
                print(f"❌ 目標{goal_id}のタスク登録失敗: {e}")

        # ============================================================
        # 実行結果サマリー
        # ============================================================
        print()
        print("=" * 70)
        print("📊 実行結果サマリー")
        print("=" * 70)
        print(f"検出した低進捗目標: {len(low_progress_goals)}個")
        print(f"処理した目標: {processed_goals}個")

        if processed_goals > 0:
            print("🎉 PM Agent自動化が正常に完了しました")
        else:
            print("⚠️ PM Agent自動化が一部エラーで完了しました")

        print(f"完了日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        return processed_goals > 0

    except Exception as e:
        print(f"❌ システムエラー: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        if browser:
            print("🧹 ブラウザをクリーンアップ中...")
            await browser.cleanup()


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
