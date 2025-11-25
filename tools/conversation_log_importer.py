#!/usr/bin/env python3
"""
会話ログインポーター

.txtファイルの会話ログをパースして
ナレッジベース用のスプレッドシートに統合
"""

import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, List

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from dotenv import load_dotenv

load_dotenv(".env")

from tools.sheets_manager import GoogleSheetsManager


class ConversationLogImporter:
    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
        self.spreadsheet = sheets_manager.gc.open_by_key(os.getenv("SPREADSHEET_ID"))

    def parse_conversation_log(self, file_path: str) -> List[Dict[str, Any]]:
        """
        会話ログをパースして構造化データに変換

        パース対象:
        - エラーメッセージ
        - 解決方法
        - タスクの成功/失敗
        - 判断プロセス
        """

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        parsed_data = {"task_logs": [], "retry_logs": [], "context_logs": []}

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # パターン1: エラーと解決（retry_log用）
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        error_patterns = [
            r"(?:エラー|ERROR|error|失敗|Failed)[:：]?\s*(.+?)(?:\n|$)",
            r"❌\s*(.+?)(?:\n|$)",
            r"Exception:\s*(.+?)(?:\n|$)",
        ]

        resolution_patterns = [
            r"(?:解決|修正|対応|fix|Fixed)[:：]?\s*(.+?)(?:\n|$)",
            r"✅\s*(.+?)(?:\n|$)",
        ]

        for error_pattern in error_patterns:
            for match in re.finditer(error_pattern, content, re.IGNORECASE):
                error_text = match.group(1).strip()

                # 解決方法を近くから探す
                resolution = None
                context_start = max(0, match.end())
                context_end = min(len(content), match.end() + 500)
                context = content[context_start:context_end]

                for res_pattern in resolution_patterns:
                    res_match = re.search(res_pattern, context, re.IGNORECASE)
                    if res_match:
                        resolution = res_match.group(1).strip()
                        break

                parsed_data["retry_logs"].append(
                    {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "task_id": f'IMPORT_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                        "attempt": 1,
                        "error": error_text[:500],  # 最大500文字
                        "strategy": resolution[:500] if resolution else "未解決",
                    }
                )

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # パターン2: タスク実行（task_execution_log用）
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        task_patterns = [
            r"(?:タスク|Task|TASK)[:：]\s*(.+?)(?:\n|$)",
            r"(?:実行|実施|Execute)[:：]\s*(.+?)(?:\n|$)",
        ]

        for task_pattern in task_patterns:
            for match in re.finditer(task_pattern, content, re.IGNORECASE):
                task_desc = match.group(1).strip()

                # ステータス判定
                status = "completed"
                if "失敗" in task_desc or "error" in task_desc.lower():
                    status = "failed"
                elif "進行中" in task_desc or "progress" in task_desc.lower():
                    status = "in_progress"

                parsed_data["task_logs"].append(
                    {
                        "log_id": len(parsed_data["task_logs"]) + 174,  # 既存173件+1
                        "task_id": len(parsed_data["task_logs"]) + 439,
                        "task_description": task_desc[:200],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "agent_role": "imported",
                        "status": status,
                        "quality_score": 8 if status == "completed" else 5,
                        "output_summary": "",
                        "error_count": 1 if status == "failed" else 0,
                        "retry_count": 0,
                    }
                )

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # パターン3: 判断プロセス（context_log用）
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        decision_patterns = [
            r"(?:判断|決定|Decision)[:：]\s*(.+?)(?:\n|$)",
            r"(?:理由|Reason)[:：]\s*(.+?)(?:\n|$)",
        ]

        for decision_pattern in decision_patterns:
            for match in re.finditer(decision_pattern, content, re.IGNORECASE):
                decision_text = match.group(1).strip()

                parsed_data["context_logs"].append(
                    {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "log_id": f'CTX_IMPORT_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                        "task_id": f'IMPORT_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                        "error_type": "imported_decision",
                        "error_message": decision_text[:200],
                        "context": decision_text[:500],
                        "decision": "documented",
                        "reasoning": decision_text[:500],
                        "confidence": 0.7,
                        "alternative_actions": "",
                        "success": True,
                        "feedback": "",
                        "lessons_learned": decision_text[:300],
                        "pattern_id": "",
                        "similar_cases": "",
                    }
                )

        return parsed_data

    def import_to_sheets(self, parsed_data: Dict[str, List[Dict]]):
        """パースしたデータをスプレッドシートに追加"""

        print("📊 スプレッドシートにインポート中...")
        print()

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # task_execution_log
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        if parsed_data["task_logs"]:
            print(f"【task_execution_log】 {len(parsed_data['task_logs'])}件")

            task_sheet = self.spreadsheet.worksheet("task_execution_log")

            for task in parsed_data["task_logs"]:
                row = [
                    task["log_id"],
                    task["task_id"],
                    task["task_description"],
                    task["timestamp"],
                    task["agent_role"],
                    task["status"],
                    task["quality_score"],
                    task["output_summary"],
                    task["error_count"],
                    task["retry_count"],
                ]
                task_sheet.append_rows(row)

            print(f"   ✅ {len(parsed_data['task_logs'])}件追加")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # retry_log
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        if parsed_data["retry_logs"]:
            print(f"【retry_log】 {len(parsed_data['retry_logs'])}件")

            retry_sheet = self.spreadsheet.worksheet("retry_log")

            for retry in parsed_data["retry_logs"]:
                row = [
                    retry["timestamp"],
                    retry["task_id"],
                    retry["attempt"],
                    retry["error"],
                    retry["strategy"],
                ]
                retry_sheet.append_rows(row)

            print(f"   ✅ {len(parsed_data['retry_logs'])}件追加")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # context_log
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        if parsed_data["context_logs"]:
            print(f"【context_log】 {len(parsed_data['context_logs'])}件")

            context_sheet = self.spreadsheet.worksheet("context_log")

            for ctx in parsed_data["context_logs"]:
                row = [
                    ctx["timestamp"],
                    ctx["log_id"],
                    ctx["task_id"],
                    ctx["error_type"],
                    ctx["error_message"],
                    ctx["context"],
                    ctx["decision"],
                    ctx["reasoning"],
                    ctx["confidence"],
                    ctx["alternative_actions"],
                    ctx["success"],
                    ctx["feedback"],
                    ctx["lessons_learned"],
                    ctx["pattern_id"],
                ]
                context_sheet.append_rows(row)

            print(f"   ✅ {len(parsed_data['context_logs'])}件追加")

        print()
        print("✅ インポート完了")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="会話ログインポーター")
    parser.add_argument("files", nargs="+", help=".txtファイルのパス")
    parser.add_argument(
        "--dry-run", action="store_true", help="パース結果のみ表示（インポートしない）"
    )

    args = parser.parse_args()

    # GoogleSheetsManager初期化
    sheets = GoogleSheetsManager(
        spreadsheet_id=os.getenv("SPREADSHEET_ID"),
        service_account_file="configuration/service_account.json",
    )

    importer = ConversationLogImporter(sheets)

    all_parsed_data = {"task_logs": [], "retry_logs": [], "context_logs": []}

    # 各ファイルをパース
    for file_path in args.files:
        print(f"📄 パース中: {file_path}")
        parsed = importer.parse_conversation_log(file_path)

        all_parsed_data["task_logs"].extend(parsed["task_logs"])
        all_parsed_data["retry_logs"].extend(parsed["retry_logs"])
        all_parsed_data["context_logs"].extend(parsed["context_logs"])

    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 パース結果:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"   タスクログ: {len(all_parsed_data['task_logs'])}件")
    print(f"   リトライログ: {len(all_parsed_data['retry_logs'])}件")
    print(f"   判断ログ: {len(all_parsed_data['context_logs'])}件")
    print()

    if args.dry_run:
        print("⚠️  --dry-run モード: インポートをスキップ")
    else:
        print("インポートしますか？ (Y/n): ", end="")
        confirm = input().strip()

        if confirm.lower() != "n":
            importer.import_to_sheets(all_parsed_data)
        else:
            print("❌ キャンセル")
