#!/usr/bin/env python3
"""
PM Agent 完全自動化システム - Gemini統合版
- 進捗監視
- タスク分解（Gemini AI使用）
- タスク登録
"""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, "/workspaces/gemini_AI_Agent")

# _WIPディレクトリから直接インポート

from agents.pm_agent.progress_monitor import ProgressMonitorAgent
from agents.pm_agent.task_breakdown_gemini import GeminiTaskBreakdownAgent  # Gemini統合版
from agents.pm_agent.task_registration import TaskRegistrationAgent
from agents.pm_agent.task_exporter import TaskExportAgent  # タスク詳細エクスポート
from tools.sheets_manager import GoogleSheetsManager
from browser_control.browser_controller import BrowserController
from configuration.config_loader import ConfigLoader


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ステータス統一ルール
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# project_goal: planning/active/paused/completed/cancelled
# pm_tasks: pending/in_progress/review/completed/failed/skipped/cancelled
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


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
        # 初期化
        # ============================================================

        # Google Sheets接続
        spreadsheet_id = ConfigLoader.get("spreadsheet_id")
        service_account_file = ConfigLoader.get("service_account_file")
        sheets_manager = GoogleSheetsManager(spreadsheet_id, service_account_file)

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
        progress_monitor = ProgressMonitorAgent(sheets_manager)
        task_breakdown = GeminiTaskBreakdownAgent(sheets_manager, browser)
        task_registration = TaskRegistrationAgent(sheets_manager)
        task_exporter = TaskExportAgent()  # タスク詳細エクスポート

        # ============================================================
        # Phase 1: 進捗監視
        # ============================================================
        print("【Phase 1】進捗監視")
        print("-" * 70)

        low_progress_goals = await progress_monitor.detect_low_progress_goals(threshold=0.7)  # 70%未満の目標を検出

        stats["low_progress_goals"] = len(low_progress_goals)

        if not low_progress_goals:
            print("✅ すべての目標が順調に進行しています")
            return

        print(f"⚠️  {len(low_progress_goals)}個の低進捗目標を検出:")
        for goal in low_progress_goals:
            # 安全にキーにアクセス
            goal_id = goal.get("goal_id", "Unknown")
            progress = goal.get("progress", goal.get("completion_rate", 0))
            status = goal.get("status", goal.get("priority", "unknown"))
            print(f"  - 目標{goal_id}: {progress:.1%} ({status})")
        print()

        # ============================================================
        # Phase 2-3: 各目標に対してタスク生成＆登録
        # ============================================================
        for goal in low_progress_goals:
            goal_id = goal["goal_id"]
            goal_title = goal.get("title", f"目標{goal_id}")
            goal_description = goal.get("description", "")

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
                    goal_id=goal_id,
                    goal_title=goal_title,
                    goal_description=goal_description,
                    context={
                        "現在の進捗": f"{goal.get('progress', goal.get('completion_rate', 0)):.1%}",
                        "完了タスク": f"{goal.get('completed_tasks', 0)}/{goal.get('total_tasks', 0)}",
                    },
                    max_tasks=5,  # 一度に5個まで
                )

                stats["tasks_generated"] += len(generated_tasks)
                print(f"✅ {len(generated_tasks)}個のタスクを生成")

                # タスク詳細をMarkdownファイルにエクスポート
                if generated_tasks:
                    try:
                        export_path = task_exporter.export_tasks(
                            goal_id=goal_id, goal_title=goal_title, tasks=generated_tasks
                        )
                        print(f"📄 詳細ファイル: {export_path}")
                    except Exception as export_error:
                        print(f"⚠️ エクスポートエラー（続行）: {export_error}")

                print()

            except Exception as e:
                error_msg = f"目標{goal_id}のタスク生成失敗: {e}"
                print(f"❌ {error_msg}")
                stats["errors"].append(error_msg)
                continue

            # タスク登録
            print(f"【Phase 3】目標{goal_id}のタスク登録")
            print("-" * 70)

            try:
                # デバッグ: export_pathの値を確認
                print(f"🔍 export_path = {export_path}")

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
    print(f"検出した低進捗目標: {stats['low_progress_goals']}個")
    print(f"生成したタスク: {stats['tasks_generated']}個")
    print(f"登録したタスク: {stats['tasks_registered']}個")
    print(f"エラー: {len(stats['errors'])}件")

    if stats["errors"]:
        print("\n⚠️ エラー詳細:")
        for error in stats["errors"]:
            print(f"  - {error}")

    print(f"\n完了日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    if stats["errors"]:
        print("\n⚠️ PM Agent自動化が一部エラーで完了しました")
    else:
        print("\n🎉 PM Agent自動化が正常に完了しました！")


if __name__ == "__main__":
    asyncio.run(main())
