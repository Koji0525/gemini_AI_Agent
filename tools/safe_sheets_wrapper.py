"""
SafeSheetsWrapper v2.3 - Google Sheets操作の安全なラッパー

変更履歴:
- v2.3: append_data → append_rows に修正（実際のAPI名に合わせる）
- v2.2: API検証ロジック追加
- v2.1: エラーハンドリング強化
"""

import logging
import os
import sys
from typing import Any, List, Optional

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

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
        self._verify_api()

    def _verify_api(self):
        """API検証"""
        required_methods = ["read_range", "append_rows", "update_range"]
        missing = [m for m in required_methods if not hasattr(self.sheets, m)]

        if missing:
            logger.warning(f"⚠️  一部メソッドが見つかりません: {missing}")
        else:
            logger.info("✅ すべての必須メソッドが利用可能です")

    def safe_read(self, range_notation: str, default: Optional[List] = None) -> List[List[Any]]:
        """
        データを安全に読み込み

        Args:
            range_notation: 範囲表記（例: 'pm_tasks!A1:Z10'）
            default: エラー時のデフォルト値

        Returns:
            読み込んだデータ（2次元配列）
        """
        try:
            logger.debug(f"📖 データ読み込み: {range_notation}")
            result = self.sheets.read_range(range_notation)

            if not result:
                logger.warning(f"⚠️  データなし: {range_notation}")
                return default if default is not None else []

            logger.info(f"✅ データ読み込み成功: {len(result)}行")
            return result

        except Exception as e:
            logger.error(f"❌ データ読み込み失敗 ({range_notation}): {e}")
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

            logger.info(f"📝 データ追記開始: {sheet_name} ({len(values)}行)")
            logger.debug(f"   データ内容: {values[:2]}...")  # 最初の2行のみ表示

            # 正しいメソッド名: append_rows
            self.sheets.append_rows(sheet_name, values)

            logger.info(f"✅ データ追記成功: {sheet_name}")
            return True

        except AttributeError as e:
            logger.error(f"❌ メソッドが見つかりません: {e}")
            logger.error(
                f"   利用可能なメソッド: {[m for m in dir(self.sheets) if 'append' in m.lower()]}"
            )
            return False

        except Exception as e:
            logger.error(f"❌ データ追記失敗 ({sheet_name}): {e}")
            import traceback

            logger.error(traceback.format_exc())
            return False

    def safe_update(self, range_notation: str, values: List[List[Any]]) -> bool:
        """
        セルを安全に更新

        Args:
            range_notation: 範囲表記（例: 'pm_tasks!A2:D2'）
            values: 更新するデータ（2次元配列）

        Returns:
            成功: True, 失敗: False
        """
        try:
            # 1次元配列を2次元に変換
            if values and not isinstance(values[0], list):
                values = [values]

            logger.info(f"📝 セル更新開始: {range_notation}")

            # 正しいメソッド名: update_range
            self.sheets.update_range(range_notation, values)

            logger.info(f"✅ セル更新成功: {range_notation}")
            return True

        except AttributeError as e:
            logger.error(f"❌ メソッドが見つかりません: {e}")
            logger.error(
                f"   利用可能なメソッド: {[m for m in dir(self.sheets) if 'update' in m.lower()]}"
            )
            return False

        except Exception as e:
            logger.error(f"❌ セル更新失敗 ({range_notation}): {e}")
            import traceback

            logger.error(traceback.format_exc())
            return False


# ====================
# テスト実行
# ====================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    from browser_control.sheets_manager import GoogleSheetsManager

    print("🧪 SafeSheetsWrapper v2.3 テスト")

    sheets = GoogleSheetsManager()
    safe_sheets = SafeSheetsWrapper(sheets)

    # 読み込みテスト
    data = safe_sheets.safe_read("pm_tasks!A1:Z5", default=[])
    print(f"\n✅ 読み込みテスト: {len(data)}行")

    # 書き込みテスト（ドライラン）
    test_data = [["TEST_001", "テスト", "HIGH", "PENDING"]]
    print(f"\n🔍 書き込みテスト準備完了")
    print(f"   データ: {test_data}")
    print(f"   ※実際の書き込みは手動確認後に実行してください")
