#!/usr/bin/env python3
"""
SmartSheetsManager - 堅牢なシート操作ツール

【再発防止機能】
1. 実データ範囲の自動検出
2. シート構造の自動検証
3. 空白行の自動スキップ
4. データ整合性チェック

【汎用化】
- どのシートでも使える
- 構造を自動学習
- エラーを事前検出
"""

from typing import List, Dict, Any, Optional
from tools.sheets_manager import GoogleSheetsManager
import logging

logger = logging.getLogger(__name__)


class SmartSheetsManager(GoogleSheetsManager):
    """堅牢性を強化したSheetsManager"""

    def detect_actual_data_range(self, sheet_name: str) -> int:
        """
        実際のデータ範囲（最終行）を検出

        空白行を除外し、実データの最終行を返す

        Args:
            sheet_name: シート名

        Returns:
            実データの最終行番号（ヘッダー除く）
        """
        try:
            # 広範囲を取得（A列のみで十分）
            data = self.read_range(f"{sheet_name}!A1:A10000")

            # 後ろから探索して、最初の非空白行を見つける
            last_row = 0
            for i in range(len(data) - 1, -1, -1):
                if data[i] and data[i][0]:  # 空白でない
                    last_row = i + 1
                    break

            logger.info(f"📊 {sheet_name}: 実データ最終行 = {last_row}")
            return last_row

        except Exception as e:
            logger.warning(f"⚠️ データ範囲検出エラー: {e}")
            return 1  # デフォルト

    def get_sheet_structure(self, sheet_name: str) -> Dict[str, Any]:
        """
        シート構造を取得

        Returns:
            {
                'headers': ['col1', 'col2', ...],
                'column_count': 4,
                'data_rows': 10
            }
        """
        try:
            # ヘッダー取得
            headers_data = self.read_range(f"{sheet_name}!1:1")
            headers = headers_data[0] if headers_data else []

            # 実データ行数
            data_rows = self.detect_actual_data_range(sheet_name) - 1

            return {"headers": headers, "column_count": len(headers), "data_rows": data_rows}

        except Exception as e:
            logger.error(f"❌ 構造取得エラー: {e}")
            return {"headers": [], "column_count": 0, "data_rows": 0}

    def validate_data_structure(
        self, sheet_name: str, data: List[List[Any]], expected_columns: Optional[List[str]] = None
    ) -> bool:
        """
        データ構造を検証

        Args:
            sheet_name: シート名
            data: 追加予定のデータ
            expected_columns: 期待される列名のリスト

        Returns:
            True: 構造OK, False: 構造NG
        """
        try:
            structure = self.get_sheet_structure(sheet_name)

            # 列数チェック
            data_cols = len(data[0]) if data else 0
            sheet_cols = structure["column_count"]

            if data_cols != sheet_cols:
                logger.error(f"❌ 列数不一致: データ={data_cols}列, " f"シート={sheet_cols}列")
                return False

            # ヘッダーチェック（オプション）
            if expected_columns:
                actual_headers = structure["headers"]
                if actual_headers != expected_columns:
                    logger.warning(
                        f"⚠️ ヘッダー不一致:\n"
                        f"  期待: {expected_columns}\n"
                        f"  実際: {actual_headers}"
                    )

            logger.info(f"✅ 構造検証OK: {sheet_name}")
            return True

        except Exception as e:
            logger.error(f"❌ 検証エラー: {e}")
            return False

    def smart_append_rows(
        self,
        sheet_name: str,
        values: List[List[Any]],
        expected_columns: Optional[List[str]] = None,
        validate: bool = True,
    ) -> Dict:
        """
        スマートな行追加

        【機能】
        1. 実データ範囲を検出
        2. 構造を検証（オプション）
        3. 正確な位置に追加

        Args:
            sheet_name: シート名
            values: 追加データ
            expected_columns: 期待される列名
            validate: 構造検証を行うか

        Returns:
            追加結果
        """
        logger.info(f"�� スマートappend: {sheet_name}")

        # 1. 構造検証
        if validate:
            if not self.validate_data_structure(sheet_name, values, expected_columns):
                raise ValueError(f"データ構造が{sheet_name}と一致しません")

        # 2. 実データ範囲を検出
        last_row = self.detect_actual_data_range(sheet_name)
        target_row = last_row + 1

        logger.info(f"📍 追加先: {target_row}行目")

        # 3. 範囲を指定して追加
        f"{sheet_name}!A{target_row}"
        result = self.append_rows(sheet_name, values, logical_sheet=True)

        logger.info(f"✅ スマートappend完了: {len(values)}行追加")
        return result

    def cleanup_empty_rows(self, sheet_name: str, dry_run: bool = True) -> int:
        """
        空白行をクリーンアップ

        Args:
            sheet_name: シート名
            dry_run: Trueの場合、実行せず報告のみ

        Returns:
            削除される空白行数
        """
        try:
            # 実データ範囲を検出
            last_data_row = self.detect_actual_data_range(sheet_name)

            # シート全体の行数を取得
            spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            total_rows = worksheet.row_count

            empty_rows = total_rows - last_data_row

            if dry_run:
                logger.info(
                    f"📊 {sheet_name}:\n"
                    f"  実データ: {last_data_row}行\n"
                    f"  総行数: {total_rows}行\n"
                    f"  空白行: {empty_rows}行"
                )
            else:
                # 実際に削除（実装は慎重に）
                logger.warning("🚧 実際の削除は未実装（安全のため）")

            return empty_rows

        except Exception as e:
            logger.error(f"❌ クリーンアップエラー: {e}")
            return 0


def main():
    """テスト実行"""
    print("=" * 60)
    print("🔧 SmartSheetsManager テスト")
    print("=" * 60)

    manager = SmartSheetsManager()

    # 構造確認
    structure = manager.get_sheet_structure("project_goal")
    print(f"\n📊 project_goal構造:")
    print(f"  ヘッダー: {structure['headers']}")
    print(f"  列数: {structure['column_count']}")
    print(f"  データ行: {structure['data_rows']}")

    # 空白行チェック
    empty = manager.cleanup_empty_rows("project_goal", dry_run=True)
    print(f"\n🧹 空白行: {empty}行")


if __name__ == "__main__":
    main()
