#!/usr/bin/env python3
"""
修正提案システムのテスト

エラーが発生した時に、knowledge_baseから
類似の修正レシピを提案する
"""

import sys
import os
from typing import List, Dict

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from dotenv import load_dotenv

load_dotenv(".env")

from tools.sheets_manager import GoogleSheetsManager


class FixSuggestionSystem:
    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
        self.spreadsheet = sheets_manager.gc.open_by_key(os.getenv("SPREADSHEET_ID"))

    def search_similar_errors(self, error_text: str) -> List[Dict]:
        """類似エラーを検索"""

        # knowledge_baseから修正レシピを取得
        kb_sheet = self.spreadsheet.worksheet("knowledge_base")
        data = kb_sheet.get_all_values()

        if len(data) <= 1:
            return []

        # fix_recipeタイプのみ
        fix_recipes = []
        for row in data[1:]:
            if len(row) >= 3 and row[2] == "fix_recipe":
                fix_recipes.append({"kb_id": row[0], "timestamp": row[1], "pattern_data": row[4]})

        # 簡易的な類似度計算（キーワードマッチ）
        error_keywords = set(error_text.lower().split())

        similar_recipes = []
        for recipe in fix_recipes:
            recipe_text = recipe["pattern_data"].lower()
            recipe_keywords = set(recipe_text.split())

            # 共通キーワード数
            common = error_keywords & recipe_keywords

            if len(common) >= 2:  # 2個以上共通
                similar_recipes.append({"recipe": recipe, "similarity": len(common)})

        # 類似度でソート
        similar_recipes.sort(key=lambda x: x["similarity"], reverse=True)

        return [r["recipe"] for r in similar_recipes[:3]]

    def suggest_fix(self, error_text: str):
        """修正提案"""

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔍 エラー分析")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()
        print(f"エラー: {error_text}")
        print()

        similar = self.search_similar_errors(error_text)

        if not similar:
            print("❌ 類似の修正レシピが見つかりません")
            print("   → 新しいエラーパターンです")
            return

        print(f"✅ {len(similar)}件の類似レシピが見つかりました")
        print()

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("💡 修正提案")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()

        for i, recipe in enumerate(similar, 1):
            print(f"【提案{i}】")

            # パターンデータをパース
            pattern_str = recipe["pattern_data"]

            # 簡易パース（辞書風文字列から抽出）
            import re

            error_match = re.search(r"'error':\s*'([^']+)'", pattern_str)
            solution_match = re.search(r"'solution':\s*'([^']+)'", pattern_str)

            if error_match and solution_match:
                past_error = error_match.group(1)[:100]
                past_solution = solution_match.group(1)[:200]

                print(f"   過去の類似エラー:")
                print(f"      {past_error}...")
                print()
                print(f"   解決方法:")
                print(f"      {past_solution}...")
                print()
                print(f"   ナレッジID: {recipe['kb_id']}")
                print(f"   記録日時: {recipe['timestamp']}")
            else:
                print(f"   データ: {pattern_str[:200]}...")

            print()


if __name__ == "__main__":
    sheets = GoogleSheetsManager(
        spreadsheet_id=os.getenv("SPREADSHEET_ID"), service_account_file="configuration/service_account.json"
    )

    system = FixSuggestionSystem(sheets)

    # テストケース
    test_errors = [
        "ModuleNotFoundError: No module named 'dotenv'",
        "APIError: [429]: Quota exceeded for quota metric 'Write requests'",
        "401 Unauthorized - authentication failed",
        "Read timeout at url",
        "ImportError: cannot import name 'PMAgent'",
    ]

    for i, error in enumerate(test_errors, 1):
        print(f"\n{'='*60}")
        print(f"テストケース {i}/{len(test_errors)}")
        print(f"{'='*60}\n")

        system.suggest_fix(error)

        if i < len(test_errors):
            input("\n[Enter]で次のテストケースへ...")
