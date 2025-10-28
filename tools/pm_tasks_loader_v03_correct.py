#!/usr/bin/env python3
"""
PMTasksLoader - スネークケース対応版
スプレッドシートがスネークケースなので、そのまま使用
"""

from typing import List, Dict, Any, Optional
from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import get_config


class PMTasksLoader:
    """pm_tasksシートからタスクを読み込むクラス"""

    # スプレッドシートの列名がすでにスネークケースなので、
    # マッピング不要（そのまま使用）
    # 念のため、空白列名などの対応のみ

    def __init__(self):
        """初期化"""
        self.sheets_client = None
        self.spreadsheet_id = None
        self.pm_sheet_name = "pm_tasks"

        try:
            sheets_manager = GoogleSheetsManager(
                spreadsheet_id=get_config("SPREADSHEET_ID"), service_account_file=get_config("SERVICE_ACCOUNT_FILE")
            )
            self.sheets_client = sheets_manager.gc
            self.spreadsheet_id = get_config("SPREADSHEET_ID")
            print("✅ Google Sheetsクライアント初期化成功")
        except Exception as e:
            print(f"⚠️ Google Sheets初期化失敗: {e}")

    def load_tasks(self, max_tasks: Optional[int] = None, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """タスクを読み込む"""
        if self.sheets_client and self.spreadsheet_id:
            try:
                tasks = self._load_from_sheets(max_tasks, status_filter)
                if tasks:
                    return tasks
                print("⚠️ メインSheets失敗、フォールバックを試行...")
            except Exception as e:
                print(f"⚠️ Sheets読み込みエラー: {e}")

        return []

    def _load_from_sheets(self, max_tasks: Optional[int], status_filter: Optional[str]) -> List[Dict[str, Any]]:
        """Google Sheetsからタスクを読み込む（スネークケース対応）"""
        try:
            spreadsheet = self.sheets_client.open_by_key(self.spreadsheet_id)
            sheet = spreadsheet.worksheet(self.pm_sheet_name)

            all_values = sheet.get_all_values()

            if not all_values or len(all_values) < 2:
                return []

            # ヘッダー行（実際の列名）
            headers = all_values[0]
            data_rows = all_values[1:]

            tasks = []

            for row in data_rows:
                if len(row) < len(headers):
                    # 行の長さを揃える
                    row = row + [""] * (len(headers) - len(row))

                # そのままスネークケースの辞書を作成
                task = dict(zip(headers, row))

                # 空のタスクをスキップ
                if not task.get("task_id"):
                    continue

                # ステータスフィルター
                if status_filter:
                    task_status = task.get("status", "").lower()
                    if task_status != status_filter.lower():
                        continue

                tasks.append(task)

                if max_tasks and len(tasks) >= max_tasks:
                    break

            print(f"✅ Sheetsから {len(tasks)} タスク読み込み成功")
            return tasks

        except Exception as e:
            print(f"❌ Sheets読み込み失敗: {e}")
            import traceback

            traceback.print_exc()
            return []


# テスト用
if __name__ == "__main__":
    loader = PMTasksLoader()
    tasks = loader.load_tasks(max_tasks=5, status_filter="pending")

    print(f"\n=== テスト結果 ===")
    print(f"読み込みタスク数: {len(tasks)}")

    if tasks:
        first = tasks[0]
        print(f"\n最初のタスク:")
        print(f"  キー: {list(first.keys())}")
        print(f"  task_id: {first.get('task_id')}")
        print(f"  parent_goal_id: {first.get('parent_goal_id')}")
        print(f"  status: {first.get('status')}")
