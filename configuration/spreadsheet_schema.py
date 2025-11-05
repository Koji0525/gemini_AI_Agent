"""
スプレッドシート列定義（システムの中核インターフェース）
要件定義書 v3.0 に基づく正式な仕様
"""

# pm_tasksシートの列定義
PM_TASKS_SCHEMA = {
    "sheet_name": "pm_tasks",
    "columns": [
        {"index": 0, "name": "task_id", "required": True, "type": "string"},
        {"index": 1, "name": "parent_goal_id", "required": False, "type": "string"},
        {"index": 2, "name": "description", "required": True, "type": "string"},
        {"index": 3, "name": "required_role", "required": True, "type": "string"},
        {"index": 4, "name": "status", "required": True, "type": "string"},
        {"index": 5, "name": "priority", "required": True, "type": "string"},
        {"index": 6, "name": "estimated_time", "required": False, "type": "int"},
        {"index": 7, "name": "dependencies", "required": False, "type": "string"},
        {"index": 8, "name": "created_at", "required": True, "type": "string"},
        {"index": 9, "name": "batch_id", "required": False, "type": "string"}
    ],
    "total_columns": 10
}

# task_execution_logシートの列定義
TASK_EXECUTION_LOG_SCHEMA = {
    "sheet_name": "task_execution_log",
    "columns": [
        {"index": 0, "name": "log_id", "required": True, "type": "string"},
        {"index": 1, "name": "task_id", "required": True, "type": "string"},
        {"index": 2, "name": "task_description", "required": True, "type": "string"},
        {"index": 3, "name": "timestamp", "required": True, "type": "string"},
        {"index": 4, "name": "agent_role", "required": True, "type": "string"},
        {"index": 5, "name": "output_summary", "required": False, "type": "string"},
        {"index": 6, "name": "output_data", "required": False, "type": "string"},
        {"index": 7, "name": "status", "required": True, "type": "string"},
        {"index": 8, "name": "Quality_Score", "required": False, "type": "int"},
        {"index": 9, "name": "Quality_description", "required": False, "type": "string"},
        {"index": 10, "name": "elapsed_time", "required": False, "type": "float"},
        {"index": 11, "name": "retry_count", "required": False, "type": "int"},
        {"index": 12, "name": "error_type", "required": False, "type": "string"},
        {"index": 13, "name": "fix_applied", "required": False, "type": "bool"}
    ],
    "total_columns": 14
}

# 全スキーマの辞書
SPREADSHEET_SCHEMAS = {
    "pm_tasks": PM_TASKS_SCHEMA,
    "task_execution_log": TASK_EXECUTION_LOG_SCHEMA
}

def get_schema(sheet_name):
    """指定されたシートのスキーマを取得"""
    return SPREADSHEET_SCHEMAS.get(sheet_name)

def get_column_names(sheet_name):
    """指定されたシートの列名リストを取得"""
    schema = get_schema(sheet_name)
    if schema:
        return [col["name"] for col in schema["columns"]]
    return []

def validate_row_data(sheet_name, row_data):
    """行データがスキーマに適合するか検証"""
    schema = get_schema(sheet_name)
    if not schema:
        return False, f"Unknown sheet: {sheet_name}"
    
    # 列数チェック
    if len(row_data) != schema["total_columns"]:
        return False, f"Column count mismatch: expected {schema['total_columns']}, got {len(row_data)}"
    
    # 必須フィールドチェック
    for col in schema["columns"]:
        if col["required"] and not row_data[col["index"]]:
            return False, f"Required field '{col['name']}' is empty"
    
    return True, "Valid"

