#!/usr/bin/env python3
"""
task_execution_log → 次のタスク実行 へのフィードバックループ
Phase 3.5実装
"""

from typing import List, Dict, Any
from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import get_config


class FeedbackLoop:
    """実行ログから学習し、次の実行を改善"""

    def __init__(self):
        self.sheets = GoogleSheetsManager(
            spreadsheet_id=get_config("SPREADSHEET_ID"), service_account_file=get_config("SERVICE_ACCOUNT_FILE")
        )

    def analyze_recent_failures(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        最近の失敗タスクを分析

        Returns:
            失敗パターンのリスト
        """
        log_sheet = self.sheets.gc.open_by_key(get_config("SPREADSHEET_ID")).worksheet("task_execution_log")

        all_logs = log_sheet.get_all_records()

        # 失敗したタスクを抽出（status列が 'failed' 等）
        failures = [log for log in all_logs[-limit:] if log.get("status", "").lower() in ["failed", "error", "失敗"]]

        return failures

    def get_task_context(self, task_id: str) -> Dict[str, Any]:
        """
        タスクIDから過去の実行履歴を取得

        Returns:
            {
                'success_count': 成功回数,
                'failure_count': 失敗回数,
                'common_errors': よくあるエラー,
                'last_success_method': 最後に成功した方法
            }
        """
        pass

    def suggest_improvements(self, task: Dict[str, Any]) -> List[str]:
        """
        タスクの過去履歴から改善提案を生成

        Returns:
            改善提案のリスト
        """
        pass


if __name__ == "__main__":
    loop = FeedbackLoop()
    failures = loop.analyze_recent_failures()
    print(f"最近の失敗: {len(failures)}件")
    for f in failures[:5]:
        print(f"  - タスクID: {f.get('task_id')}, エラー: {f.get('error_message', 'N/A')[:50]}")
