"""
シート更新の統一インターフェース（再発防止機能統合版）

【目的】
- 複数のGoogleSheetsManager実装に対応
- メソッド名の違いを吸収
- エラー時の自動フォールバック

【横展開可能な設計】
- 新しいメソッドが追加されても自動対応
- 既存コードの修正不要
"""

from typing import List, Any
import logging

logger = logging.getLogger(__name__)


class SheetsUpdateAdapter:
    """シート更新の汎用アダプター"""

    def __init__(self, sheets_manager):
        self.sheets = sheets_manager
        self._detect_methods()

    def _detect_methods(self):
        """利用可能なメソッドを自動検出"""
        # 優先順位順にメソッドを試す
        self.update_method = None
        self.append_method = None

        # 更新系メソッド
        for method in ["update_range", "update_cells", "update_values", "write_range"]:
            if hasattr(self.sheets, method):
                self.update_method = getattr(self.sheets, method)
                logger.info(f"✅ 更新メソッド検出: {method}")
                break

        # 追加系メソッド
        for method in ["append_rows", "append_row", "append"]:
            if hasattr(self.sheets, method):
                self.append_method = getattr(self.sheets, method)
                logger.info(f"✅ 追加メソッド検出: {method}")
                break

    def update_cell(self, range_name: str, values: List[List[Any]]) -> bool:
        """セル更新（堅牢版）"""
        try:
            if self.update_method:
                self.update_method(range_name, values)
                return True

            # フォールバック: 直接API呼び出し
            if hasattr(self.sheets, "service"):
                body = {"values": values}
                self.sheets.service.spreadsheets().values().update(
                    spreadsheetId=self.sheets.spreadsheet_id,
                    range=range_name,
                    valueInputOption="RAW",
                    body=body,
                ).execute()
                return True

            logger.error("❌ 利用可能な更新メソッドがありません")
            return False

        except Exception as e:
            logger.error(f"❌ セル更新エラー: {e}")
            return False

    def append_row(self, sheet_name: str, values: List[Any]) -> bool:
        """行追加（堅牢版）"""
        try:
            if self.append_method:
                self.append_method(sheet_name, [values])
                return True

            # フォールバック: 末尾検出 + 更新
            if self.update_method:
                # 既存データを取得
                data = self.sheets.read_range(f"{sheet_name}!A:Z")
                next_row = len(data) + 1
                range_name = f"{sheet_name}!A{next_row}"
                return self.update_cell(range_name, [values])

            logger.error("❌ 利用可能な追加メソッドがありません")
            return False

        except Exception as e:
            logger.error(f"❌ 行追加エラー: {e}")
            return False
