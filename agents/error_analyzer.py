#!/usr/bin/env python3
"""
エラー分析エージェント

task_execution_log からエラーを収集・分類し、
error_analysis シートに記録する
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import re

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import ConfigLoader


class ErrorAnalyzer:
    """エラー分析エージェント"""

    # エラー分類パターン
    ERROR_PATTERNS = {
        "timeout": [r"timeout", r"timed out", r"time limit exceeded", r"asyncio\.TimeoutError"],
        "authentication": [r"authentication failed", r"login failed", r"credentials", r"unauthorized", r"401"],
        "data_format": [r"json", r"parse error", r"invalid format", r"malformed", r"decode error"],
        "dependency": [r"dependency", r"not found", r"missing", r"import error", r"module"],
        "network": [r"connection", r"network", r"socket", r"dns", r"host"],
        "permission": [r"permission", r"access denied", r"forbidden", r"403"],
    }

    def __init__(self, sheets_manager: GoogleSheetsManager = None):
        """初期化"""
        if sheets_manager is None:
            config = ConfigLoader()
            spreadsheet_id = config.get("SPREADSHEET_ID")
            service_account_file = config.get("GOOGLE_SERVICE_ACCOUNT_FILE")
            self.sheets_manager = GoogleSheetsManager(spreadsheet_id, service_account_file)
        else:
            self.sheets_manager = sheets_manager

        self.spreadsheet_id = self.sheets_manager.spreadsheet_id

    def get_execution_logs(self, status_filter: str = "failed") -> List[Dict[str, Any]]:
        """task_execution_log からログを取得"""
        spreadsheet = self.sheets_manager.gc.open_by_key(self.spreadsheet_id)

        try:
            worksheet = spreadsheet.worksheet("task_execution_log")
        except Exception as e:
            print(f"⚠️ task_execution_log シートが見つかりません: {e}")
            return []

        all_values = worksheet.get_all_values()

        if len(all_values) < 2:
            return []

        headers = all_values[0]
        valid_headers = {}
        for i, header in enumerate(headers):
            if header and header.strip():
                valid_headers[i] = header.strip()

        logs = []
        for row_values in all_values[1:]:
            row_dict = {}
            for col_idx, header_name in valid_headers.items():
                if col_idx < len(row_values):
                    row_dict[header_name] = row_values[col_idx]
                else:
                    row_dict[header_name] = ""

            if any(row_dict.values()):
                status = row_dict.get("status", "").lower()
                if status_filter == "all" or status == status_filter:
                    logs.append(row_dict)

        return logs

    def classify_error(self, error_message: str) -> str:
        """エラーメッセージを分類"""
        if not error_message:
            return "unknown"

        error_lower = error_message.lower()

        for error_type, patterns in self.ERROR_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, error_lower):
                    return error_type

        return "other"

    def analyze_logs(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ログを分析"""
        analysis = {"total_errors": len(logs), "by_type": {}, "by_task": {}, "recent_errors": [], "most_common": []}

        for log in logs:
            error_msg = log.get("error", "") or log.get("result", "")
            error_type = self.classify_error(error_msg)
            task_id = log.get("task_id", "Unknown")

            # エラータイプ別集計
            if error_type not in analysis["by_type"]:
                analysis["by_type"][error_type] = 0
            analysis["by_type"][error_type] += 1

            # タスク別集計
            if task_id not in analysis["by_task"]:
                analysis["by_task"][task_id] = 0
            analysis["by_task"][task_id] += 1

        # 最新5件
        analysis["recent_errors"] = logs[-5:] if len(logs) > 5 else logs

        # 頻度順
        sorted_types = sorted(analysis["by_type"].items(), key=lambda x: x[1], reverse=True)
        analysis["most_common"] = sorted_types[:5]

        return analysis

    def ensure_error_analysis_sheet(self):
        """error_analysis シートを作成（存在しない場合）"""
        spreadsheet = self.sheets_manager.gc.open_by_key(self.spreadsheet_id)

        try:
            worksheet = spreadsheet.worksheet("error_analysis")
            print("✅ error_analysis シート存在確認")
            return worksheet
        except Exception:
            print("📝 error_analysis シートを作成中...")

            worksheet = spreadsheet.add_worksheet(title="error_analysis", rows=1000, cols=15)

            # ヘッダー行を設定
            headers = [
                "error_id",
                "task_id",
                "error_type",
                "severity",
                "error_message",
                "root_cause",
                "occurrence_count",
                "first_seen",
                "last_seen",
                "status",
                "resolution",
                "created_at",
                "updated_at",
                "notes",
                "priority",
            ]

            worksheet.update("A1:O1", [headers])
            print("✅ error_analysis シートを作成しました")

            return worksheet

    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """分析レポートを生成"""
        report = []
        report.append("=" * 70)
        report.append("📊 エラー分析レポート")
        report.append("=" * 70)
        report.append(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append(f"総エラー数: {analysis['total_errors']}件")
        report.append("")

        if analysis["by_type"]:
            report.append("【エラータイプ別】")
            for error_type, count in analysis["most_common"]:
                percentage = (count / analysis["total_errors"]) * 100
                report.append(f"  {error_type}: {count}件 ({percentage:.1f}%)")
            report.append("")

        if analysis["recent_errors"]:
            report.append("【最新のエラー（5件）】")
            for i, log in enumerate(analysis["recent_errors"][-5:], 1):
                task_id = log.get("task_id", "Unknown")
                error = log.get("error", "") or log.get("result", "")
                timestamp = log.get("timestamp", "") or log.get("created_at", "")
                report.append(f"  {i}. タスク#{task_id} ({timestamp})")
                report.append(f"     {error[:100]}")
            report.append("")

        report.append("=" * 70)

        return "\n".join(report)

    def run_analysis(self) -> Dict[str, Any]:
        """エラー分析を実行"""
        print("🔍 エラー分析を開始...")
        print()

        # ログ取得
        print("�� task_execution_log からエラーを取得中...")
        logs = self.get_execution_logs(status_filter="failed")
        print(f"✅ {len(logs)}件のエラーログを取得")
        print()

        if not logs:
            print("⚠️ エラーログがありません")
            return {"total_errors": 0}

        # 分析実行
        print("🧮 エラーを分析中...")
        analysis = self.analyze_logs(logs)
        print("✅ 分析完了")
        print()

        # レポート生成
        report = self.generate_report(analysis)
        print(report)

        # error_analysis シート作成
        print()
        print("📝 error_analysis シートを確認/作成中...")
        self.ensure_error_analysis_sheet()

        return analysis


def main():
    """メイン実行関数"""
    analyzer = ErrorAnalyzer()
    analysis = analyzer.run_analysis()

    print()
    print("🎉 エラー分析完了！")


if __name__ == "__main__":
    main()
