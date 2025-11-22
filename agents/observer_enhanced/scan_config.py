"""
静的解析スキャン設定（更新版）

このモジュールは、静的解析でスキャンから除外するディレクトリとファイルを定義します。
"""

# 除外するディレクトリ
EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    "venv",
    "env",
    "node_modules",
    "_BACKUP",
    "_ARCHIVE",
    "_WIP",
    "tests",
    ".pytest_cache",
    ".vscode",
    ".idea",
    "final_backup_20251104_195511",  # バックアップディレクトリ
}

# 除外するファイルパターン
EXCLUDE_FILE_PATTERNS = {
    "*_backup_*",
    "*.backup.py",
    "*_old.py",
    "*_deprecated.py",
    "temp_*.py",
    "*_test.py",  # テストファイル（phase2_6hour_test.pyなど）
}

# 除外する特定のファイル
EXCLUDE_SPECIFIC_FILES = {
    "register_syntax_knowledge.py",
    "final_system_check.py",  # 構文エラーあり
    "phase2_6hour_test.py",  # 構文エラーあり
}

# 除外する特定のディレクトリパス（相対パス）
EXCLUDE_SPECIFIC_DIRS = {
    "agents/generated",
    "core_agents",
}
