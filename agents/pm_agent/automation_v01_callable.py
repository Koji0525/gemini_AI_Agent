#!/usr/bin/env python3
"""
PM Agent自動化 - 呼び出し可能版
元のautomation.pyを関数化（正しい初期化方法使用）
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 元のautomation.pyと同じインポート
from agents.pm_agent.progress_monitor import ProgressMonitorAgent
from agents.pm_agent.task_breakdown_gemini import GeminiTaskBreakdownAgent
from agents.pm_agent.task_registration import TaskRegistrationAgent
from agents.pm_agent.task_exporter import TaskExportAgent
from tools.sheets_manager import GoogleSheetsManager
from browser_control.browser_controller import BrowserController
from configuration.config_loader import get_config


async def run_automation(goal_id: str = None, max_tasks: int = 5) -> dict:
    """
    PM Agent自動化を実行（呼び出し可能版）

    Args:
        goal_id: 特定のゴールIDを指定（Noneの場合は全ての低進捗ゴールを処理）
        max_tasks: 1ゴールあたりの最大タスク数

    Returns:
        実行結果の辞書
    """

    stats = {"goals_processed": 0, "tasks_generated": 0, "tasks_registered": 0, "errors": []}

    browser = None

    try:
        print("\n" + "=" * 70)
        print("🚀 PM Agent自動化 - 呼び出し可能版")
        if goal_id:
            print(f"   対象ゴール: {goal_id}")
        print("=" * 70)

        # コンポーネント初期化
        sheets_manager = GoogleSheetsManager(
            spreadsheet_id=get_config("SPREADSHEET_ID"), service_account_file=get_config("SERVICE_ACCOUNT_FILE")
        )

        progress_monitor = ProgressMonitorAgent(sheets_manager)
        task_registration = TaskRegistrationAgent(sheets_manager)
        task_exporter = TaskExportAgent()

        # ブラウザ初期化（元のautomation.pyと同じ方法）
        print("\n🌐 ブラウザ初期化中...")
        browser = BrowserController()
        # BrowserControllerは__init__で自動初期化される

        # GeminiTaskBreakdownAgentにはsheets_managerも渡す
        task_breakdown = GeminiTaskBreakdownAgent(sheets_manager, browser)
        print("✅ ブラウザ初期化完了")

        # Phase 1: 低進捗ゴール検出
        print("\n【Phase 1】低進捗ゴール検出")
        print("-" * 70)

        if goal_id:
            # 特定のゴールを処理
            try:
                goal_sheet = sheets_manager.gc.open_by_key(get_config("SPREADSHEET_ID")).worksheet("project_goal")

                all_goals = goal_sheet.get_all_records()
                target_goal = None

                for g in all_goals:
                    if str(g.get("goal_id")) == str(goal_id):
                        target_goal = g
                        break

                if target_goal:
                    low_progress_goals = [
                        {
                            "goal_id": goal_id,
                            "title": target_goal.get("title", f"目標{goal_id}"),
                            "description": target_goal.get("description", ""),
                        }
                    ]
                    print(f"✅ 指定されたゴール: {goal_id} - {target_goal.get('title', '')}")
                else:
                    low_progress_goals = [{"goal_id": goal_id, "title": f"目標{goal_id}", "description": ""}]
                    print(f"✅ 指定されたゴール: {goal_id}（詳細情報なし）")
            except Exception as e:
                print(f"⚠️ ゴール情報取得エラー: {e}")
                low_progress_goals = [{"goal_id": goal_id, "title": f"目標{goal_id}", "description": ""}]
        else:
            # 全ての低進捗ゴールを取得
            low_progress_goals = await progress_monitor.detect_low_progress_goals(
                progress_threshold=0.7, status_filter="active"
            )
            print(f"✅ 低進捗ゴール: {len(low_progress_goals)}個")

            if low_progress_goals:
                for g in low_progress_goals:
                    print(f"  - 目標{g.get('goal_id')}: {g.get('title', 'N/A')}")

        stats["goals_processed"] = len(low_progress_goals)

        if not low_progress_goals:
            print("⚠️ 処理対象のゴールがありません")
            return stats

        # Phase 2-3: 各ゴールを処理
        for goal in low_progress_goals:
            current_goal_id = goal["goal_id"]

            try:
                # Phase 2: タスク分解
                print(f"\n【Phase 2】目標{current_goal_id}のタスク分解（Gemini使用）")
                print("-" * 70)

                generated_tasks = await task_breakdown.generate_tasks(
                    goal_id=current_goal_id,
                    goal_title=goal.get("title", ""),
                    goal_description=goal.get("description", ""),
                    max_tasks=max_tasks,
                )

                print(f"✅ {len(generated_tasks)}個のタスクを生成")
                stats["tasks_generated"] += len(generated_tasks)

                if not generated_tasks:
                    print("⚠️ タスクが生成されませんでした")
                    continue

                # タスク詳細をエクスポート
                export_path = task_exporter.export_tasks(goal_id=current_goal_id, tasks=generated_tasks)
                print(f"📄 詳細ファイル: {export_path}")

                # Phase 3: タスク登録
                print(f"\n【Phase 3】目標{current_goal_id}のタスク登録")
                print("-" * 70)

                registered_count = await task_registration.register_tasks(
                    goal_id=current_goal_id, tasks=generated_tasks, detail_file_path=export_path
                )

                stats["tasks_registered"] += registered_count
                print(f"✅ {registered_count}個のタスクを登録")

            except Exception as e:
                error_msg = f"目標{current_goal_id}の処理失敗: {e}"
                print(f"❌ {error_msg}")
                import traceback

                traceback.print_exc()
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

    # サマリー表示
    print("\n" + "=" * 70)
    print("📊 実行結果サマリー")
    print("=" * 70)
    print(f"処理したゴール: {stats['goals_processed']}個")
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
        print("\n⚠️ 自動化が一部エラーで完了")
    else:
        print("\n🎉 自動化が正常に完了！")

    return stats


async def main():
    """スタンドアロン実行用のメイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description="PM Agent自動化（呼び出し可能版）")
    parser.add_argument("--goal-id", type=str, help="特定のゴールIDを指定")
    parser.add_argument("--max-tasks", type=int, default=5, help="最大タスク数（デフォルト: 5）")

    args = parser.parse_args()

    await run_automation(goal_id=args.goal_id, max_tasks=args.max_tasks)


if __name__ == "__main__":
    asyncio.run(main())
