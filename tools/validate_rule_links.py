#!/usr/bin/env python3
"""ルールリンク検証ツール"""

import sys
import os

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from dotenv import load_dotenv

load_dotenv(".env")

from tools.sheets_manager import GoogleSheetsManager
from pathlib import Path


def validate_links():
    """全ルールのdoc_linkを検証"""

    sheets = GoogleSheetsManager(
        spreadsheet_id=os.getenv("SPREADSHEET_ID"), service_account_file="configuration/service_account.json"
    )

    spreadsheet = sheets.gc.open_by_key(os.getenv("SPREADSHEET_ID"))
    rules_sheet = spreadsheet.worksheet("dev_rules")

    all_data = rules_sheet.get_all_values()

    print("🔍 ルールリンク検証")
    print()

    issues = []

    for i, row in enumerate(all_data[1:], start=2):
        rule_id = row[0]
        doc_link = row[4]

        # ローカルファイルへのリンクか確認
        if doc_link.startswith("docs/"):
            # アンカー部分を除去
            file_path = doc_link.split("#")[0]

            if not Path(file_path).exists():
                issues.append({"rule_id": rule_id, "link": doc_link, "issue": "ファイルが存在しない"})
                print(f"❌ {rule_id}: {doc_link}")
                print(f"   → ファイルが存在しません")
            else:
                print(f"✅ {rule_id}: {doc_link}")

        elif doc_link.startswith("https://"):
            # 外部リンク
            if "xxx" in doc_link or "example" in doc_link:
                issues.append({"rule_id": rule_id, "link": doc_link, "issue": "ダミーリンク"})
                print(f"⚠️  {rule_id}: ダミーリンク")
            else:
                print(f"🔗 {rule_id}: 外部リンク")
        else:
            issues.append({"rule_id": rule_id, "link": doc_link, "issue": "不明な形式"})
            print(f"❓ {rule_id}: 不明な形式")

    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if issues:
        print(f"⚠️  {len(issues)}件の問題を検出")
        return False
    else:
        print("✅ 全リンクOK")
        return True


if __name__ == "__main__":
    if not validate_links():
        sys.exit(1)
