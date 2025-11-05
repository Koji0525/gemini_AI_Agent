"""
PMTasksLoader - スネークケース対応版 + ステータス更新機能追加
スプレッドシートがスネークケースなので、そのまま使用
"""

from typing import List, Dict, Any, Optional
from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import get_config


class PMTasksLoader:
    """pm_tasksシートからタスクを読み込むクラス"""

    def __init__(self):
        """初期化"""
        self.sheets_client = None
        self.spreadsheet_id = None
        self.pm_sheet_name = "pm_tasks"
        self.worksheet = None

        try:
            sheets_manager = GoogleSheetsManager(
                spreadsheet_id=get_config("SPREADSHEET_ID"),
                service_account_file=get_config("SERVICE_ACCOUNT_FILE"),
            )
            self.sheets_client = sheets_manager.gc
            self.spreadsheet_id = get_config("SPREADSHEET_ID")

            # ワークシートを事前に取得（update_task_statusで使用）
            spreadsheet = self.sheets_client.open_by_key(self.spreadsheet_id)
            self.worksheet = spreadsheet.worksheet(self.pm_sheet_name)

            print("✅ Google Sheetsクライアント初期化成功")
        except Exception as e:
            print(f"⚠️ Google Sheets初期化失敗: {e}")

    def load_tasks(
        self, max_tasks: Optional[int] = None, status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
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

    def _load_from_sheets(
        self, max_tasks: Optional[int], status_filter: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Google Sheetsからタスクを読み込む（スネークケース対応 + row_number追加）"""
        try:
            if not self.worksheet:
                spreadsheet = self.sheets_client.open_by_key(self.spreadsheet_id)
                self.worksheet = spreadsheet.worksheet(self.pm_sheet_name)

            all_values = self.worksheet.get_all_values()

            if not all_values or len(all_values) < 2:
                return []

            # ヘッダー行（実際の列名）
            headers = all_values[0]
            data_rows = all_values[1:]

            # status列のインデックスを取得（更新時に使用）
            try:
                self.status_col_index = headers.index("status") + 1  # gspreadは1-indexed
            except ValueError:
                print("⚠️ 'status'列が見つかりません。デフォルトで5列目を使用")
                self.status_col_index = 5

            tasks = []

            for row_idx, row in enumerate(data_rows, start=2):  # start=2: ヘッダー行の次から
                if len(row) < len(headers):
                    # 行の長さを揃える
                    row = row + [""] * (len(headers) - len(row))

                # そのままスネークケースの辞書を作成
                task = dict(zip(headers, row))

                # 空のタスクをスキップ
                if not task.get("task_id"):
                    continue

                # 重要: row_number を追加（Google Sheetsの実際の行番号）
                task["row_number"] = row_idx

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

    def update_task_status(self, task_id: str, status: str) -> bool:
        """
        タスクのステータスを更新

        Args:
            task_id: タスクID
            status: 新しいステータス (pending/in_progress/completed/failed)

        Returns:
            bool: 更新成功時True、失敗時False
        """
        try:
            if not self.worksheet:
                print(f"❌ ワークシートが初期化されていません")
                return False

            # task_idから行番号を検索
            all_values = self.worksheet.get_all_values()
            headers = all_values[0]

            try:
                task_id_col_index = headers.index("task_id")
            except ValueError:
                print(f"❌ 'task_id'列が見つかりません")
                return False

            # task_idが一致する行を検索
            row_number = None
            for row_idx, row in enumerate(all_values[1:], start=2):
                if len(row) > task_id_col_index and row[task_id_col_index] == task_id:
                    row_number = row_idx
                    break

            if not row_number:
                print(f"❌ task_id '{task_id}' が見つかりません")
                return False

            # ステータス列を更新
            self.worksheet.update_cell(row_number, self.status_col_index, status)
            print(f"✅ タスク {task_id} (行{row_number}) のステータスを '{status}' に更新しました")
            return True

        except Exception as e:
            print(f"❌ ステータス更新エラー (task_id: {task_id}): {e}")
            import traceback

            traceback.print_exc()
            return False

    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        task_idからタスク情報を取得

        Args:
            task_id: タスクID

        Returns:
            タスク辞書 or None
        """
        tasks = self.load_tasks()
        for task in tasks:
            if task.get("task_id") == task_id:
                return task
        return None


# テスト用
if __name__ == "__main__":
    loader = PMTasksLoader()

    # テスト1: タスク読み込み
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
        print(f"  row_number: {first.get('row_number')}")  # 追加確認

        # テスト2: ステータス更新（コメントアウト推奨）
        # test_task_id = first.get('task_id')
        # print(f"\n=== ステータス更新テスト ===")
        # success = loader.update_task_status(test_task_id, "in_progress")
        # print(f"更新結果: {'成功' if success else '失敗'}")
