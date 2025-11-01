#!/usr/bin/env python3
"""
WordPress自動設定スクリプト
設計図に基づいてWordPressを自動設定する
"""
import asyncio
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from browser_control.browser_controller import BrowserController
from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import ConfigLoader


async def main():
    """WordPress自動設定メイン関数"""
    print("🚀 WordPress自動設定システム 起動")
    print("=" * 50)

    browser = None
    try:
        # 設定読み込み
        config = ConfigLoader()
        spreadsheet_id = config.get("SPREADSHEET_ID")
        service_account_file = config.get("GOOGLE_SERVICE_ACCOUNT_FILE")

        # WordPress設定
        wp_url = config.get("WP_URL")
        wp_user = config.get("WP_USER")
        wp_pass = config.get("WP_PASS")

        if not all([wp_url, wp_user, wp_pass]):
            print("❌ WordPress設定が不完全です。.envファイルを確認してください")
            return

        print(f"🌐 WordPressサイト: {wp_url}")
        print(f"👤 ユーザー: {wp_user}")

        # ブラウザとSheetsManagerを初期化
        browser = BrowserController()

        sheets = GoogleSheetsManager(spreadsheet_id, service_account_file)

        # 1. アクティブな目標を取得
        print("\n1. 📋 アクティブな目標を検索中...")
        active_goals = await get_active_goals(sheets)

        if not active_goals:
            print("ℹ️ アクティブな目標が見つかりませんでした")
            return

        print(f"🎯 アクティブな目標: {len(active_goals)}件")

        # 2. 設計図統合PM Agentで処理
        from agents.pm_agent.design_integrated_pm import DesignIntegratedPMAgent

        pm_agent = DesignIntegratedPMAgent(sheets, browser)

        results = []
        for goal in active_goals[:2]:  # 最大2つの目標を処理
            goal_id = goal.get("id")
            print(f"\n--- 目標 {goal_id} を処理中 ---")

            result = await pm_agent.process_goal_with_design(goal_id)
            results.append(result)

            if result.get("success"):
                print(f"✅ 目標 {goal_id} の処理が完了しました")
            else:
                print(f"❌ 目標 {goal_id} の処理に失敗しました")

        # 3. 実行結果のサマリー
        print("\n📊 実行結果サマリー:")
        successful = sum(1 for r in results if r.get("success"))
        designs_generated = sum(1 for r in results if r.get("design_generated"))
        total_tasks = sum(r.get("tasks_generated", 0) for r in results)

        print(f"  処理した目標: {len(results)}件")
        print(f"  成功: {successful}件")
        print(f"  設計図生成: {designs_generated}件")
        print(f"  生成されたタスク: {total_tasks}件")

        # 4. 次のステップの案内
        if total_tasks > 0:
            print(f"\n🎯 次のステップ:")
            print(f"  タスクを実行: DISPLAY=:1 python3 agents/pm_agent/automation.py")
            print(f"  または個別実行: DISPLAY=:1 python3 run_pm_tasks_adaptive.py --max-tasks 5")

        print("\n🎉 WordPress自動設定が完了しました！")

    except Exception as e:
        print(f"❌ システムエラー: {e}")
        import traceback

        traceback.print_exc()

    finally:
        if browser:
            await browser.cleanup()
            print("🧹 ブラウザをクリーンアップしました")


async def get_active_goals(sheets_manager) -> list:
    """アクティブな目標を取得"""
    try:
        spreadsheet = sheets_manager.gc.open_by_key(sheets_manager.spreadsheet_id)
        goal_sheet = spreadsheet.worksheet("project_goal")
        goals = goal_sheet.get_all_records()

        active_goals = [goal for goal in goals if goal.get("status") == "active"]
        return active_goals

    except Exception as e:
        print(f"❌ 目標取得エラー: {e}")
        return []


if __name__ == "__main__":
    asyncio.run(main())
