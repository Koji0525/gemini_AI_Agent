"""
同期設定ファイル - 簡単に設定を変更可能
"""

# 自動同期設定
AUTO_SYNC_ENABLED = True  # Trueにすると自動同期が有効
SYNC_INTERVAL_MINUTES = 60  # 同期間隔（分）
MAX_SYNC_ROWS = 100  # 最大保持行数

# 同期対象のシート設定
SYNC_SHEETS = {
    'progress_dashboard': True,
    'project_goal': True, 
    'pm_tasks': True
}

# 通知設定
NOTIFICATIONS = {
    'on_success': True,
    'on_error': True,
    'log_level': 'INFO'  # DEBUG, INFO, WARNING, ERROR
}

# データフィルタ設定
FILTERS = {
    'min_progress_rate': 0,  # 最小進捗率（%）
    'include_completed': False,  # 完了したゴールを含む
    'priority_levels': [1, 2, 3]  # 同期する優先度
}
