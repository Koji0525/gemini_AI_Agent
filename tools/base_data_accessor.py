"""
BaseDataAccessor - 全コンポーネント統一のデータアクセスパターン
TaskExecutorの成功パターンをベースクラス化
"""

import logging
from abc import ABC
from typing import Any, Dict, List, Optional

from tools.safe_sheets_wrapper import SafeSheetsWrapper
from tools.sheets_manager import GoogleSheetsManager

logger = logging.getLogger(__name__)


class BaseDataAccessor(ABC):
    """
    全コンポーネント統一のデータアクセスベースクラス
    TaskExecutorの成功パターンを標準化
    """

    def __init__(self, sheets_manager: GoogleSheetsManager = None):
        """
        初期化

        Args:
            sheets_manager: GoogleSheetsManager（Noneの場合は新規作成）
        """
        if sheets_manager is None:
            self.sheets = GoogleSheetsManager()
        else:
            self.sheets = sheets_manager

        self.safe_sheets = SafeSheetsWrapper(self.sheets)

        # シートごとの列構造キャッシュ
        self._column_maps = {}

    def _get_column_map(self, sheet_name: str, force_reload: bool = False) -> Dict[str, int]:
        """
        シートの列構造を取得（キャッシュ機能付き）

        Args:
            sheet_name: シート名（例: 'project_goal', 'pm_tasks'）
            force_reload: キャッシュを無視して再読み込み

        Returns:
            列名→インデックスのマッピング
        """
        # キャッシュチェック
        if not force_reload and sheet_name in self._column_maps:
            return self._column_maps[sheet_name]

        try:
            # ヘッダー行を読み取り
            headers_data = self.safe_sheets.safe_read(f"{sheet_name}!A1:Z1", default=[])

            if not headers_data or len(headers_data) == 0:
                logger.error(f"❌ {sheet_name}: ヘッダー行が取得できません")
                return {}

            headers = headers_data[0]

            # 列名→インデックスのマッピング作成
            column_map = {header: idx for idx, header in enumerate(headers)}

            # キャッシュに保存
            self._column_maps[sheet_name] = column_map

            logger.info(f"✅ {sheet_name}列構造: {list(column_map.keys())}")

            return column_map

        except Exception as e:
            logger.error(f"❌ {sheet_name}列構造取得エラー: {e}")
            return {}

    def _convert_row_to_dict(self, row: List[Any], column_map: Dict[str, int]) -> Dict[str, Any]:
        """
        行データを辞書に変換（TaskExecutorパターン）

        Args:
            row: データ行
            column_map: 列名→インデックスのマッピング

        Returns:
            辞書形式のデータ
        """
        result = {}

        for col_name, col_idx in column_map.items():
            if col_idx < len(row):
                result[col_name] = row[col_idx]
            else:
                result[col_name] = ""

        return result

    def read_sheet_as_dicts(
        self, sheet_name: str, range_spec: str = "A2:Z1000", filter_func: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        シートからデータを辞書のリストとして取得

        Args:
            sheet_name: シート名
            range_spec: 範囲指定（デフォルト: A2:Z1000）
            filter_func: フィルタ関数（Optional）

        Returns:
            辞書のリスト
        """
        try:
            # 列構造を取得
            column_map = self._get_column_map(sheet_name)

            if not column_map:
                logger.error(f"❌ {sheet_name}: 列構造が取得できません")
                return []

            # データ行を読み取り
            data_rows = self.safe_sheets.safe_read(f"{sheet_name}!{range_spec}", default=[])

            if not data_rows:
                logger.info(f"ℹ️ {sheet_name}: データがありません")
                return []

            # リスト→辞書変換
            result = [self._convert_row_to_dict(row, column_map) for row in data_rows]

            # フィルタ適用
            if filter_func:
                result = [item for item in result if filter_func(item)]

            return result

        except Exception as e:
            logger.error(f"❌ {sheet_name}読み取りエラー: {e}")
            import traceback

            traceback.print_exc()
            return []

    def get_column_index(self, sheet_name: str, column_name: str) -> Optional[int]:
        """
        列名からインデックスを取得

        Args:
            sheet_name: シート名
            column_name: 列名

        Returns:
            インデックス（見つからない場合はNone）
        """
        column_map = self._get_column_map(sheet_name)
        return column_map.get(column_name)

    def diagnose_sheet_structure(self, sheet_name: str) -> Dict[str, Any]:
        """
        シート構造の診断

        Args:
            sheet_name: シート名

        Returns:
            診断結果
        """
        try:
            column_map = self._get_column_map(sheet_name, force_reload=True)

            # データ行を読み取り
            data_rows = self.safe_sheets.safe_read(f"{sheet_name}!A2:Z10", default=[])

            diagnosis = {
                "sheet_name": sheet_name,
                "has_headers": len(column_map) > 0,
                "column_count": len(column_map),
                "columns": list(column_map.keys()),
                "data_row_count": len(data_rows),
                "status": "ok" if len(column_map) > 0 else "error",
            }

            return diagnosis

        except Exception as e:
            return {"sheet_name": sheet_name, "status": "error", "error": str(e)}


# テスト・診断ツール
if __name__ == "__main__":
    print("🧪 BaseDataAccessor テスト\n")

    accessor = BaseDataAccessor()

    # テスト1: project_goal 診断
    print("テスト1: project_goal 診断")
    diagnosis = accessor.diagnose_sheet_structure("project_goal")
    print(f"  ステータス: {diagnosis['status']}")
    print(f"  列数: {diagnosis['column_count']}")
    print(f"  列名: {diagnosis['columns']}")
    print(f"  データ行数: {diagnosis['data_row_count']}")

    # テスト2: active/pending ゴール取得
    print("\nテスト2: active/pending ゴール取得")
    goals = accessor.read_sheet_as_dicts(
        "project_goal", filter_func=lambda g: g.get("status", "").lower() in ["active", "pending"]
    )
    print(f"  取得件数: {len(goals)}")
    for goal in goals:
        print(
            f"    • {goal.get('goal_id')} - {goal.get('status')} - {goal.get('goal_description', '')[:50]}..."
        )

    # テスト3: pm_tasks 診断
    print("\nテスト3: pm_tasks 診断")
    diagnosis = accessor.diagnose_sheet_structure("pm_tasks")
    print(f"  ステータス: {diagnosis['status']}")
    print(f"  列数: {diagnosis['column_count']}")
    print(f"  データ行数: {diagnosis['data_row_count']}")
