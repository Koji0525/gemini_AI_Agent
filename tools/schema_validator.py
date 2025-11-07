"""
スキーマバリデーター

スプレッドシート書き込み前にデータがスキーマに準拠しているかチェック
"""

import logging
from typing import Any, Dict, List

from config.schemas import get_schema

logger = logging.getLogger(__name__)


class SchemaValidator:
    """スキーマバリデーションクラス"""

    @staticmethod
    def validate_row(sheet_name: str, row_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        1行のデータをスキーマに対してバリデーション

        Args:
            sheet_name: シート名（例: 'pm_tasks'）
            row_data: 検証するデータ（辞書形式）

        Returns:
            (is_valid, error_messages)
        """
        try:
            # スキーマ取得
            schema = get_schema(sheet_name)
            if not schema:
                logger.warning(f"⚠️ スキーマが見つかりません: {sheet_name}")
                return True, []  # スキーマがない場合はスキップ

            headers = schema.get("headers", [])
            required_fields = schema.get("required_fields", [])

            errors = []

            # 必須項目チェック
            for field in required_fields:
                if field not in row_data or not row_data[field]:
                    errors.append(f"必須項目が空: {field}")

            # 存在しないフィールドチェック
            for field in row_data.keys():
                if field not in headers:
                    errors.append(f"不明なフィールド: {field}")

            if errors:
                logger.warning(f"⚠️ バリデーションエラー: {errors}")
                return False, errors

            return True, []

        except Exception as e:
            logger.error(f"❌ バリデーションエラー: {e}")
            return False, [str(e)]

    @staticmethod
    def validate_rows(sheet_name: str, rows_data: List[Dict[str, Any]]) -> tuple[bool, List[str]]:
        """
        複数行のデータをバリデーション

        Returns:
            (all_valid, all_errors)
        """
        all_errors = []
        all_valid = True

        for i, row in enumerate(rows_data):
            is_valid, errors = SchemaValidator.validate_row(sheet_name, row)
            if not is_valid:
                all_valid = False
                all_errors.extend([f"行{i+1}: {e}" for e in errors])

        return all_valid, all_errors

    @staticmethod
    def fill_missing_fields(sheet_name: str, row_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        必須項目が空の場合にデフォルト値で埋める

        Returns:
            補完されたデータ
        """
        try:
            schema = get_schema(sheet_name)
            if not schema:
                return row_data

            headers = schema.get("headers", [])

            # 全てのヘッダーに対してデフォルト値を設定
            filled_data = {}
            for header in headers:
                if header in row_data and row_data[header]:
                    filled_data[header] = row_data[header]
                else:
                    # デフォルト値
                    filled_data[header] = ""

            return filled_data

        except Exception as e:
            logger.error(f"❌ データ補完エラー: {e}")
            return row_data


if __name__ == "__main__":
    # テスト
    validator = SchemaValidator()

    # テストデータ（不完全）
    test_data = {
        "task_id": "TASK_001",
        "description": "テストタスク",
        "status": "pending",
        # parent_goal_id が欠落
    }

    is_valid, errors = validator.validate_row("pm_tasks", test_data)
    print(f"✅ バリデーション結果: {is_valid}")
    print(f"📋 エラー: {errors}")

    # 補完
    filled = validator.fill_missing_fields("pm_tasks", test_data)
    print(f"✅ 補完後: {filled}")
