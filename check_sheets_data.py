#!/usr/bin/env python3
"""
Google Sheetsの実際のデータを確認するスクリプト
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from configuration.config_loader import ConfigLoader
from tools.sheets_manager import GoogleSheetsManager


def check_sheets_data():
    """シートデータを確認"""
    try:
        config = ConfigLoader()
        spreadsheet_id = config.get("SPREADSHEET_ID")
        service_account_file = config.get("GOOGLE_SERVICE_ACCOUNT_FILE")

        print("🔧 SheetsManagerを初期化中...")
        sheets = GoogleSheetsManager(spreadsheet_id, service_account_file)

        # スプレッドシートを開く
        spreadsheet = sheets.gc.open_by_key(spreadsheet_id)

        print("📋 利用可能なシート一覧:")
        worksheets = spreadsheet.worksheets()
        for i, ws in enumerate(worksheets, 1):
            print(f"  {i}. {ws.title} (行: {ws.row_count}, 列: {ws.col_count})")

        # project_goal シートを確認
        print("\n�� project_goal シート:")
        try:
            goal_sheet = spreadsheet.worksheet("project_goal")
            goals = goal_sheet.get_all_records()
            print(f"  目標数: {len(goals)}")
            for i, goal in enumerate(goals[:3], 1):
                print(
                    f"  {i}. ID: {goal.get('id', 'N/A')}, タイトル: {goal.get('title', 'N/A')}, ステータス: {goal.get('status', 'N/A')}"
                )
        except Exception as e:
            print(f"  ❌ project_goal シートの読み込みエラー: {e}")

        # pm_tasks シートを確認
        print("\n📝 pm_tasks シート:")
        try:
            task_sheet = spreadsheet.worksheet("pm_tasks")
            tasks = task_sheet.get_all_records()
            print(f"  タスク数: {len(tasks)}")

            # ステータス別の集計
            status_count = {}
            for task in tasks:
                status = task.get("status", "unknown")
                status_count[status] = status_count.get(status, 0) + 1

            print(f"  ステータス別: {status_count}")

            # 最近のタスクを表示
            recent_tasks = tasks[-3:] if tasks else []
            for i, task in enumerate(recent_tasks, 1):
                print(f"  {i}. タイトル: {task.get('title', 'No title')}")
                print(f"     ステータス: {task.get('status', 'N/A')}, エージェント: {task.get('agent', 'N/A')}")

        except Exception as e:
            print(f"  ❌ pm_tasks シートの読み込みエラー: {e}")

        # task_execution_log シートを確認
        print("\n📊 task_execution_log シート:")
        try:
            log_sheet = spreadsheet.worksheet("task_execution_log")
            logs = log_sheet.get_all_records()
            print(f"  実行ログ数: {len(logs)}")

            # ステータス別の集計
            status_count = {}
            for log in logs:
                status = log.get("result_status", "unknown")
                status_count[status] = status_count.get(status, 0) + 1

            print(f"  結果別: {status_count}")

            # 最近のログを表示
            recent_logs = logs[-3:] if logs else []
            for i, log in enumerate(recent_logs, 1):
                print(f"  {i}. タスク: {log.get('task_title', 'No title')}")
                print(f"     結果: {log.get('result_status', 'N/A')}, 日時: {log.get('execution_date', 'N/A')}")

        except Exception as e:
            print(f"  ❌ task_execution_log シートの読み込みエラー: {e}")

    except Exception as e:
        print(f"❌ 全体エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    check_sheets_data()
