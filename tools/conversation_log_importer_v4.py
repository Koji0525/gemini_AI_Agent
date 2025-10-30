#!/usr/bin/env python3
"""
会話ログインポーター v4（品質フィルター強化版）

改善点:
- コード断片を除外
- 最小文字数チェック
- 意味のある内容のみ抽出
- 品質スコアによるフィルタリング
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


class QualityFilter:
    """品質フィルター"""

    @staticmethod
    def is_code_fragment(text: str) -> bool:
        """コード断片かどうか判定"""
        code_indicators = [
            r"def\s+\w+\s*\(",  # 関数定義
            r"class\s+\w+",  # クラス定義
            r"import\s+\w+",  # import文
            r"from\s+\w+\s+import",  # from import
            r"[\{\}\[\]\(\)].*[\{\}\[\]\(\)]",  # 括弧が多い
            r"^\s*[#/\*]",  # コメント開始
            r'\.py["\']?$',  # .pyで終わる
            r"^[-=]{3,}$",  # ハイフンや等号だけ
            r"^\s*$",  # 空行
        ]

        for pattern in code_indicators:
            if re.search(pattern, text):
                return True

        return False

    @staticmethod
    def is_meaningful(text: str, min_length: int = 10) -> bool:
        """意味のあるテキストかどうか"""
        # 最小文字数チェック
        if len(text.strip()) < min_length:
            return False

        # 記号だけでないかチェック
        alphanumeric = re.sub(r"[^\w\s]", "", text)
        if len(alphanumeric) < min_length // 2:
            return False

        # コード断片でないかチェック
        if QualityFilter.is_code_fragment(text):
            return False

        return True

    @staticmethod
    def extract_meaningful_part(text: str, max_length: int = 200) -> str:
        """意味のある部分を抽出"""
        # 改行で分割
        lines = text.split("\n")

        meaningful_lines = []
        for line in lines:
            line = line.strip()
            if QualityFilter.is_meaningful(line, min_length=5):
                meaningful_lines.append(line)

        result = " ".join(meaningful_lines[:3])  # 最初の3行まで
        return result[:max_length]


class ConversationLogImporterV4:
    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
        self.spreadsheet = sheets_manager.gc.open_by_key(os.getenv("SPREADSHEET_ID"))
        self.quality_filter = QualityFilter()

    def parse_conversation_log(self, file_path: str) -> Dict[str, List[Dict]]:
        """
        会話ログをパース（v4 - 品質フィルター強化）
        """

        print(f"📄 パース中: {file_path}")
        print("   v4エンジン: 品質フィルター + 意味抽出")
        print()

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        parsed_data = {"task_logs": [], "retry_logs": [], "context_logs": []}

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # エラーと解決策を抽出（品質フィルター付き）
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        error_pattern = r"❌\s*(.+?)(?=\n\n|\n✅|\Z)"
        solution_pattern = r"✅\s*(.+?)(?=\n\n|\n❌|\Z)"

        error_matches = list(re.finditer(error_pattern, content, re.DOTALL))
        solution_matches = list(re.finditer(solution_pattern, content, re.DOTALL))

        print(f"   エラー候補: {len(error_matches)}個")
        print(f"   解決候補: {len(solution_matches)}個")

        for error_match in error_matches:
            error_text = error_match.group(1).strip()

            # 品質チェック
            if not self.quality_filter.is_meaningful(error_text, min_length=15):
                continue

            error_clean = self.quality_filter.extract_meaningful_part(error_text, max_length=500)

            # 近くの解決策を探す
            solution = None
            for sol_match in solution_matches:
                # エラーの後500文字以内に解決策があるか
                if 0 < sol_match.start() - error_match.end() < 500:
                    solution_text = sol_match.group(1).strip()
                    if self.quality_filter.is_meaningful(solution_text, min_length=10):
                        solution = self.quality_filter.extract_meaningful_part(solution_text, max_length=500)
                        break

            parsed_data["retry_logs"].append(
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "task_id": f'IMPORT_V4_{datetime.now().strftime("%Y%m%d")}_{len(parsed_data["retry_logs"])}',
                    "attempt": 1,
                    "error": error_clean,
                    "strategy": solution if solution else "未解決",
                }
            )

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # タスクを抽出（厳格な品質チェック）
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        # パターン1: "タスク:" で始まる行
        task_pattern1 = r"(?:タスク|Task)[:：]\s*(.+?)(?:\n\n|\Z)"

        # パターン2: リスト項目（番号付き、箇条書き）
        task_pattern2 = r"(?:^|\n)(?:\d+\.|\-|\*)\s+(.+?)(?:\n|$)"

        task_matches = []
        task_matches.extend(re.finditer(task_pattern1, content, re.IGNORECASE | re.DOTALL))
        task_matches.extend(re.finditer(task_pattern2, content, re.MULTILINE))

        print(f"   タスク候補: {len(task_matches)}個")

        for match in task_matches:
            task_desc = match.group(1).strip()

            # 厳格な品質チェック
            if not self.quality_filter.is_meaningful(task_desc, min_length=20):
                continue

            task_clean = self.quality_filter.extract_meaningful_part(task_desc, max_length=200)

            # ステータス判定
            status = "completed"
            quality_score = 7

            if any(x in task_clean.lower() for x in ["error", "failed", "エラー", "失敗"]):
                status = "failed"
                quality_score = 4
            elif any(x in task_clean.lower() for x in ["✅", "成功", "success", "完了", "done"]):
                status = "completed"
                quality_score = 9

            parsed_data["task_logs"].append(
                {
                    "log_id": 224 + len(parsed_data["task_logs"]),
                    "task_id": 489 + len(parsed_data["task_logs"]),
                    "task_description": task_clean,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "agent_role": "imported_v4",
                    "status": status,
                    "quality_score": quality_score,
                    "output_summary": "",
                    "error_count": 1 if status == "failed" else 0,
                    "retry_count": 0,
                }
            )

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 判断プロセスを抽出
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        # エラー→解決のペアから判断ログを生成
        for i, retry in enumerate(parsed_data["retry_logs"][:50]):
            if retry["strategy"] != "未解決":
                parsed_data["context_logs"].append(
                    {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "log_id": f'CTX_IMPORT_V4_{datetime.now().strftime("%Y%m%d")}_{i}',
                        "task_id": retry["task_id"],
                        "error_type": "imported_error",
                        "error_message": retry["error"][:200],
                        "context": f"エラー発生 → 解決方法適用",
                        "decision": "fix",
                        "reasoning": retry["strategy"][:500],
                        "confidence": 0.8,
                        "alternative_actions": "",
                        "success": True,
                        "feedback": "",
                        "lessons_learned": f"{retry['error'][:100]} → {retry['strategy'][:100]}",
                        "pattern_id": "",
                        "similar_cases": "",
                    }
                )

        print()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📊 品質フィルター後:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"   タスクログ: {len(parsed_data['task_logs'])}件（品質保証済み）")
        print(f"   リトライログ: {len(parsed_data['retry_logs'])}件（品質保証済み）")
        print(f"   判断ログ: {len(parsed_data['context_logs'])}件（品質保証済み）")

        return parsed_data

    def import_to_sheets_batch(self, parsed_data: Dict[str, List[Dict]]):
        """バッチインポート（v2と同じ）"""

        print()
        print("📊 スプレッドシートにインポート中...")
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
                    print(f"   ✅ バッチ {batch_num}/{total_batches}")
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

    parser = argparse.ArgumentParser(description="会話ログインポーター v4")
    parser.add_argument("files", nargs="+", help=".txtファイルのパス")
    parser.add_argument("--dry-run", action="store_true", help="パース結果のみ表示")

    args = parser.parse_args()

    sheets = GoogleSheetsManager(
        spreadsheet_id=os.getenv("SPREADSHEET_ID"), service_account_file="configuration/service_account.json"
    )

    importer = ConversationLogImporterV4(sheets)

    all_parsed_data = {"task_logs": [], "retry_logs": [], "context_logs": []}

    for file_path in args.files:
        parsed = importer.parse_conversation_log(file_path)

        all_parsed_data["task_logs"].extend(parsed["task_logs"])
        all_parsed_data["retry_logs"].extend(parsed["retry_logs"])
        all_parsed_data["context_logs"].extend(parsed["context_logs"])

    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 最終結果:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"   タスクログ: {len(all_parsed_data['task_logs'])}件")
    print(f"   リトライログ: {len(all_parsed_data['retry_logs'])}件")
    print(f"   判断ログ: {len(all_parsed_data['context_logs'])}件")
    print()

    if args.dry_run:
        print("⚠️  --dry-run モード")

        if all_parsed_data["task_logs"]:
            print()
            print("【タスクログサンプル（最初の3件）】")
            for i, task in enumerate(all_parsed_data["task_logs"][:3], 1):
                print(f"{i}. {task['task_description']}")
                print(f"   ステータス: {task['status']}, 品質: {task['quality_score']}")
                print()

        if all_parsed_data["retry_logs"]:
            print("【retry_logサンプル（最初の3件）】")
            for i, retry in enumerate(all_parsed_data["retry_logs"][:3], 1):
                print(f"{i}. エラー: {retry['error'][:80]}...")
                print(f"   解決: {retry['strategy'][:80]}...")
                print()
    else:
        importer.import_to_sheets_batch(all_parsed_data)
