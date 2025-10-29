"""
learned_patterns シートのセットアップ
学習済みパターンを永続化するためのシート作成
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import ConfigLoader


def setup_learned_patterns_sheet():
    """learned_patternsシートを作成"""

    config = ConfigLoader()
    sheets = GoogleSheetsManager(
        spreadsheet_id=config.get("SPREADSHEET_ID"), service_account_file=config.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    )

    # スプレッドシートを開く
    spreadsheet = sheets.gc.open_by_key(sheets.spreadsheet_id)

    # シートが既に存在するか確認
    try:
        worksheet = spreadsheet.worksheet("learned_patterns")
        print("✅ learned_patterns シートは既に存在します")
        return
    except:
        print("📝 learned_patterns シートを新規作成します")

    # 新しいシートを作成
    worksheet = spreadsheet.add_worksheet(title="learned_patterns", rows=1000, cols=20)

    # ヘッダー行を設定
    headers = [
        "pattern_id",
        "pattern_type",  # success / failure
        "agent_role",
        "task_description",
        "conditions",
        "outcome",
        "confidence_score",
        "usage_count",
        "success_rate",
        "learned_at",
        "last_used_at",
        "recommendation",
        "tags",
        "similar_patterns",
        "notes",
    ]

    worksheet.update("A1:O1", [headers])

    # ヘッダー行を太字にする
    worksheet.format(
        "A1:O1", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}}
    )

    print("✅ learned_patterns シートを作成しました")
    print(f"   ヘッダー: {', '.join(headers)}")


if __name__ == "__main__":
    setup_learned_patterns_sheet()
