#!/usr/bin/env python3
"""
SheetsStructureValidator - スプレッドシート構造検証
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
from typing import List, Dict, Any
from tools.safe_sheets_wrapper import SafeSheetsWrapper

logger = logging.getLogger(__name__)


class SheetsStructureValidator:
    """スプレッドシート構造検証"""

    def __init__(self, sheets_manager):
        self.sheets = SafeSheetsWrapper(sheets_manager)
        logger.info("✅ SheetsStructureValidator 初期化完了")

    def validate_sheet(self, sheet_name: str, expected_headers: List[str]) -> bool:
        """シート構造を検証"""
        try:
            # 範囲指定でヘッダー行を読み込み
            range_name = f"{sheet_name}!A1:Z1"
            data = self.sheets.safe_read(range_name, default=[])

            if not data:
                logger.warning(f"⚠️ {sheet_name}: ヘッダー行が空です")
                return False

            actual_headers = data[0] if isinstance(data[0], list) else data
            actual_headers = [h for h in actual_headers if h]

            if actual_headers == expected_headers:
                logger.info(f"✅ {sheet_name}: ヘッダー一致")
                return True
            else:
                logger.warning(f"⚠️ {sheet_name}: ヘッダー不一致")
                logger.warning(f"   期待: {expected_headers}")
                logger.warning(f"   実際: {actual_headers}")
                return False

        except Exception as e:
            logger.error(f"❌ {sheet_name} 検証エラー: {e}")
            return False


if __name__ == "__main__":
    print("📦 sheets_structure_validator.py")
    print("✅ モジュールインポート問題修正済み")
