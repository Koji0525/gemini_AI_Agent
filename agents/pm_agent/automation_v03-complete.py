#!/usr/bin/env python3
"""
PM Agent 完全自動化システム（全フェーズ統合版・修正版）

Phase 1: 進捗監視（スキップ可能）
Phase 2: タスク分解（Gemini）
Phase 3: タスク登録
Phase 4: タスク実行準備
"""

import asyncio
import sys
import os
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
    """
    空セルに対応したシートデータ取得

    Args:
        sheets_manager: GoogleSheetsManagerインスタンス
        spreadsheet_id: スプレッドシートID
        sheet_name: シート名

    Returns:
        list: 辞書のリスト
    """
    spreadsheet = sheets_manager.gc.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet(sheet_name)

    # すべての値を取得
    all_values = worksheet.get_all_values()

    if len(all_values) < 2:
        return []

    # ヘッダー行を取得
    headers = all_values[0]

    # 空でないヘッダーのインデックスを特定
    valid_headers = {}
    for i, header in enumerate(headers):
        if header and header.strip():
            valid_headers[i] = header.strip()

    # データ行を辞書に変換
    result = []
    for row_values in all_values[1:]:
        row_dict = {}
        for col_idx, header_name in valid_headers.items():
            if col_idx < len(row_values):
                row_dict[header_name] = row_values[col_idx]
            else:
                row_dict[header_name] = ""

        # 空行はスキップ
        if any(row_dict.values()):
            result.append(row_dict)

    return result


async def main():
    """メイン実行関数（全フェーズ強制実行）"""
    print("=" * 70)
    print("🤖 PM Agent 完全自動化システム（全フェーズ統合版）")
    print("=" * 70)
    print(f"開始日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 設定読み込み
    config = ConfigLoader()
    spreadsheet_id = config.get("SPREADSHEET_ID") or config.get("spreadsheet_id")
    service_account_file = config.get("GOOGLE_SERVICE_ACCOUNT_FILE") or config.get("service_account_file")

    print(f"📊 スプレッドシートID: {spreadsheet_id}")
    print(f"🔑 サービスアカウント: {service_account_file}")

    # Google Sheets接続
    sheets_manager = GoogleSheetsManager(spreadsheet_id, service_account_file)
    print("✅ Google Sheets接続成功")

    browser = None
    try:
        # ============================================================
        # BrowserController初期化
        # ============================================================
        print("🌐 BrowserController初期化中...")
        browser = BrowserController()
        await browser.setup_browser()
        print("✅ ブラウザ初期化完了")

        # ============================================================
        # Geminiページ移動
        # ============================================================
        print("🤖 Geminiページに移動中...")
        await browser.navigate_to_gemini()
        print("✅ Gemini準備完了")

        # ============================================================
        # 【Phase 1】進捗監視（スキップして全ゴールを対象）
        # ============================================================
        print()
        print("【Phase 1】進捗監視（スキップして全ゴールを対象）")
        print("-" * 70)

        # 空セル対応版でデータ取得
        all_goals_data = get_sheet_data_robust(sheets_manager, spreadsheet_id, "project_goal")

        # アクティブなゴールをフィルタ
        goals = []
        for row in all_goals_data:
            goal_id = row.get("goal_id")
            status = row.get("status", "").lower()
            goal_desc = row.get("goal_description", "")

            # goal_id があり、status が planning または active のもの
            if goal_id and status in ["planning", "active"] and goal_desc:
                goals.append({"goal_id": goal_id, "goal_description": goal_desc, "status": status})

        if not goals:
            print("⚠️ アクティブなゴールがありません")
            print("📝 新しいゴールを project_goal シートに追加してください")
            print("   （status: planning または active、goal_description 必須）")
            return

        print(f"✅ {len(goals)}個のアクティブなゴールを発見")
        for g in goals:
            print(f"  - ゴール #{g['goal_id']}: {g['goal_description'][:50]}...")

        # ============================================================
        # 【Phase 2】タスク分解（Gemini）
        # ============================================================
        print()
        print("【Phase 2】タスク分解（Gemini統合）")
        print("-" * 70)

        task_breakdown = GeminiTaskBreakdownAgent(sheets_manager, browser)
        task_registration = TaskRegistrationAgent(sheets_manager)
        task_exporter = TaskExportAgent()

        total_registered = 0

        for goal in goals:
            goal_id = goal["goal_id"]
            goal_desc = goal["goal_description"]

            print(f"\n🎯 ゴール #{goal_id}: {goal_desc[:100]}")

            # タスク分解実行
            try:
                tasks = await task_breakdown.generate_tasks_for_goal(
                    goal_id=goal_id, goal_title=f"ゴール{goal_id}", goal_description=goal_desc
                )

                if not tasks:
                    print("⚠️ タスク分解に失敗しました")
                    continue

                print(f"✅ {len(tasks)}個のタスクに分解しました")

                # ============================================================
                # 【Phase 3】タスク登録（ゴール単位）
                # ============================================================
                print(f"\n【Phase 3】ゴール #{goal_id} のタスク登録")
                print("-" * 50)

                # タスク詳細をエクスポート
                export_path = task_exporter.export_tasks(goal_id, tasks)
                print(f"📄 タスク詳細をエクスポート: {export_path}")

                # ✅ 正しい呼び出し方: リスト全体を渡す
                registered_count = await task_registration.register_tasks(
                    goal_id=goal_id, tasks=tasks, detail_file_path=export_path  # リスト全体
                )

                print(f"✅ {registered_count}個のタスクを登録しました")
                total_registered += registered_count

            except Exception as e:
                print(f"❌ エラー: {e}")
                import traceback

                traceback.print_exc()
                continue

        print()
        print("=" * 70)
        print(f"🎉 タスク生成・登録完了！（合計 {total_registered}個）")
        print("=" * 70)

        # ============================================================
        # 【Phase 4】タスク実行準備
        # ============================================================
        print()
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
        print(f"❌ エラー発生: {e}")
        import traceback

        traceback.print_exc()

    finally:
        if browser:
            print("🧹 ブラウザをクリーンアップ中...")
            await browser.cleanup()
            print("✅ クリーンアップ完了")


if __name__ == "__main__":
    asyncio.run(main())
