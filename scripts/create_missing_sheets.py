#!/usr/bin/env python3
"""不足しているシートを自動作成"""

import sys
import os

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from dotenv import load_dotenv

load_dotenv("/workspaces/gemini_AI_Agent/.env")

from tools.sheets_manager import GoogleSheetsManager


def create_missing_sheets():
    """不足シートを作成"""

    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    sheets = GoogleSheetsManager(
        spreadsheet_id=spreadsheet_id, service_account_file="configuration/service_account.json"
    )

    spreadsheet = sheets.gc.open_by_key(spreadsheet_id)

    # 必要なシート定義
    required_sheets = {
        "retry_log": ["timestamp", "task_id", "attempt", "error", "strategy"],
        "feedback_queue": ["timestamp", "task_id", "feedback_type", "content", "status"],
        "agent_registry": ["agent_id", "agent_name", "capabilities", "status", "created_at"],
    }

    for sheet_name, headers in required_sheets.items():
        try:
            # 存在確認
            spreadsheet.worksheet(sheet_name)
            print(f"✅ {sheet_name}: 既に存在")
        except:
            # 作成

            # 標準環境変数ローダー（自動追加）import sysfrom pathlib import Pathsys.path.insert(0, str(Path(__file__).parent.parent))from tools.env_loader import StandardEnvLoaderif not StandardEnvLoader.load_and_verify():    print("環境変数の読み込みに失敗しました")    sys.exit(1)
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=len(headers))
            worksheet.update("A1:" + chr(65 + len(headers) - 1) + "1", [headers])
            print(f"✅ {sheet_name}: 作成完了")

    print("\n✅ 全シート準備完了")


if __name__ == "__main__":
    create_missing_sheets()
