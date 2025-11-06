#!/usr/bin/env python3
"""運用ルール管理シート作成"""

import sys
import os

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from dotenv import load_dotenv

load_dotenv(".env")

from tools.sheets_manager import GoogleSheetsManager


def setup_rules_management():
    """ルール管理シート初期化"""

    sheets = GoogleSheetsManager(
        spreadsheet_id=os.getenv("SPREADSHEET_ID"),
        service_account_file="configuration/service_account.json",
    )

    spreadsheet = sheets.gc.open_by_key(os.getenv("SPREADSHEET_ID"))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # シート1: 運用ルール（AI用・簡潔版）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    try:
        rules_sheet = spreadsheet.worksheet("dev_rules")
    except:
        rules_sheet = spreadsheet.add_worksheet("dev_rules", 100, 10)

    headers = [
        "rule_id",
        "category",
        "rule_summary",
        "command",
        "doc_link",
        "priority",
        "created_at",
        "updated_at",
        "status",
    ]

    sample_rules = [
        [
            "R001",
            "backup",
            "ファイル修正前バックアップ",
            "python3 tools/file_version_manager.py --backup <file> --reason <reason>",
            "https://docs.google.com/document/d/xxx/edit#bookmark=backup",
            "critical",
            "2025-10-30",
            "2025-10-30",
            "active",
        ],
        [
            "R002",
            "naming",
            "バージョン命名規則",
            "file_v01_feature.py形式（アンダースコア、2桁）",
            "https://docs.google.com/document/d/xxx/edit#bookmark=naming",
            "high",
            "2025-10-30",
            "2025-10-30",
            "active",
        ],
        [
            "R003",
            "testing",
            "外部API操作は必ずモックテスト",
            "python3 tools/generate_unit_test.py <file> <function>",
            "https://docs.google.com/document/d/xxx/edit#bookmark=testing",
            "high",
            "2025-10-30",
            "2025-10-30",
            "active",
        ],
    ]

    rules_sheet.update("A1:I1", [headers])
    rules_sheet.update("A2:I4", sample_rules)

    print("✅ dev_rules シート作成")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # シート2: 効率化ツール一覧
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    try:
        tools_sheet = spreadsheet.worksheet("dev_tools")
    except:
        tools_sheet = spreadsheet.add_worksheet("dev_tools", 100, 10)

    tool_headers = [
        "tool_id",
        "tool_name",
        "purpose",
        "command",
        "use_case",
        "time_saved",
        "created_at",
        "status",
    ]

    tools = [
        [
            "T001",
            "file_version_manager",
            "バージョン管理＆バックアップ",
            "python3 tools/file_version_manager.py",
            "修正前のバックアップ",
            "5分/回",
            "2025-10-30",
            "active",
        ],
        [
            "T002",
            "generate_unit_test",
            "単体テスト自動生成",
            "python3 tools/generate_unit_test.py",
            "テストコード作成",
            "10分/回",
            "2025-10-30",
            "active",
        ],
        [
            "T003",
            "health_check",
            "プロジェクト健全性チェック",
            "./scripts/health_check.sh",
            "コミット前確認",
            "15分/回",
            "2025-10-30",
            "active",
        ],
    ]

    tools_sheet.update("A1:H1", [tool_headers])
    tools_sheet.update("A2:H4", tools)

    print("✅ dev_tools シート作成")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # シート3: ルール改定履歴
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # 標準環境変数ローダー（自動追加）import sysfrom pathlib import Pathsys.path.insert(0, str(Path(__file__).parent.parent))from tools.env_loader import StandardEnvLoaderif not StandardEnvLoader.load_and_verify():    print("環境変数の読み込みに失敗しました")    sys.exit(1)
    try:
        history_sheet = spreadsheet.worksheet("rule_history")
    except:
        history_sheet = spreadsheet.add_worksheet("rule_history", 200, 8)

    history_headers = [
        "timestamp",
        "rule_id",
        "change_type",
        "old_value",
        "new_value",
        "reason",
        "changed_by",
    ]

    history_sheet.update("A1:G1", [history_headers])

    print("✅ rule_history シート作成")
    print("\n🎉 ルール管理システム構築完了")


if __name__ == "__main__":
    setup_rules_management()
