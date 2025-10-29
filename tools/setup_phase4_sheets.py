"""
Phase 4用のGoogle Sheetsシート作成
- improvement_suggestions
- ab_test_results
- auto_generated_code
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import ConfigLoader


def setup_improvement_suggestions_sheet():
    """improvement_suggestionsシートを作成"""

    config = ConfigLoader()
    sheets = GoogleSheetsManager(
        spreadsheet_id=config.get("SPREADSHEET_ID"), service_account_file=config.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    )

    spreadsheet = sheets.gc.open_by_key(sheets.spreadsheet_id)

    # 1. improvement_suggestions シート
    try:
        worksheet = spreadsheet.worksheet("improvement_suggestions")
        print("✅ improvement_suggestions シートは既に存在します")
    except:
        print("📝 improvement_suggestions シートを作成中...")
        worksheet = spreadsheet.add_worksheet(title="improvement_suggestions", rows=1000, cols=15)

        headers = [
            "suggestion_id",
            "timestamp",
            "priority",  # 高/中/低
            "category",  # performance/reliability/usability
            "title",
            "description",
            "expected_benefit",
            "implementation_difficulty",  # 易/中/難
            "roi_score",  # 投資対効果
            "status",  # pending/approved/implemented/rejected
            "generated_by",  # AI/human
            "approved_by",
            "approved_at",
            "implementation_notes",
            "result",
        ]

        worksheet.update("A1:O1", [headers])
        worksheet.format(
            "A1:O1", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}}
        )
        print("✅ improvement_suggestions シート作成完了")

    # 2. ab_test_results シート
    try:
        worksheet = spreadsheet.worksheet("ab_test_results")
        print("✅ ab_test_results シートは既に存在します")
    except:
        print("📝 ab_test_results シートを作成中...")
        worksheet = spreadsheet.add_worksheet(title="ab_test_results", rows=500, cols=12)

        headers = [
            "experiment_id",
            "suggestion_id",
            "start_date",
            "end_date",
            "variant_a_description",
            "variant_b_description",
            "variant_a_success_rate",
            "variant_b_success_rate",
            "sample_size",
            "p_value",
            "statistical_significance",
            "decision",  # adopt_b/keep_a/continue_testing
        ]

        worksheet.update("A1:L1", [headers])
        worksheet.format(
            "A1:L1", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}}
        )
        print("✅ ab_test_results シート作成完了")

    # 3. auto_generated_code シート
    try:
        worksheet = spreadsheet.worksheet("auto_generated_code")
        print("✅ auto_generated_code シートは既に存在します")
    except:
        print("📝 auto_generated_code シートを作成中...")
        worksheet = spreadsheet.add_worksheet(title="auto_generated_code", rows=500, cols=10)

        headers = [
            "code_id",
            "suggestion_id",
            "generated_at",
            "code_type",  # python/bash/config
            "file_path",
            "code_snippet",
            "test_status",  # passed/failed/pending
            "approval_status",  # pending/approved/rejected
            "deployed_at",
            "notes",
        ]

        worksheet.update("A1:J1", [headers])
        worksheet.format(
            "A1:J1", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}}
        )
        print("✅ auto_generated_code シート作成完了")

    print("\n✅ Phase 4用シートのセットアップ完了！")


if __name__ == "__main__":
    setup_improvement_suggestions_sheet()
