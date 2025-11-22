"""
静的解析スキャン設定

このモジュールは、静的解析でスキャンから除外するディレクトリとファイルを定義します。
"""

# 除外するディレクトリ
EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    "venv",
    "env",
    "node_modules",
    "_BACKUP",  # バックアップディレクトリ
    "_ARCHIVE",  # アーカイブディレクトリ
    "_WIP",  # 作業中ディレクトリ
    "tests",  # テストディレクトリ（オプション）
    ".pytest_cache",
    ".vscode",
    ".idea",
}

# 除外するファイルパターン
EXCLUDE_FILE_PATTERNS = {
    "*_backup_*",  # バックアップファイル
    "*.backup.py",  # .backup.py拡張子
    "*_old.py",  # 古いファイル
    "*_deprecated.py",  # 非推奨ファイル
    "temp_*.py",  # 一時ファイル
}

# 除外する特定のファイル
EXCLUDE_SPECIFIC_FILES = {
    "register_syntax_knowledge.py",  # 構文エラーあり
}

# 除外する特定のディレクトリパス（相対パス）
EXCLUDE_SPECIFIC_DIRS = {
    "agents/generated",  # 自動生成ファイル
    "core_agents",  # バックアップを含む古いディレクトリ
}
