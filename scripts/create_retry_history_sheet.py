"""
retry_historyシート作成スクリプト（修正版）

GoogleSheetsManagerの実際の構造に対応
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.sheets_manager import GoogleSheetsManager
from dotenv import load_dotenv
import gspread

# .envファイル読み込み
load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")


def create_retry_history_sheet():
    """retry_historyシートを作成"""

    try:
        print(f"\nGoogleSheetsManager初期化中... (ID: {SPREADSHEET_ID[:20]}...)")
        sheets = GoogleSheetsManager(spreadsheet_id=SPREADSHEET_ID)

        # クライアント初期化
        sheets.setup_client()

        # gspreadクライアント取得
        if hasattr(sheets, "gc"):
            client = sheets.gc
        elif hasattr(sheets, "client"):
            client = sheets.client
        else:
            raise AttributeError("gspreadクライアントが見つかりません")

        sheet_name = "retry_log"

        print(f"\n'{sheet_name}' シート作成/更新中...")

        # スプレッドシートを開く
        spreadsheet = client.open_by_key(SPREADSHEET_ID)

        # シートが存在するか確認
        try:
            sheet = spreadsheet.worksheet(sheet_name)
            print(f"✅ '{sheet_name}' シートは既に存在します")

            # ヘッダー確認
            headers = sheet.row_values(1)
            if headers:
                print(f"   現在のヘッダー: {headers[:3]}...")
                return True

        except gspread.exceptions.WorksheetNotFound:
            print(f"📝 '{sheet_name}' シートを新規作成します")

            # シート作成
            sheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)

            # ヘッダー設定
            headers = [
                "retry_id",
                "timestamp",
                "task_name",
                "attempt_number",
                "error_type",
                "error_message",
                "strategy_used",
                "wait_time_sec",
                "status",
                "duration_sec",
            ]

            sheet.append_row(headers)

            # ヘッダー行をフォーマット
            sheet.format(
                "A1:J1",
                {
                    "textFormat": {"bold": True},
                    "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9},
                },
            )

            print(f"✅ '{sheet_name}' シート作成完了")
            print(f"   ヘッダー: {len(headers)}列")

        return True

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback

        # 標準環境変数ローダー（自動追加）import sysfrom pathlib import Pathsys.path.insert(0, str(Path(__file__).parent.parent))from tools.env_loader import StandardEnvLoaderif not StandardEnvLoader.load_and_verify():    print("環境変数の読み込みに失敗しました")    sys.exit(1)

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("retry_historyシート作成")
    print("=" * 60)

    success = create_retry_history_sheet()

    print("\n" + "=" * 60)
    if success:
        print("✅ 処理完了")
    else:
        print("❌ 処理失敗")
    print("=" * 60)
