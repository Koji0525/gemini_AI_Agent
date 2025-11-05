"""
PMTasksLoaderの修正版 - ステータス更新メソッド追加
"""

import os
from typing import List, Dict, Any
from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import ConfigLoader
from datetime import datetime


class PMTasksLoader:
    def __init__(self, spreadsheet_id: str = None):
        self.config = ConfigLoader()
        self.spreadsheet_id = spreadsheet_id or self.config.get("SPREADSHEET_ID")
        self.sheets_manager = GoogleSheetsManager(self.spreadsheet_id)

        # シート名の設定
        self.tasks_sheet = "pm_tasks"
        self.execution_log_sheet = "task_execution_log"

    def update_task_status(self, task_id: str, status: str, details: str = ""):
        """タスクのステータスを更新"""
        try:
            # pm_tasksシートの更新
            tasks_data = self.sheets_manager.read_sheet(self.tasks_sheet)
            if not tasks_data:
                print("❌ pm_tasksシートのデータを読み込めません")
                return False

            # ヘッダー行を取得
            headers = tasks_data[0]
            task_id_col = headers.index("task_id") if "task_id" in headers else None
            status_col = headers.index("status") if "status" in headers else None

            if task_id_col is None or status_col is None:
                print("❌ 必要なカラムが見つかりません")
                return False

            # タスクIDで検索してステータス更新
            updated = False
            for i, row in enumerate(tasks_data[1:], start=2):  # 行番号は2から
                if len(row) > task_id_col and row[task_id_col] == task_id:
                    # 行を拡張してstatusカラムを確保
                    while len(row) <= status_col:
                        row.append("")
                    row[status_col] = status

                    # シートを更新
                    self.sheets_manager.update_cell(
                        self.tasks_sheet, f"{chr(65 + status_col)}{i}", status
                    )
                    updated = True
                    print(f"✅ タスク {task_id} のステータスを {status} に更新")
                    break

            # 実行ログにも記録
            if updated and details:
                self._log_execution(task_id, status, details)

            return updated

        except Exception as e:
            print(f"❌ ステータス更新エラー: {e}")
            return False

    def _log_execution(self, task_id: str, status: str, details: str):
        """実行ログを記録"""
        try:
            log_data = self.sheets_manager.read_sheet(self.execution_log_sheet)
            headers = log_data[0] if log_data else []

            new_log = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "task_id": task_id,
                "status": status,
                "details": details,
            }

            # ヘッダーに合わせて行を作成
            row = []
            for header in headers:
                row.append(new_log.get(header, ""))

            self.sheets_manager.append_row(self.execution_log_sheet, row)
            print(f"📝 実行ログを記録: {task_id} - {status}")

        except Exception as e:
            print(f"❌ ログ記録エラー: {e}")
