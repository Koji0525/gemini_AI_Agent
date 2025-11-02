"""
シート統合マッピング
重複シートを統一し、コードの参照を更新
"""

SHEET_CONSOLIDATION = {
    # 統合元 → 統合先
    "project_goal": "project_goal",  # project_goalに統合（33箇所 > 8箇所）
    "execution_history": "execution_history",  # execution_historyに統合
    "retry_log": "retry_log",  # retry_logに統合（5箇所 > 3箇所）
    "learning_patterns": "learning_patterns",  # learning_patternsに統合（13箇所 > 4箇所）
}

# 統合後の標準シート名
CANONICAL_SHEETS = {
    "project_goal": "project_goal",  # 目標管理
    "pm_tasks": "pm_tasks",  # タスク管理
    "pm_task_queue": "pm_task_queue",  # タスクキュー
    "task_execution_log": "task_execution_log",  # 実行ログ
    "execution_history": "execution_history",  # 実行履歴
    "retry_log": "retry_log",  # リトライログ
    "knowledge_base": "knowledge_base",  # ナレッジベース
    "learning_patterns": "learning_patterns",  # 学習パターン
    "context_log": "context_log",  # コンテキストログ
}


def get_canonical_name(sheet_name: str) -> str:
    """シート名を正規化"""
    return SHEET_CONSOLIDATION.get(sheet_name, sheet_name)
