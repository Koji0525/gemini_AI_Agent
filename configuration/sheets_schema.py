"""
Google Sheets 構造定義の統一管理
全エージェントがこのファイルを参照することで、構造の一元管理を実現
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. project_goal シート構造（実際の4列に統一）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT_GOAL_SCHEMA = {
    "sheet_name": "project_goal",
    "headers": ["goal_id", "goal_description", "status", "created_at"],
    "column_mapping": {
        "goal_id": 0,  # A列
        "goal_description": 1,  # B列
        "status": 2,  # C列
        "created_at": 3,  # D列
    },
    "default_values": {"status": "pending", "created_at": ""},  # タイムスタンプは動的生成
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. pm_tasks シート構造（実際の13列に統一）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PM_TASKS_SCHEMA = {
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
        "execution_type",
    ],
    "column_mapping": {
        "task_id": 0,
        "parent_goal_id": 1,
        "description": 2,
        "required_role": 3,
        "status": 4,
        "priority": 5,
        "estimated_time": 6,
        "dependencies": 7,
        "created_at": 8,
        "batch_id": 9,
        "detail_file_path": 10,
        "blank": 11,
        "execution_type": 12,
    },
    "default_values": {
        "status": "pending",
        "priority": "medium",
        "estimated_time": "",
        "dependencies": "",
        "created_at": "",
        "batch_id": "",
        "detail_file_path": "",
        "blank": "",
        "execution_type": "manual",
    },
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. task_execution_log シート構造（実際の14列に統一）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TASK_EXECUTION_LOG_SCHEMA = {
    "sheet_name": "task_execution_log",
    "headers": [
        "log_id",
        "task_id",
        "task_description",
        "timestamp",
        "agent_role",
        "output_summary",
        "output_data",
        "status",
        "Quality_Score",
        "Quality_description",
        "elapsed_time",
        "retry_count",
        "error_type",
        "fix_applied",
    ],
    "column_mapping": {
        "log_id": 0,
        "task_id": 1,
        "task_description": 2,
        "timestamp": 3,
        "agent_role": 4,
        "output_summary": 5,
        "output_data": 6,
        "status": 7,
        "Quality_Score": 8,
        "Quality_description": 9,
        "elapsed_time": 10,
        "retry_count": 11,
        "error_type": 12,
        "fix_applied": 13,
    },
    "default_values": {
        "status": "pending",
        "Quality_Score": "",
        "Quality_description": "",
        "elapsed_time": "",
        "retry_count": "0",
        "error_type": "",
        "fix_applied": "",
    },
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. ヘルパー関数
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def get_schema(sheet_name: str) -> dict:
    """シート名から構造定義を取得"""
    schemas = {
        "project_goal": PROJECT_GOAL_SCHEMA,
        "pm_tasks": PM_TASKS_SCHEMA,
        "task_execution_log": TASK_EXECUTION_LOG_SCHEMA,
    }
    return schemas.get(sheet_name, {})


def validate_row(sheet_name: str, row: list) -> bool:
    """行データが期待される列数と一致するか検証"""
    schema = get_schema(sheet_name)
    if not schema:
        return False
    expected_cols = len(schema["headers"])
    return len(row) == expected_cols


def row_to_dict(sheet_name: str, row: list) -> dict:
    """行データを辞書に変換（ヘッダーをキーとして使用）"""
    schema = get_schema(sheet_name)
    if not schema:
        return {}

    headers = schema["headers"]
    # 行の長さがヘッダーより短い場合は空文字で埋める
    padded_row = row + [""] * (len(headers) - len(row))
    return dict(zip(headers, padded_row[: len(headers)]))


def dict_to_row(sheet_name: str, data: dict) -> list:
    """辞書を行データに変換（デフォルト値で不足を補完）"""
    schema = get_schema(sheet_name)
    if not schema:
        return []

    headers = schema["headers"]
    defaults = schema["default_values"]

    row = []
    for header in headers:
        value = data.get(header, defaults.get(header, ""))
        row.append(value)

    return row


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. スキーマ情報の表示
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def print_schema_info():
    """全スキーマ情報を表示"""
    schemas = [PROJECT_GOAL_SCHEMA, PM_TASKS_SCHEMA, TASK_EXECUTION_LOG_SCHEMA]

    for schema in schemas:
        print(f"\n📋 {schema['sheet_name']}")
        print(f"   列数: {len(schema['headers'])}")
        print(f"   ヘッダー: {schema['headers']}")


if __name__ == "__main__":
    print_schema_info()
