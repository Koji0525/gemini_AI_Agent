#!/usr/bin/env python3
"""
SafeSheetsWrapper v2.1 - 範囲指定対応版
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class SafeSheetsWrapper:
    """GoogleSheetsManager の安全なラッパー（範囲指定対応）"""

    REQUIRED_METHODS = [
        "read_sheet",  # シート全体
        "get_sheet_data",  # 辞書形式
        "write_sheet",  # 書き込み
        "read_range",  # 範囲指定（新規）
    ]

    def __init__(self, sheets_manager):
        if isinstance(sheets_manager, SafeSheetsWrapper):
            logger.info("✅ 既に SafeSheetsWrapper - そのまま使用")
            self.sheets = sheets_manager.sheets
        else:
            self.sheets = sheets_manager
            self._validate_api()

        logger.info("✅ SafeSheetsWrapper v2.1 を初期化しました")

    def _validate_api(self):
        """API検証"""
        missing = []
        for method in self.REQUIRED_METHODS:
            if not hasattr(self.sheets, method):
                missing.append(method)

        if missing:
            logger.error(f"❌ 必須メソッドが見つかりません: {missing}")
            raise AttributeError(f"Required method '{missing[0]}' not found")

        logger.info("✅ API検証完了: すべての必須メソッドが存在します")

    def safe_read(self, range_spec: str, default: Any = None) -> Any:
        """
        安全な読み込み（範囲指定対応）

        Args:
            range_spec: 'sheet_name!A1:Z10' または 'sheet_name'
            default: エラー時のデフォルト値

        Returns:
            範囲指定: List[List[Any]]
            シート名のみ: List[Dict[str, Any]]
        """
        try:
            # 範囲指定があればread_range、なければread_sheet
            if "!" in range_spec:
                data = self.sheets.read_range(range_spec)
            else:
                data = self.sheets.read_sheet(range_spec)

            logger.info(
                f"✅ '{range_spec}' から {len(data) if data else 0} 件のデータを読み込みました"
            )
            return data if data else default

        except Exception as e:
            logger.warning(f"⚠️ 読み込みエラー ({range_spec}): {e}")
            return default

    def safe_get_data(self, sheet_name: str, default: Any = None) -> List[Dict[str, Any]]:
        """安全なデータ取得（辞書形式）"""
        try:
            data = self.sheets.get_sheet_data(sheet_name)
            logger.info(
                f"✅ '{sheet_name}' から {len(data) if data else 0} 件のデータを取得しました"
            )
            return data if data else default
        except Exception as e:
            logger.warning(f"⚠️ データ取得エラー ({sheet_name}): {e}")
            return default

    def safe_write(self, sheet_name: str, data: List[List[Any]]) -> bool:
        """安全な書き込み"""
        try:
            if data and not isinstance(data[0], list):
                data = [data]

            result = self.sheets.write_sheet(sheet_name, data)

            if result:
                logger.info(f"✅ '{sheet_name}' に {len(data)} 行を書き込みました")
            else:
                logger.warning(f"⚠️ '{sheet_name}' への書き込みが失敗しました")

            return result
        except Exception as e:
            logger.error(f"❌ 書き込みエラー ({sheet_name}): {e}")
            return False

    def safe_append(self, sheet_name: str, values: List[List[Any]]) -> bool:
        """safe_writeのエイリアス"""
        return self.safe_write(sheet_name, values)


if __name__ == "__main__":
    print("=" * 60)
    print("📦 SafeSheetsWrapper v2.1 - 範囲指定対応版")
    print("=" * 60)
    print("\n✅ 必須メソッド:")
    for i, method in enumerate(SafeSheetsWrapper.REQUIRED_METHODS, 1):
        print(f"   {i}. {method}")
    print("\n✅ 使用例:")
    print("   safe_read('project_goal!A1:Z1')  # ヘッダー行")
    print("   safe_read('pm_tasks')             # シート全体")
    print("=" * 60)
