"""
SafeSheetsWrapper v1.1 - .env 自動読み込み対応版
"""

import logging
from typing import List, Any, Optional
from tools.sheets_manager import GoogleSheetsManager

# .env ファイルの自動読み込み
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SafeSheetsWrapper:
    """
    Google Sheets 安全操作ラッパー v1.1

    エラー時のフォールバック機能を提供
    """

    def __init__(self, sheets_manager: GoogleSheetsManager):
        """
        初期化

        Args:
            sheets_manager: GoogleSheetsManager インスタンス
        """
        self.sheets = sheets_manager
        logger.info("✅ SafeSheetsWrapper 初期化完了")

    def safe_read(self, range_name: str, default: List[List[Any]] = None) -> List[List[Any]]:
        """
        安全な読み取り（エラー時はデフォルト値を返す）

        Args:
            range_name: シート範囲
            default: エラー時のデフォルト値

        Returns:
            データ or デフォルト値
        """
        try:
            return self.sheets.read_range(range_name)
        except Exception as e:
            logger.warning(f"⚠️ データなし: {range_name}")
            return default if default is not None else []

    def safe_append(self, range_name: str, values: List[List[Any]]) -> bool:
        """
        安全な追加（エラー時は False を返す）

        Args:
            range_name: シート名
            values: 追加するデータ

        Returns:
            成功: True, 失敗: False
        """
        try:
            return self.sheets.append_rows(range_name, values)
        except Exception as e:
            logger.error(f"❌ 追加失敗: {range_name} - {e}")
            return False

    def safe_update(self, range_name: str, values: List[List[Any]]) -> bool:
        """
        安全な更新（エラー時は False を返す）

        Args:
            range_name: シート範囲
            values: 更新するデータ

        Returns:
            成功: True, 失敗: False
        """
        try:
            return self.sheets.update_range(range_name, values)
        except Exception as e:
            logger.error(f"❌ 更新失敗: {range_name} - {e}")
            return False
