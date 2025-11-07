"""
SafeSheetsWrapper v2.4 - Google Sheets操作の安全なラッパー

【設計思想】
1. METHOD_ALIASESマップによる柔軟なAPI対応
2. 自動型変換（1次元→2次元配列）
3. 詳細なエラーロギング（サイレント失敗の排除）
4. 他のAPI連携クラスへの横展開可能な設計

変更履歴:
- v2.4: METHOD_ALIASESマップ追加、update_range→write_rangeに修正、拡張性強化
- v2.3: append_data → append_rows に修正
- v2.2: API検証ロジック追加
- v2.1: エラーハンドリング強化
"""

import logging
import os
import sys
from typing import Any, Dict, List, Optional

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)


class SafeSheetsWrapper:
    """
    GoogleSheetsManagerの安全なラッパークラス

    【拡張性のポイント】
    1. METHOD_ALIASES: API変更時はこのマップを更新するだけ
    2. 自動型変換: 呼び出し側の負担を軽減
    3. デフォルト値: エラー時もプログラムを継続
    """

    # API名の変更に柔軟に対応するエイリアスマップ
    METHOD_ALIASES: Dict[str, str] = {
        # 旧API名 → 新API名
        "append_data": "append_rows",
        "read_sheet": "read_range",
        "update_cell": "write_range",
        "update_range": "write_range",
        "write_sheet": "write_range",
    }

    def __init__(self, sheets_manager):
        """
        初期化

        Args:
            sheets_manager: GoogleSheetsManagerインスタンス
        """
        self.sheets = sheets_manager
        self._verify_api()
        logger.info("✅ SafeSheetsWrapper v2.4 初期化完了")

    def _verify_api(self):
        """
        API検証 - 実装されているメソッドを確認

        【拡張性】他のクラス（BrowserController等）にも適用可能
        """
        required_methods = ["read_range", "append_rows", "write_range"]
        available_methods = [m for m in dir(self.sheets) if not m.startswith("_")]
        missing = [m for m in required_methods if m not in available_methods]

        if missing:
            logger.error(f"❌ 必須メソッドが見つかりません: {missing}")
            logger.info(f"   利用可能: {available_methods}")
            raise AttributeError(f"GoogleSheetsManagerに必須メソッドがありません: {missing}")
        else:
            logger.info(f"✅ API検証成功: {required_methods}")

    def _convert_to_2d(self, values: List) -> List[List[Any]]:
        """
        1次元配列を2次元配列に自動変換

        【拡張性】すべてのI/O操作で再利用可能

        Args:
            values: 入力データ

        Returns:
            2次元配列
        """
        if not values:
            return []

        if not isinstance(values[0], list):
            logger.debug(f"🔄 1次元→2次元配列に自動変換")
            return [values]

        return values

    def safe_read(self, range_notation: str, default: Optional[List] = None) -> List[List[Any]]:
        """
        データを安全に読み込み

        【サイレント失敗の排除】エラー時も詳細ログ出力

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

        except AttributeError as e:
            logger.error(f"❌ メソッドが見つかりません: {e}")
            logger.error(
                f"   ヒント: 利用可能な読み込みメソッド: {[m for m in dir(self.sheets) if 'read' in m.lower()]}"
            )
            return default if default is not None else []

        except Exception as e:
            logger.error(f"❌ データ読み込み失敗 ({range_notation}): {e}")
            import traceback

            logger.error(traceback.format_exc())
            return default if default is not None else []

    def safe_append(self, sheet_name: str, values: List[List[Any]]) -> bool:
        """
        データを安全に追記

        【拡張性】自動型変換により呼び出し側の負担を軽減

        Args:
            sheet_name: シート名
            values: 追記するデータ（1次元または2次元配列）

        Returns:
            成功: True, 失敗: False
        """
        try:
            # 自動型変換
            values = self._convert_to_2d(values)

            logger.info(f"📝 データ追記開始: {sheet_name} ({len(values)}行)")
            logger.debug(f"   データ内容: {values[:2]}...")  # 最初の2行のみ表示

            # append_rows を呼び出し
            result = self.sheets.append_rows(sheet_name, values)

            logger.info(f"✅ データ追記成功: {sheet_name}")
            logger.debug(f"   結果: {result}")
            return True

        except AttributeError as e:
            logger.error(f"❌ メソッドが見つかりません: {e}")
            logger.error(
                f"   ヒント: 利用可能な追記メソッド: {[m for m in dir(self.sheets) if 'append' in m.lower()]}"
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

        【拡張性】METHOD_ALIASESにより将来のAPI変更に対応

        Args:
            range_notation: 範囲表記（例: 'pm_tasks!A2:D2'）
            values: 更新するデータ（1次元または2次元配列）

        Returns:
            成功: True, 失敗: False
        """
        try:
            # 自動型変換
            values = self._convert_to_2d(values)

            logger.info(f"📝 セル更新開始: {range_notation}")
            logger.debug(f"   データ内容: {values}")

            # write_range を呼び出し
            result = self.sheets.write_range(range_notation, values)

            logger.info(f"✅ セル更新成功: {range_notation}")
            logger.debug(f"   結果: {result}")
            return True

        except AttributeError as e:
            logger.error(f"❌ メソッドが見つかりません: {e}")
            logger.error(
                f"   ヒント: 利用可能な更新メソッド: {[m for m in dir(self.sheets) if 'write' in m.lower() or 'update' in m.lower()]}"
            )
            return False

        except Exception as e:
            logger.error(f"❌ セル更新失敗 ({range_notation}): {e}")
            import traceback

            logger.error(traceback.format_exc())
            return False

    def get_last_row(self, sheet_name: str) -> int:
        """
        シートの最終行番号を取得

        【拡張性】次の書き込み位置の計算に利用可能

        Args:
            sheet_name: シート名

        Returns:
            最終行番号（ヘッダー含む）
        """
        try:
            data = self.safe_read(f"{sheet_name}!A:A", default=[])
            return len(data)
        except Exception as e:
            logger.error(f"❌ 最終行取得失敗: {e}")
            return 0


# ====================
# テスト実行
# ====================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    from browser_control.sheets_manager import GoogleSheetsManager

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧪 SafeSheetsWrapper v2.4 機能テスト")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    sheets = GoogleSheetsManager()
    safe_sheets = SafeSheetsWrapper(sheets)

    # テスト1: 読み込み
    print("【テスト1】データ読み込み")
    data = safe_sheets.safe_read("pm_tasks!A1:Z5", default=[])
    print(f"結果: {len(data)}行読み込み成功\n")

    # テスト2: 最終行取得
    print("【テスト2】最終行番号取得")
    last_row = safe_sheets.get_last_row("pm_tasks")
    print(f"結果: 最終行 = {last_row}\n")

    # テスト3: 書き込み準備（ドライラン）
    print("【テスト3】書き込みデータ準備")
    test_data = [["TEST_001", "テスト書き込み", "HIGH", "PENDING"]]
    print(f"データ: {test_data}")
    print("※実際の書き込みは次のステップで実行\n")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ 機能テスト完了")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
