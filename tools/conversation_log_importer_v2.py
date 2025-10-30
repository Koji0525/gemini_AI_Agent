#!/usr/bin/env python3
"""
会話ログインポーター v2（バッチ処理 + レート制限対応）
"""

import sys
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from dotenv import load_dotenv

load_dotenv(".env")

from tools.sheets_manager import GoogleSheetsManager


class ConversationLogImporterV2:
    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
        self.spreadsheet = sheets_manager.gc.open_by_key(os.getenv("SPREADSHEET_ID"))

    def parse_conversation_log(self, file_path: str) -> Dict[str, List[Dict]]:
        """会話ログをパース（v1と同じ）"""

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        parsed_data = {"task_logs": [], "retry_logs": [], "context_logs": []}

        # エラーパターン
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
                        "error": error_text[:500],
                        "strategy": resolution[:500] if resolution else "未解決",
                    }
                )

        # タスクパターン
        task_patterns = [
            r"(?:タスク|Task|TASK)[:：]\s*(.+?)(?:\n|$)",
            r"(?:実行|実施|Execute)[:：]\s*(.+?)(?:\n|$)",
        ]

        for task_pattern in task_patterns:
            for match in re.finditer(task_pattern, content, re.IGNORECASE):
                task_desc = match.group(1).strip()

                status = "completed"
                if "失敗" in task_desc or "error" in task_desc.lower():
                    status = "failed"
                elif "進行中" in task_desc or "progress" in task_desc.lower():
                    status = "in_progress"

                parsed_data["task_logs"].append(
                    {
                        "log_id": len(parsed_data["task_logs"]) + 174,
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

        return parsed_data

    def import_to_sheets_batch(self, parsed_data: Dict[str, List[Dict]]):
        """
        バッチ処理でスプレッドシートに追加（レート制限対応）
        """

        print("📊 スプレッドシートにインポート中（バッチ処理）...")
        print()

        BATCH_SIZE = 100  # 一度に100行ずつ
        SLEEP_TIME = 2  # バッチ間で2秒待機

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # task_execution_log
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        if parsed_data["task_logs"]:
            print(f"【task_execution_log】 {len(parsed_data['task_logs'])}件")

            task_sheet = self.spreadsheet.worksheet("task_execution_log")

            rows = []
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
                rows.append(row)

            # バッチ書き込み
            for i in range(0, len(rows), BATCH_SIZE):
                batch = rows[i : i + BATCH_SIZE]
                task_sheet.append_rows(batch)
                print(f"   ✅ {i+len(batch)}/{len(rows)}件追加")

                if i + BATCH_SIZE < len(rows):
                    time.sleep(SLEEP_TIME)

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # retry_log
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        if parsed_data["retry_logs"]:
            print(f"【retry_log】 {len(parsed_data['retry_logs'])}件")

            retry_sheet = self.spreadsheet.worksheet("retry_log")

            rows = []
            for retry in parsed_data["retry_logs"]:
                row = [retry["timestamp"], retry["task_id"], retry["attempt"], retry["error"], retry["strategy"]]
                rows.append(row)

            # バッチ書き込み
            total_batches = (len(rows) + BATCH_SIZE - 1) // BATCH_SIZE
            print(f"   バッチ数: {total_batches}")
            print()

            for i in range(0, len(rows), BATCH_SIZE):
                batch = rows[i : i + BATCH_SIZE]
                batch_num = (i // BATCH_SIZE) + 1

                try:
                    retry_sheet.append_rows(batch)
                    print(f"   ✅ バッチ {batch_num}/{total_batches}: {len(batch)}件追加")

                    if i + BATCH_SIZE < len(rows):
                        print(f"      ⏳ {SLEEP_TIME}秒待機（レート制限回避）...")
                        time.sleep(SLEEP_TIME)

                except Exception as e:
                    print(f"   ❌ バッチ {batch_num}でエラー: {e}")
                    print(f"      → 60秒待機してリトライ...")
                    time.sleep(60)

                    try:
                        retry_sheet.append_rows(batch)
                        print(f"   ✅ バッチ {batch_num}: リトライ成功")
                    except Exception as e2:
                        print(f"   ❌ リトライ失敗: {e2}")
                        print(f"   ⚠️  バッチ {batch_num}をスキップします")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # context_log
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        if parsed_data["context_logs"]:
            print(f"【context_log】 {len(parsed_data['context_logs'])}件")

            context_sheet = self.spreadsheet.worksheet("context_log")

            rows = []
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
                rows.append(row)

            # バッチ書き込み
            for i in range(0, len(rows), BATCH_SIZE):
                batch = rows[i : i + BATCH_SIZE]
                context_sheet.append_rows(batch)
                print(f"   ✅ {i+len(batch)}/{len(rows)}件追加")

                if i + BATCH_SIZE < len(rows):
                    time.sleep(SLEEP_TIME)

        print()
        print("✅ インポート完了")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="会話ログインポーター v2")
    parser.add_argument("files", nargs="+", help=".txtファイルのパス")
    parser.add_argument("--dry-run", action="store_true", help="パース結果のみ表示")
    parser.add_argument("--batch-size", type=int, default=100, help="バッチサイズ（デフォルト100）")

    args = parser.parse_args()

    sheets = GoogleSheetsManager(
        spreadsheet_id=os.getenv("SPREADSHEET_ID"), service_account_file="configuration/service_account.json"
    )

    importer = ConversationLogImporterV2(sheets)

    all_parsed_data = {"task_logs": [], "retry_logs": [], "context_logs": []}

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
        print("インポートを開始します...")
        print(f"（バッチサイズ: {args.batch_size}, レート制限回避: 有効）")
        print()

        importer.import_to_sheets_batch(all_parsed_data)
