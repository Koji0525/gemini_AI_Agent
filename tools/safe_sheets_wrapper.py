"""
SafeSheetsWrapper - GoogleSheetsManager の安全なラッパー
実際のAPI仕様（read_sheet, get_sheet_data, write_sheet）に基づく

運用ルール17: スプレッドシート連携の安全化
"""

import sys
import os
import logging
from typing import List, Dict, Any, Optional

# プロジェクトルートをパスに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from tools.sheets_manager import GoogleSheetsManager

logger = logging.getLogger(__name__)


class SafeSheetsWrapper:
    """
    GoogleSheetsManager の安全なラッパークラス

    実際のメソッド名:
    - read_sheet(sheet_name) -> List[Dict]
    - get_sheet_data(sheet_name) -> List[Dict]
    - write_sheet(sheet_name, data: List[List]) -> bool
    """

    def __init__(self, sheets_manager: GoogleSheetsManager):
        """
        Args:
            sheets_manager: GoogleSheetsManager インスタンス
        """
        self.sheets = sheets_manager
        self._validate_api()
        logger.info("✅ SafeSheetsWrapper を初期化しました")

    def _validate_api(self):
        """実際のメソッドが存在するか確認"""
        required_methods = ["read_sheet", "write_sheet", "get_sheet_data"]

        for method in required_methods:
            if not hasattr(self.sheets, method):
                logger.error(f"❌ GoogleSheetsManager に '{method}' メソッドが存在しません")
                raise AttributeError(f"Required method '{method}' not found")

        logger.info("✅ API検証完了: すべての必須メソッドが存在します")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 読み取り系メソッド（実際のAPIに基づく）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def safe_read(
        self, sheet_name: str, default: Optional[List[Dict]] = None
    ) -> List[Dict[str, Any]]:
        """
        安全なシート読み取り（エラー時はデフォルト値を返す）

        Args:
            sheet_name: シート名（例: 'project_goal'）
            default: エラー時の戻り値（デフォルトは空リスト）

        Returns:
            辞書のリスト（各行がDict）
        """
        if default is None:
            default = []

        try:
            # 実際のメソッド名: read_sheet
            result = self.sheets.read_sheet(sheet_name)
            logger.info(f"✅ '{sheet_name}' から {len(result)} 件のデータを読み込みました")
            return result

        except Exception as e:
            logger.warning(f"⚠️ '{sheet_name}' の読み取りエラー: {e}")
            logger.info(f"   デフォルト値を返します")
            return default

    def read_range(self, range_spec: str, default: Optional[List[List]] = None) -> List[List[Any]]:
        """
        範囲指定読み取り（互換性メソッド）

        実際のAPIには存在しないため、sheet_nameを抽出してread_sheetを呼び出す

        Args:
            range_spec: 'sheet_name!A1:Z10' 形式または 'sheet_name'
            default: エラー時の戻り値

        Returns:
            2次元配列（ヘッダー行を含む）
        """
        if default is None:
            default = []

        try:
            # 'sheet_name!A1:Z10' から sheet_name を抽出
            sheet_name = range_spec.split("!")[0] if "!" in range_spec else range_spec

            # 辞書のリストを取得
            dict_data = self.safe_read(sheet_name, default=[])

            if not dict_data:
                return default

            # 辞書を2次元配列に変換
            headers = list(dict_data[0].keys())
            result = [headers]  # ヘッダー行

            for row_dict in dict_data:
                row = [row_dict.get(h, "") for h in headers]
                result.append(row)

            logger.info(f"✅ '{range_spec}' から {len(result)} 行を取得しました（ヘッダー含む）")
            return result

        except Exception as e:
            logger.warning(f"⚠️ '{range_spec}' の読み取りエラー: {e}")
            return default

    def get_sheet_data(self, sheet_name: str) -> List[Dict[str, Any]]:
        """
        シートデータを取得（read_sheetのエイリアス）

        Args:
            sheet_name: シート名

        Returns:
            辞書のリスト
        """
        return self.safe_read(sheet_name, default=[])

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 書き込み系メソッド
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def safe_write(self, sheet_name: str, data: List[List[Any]]) -> bool:
        """
        安全なシート書き込み

        Args:
            sheet_name: シート名
            data: 2次元配列

        Returns:
            成功時True
        """
        try:
            # 1次元配列の場合は2次元に変換
            if data and not isinstance(data[0], list):
                logger.info("   1次元配列を2次元に自動変換します")
                data = [[item] for item in data]

            # 実際のメソッド名: write_sheet
            result = self.sheets.write_sheet(sheet_name, data)

            if result:
                logger.info(f"✅ '{sheet_name}' に {len(data)} 行を書き込みました")
            else:
                logger.warning(f"⚠️ '{sheet_name}' への書き込みが失敗しました")

            return result

        except Exception as e:
            logger.error(f"❌ '{sheet_name}' への書き込みエラー: {e}")
            return False

    def safe_append(self, sheet_name: str, rows: List[List[Any]]) -> bool:
        """
        安全な行追加

        Args:
            sheet_name: シート名
            rows: 追加する行のリスト（2次元配列）

        Returns:
            成功時True
        """
        try:
            # 既存データを取得
            current_dict_data = self.safe_read(sheet_name, default=[])

            if current_dict_data:
                # ヘッダーを取得
                headers = list(current_dict_data[0].keys())

                # 既存データを2次元配列に変換
                data_2d = [headers]  # ヘッダー行
                for row_dict in current_dict_data:
                    data_2d.append([row_dict.get(h, "") for h in headers])

                # 新しい行を追加
                for row in rows:
                    # 1次元の場合はそのまま、2次元の場合は最初の要素
                    if isinstance(row, list):
                        data_2d.append(row)
                    else:
                        data_2d.append([row])
            else:
                # 空のシートの場合
                data_2d = rows

            # 書き込み
            return self.safe_write(sheet_name, data_2d)

        except Exception as e:
            logger.error(f"❌ '{sheet_name}' への行追加エラー: {e}")
            return False

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # メソッド名の自動修正（互換性）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def __getattr__(self, name: str):
        """
        存在しないメソッド名を自動修正

        よくある間違い:
        - read_data → safe_read
        - get_data → safe_read
        - append_row → safe_append
        """
        method_mapping = {
            "read_data": "safe_read",
            "get_data": "safe_read",
            "load_data": "safe_read",
            "write_data": "safe_write",
            "update_data": "safe_write",
            "append_data": "safe_append",
            "add_row": "safe_append",
            "append_row": "safe_append",
        }

        if name in method_mapping:
            correct_name = method_mapping[name]
            logger.warning(f"⚠️ メソッド名を自動修正: {name} → {correct_name}")
            return getattr(self, correct_name)

        # 類似メソッドを提案
        available = [m for m in dir(self) if not m.startswith("_") and callable(getattr(self, m))]
        similar = [m for m in available if name.lower() in m.lower()]

        if similar:
            logger.error(f"❌ メソッド '{name}' は存在しません")
            logger.info(f"💡 もしかして: {', '.join(similar[:3])}")

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# テスト実行
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

    print("\n" + "=" * 60)
    print("🧪 SafeSheetsWrapper テスト")
    print("=" * 60)

    try:
        sheets = GoogleSheetsManager()
        safe_sheets = SafeSheetsWrapper(sheets)

        # テスト1: 安全な読み取り
        print("\n📋 テスト1: 安全な読み取り（辞書形式）")
        data = safe_sheets.safe_read("project_goal", default=[])
        print(f"   取得件数: {len(data)} 件")
        if data:
            print(f"   最初のキー: {list(data[0].keys())}")

        # テスト2: 範囲指定読み取り（2次元配列形式）
        print("\n📋 テスト2: 範囲指定読み取り（2次元配列形式）")
        range_data = safe_sheets.read_range("project_goal!A1:Z10", default=[])
        print(f"   取得行数: {len(range_data)} 行")
        if range_data:
            print(f"   ヘッダー: {range_data[0]}")

        # テスト3: メソッド名の自動修正
        print("\n📋 テスト3: メソッド名の自動修正")
        try:
            data = safe_sheets.read_data("pm_tasks")  # read_data → safe_read
            print(f"   自動修正成功: {len(data)} 件")
        except Exception as e:
            print(f"   エラー: {e}")

        print("\n" + "=" * 60)
        print("✅ テスト完了")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ テスト中にエラー: {e}")
        import traceback

        traceback.print_exc()
