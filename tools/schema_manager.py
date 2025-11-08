"""
SchemaManager - スキーマ管理の統一インターフェース

【目的】
- config/schemas.pyへの安全なアクセス
- 依存関係エラーの回避
- スキーマへのアクセスを統一化

【使い方】
from tools.schema_manager import SchemaManager
schema = SchemaManager.get_schema('pm_tasks')
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# スキーマ定義（config/schemas.pyから独立）
SCHEMAS = {
    "pm_tasks": {
        "sheet_name": "pm_tasks",
        "headers": [
            "task_id",
            "parent_goal_id",
            "description",
            "required_role",
            "status",
            "priority",
            "estimated_time",
            "dependencies",
            "created_at",
            "batch_id",
            "detail_file_path",
            "blank",
        ],
        "required_fields": [
            "task_id",
            "parent_goal_id",
            "description",
            "required_role",
            "status",
            "priority",
        ],
        "default_values": {
            "status": "pending",
            "priority": "medium",
            "estimated_time": "1h",
            "dependencies": "",
            "batch_id": "",
            "detail_file_path": "",
            "blank": "",
        },
    },
    "project_goal": {
        "sheet_name": "project_goal",
        "headers": [
            "goal_id",
            "goal_description",
            "status",
            "created_at",
            "completed_at",
            "progress",
        ],
        "required_fields": ["goal_id", "goal_description", "status"],
        "default_values": {"status": "active", "completed_at": "", "progress": "0"},
    },
    "task_execution_log": {
        "sheet_name": "task_execution_log",
        "headers": [
            "execution_id",
            "task_id",
            "status",
            "output",
            "error_message",
            "executed_at",
            "execution_time",
        ],
        "required_fields": ["execution_id", "task_id", "status", "executed_at"],
        "default_values": {"output": "", "error_message": "", "execution_time": ""},
    },
}


class SchemaManager:
    """スキーマ管理クラス"""

    @staticmethod
    def get_schema(sheet_name: str) -> Optional[Dict[str, Any]]:
        """
        スキーマを取得

        Args:
            sheet_name: シート名（例: 'pm_tasks'）

        Returns:
            スキーマ定義（辞書）
        """
        schema = SCHEMAS.get(sheet_name)
        if not schema:
            logger.warning(f"⚠️ スキーマが見つかりません: {sheet_name}")
            return None
        return schema

    @staticmethod
    def get_headers(sheet_name: str) -> List[str]:
        """ヘッダー一覧を取得"""
        schema = SchemaManager.get_schema(sheet_name)
        if not schema:
            return []
        return schema.get("headers", [])

    @staticmethod
    def get_required_fields(sheet_name: str) -> List[str]:
        """必須項目一覧を取得"""
        schema = SchemaManager.get_schema(sheet_name)
        if not schema:
            return []
        return schema.get("required_fields", [])

    @staticmethod
    def get_default_values(sheet_name: str) -> Dict[str, str]:
        """デフォルト値を取得"""
        schema = SchemaManager.get_schema(sheet_name)
        if not schema:
            return {}
        return schema.get("default_values", {})

    @staticmethod
    def create_empty_row(sheet_name: str, partial_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        スキーマに基づいて完全な行データを作成

        Args:
            sheet_name: シート名
            partial_data: 部分的なデータ（辞書）

        Returns:
            完全な行データ（全ての項目が埋まっている）
        """
        schema = SchemaManager.get_schema(sheet_name)
        if not schema:
            return partial_data or {}

        headers = schema.get("headers", [])
        default_values = schema.get("default_values", {})

        # 完全な行データを作成
        row_data = {}
        for header in headers:
            if partial_data and header in partial_data:
                row_data[header] = partial_data[header]
            elif header in default_values:
                row_data[header] = default_values[header]
            else:
                row_data[header] = ""

        return row_data

    @staticmethod
    def validate_row(sheet_name: str, row_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        行データをバリデーション

        Returns:
            (is_valid, error_messages)
        """
        schema = SchemaManager.get_schema(sheet_name)
        if not schema:
            return True, []

        required_fields = schema.get("required_fields", [])
        errors = []

        # 必須項目チェック
        for field in required_fields:
            if field not in row_data or not row_data[field]:
                errors.append(f"必須項目が空: {field}")

        if errors:
            return False, errors

        return True, []


if __name__ == "__main__":
    # テスト
    manager = SchemaManager()

    # スキーマ取得
    print("📊 pm_tasksスキーマ:")
    schema = manager.get_schema("pm_tasks")
    print(f"  headers: {schema['headers']}")
    print(f"  required_fields: {schema['required_fields']}")

    # 不完全なデータを完全にする
    print("\n🔧 不完全なデータを補完:")
    partial = {"task_id": "TASK_001", "description": "テストタスク"}
    print(f"  入力: {partial}")

    complete = manager.create_empty_row("pm_tasks", partial)
    print(f"  出力: {complete}")

    # バリデーション
    print("\n🛡️ バリデーション:")
    is_valid, errors = manager.validate_row("pm_tasks", partial)
    print(f"  結果: {is_valid}")
    print(f"  エラー: {errors}")
