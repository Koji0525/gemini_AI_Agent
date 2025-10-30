#!/usr/bin/env python3
"""運用ルール検索（AI用）"""

import sys
import os

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from dotenv import load_dotenv

load_dotenv(".env")

from tools.sheets_manager import GoogleSheetsManager


def search_rules(keyword: str):
    """ルール検索"""

    sheets = GoogleSheetsManager(
        spreadsheet_id=os.getenv("SPREADSHEET_ID"), service_account_file="configuration/service_account.json"
    )

    spreadsheet = sheets.gc.open_by_key(os.getenv("SPREADSHEET_ID"))
    rules_sheet = spreadsheet.worksheet("dev_rules")

    all_rules = rules_sheet.get_all_values()

    results = []
    for row in all_rules[1:]:  # ヘッダー除外
        if keyword.lower() in " ".join(row).lower():
            results.append(
                {
                    "rule_id": row[0],
                    "category": row[1],
                    "summary": row[2],
                    "command": row[3],
                    "doc_link": row[4],
                    "priority": row[5],
                }
            )

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python3 tools/rule_search.py <キーワード>")
        sys.exit(1)

    keyword = sys.argv[1]
    results = search_rules(keyword)

    if results:
        print(f"\n🔍 '{keyword}' の検索結果: {len(results)}件\n")
        for r in results:
            print(f"[{r['rule_id']}] {r['summary']}")
            print(f"   カテゴリ: {r['category']}")
            print(f"   コマンド: {r['command']}")
            print(f"   📄 ドキュメント: {r['doc_link']}")
            print(f"   優先度: {r['priority']}")
            print()
    else:
        print(f"❌ '{keyword}' に一致するルールが見つかりません")
