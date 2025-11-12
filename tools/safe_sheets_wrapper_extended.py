"""
SafeSheetsWrapper拡張版 - 辞書変換機能付き
スプレッドシートのデータを自動的に辞書形式に変換
"""

from typing import Any, Dict, List

from tools.safe_sheets_wrapper import SafeSheetsWrapper
from tools.sheets_manager import GoogleSheetsManager


class SafeSheetsWrapperExtended(SafeSheetsWrapper):
    """
    SafeSheetsWrapper拡張版
    スキーマ定義に基づいて自動的にリスト→辞書変換を行う
    """

    # スキーマ定義（シート名 → 列名マッピング）
    SCHEMAS = {
        "project_goal": ["goal_id", "status", "description"],
        "pm_tasks": [
            "task_id",
            "parent_goal_id",
            "description",
            "required_role",
            "status",
            "priority",
            "estimated_time",
            "dependencies",
            "created_at",
            "batch_id",
            "detail_file_path",
        ],
        "task_execution_log": [
            "task_id",
            "execution_id",
            "status",
            "start_time",
            "end_time",
            "result",
            "error_message",
            "log_file_path",
        ],
    }

    def __init__(self, sheets_manager: GoogleSheetsManager):
        super().__init__(sheets_manager)

    def safe_read_as_dicts(
        self, range_name: str, default: List[Dict[str, Any]] = None, schema: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        スプレッドシートからデータを読み取り、辞書のリストとして返す

        Args:
            range_name: 範囲指定（例: 'project_goal!A2:C100'）
            default: デフォルト値
            schema: 列名のリスト（省略時は自動推定）

        Returns:
            辞書のリスト
        """
        if default is None:
            default = []

        # リスト形式でデータ取得
        rows = self.safe_read(range_name, default=[])

        if not rows or len(rows) == 0:
            return default

        # スキーマ決定
        if schema is None:
            # シート名からスキーマを推定
            sheet_name = range_name.split("!")[0]
            schema = self.SCHEMAS.get(sheet_name, None)

        if schema is None:
            # スキーマが不明な場合は1行目をヘッダーとして使用
            if len(rows) > 0:
                schema = rows[0]
                rows = rows[1:]
            else:
                return default

        # リスト → 辞書変換
        result = []
        for row in rows:
            row_dict = {}
            for i, col_name in enumerate(schema):
                if i < len(row):
                    row_dict[col_name] = row[i]
                else:
                    row_dict[col_name] = ""
            result.append(row_dict)

        return result

    def get_sheet_schema(self, sheet_name: str) -> List[str]:
        """シートのスキーマを取得"""
        return self.SCHEMAS.get(sheet_name, [])


# テスト
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    sheets = GoogleSheetsManager()
    wrapper = SafeSheetsWrapperExtended(sheets)

    print("🧪 テスト1: project_goal を辞書形式で取得")
    goals = wrapper.safe_read_as_dicts("project_goal!A2:C10", default=[])
    print(f"取得件数: {len(goals)}")
    if goals:
        print(f"最初のゴール: {goals[0]}")
        print(f"  goal_id: {goals[0].get('goal_id')}")
        print(f"  status: {goals[0].get('status')}")
        print(f"  description: {goals[0].get('description')}")

    print("\n🧪 テスト2: pm_tasks を辞書形式で取得")
    tasks = wrapper.safe_read_as_dicts("pm_tasks!A2:K10", default=[])
    print(f"取得件数: {len(tasks)}")
    if tasks:
        print(f"最初のタスク: {tasks[0].get('task_id')} - {tasks[0].get('status')}")
