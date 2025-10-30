#!/usr/bin/env python3
"""
会話ログインポーター v3（高精度パーシング）

改善点:
- より多様なパターンに対応
- 会話の文脈を考慮
- コードブロックとエラーを抽出
- セクション単位で処理
"""

import sys
import os
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Tuple

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from dotenv import load_dotenv

load_dotenv(".env")

from tools.sheets_manager import GoogleSheetsManager


class ConversationLogImporterV3:
    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
        self.spreadsheet = sheets_manager.gc.open_by_key(os.getenv("SPREADSHEET_ID"))

    def split_into_conversations(self, content: str) -> List[Dict[str, str]]:
        """会話を発言単位に分割"""

        conversations = []

        # パターン1: マークダウン風の会話
        pattern1 = r"(?:^|\n)((?:User|Human|Assistant|AI|Claude)[:：]\s*(.+?)(?=(?:\n(?:User|Human|Assistant|AI|Claude)[:：])|$))"

        matches = list(re.finditer(pattern1, content, re.IGNORECASE | re.DOTALL))

        for match in matches:
            role = "user" if any(x in match.group(1).lower() for x in ["user", "human"]) else "assistant"
            text = match.group(2).strip()

            conversations.append({"role": role, "content": text})

        # パターン2: シンプルな改行区切り（上記がヒットしない場合）
        if not conversations:
            paragraphs = content.split("\n\n")
            for i, para in enumerate(paragraphs):
                if para.strip():
                    # 簡易的に奇数番目をuser、偶数番目をassistantと仮定
                    conversations.append({"role": "user" if i % 2 == 0 else "assistant", "content": para.strip()})

        return conversations

    def extract_errors_and_solutions(self, conversations: List[Dict]) -> List[Tuple[str, str, str]]:
        """エラーと解決策を抽出"""

        errors_and_solutions = []

        for i, conv in enumerate(conversations):
            content = conv["content"]

            # エラーパターン（より広範囲）
            error_patterns = [
                r"(?:error|exception|failed|エラー|失敗|問題)[:：]?\s*(.+?)(?:\n|$)",
                r"❌\s*(.+?)(?:\n|$)",
                r"Traceback.*?(\w+Error:.+?)(?:\n\n|\Z)",
                r"Exception:\s*(.+?)(?:\n|$)",
                r"(\d{3}\s+(?:Error|Bad Request|Not Found|Forbidden))",
            ]

            for error_pattern in error_patterns:
                error_matches = re.finditer(error_pattern, content, re.IGNORECASE | re.DOTALL)

                for error_match in error_matches:
                    error_text = error_match.group(1 if error_match.lastindex else 0).strip()

                    # 前後の文脈から解決策を探す
                    solution = None
                    context_start = max(0, i - 1)
                    context_end = min(len(conversations), i + 3)

                    for j in range(context_start, context_end):
                        ctx_content = conversations[j]["content"]

                        # 解決策パターン
                        solution_patterns = [
                            r"(?:解決|修正|対応|fix|fixed|solved)[:：]?\s*(.+?)(?:\n\n|$)",
                            r"✅\s*(.+?)(?:\n|$)",
                            r"(?:以下|次|this).*?(?:コマンド|command|方法).*?\n(.+?)(?:\n\n|$)",
                        ]

                        for sol_pattern in solution_patterns:
                            sol_match = re.search(sol_pattern, ctx_content, re.IGNORECASE | re.DOTALL)
                            if sol_match:
                                solution = sol_match.group(1).strip()
                                break

                        if solution:
                            break

                    # 周辺の文脈も保存
                    context_parts = []
                    for j in range(max(0, i - 1), min(len(conversations), i + 2)):
                        context_parts.append(conversations[j]["content"][:200])
                    context = " ... ".join(context_parts)

                    errors_and_solutions.append(
                        (error_text[:500], solution[:500] if solution else "未解決", context[:500])
                    )

        return errors_and_solutions

    def extract_tasks(self, conversations: List[Dict]) -> List[Dict[str, Any]]:
        """タスク情報を抽出"""

        tasks = []

        for conv in conversations:
            content = conv["content"]

            # タスクパターン（より多様）
            task_patterns = [
                r"(?:タスク|Task|TODO|実行|実施)[:：]?\s*(.+?)(?:\n|$)",
                r"(?:^|\n)(?:\d+\.|\-|\*)\s*(.+?)(?:\n|$)",  # リスト項目
                r"```(?:bash|python|sh)\n(.+?)```",  # コードブロック
            ]

            for task_pattern in task_patterns:
                task_matches = re.finditer(task_pattern, content, re.IGNORECASE | re.DOTALL)

                for match in task_matches:
                    task_desc = match.group(1).strip()

                    # ステータス判定
                    status = "completed"
                    quality_score = 7

                    if any(x in task_desc.lower() for x in ["error", "failed", "エラー", "失敗"]):
                        status = "failed"
                        quality_score = 3
                    elif any(x in task_desc.lower() for x in ["✅", "成功", "success", "完了"]):
                        status = "completed"
                        quality_score = 9
                    elif any(x in task_desc.lower() for x in ["進行中", "in progress", "wip"]):
                        status = "in_progress"
                        quality_score = 5

                    tasks.append({"description": task_desc[:200], "status": status, "quality_score": quality_score})

        return tasks

    def parse_conversation_log(self, file_path: str) -> Dict[str, List[Dict]]:
        """会話ログをパース（v3 - 高精度）"""

        print(f"📄 パース中: {file_path}")
        print("   v3エンジン: 会話形式認識 + 文脈考慮")
        print()

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 会話に分割
        conversations = self.split_into_conversations(content)
        print(f"   会話セグメント: {len(conversations)}個")

        # エラーと解決策を抽出
        errors_solutions = self.extract_errors_and_solutions(conversations)
        print(f"   エラー・解決ペア: {len(errors_solutions)}個")

        # タスクを抽出
        tasks = self.extract_tasks(conversations)
        print(f"   タスク: {len(tasks)}個")
        print()

        # データ構造化
        parsed_data = {"task_logs": [], "retry_logs": [], "context_logs": []}

        # retry_logに追加
        for i, (error, solution, context) in enumerate(errors_solutions):
            parsed_data["retry_logs"].append(
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "task_id": f'IMPORT_V3_{datetime.now().strftime("%Y%m%d")}_{i}',
                    "attempt": 1,
                    "error": error,
                    "strategy": solution,
                }
            )

        # task_execution_logに追加
        for i, task in enumerate(tasks):
            parsed_data["task_logs"].append(
                {
                    "log_id": 224 + i,  # 既存173 + v2の51 = 224
                    "task_id": 489 + i,
                    "task_description": task["description"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "agent_role": "imported_v3",
                    "status": task["status"],
                    "quality_score": task["quality_score"],
                    "output_summary": "",
                    "error_count": 1 if task["status"] == "failed" else 0,
                    "retry_count": 0,
                }
            )

        # context_logに追加（エラー・解決ペアから）
        for i, (error, solution, context) in enumerate(errors_solutions[:50]):  # 最大50件
            if solution != "未解決":
                parsed_data["context_logs"].append(
                    {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "log_id": f'CTX_IMPORT_V3_{datetime.now().strftime("%Y%m%d")}_{i}',
                        "task_id": f'IMPORT_V3_{datetime.now().strftime("%Y%m%d")}_{i}',
                        "error_type": "imported_error",
                        "error_message": error[:200],
                        "context": context,
                        "decision": "fix",
                        "reasoning": solution[:500],
                        "confidence": 0.8,
                        "alternative_actions": "",
                        "success": True,
                        "feedback": "",
                        "lessons_learned": f"エラー: {error[:100]} → 解決: {solution[:100]}",
                        "pattern_id": "",
                        "similar_cases": "",
                    }
                )

        return parsed_data

    def import_to_sheets_batch(self, parsed_data: Dict[str, List[Dict]]):
        """バッチインポート（v2と同じ）"""

        print("📊 スプレッドシートにインポート中（バッチ処理）...")
        print()

        BATCH_SIZE = 100
        SLEEP_TIME = 2

        # task_execution_log
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

            for i in range(0, len(rows), BATCH_SIZE):
                batch = rows[i : i + BATCH_SIZE]
                task_sheet.append_rows(batch)
                print(f"   ✅ {i+len(batch)}/{len(rows)}件追加")
                if i + BATCH_SIZE < len(rows):
                    time.sleep(SLEEP_TIME)

        # retry_log
        if parsed_data["retry_logs"]:
            print(f"【retry_log】 {len(parsed_data['retry_logs'])}件")

            retry_sheet = self.spreadsheet.worksheet("retry_log")

            rows = []
            for retry in parsed_data["retry_logs"]:
                row = [retry["timestamp"], retry["task_id"], retry["attempt"], retry["error"], retry["strategy"]]
                rows.append(row)

            total_batches = (len(rows) + BATCH_SIZE - 1) // BATCH_SIZE

            for i in range(0, len(rows), BATCH_SIZE):
                batch = rows[i : i + BATCH_SIZE]
                batch_num = (i // BATCH_SIZE) + 1

                try:
                    retry_sheet.append_rows(batch)
                    print(f"   ✅ バッチ {batch_num}/{total_batches}: {len(batch)}件追加")
                    if i + BATCH_SIZE < len(rows):
                        time.sleep(SLEEP_TIME)
                except Exception as e:
                    print(f"   ⚠️  エラー: {e}")
                    time.sleep(60)
                    retry_sheet.append_rows(batch)

        # context_log
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

    parser = argparse.ArgumentParser(description="会話ログインポーター v3")
    parser.add_argument("files", nargs="+", help=".txtファイルのパス")
    parser.add_argument("--dry-run", action="store_true", help="パース結果のみ表示")

    args = parser.parse_args()

    sheets = GoogleSheetsManager(
        spreadsheet_id=os.getenv("SPREADSHEET_ID"), service_account_file="configuration/service_account.json"
    )

    importer = ConversationLogImporterV3(sheets)

    all_parsed_data = {"task_logs": [], "retry_logs": [], "context_logs": []}

    for file_path in args.files:
        parsed = importer.parse_conversation_log(file_path)

        all_parsed_data["task_logs"].extend(parsed["task_logs"])
        all_parsed_data["retry_logs"].extend(parsed["retry_logs"])
        all_parsed_data["context_logs"].extend(parsed["context_logs"])

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 パース結果:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"   タスクログ: {len(all_parsed_data['task_logs'])}件")
    print(f"   リトライログ: {len(all_parsed_data['retry_logs'])}件")
    print(f"   判断ログ: {len(all_parsed_data['context_logs'])}件")
    print()

    if args.dry_run:
        print("⚠️  --dry-run モード")

        # サンプル表示
        if all_parsed_data["retry_logs"]:
            print()
            print("【retry_logサンプル（最初の3件）】")
            for i, retry in enumerate(all_parsed_data["retry_logs"][:3], 1):
                print(f"{i}. エラー: {retry['error'][:80]}...")
                print(f"   解決: {retry['strategy'][:80]}...")
                print()
    else:
        importer.import_to_sheets_batch(all_parsed_data)
