"""
SchemaValidator v2 - SchemaManagerベース

config/schemas.pyへの依存を排除し、SchemaManagerを使用
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

# プロジェクトルートをパスに追加（__main__での直接実行用）
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

from tools.schema_manager import SchemaManager

logger = logging.getLogger(__name__)


class SchemaValidator:
    """スキーマバリデーションクラス v2"""

    @staticmethod
    def validate_row(sheet_name: str, row_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        1行のデータをスキーマに対してバリデーション
        """
        return SchemaManager.validate_row(sheet_name, row_data)

    @staticmethod
    def validate_rows(sheet_name: str, rows_data: List[Dict[str, Any]]) -> tuple[bool, List[str]]:
        """
        複数行のデータをバリデーション
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
        """
        return SchemaManager.create_empty_row(sheet_name, row_data)


if __name__ == "__main__":
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧪 SchemaValidator v2 テスト")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # テスト
    validator = SchemaValidator()

    # 不完全なデータ
    test_data = {"task_id": "TASK_001", "description": "テストタスク", "status": "pending"}

    print("\n📊 バリデーション:")
    is_valid, errors = validator.validate_row("pm_tasks", test_data)
    print(f"  結果: {is_valid}")
    print(f"  エラー: {errors}")

    print("\n🔧 データ補完:")
    filled = validator.fill_missing_fields("pm_tasks", test_data)
    print(f"  補完後:")
    for key, value in filled.items():
        print(f"    {key}: {value}")

    print("\n✅ 補完後のバリデーション:")
    is_valid2, errors2 = validator.validate_row("pm_tasks", filled)
    print(f"  結果: {is_valid2}")
    print(f"  エラー: {errors2}")

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
