#!/usr/bin/env python3
"""
PM Tasks Loader (修正版)
実際のシート構造に対応
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import warnings

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from configuration.config_loader import get_config

    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    warnings.warn("configuration.config_loader が利用できません。", ImportWarning)


class PMTasksLoader:
    """Google Sheetsからタスクを読み込むローダークラス"""

    # カラム名のマッピング（実際のシート構造に対応）
    COLUMN_MAPPING = {
        "task_id": "TaskID",
        "parent_goal_id": "ParentGoalID",
        "description": "Description",
        "required_role": "Agent",
        "status": "Status",
        "priority": "Title",  # priority列に長文が入っているのでTitleとして扱う
        "estimated_time": "EstimatedTime",
        "dependencies": "Dependencies",
        "created_at": "CreatedAt",
        "batch_id": "BatchID",
    }

    def __init__(
        self,
        spreadsheet_id: Optional[str] = None,
        service_account_file: Optional[str] = None,
        pm_sheet_name: Optional[str] = None,
    ):
        """初期化"""
        if spreadsheet_id or service_account_file:
            warnings.warn("⚠️ 旧式コンストラクタを使用しています", DeprecationWarning)

        if CONFIG_AVAILABLE:
            self.spreadsheet_id = spreadsheet_id or get_config("SPREADSHEET_ID")
            self.service_account_file = service_account_file or get_config("SERVICE_ACCOUNT_FILE")
            self.pm_sheet_name = pm_sheet_name or get_config("PM_SHEET_NAME")
        else:
            self.spreadsheet_id = spreadsheet_id or ""
            self.service_account_file = service_account_file or "service_account.json"
            self.pm_sheet_name = pm_sheet_name or "pm_tasks"

        self.sheets_client = None
        self._initialize_sheets_client()

    def _initialize_sheets_client(self) -> None:
        """Google Sheetsクライアントの初期化"""
        try:
            import gspread
            from google.oauth2.service_account import Credentials

            possible_paths = [
                Path(self.service_account_file),
                Path("configuration") / self.service_account_file,
                Path(__file__).parent.parent / self.service_account_file,
                Path(__file__).parent.parent / "configuration" / self.service_account_file,
            ]

            sa_path = None
            for path in possible_paths:
                if path.exists():
                    sa_path = path
                    break

            if not sa_path:
                print(f"❌ サービスアカウントファイルが見つかりません: {self.service_account_file}")
                return

            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_file(str(sa_path), scopes=scopes)
            self.sheets_client = gspread.authorize(creds)
            print(f"✅ Google Sheetsクライアント初期化成功")

        except Exception as e:
            print(f"❌ Google Sheetsサービス初期化失敗: {e}")

    def load_tasks(self, max_tasks: Optional[int] = None, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """タスクを読み込む"""
        if self.sheets_client and self.spreadsheet_id:
            try:
                tasks = self._load_from_sheets(max_tasks, status_filter)
                if tasks:
                    return tasks
                print("⚠️ メインSheets失敗、代替スプレッドシートを試行...")
            except Exception as e:
                print(f"⚠️ Sheets読み込みエラー: {e}")

        print("⚠️ Sheets接続失敗、ローカルフォールバックを使用")
        return self._get_fallback_tasks(max_tasks)

    def _load_from_sheets(self, max_tasks: Optional[int], status_filter: Optional[str]) -> List[Dict[str, Any]]:
        """Google Sheetsからタスクを読み込む（実際の構造に対応）"""
        try:
            spreadsheet = self.sheets_client.open_by_key(self.spreadsheet_id)
            sheet = spreadsheet.worksheet(self.pm_sheet_name)

            all_values = sheet.get_all_values()
            if not all_values or len(all_values) < 2:
                return []

            # ヘッダー行（実際のカラム名）
            actual_headers = all_values[0]
            data_rows = all_values[1:]

            tasks = []
            for row in data_rows:
                if len(row) < len(actual_headers):
                    continue

                # 実際のカラム名でデータを取得
                raw_task = dict(zip(actual_headers, row))

                # 標準的なカラム名にマッピング
                task = {}
                for actual_col, standard_col in self.COLUMN_MAPPING.items():
                    if actual_col in raw_task:
                        task[standard_col] = raw_task[actual_col]

                # 空のタスクはスキップ
                if not task.get("TaskID"):
                    continue

                # ステータスフィルター
                if status_filter and task.get("Status", "").lower() != status_filter.lower():
                    continue

                tasks.append(task)

                if max_tasks and len(tasks) >= max_tasks:
                    break

            print(f"✅ Sheetsから {len(tasks)} タスク読み込み成功")
            return tasks

        except Exception as e:
            print(f"❌ Sheets読み込みエラー: {e}")
            import traceback

            traceback.print_exc()
            return []

    def _get_fallback_tasks(self, max_tasks: Optional[int]) -> List[Dict[str, Any]]:
        """フォールバック用のサンプルタスク"""
        fallback_tasks = [
            {
                "TaskID": "FALLBACK-001",
                "Title": "サンプルタスク1",
                "Description": "Google Sheets接続失敗時のフォールバックタスク",
                "Status": "未着手",
                "Priority": "中",
                "Agent": "GeneralAgent",
            }
        ]

        tasks = fallback_tasks[:max_tasks] if max_tasks else fallback_tasks
        print(f"✅ ハードコーディングフォールバックから {len(tasks)} タスク読み込み成功")
        return tasks


if __name__ == "__main__":
    """ローダーのテスト"""
    print("=== PMTasksLoader テスト ===")
    print()

    print("1. 実際のSheetsからタスク読み込み:")
    loader = PMTasksLoader()
    tasks = loader.load_tasks(max_tasks=3)

    print(f"\n📊 読み込み結果: {len(tasks)} タスク\n")

    for i, task in enumerate(tasks, 1):
        print(f"タスク {i}:")
        print(f"  TaskID: {task.get('TaskID', 'N/A')}")
        print(f"  Title: {task.get('Title', 'N/A')[:50]}...")  # 最初の50文字
        print(f"  Agent: {task.get('Agent', 'N/A')}")
        print(f"  Status: {task.get('Status', 'N/A')}")
        print(f"  Dependencies: {task.get('Dependencies', 'N/A')}")
        print()
