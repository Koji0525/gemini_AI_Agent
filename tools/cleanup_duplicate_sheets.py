import logging
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

"""
cleanup_duplicate_sheets.py

重複シートの削除（安全確認付き）

【変更の理由】
- 強制作成した4シート(pm_goals, control_flags, error_log, execution_history)を削除
- 既存シート(project_goal, setting, error_analysis, history)を使用
- データの整合性を保つ
"""


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()


logger = logging.getLogger(__name__)


def delete_duplicate_sheets():
    """重複シートを削除"""
    try:
        # 認証
        service_account_file = os.getenv(
            "GOOGLE_SERVICE_ACCOUNT_FILE", "configuration/service_account.json"
        )
        spreadsheet_id = os.getenv("SPREADSHEET_ID")

        creds = Credentials.from_service_account_file(
            service_account_file,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )

        service = build("sheets", "v4", credentials=creds)

        # 既存シート取得
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

        sheets = spreadsheet.get("sheets", [])

        # 削除対象シート
        duplicate_sheets = [
            "pm_goals",
            "control_flags",
            "error_log",
            "execution_history",
        ]

        # シートIDを取得
        sheets_to_delete = []
        for sheet in sheets:
            title = sheet["properties"]["title"]
            if title in duplicate_sheets:
                sheet_id = sheet["properties"]["sheetId"]
                sheets_to_delete.append((title, sheet_id))
                logger.info(f"🔍 削除対象: {title} (ID: {sheet_id})")

        if not sheets_to_delete:
            logger.info("ℹ️ 削除すべきシートはありません")
            return True

        # 確認プロンプト
        print("\n" + "=" * 60)
        print("⚠️  以下のシートを削除しようとしています:")
        for title, sheet_id in sheets_to_delete:
            print(f"   - {title}")
        print("\n既存のシートを使用します:")
        print("   - project_goal (pm_goalsの代わり)")
        print("   - setting (control_flagsの代わり)")
        print("   - error_analysis (error_logの代わり)")
        print("   - history (execution_historyの代わり)")
        print("=" * 60)

        confirm = input("\n削除を実行しますか？ [yes/no]: ").strip().lower()

        if confirm != "yes":
            print("❌ キャンセルしました")
            return False

        # 削除実行
        requests = []
        for title, sheet_id in sheets_to_delete:
            requests.append({"deleteSheet": {"sheetId": sheet_id}})

        body = {"requests": requests}
        # response = (
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        logger.info(f"✅ {len(sheets_to_delete)}個のシートを削除しました")

        return True

    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """メイン実行"""
    print("=" * 60)
    print("🧹 重複シート削除ツール")
    print("=" * 60)

    success = delete_duplicate_sheets()

    if success:
        print("\n✅ 完了")
        return 0
    else:
        print("\n❌ 失敗")
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    exit(main())
