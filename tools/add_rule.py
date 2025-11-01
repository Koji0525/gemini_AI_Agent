#!/usr/bin/env python3
"""対話式ルール追加ツール（doc_link自動生成版）"""

import sys
import os

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from dotenv import load_dotenv

load_dotenv(".env")

from tools.sheets_manager import GoogleSheetsManager
from datetime import datetime

# カテゴリとドキュメントセクションのマッピング
CATEGORY_SECTIONS = {
    "backup": "docs/DEVELOPMENT_RULES.md#51-バージョン管理とバックアップ",
    "naming": "docs/DEVELOPMENT_RULES.md#52-命名規則",
    "testing": "docs/DEVELOPMENT_RULES.md#92-r009-解決後の改善活動",
    "git": "docs/DEVELOPMENT_RULES.md#7-git操作ルール",
    "output_format": "docs/DEVELOPMENT_RULES.md#8-出力形式ルール",
    "debugging": "docs/DEVELOPMENT_RULES.md#9-デバッグと改善ルール",
    "improvement": "docs/DEVELOPMENT_RULES.md#9-デバッグと改善ルール",
    "documentation": "docs/DEVELOPMENT_RULES.md#6-変更理由の記載",
    "security": "docs/DEVELOPMENT_RULES.md#10-セキュリティと保守性ルール",
    "coding": "docs/DEVELOPMENT_RULES.md#10-セキュリティと保守性ルール",
    "architecture": "docs/DEVELOPMENT_RULES.md#11-アーキテクチャルール",
    "ui_selectors": "docs/DEVELOPMENT_RULES.md#11-アーキテクチャルール",
    "code_size": "docs/DEVELOPMENT_RULES.md#11-アーキテクチャルール",
}


def add_rule_interactive():
    """対話式でルールを追加"""

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🆕 新しいルールを追加")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    # 入力受付
    rule_id = input("ルールID (例: R016): ").strip()

    print("\n利用可能なカテゴリ:")
    for cat in sorted(CATEGORY_SECTIONS.keys()):
        print(f"  - {cat}")

    category = input("\nカテゴリ: ").strip()
    summary = input("概要（1行で）: ").strip()
    command = input("コマンド/手順: ").strip()
    priority = input("優先度 (critical/high/medium/low): ").strip()
    reason = input("追加理由: ").strip()

    # doc_link自動生成
    doc_link = CATEGORY_SECTIONS.get(category, "docs/DEVELOPMENT_RULES.md")

    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("確認:")
    print(f"  ID: {rule_id}")
    print(f"  カテゴリ: {category}")
    print(f"  概要: {summary}")
    print(f"  優先度: {priority}")
    print(f"  リンク: {doc_link}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    confirm = input("追加しますか？ (Y/n): ")

    if confirm.lower() == "n":
        print("❌ キャンセル")
        return

    # スプレッドシート更新
    sheets = GoogleSheetsManager(
        spreadsheet_id=os.getenv("SPREADSHEET_ID"), service_account_file="configuration/service_account.json"
    )

    spreadsheet = sheets.gc.open_by_key(os.getenv("SPREADSHEET_ID"))
    rules_sheet = spreadsheet.worksheet("dev_rules")

    # 次の行を取得
    all_data = rules_sheet.get_all_values()
    next_row = len(all_data) + 1

    # ルール追加
    today = datetime.now().strftime("%Y-%m-%d")
    new_rule = [
        [rule_id, category, summary, command, doc_link, priority, today, today, "active"]  # 自動生成されたリンク
    ]

    rules_sheet.update(f"A{next_row}:I{next_row}", new_rule)

    print(f"\n✅ {rule_id} を dev_rules に追加")

    # 履歴記録
    history_sheet = spreadsheet.worksheet("rule_history")
    history_data = history_sheet.get_all_values()
    next_history_row = len(history_data) + 1

    history = [[datetime.now().strftime("%Y-%m-%d %H:%M"), rule_id, "created", "", summary, reason, "manual"]]

    history_sheet.update(f"A{next_history_row}:G{next_history_row}", history)

    print("✅ rule_history に記録")
    print()
    print(f"📄 ドキュメント: {doc_link}")
    print(f'🔍 確認: python3 tools/rule_search.py "{category}"')


if __name__ == "__main__":
    add_rule_interactive()
