"""
SafeSheetsWrapper v2.2 - GoogleSheetsManager安全ラッパー
実際のAPIメソッド名に対応（read_range, append_data, update_cell）
"""

import logging
from typing import List, Any, Optional

logger = logging.getLogger(__name__)


class SafeSheetsWrapper:
    """GoogleSheetsManagerの安全なラッパークラス"""

    def __init__(self, sheets_manager):
        """
        初期化

        Args:
            sheets_manager: GoogleSheetsManagerインスタンス
        """
        self.sheets = sheets_manager
        self._validate_api()
        logger.info("✅ SafeSheetsWrapper v2.2 初期化完了")

    def _validate_api(self):
        """APIメソッドの存在確認（実際のGoogleSheetsManagerに合わせる）"""
        # 実際に使用するメソッドを確認
        required_methods = ["read_range", "append_data", "update_cell"]
        available_methods = [m for m in required_methods if hasattr(self.sheets, m)]

        if len(available_methods) < len(required_methods):
            missing = [m for m in required_methods if m not in available_methods]
            logger.warning(f"⚠️  一部メソッドが見つかりません: {missing}")
            logger.info(f"ℹ️  利用可能なメソッド: {available_methods}")
        else:
            logger.info(f"✅ 必須メソッド確認完了: {required_methods}")

    def safe_get_data(self, sheet_name: str, default=None) -> List[List[Any]]:
        """
        シートデータを安全に取得

        Args:
            sheet_name: シート名（例: "pm_tasks"）
            default: エラー時のデフォルト値

        Returns:
            シートデータ（2次元配列）
        """
        try:
            # read_range を使用（実際のGoogleSheetsManagerのメソッド）
            range_notation = f"{sheet_name}!A1:Z1000"
            logger.debug(f"📖 シート読み込み: {range_notation}")

            data = self.sheets.read_range(range_notation)

            if data:
                logger.info(f"✅ シート読み込み成功: {sheet_name} ({len(data)}行)")
                return data
            else:
                logger.info(f"ℹ️  シートは空です: {sheet_name}")
                return default if default is not None else []

        except Exception as e:
            logger.warning(f"⚠️  シート読み込み失敗 ({sheet_name}): {e}")
            return default if default is not None else []

    def safe_append(self, sheet_name: str, values: List[List[Any]]) -> bool:
        """
        データを安全に追記

        Args:
            sheet_name: シート名
            values: 追記するデータ（2次元配列）

        Returns:
            成功: True, 失敗: False
        """
        try:
            # 1次元配列を2次元に変換
            if values and not isinstance(values[0], list):
                values = [values]

            range_notation = f"{sheet_name}!A1"
            logger.debug(f"📝 データ追記: {range_notation}")

            result = self.sheets.append_data(range_notation, values)

            logger.info(f"✅ データ追記成功: {sheet_name} ({len(values)}行)")
            return True

        except Exception as e:
            logger.error(f"❌ データ追記失敗 ({sheet_name}): {e}")
            return False

    def safe_update(self, range_notation: str, values: List[List[Any]]) -> bool:
        """
        セルを安全に更新

        Args:
            range_notation: 範囲指定（例: "pm_tasks!A2:C2"）
            values: 更新データ（2次元配列）

        Returns:
            成功: True, 失敗: False
        """
        try:
            # 1次元配列を2次元に変換
            if values and not isinstance(values[0], list):
                values = [values]

            logger.debug(f"🔄 セル更新: {range_notation}")

            result = self.sheets.update_cell(range_notation, values)

            logger.info(f"✅ セル更新成功: {range_notation}")
            return True

        except Exception as e:
            logger.error(f"❌ セル更新失敗 ({range_notation}): {e}")
            return False

    def safe_read(self, range_notation: str, default=None) -> List[List[Any]]:
        """
        範囲指定で安全に読み込み

        Args:
            range_notation: 範囲指定（例: "pm_tasks!A1:Z100"）
            default: エラー時のデフォルト値

        Returns:
            読み込みデータ（2次元配列）
        """
        try:
            logger.debug(f"📖 範囲読み込み: {range_notation}")

            data = self.sheets.read_range(range_notation)

            if data:
                logger.info(f"✅ 範囲読み込み成功: {range_notation} ({len(data)}行)")
                return data
            else:
                logger.info(f"ℹ️  範囲は空です: {range_notation}")
                return default if default is not None else []

        except Exception as e:
            logger.warning(f"⚠️  範囲読み込み失敗 ({range_notation}): {e}")
            return default if default is not None else []
