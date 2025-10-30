#!/usr/bin/env python3
"""
会話ログ専用学習パイプライン

conversation_* シートからパターンを抽出し、
knowledge_baseに統合する
"""

import sys
import os
from typing import List, Dict, Any
from collections import Counter

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from dotenv import load_dotenv

load_dotenv(".env")

from tools.sheets_manager import GoogleSheetsManager


class ConversationLearningPipeline:
    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
        self.spreadsheet = sheets_manager.gc.open_by_key(os.getenv("SPREADSHEET_ID"))

    def extract_failure_patterns(self) -> List[Dict]:
        """conversation_errorsから失敗パターンを抽出"""

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📊 失敗パターン抽出")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()

        errors_sheet = self.spreadsheet.worksheet("conversation_errors")
        data = errors_sheet.get_all_values()

        if len(data) <= 1:
            print("⚠️  データなし")
            return []

        headers = data[0]
        rows = data[1:]

        # エラーをカテゴリ別に集計
        error_categories = []
        for row in rows:
            if len(row) >= 4:
                error_desc = row[3]

                # カテゴリ判定
                category = "unknown"
                keywords = {
                    "timeout": ["timeout", "タイムアウト", "時間切れ"],
                    "auth": ["401", "unauthorized", "認証", "権限"],
                    "api_limit": ["429", "quota", "rate limit", "制限"],
                    "import": ["import", "module", "インポート"],
                    "syntax": ["syntax", "invalid", "構文"],
                }

                for cat, kws in keywords.items():
                    if any(kw in error_desc.lower() for kw in kws):
                        category = cat
                        break

                error_categories.append({"error": error_desc, "category": category})

        # カテゴリ別に集計
        category_counts = Counter([e["category"] for e in error_categories])

        print("エラーカテゴリ別の件数:")
        for cat, count in category_counts.most_common():
            print(f"   {cat}: {count}件")

        print()

        # 頻出パターンを抽出（2回以上発生）
        patterns = []
        for cat, count in category_counts.items():
            if count >= 2:
                # 代表的なエラー例を取得
                examples = [e["error"] for e in error_categories if e["category"] == cat][:3]

                patterns.append(
                    {
                        "knowledge_type": "failure_pattern",
                        "category": cat,
                        "frequency": count,
                        "description": f"{cat}エラーが{count}回発生",
                        "examples": examples,
                        "source": "conversation_errors",
                    }
                )

        print(f"✅ {len(patterns)}個の失敗パターンを抽出")
        return patterns

    def extract_fix_recipes(self) -> List[Dict]:
        """conversation_errorsから修正レシピを抽出"""

        print()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔧 修正レシピ抽出")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()

        errors_sheet = self.spreadsheet.worksheet("conversation_errors")
        data = errors_sheet.get_all_values()

        if len(data) <= 1:
            print("⚠️  データなし")
            return []

        rows = data[1:]

        recipes = []
        for row in rows:
            if len(row) >= 6:
                error_desc = row[3]
                solution = row[4]
                success = row[5]

                # 成功した解決方法のみ
                if success == "TRUE" and solution != "未解決":
                    recipes.append(
                        {
                            "knowledge_type": "fix_recipe",
                            "error": error_desc[:200],
                            "solution": solution[:500],
                            "success_rate": "100%",
                            "source": "conversation_errors",
                        }
                    )

        print(f"✅ {len(recipes)}個の修正レシピを抽出")
        return recipes

    def extract_success_patterns(self) -> List[Dict]:
        """conversation_tasksから成功パターンを抽出"""

        print()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("✨ 成功パターン抽出")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()

        tasks_sheet = self.spreadsheet.worksheet("conversation_tasks")
        data = tasks_sheet.get_all_values()

        if len(data) <= 1:
            print("⚠️  データなし")
            return []

        rows = data[1:]

        patterns = []
        for row in rows:
            if len(row) >= 6:
                task_desc = row[3]
                status = row[4]
                quality_score = int(row[5]) if row[5].isdigit() else 0

                # 高品質タスク（品質8以上）
                if status == "completed" and quality_score >= 8:
                    patterns.append(
                        {
                            "knowledge_type": "success_pattern",
                            "task": task_desc[:200],
                            "quality_score": quality_score,
                            "status": status,
                            "source": "conversation_tasks",
                        }
                    )

        print(f"✅ {len(patterns)}個の成功パターンを抽出")
        return patterns

    def save_to_knowledge_base(self, patterns: List[Dict]):
        """knowledge_baseに保存"""

        print()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("💾 knowledge_baseに保存")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()

        kb_sheet = self.spreadsheet.worksheet("knowledge_base")

        from datetime import datetime

        for pattern in patterns:
            kb_id = f"KB_CONV_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            row = [
                kb_id,
                timestamp,
                pattern["knowledge_type"],
                pattern.get("source", "conversation"),
                str(pattern),  # 全データをJSON風文字列で
                "",  # context
                "",  # conditions
                0.8,  # confidence
                1,  # usage_count
                0,  # success_count
                "",  # last_used
                "",  # tags
                "",  # notes
            ]

            kb_sheet.append_row(row)
            print(f"   ✅ {pattern['knowledge_type']}: {kb_id}")

        print()
        print(f"✅ {len(patterns)}件保存完了")

    def run(self):
        """学習サイクル実行"""

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🎓 会話ログ学習パイプライン")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()

        all_patterns = []

        # 失敗パターン抽出
        failure_patterns = self.extract_failure_patterns()
        all_patterns.extend(failure_patterns)

        # 修正レシピ抽出
        fix_recipes = self.extract_fix_recipes()
        all_patterns.extend(fix_recipes)

        # 成功パターン抽出
        success_patterns = self.extract_success_patterns()
        all_patterns.extend(success_patterns)

        # knowledge_baseに保存
        if all_patterns:
            self.save_to_knowledge_base(all_patterns)

        print()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("✅ 学習完了")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()
        print(f"📊 抽出パターン:")
        print(f"   失敗パターン: {len(failure_patterns)}件")
        print(f"   修正レシピ: {len(fix_recipes)}件")
        print(f"   成功パターン: {len(success_patterns)}件")
        print(f"   合計: {len(all_patterns)}件")


if __name__ == "__main__":
    sheets = GoogleSheetsManager(
        spreadsheet_id=os.getenv("SPREADSHEET_ID"), service_account_file="configuration/service_account.json"
    )

    pipeline = ConversationLearningPipeline(sheets)
    pipeline.run()
