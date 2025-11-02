"""
force_create_sheets.py

Google Sheetsに必須シートを強制作成するスクリプト

【変更の理由】
- sheet_auto_creatorがシート作成に失敗
- APIを使ってシート自体を追加する必要がある
"""

import logging
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# プロジェクトルート追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# .env読み込み
load_dotenv()

logger = logging.getLogger(__name__)


def create_sheets_via_api():
    """Google Sheets APIでシートを作成"""
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build

        # 認証情報取得
        service_account_file = os.getenv(
            "GOOGLE_SERVICE_ACCOUNT_FILE", "configuration/service_account.json"
        )
        spreadsheet_id = os.getenv("SPREADSHEET_ID")

        if not spreadsheet_id:
            logger.error("❌ SPREADSHEET_IDが設定されていません")
            return False

        if not Path(service_account_file).exists():
            logger.error(f"❌ {service_account_file} が見つかりません")
            return False

        # 認証
        creds = Credentials.from_service_account_file(
            service_account_file,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )

        service = build("sheets", "v4", credentials=creds)

        # 必須シートの定義
        required_sheets = {
            "project_goal": [
                "goal_id",
                "description",
                "priority",
                "status",
                "progress",
                "created_at",
            ],
            "control_flags": ["flag_name", "value", "description", "updated_at"],
            "error_log": [
                "timestamp",
                "error_type",
                "message",
                "resolved",
                "resolution",
            ],
            "execution_history": [
                "execution_id",
                "task_id",
                "started_at",
                "completed_at",
                "status",
                "result",
            ],
        }

        # 既存シート一覧取得
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

        existing_sheets = {sheet["properties"]["title"] for sheet in spreadsheet.get("sheets", [])}
        logger.info(f"📊 既存シート: {existing_sheets}")

        # シート作成
        requests = []
        created_sheets = []

        for sheet_name, headers in required_sheets.items():
            if sheet_name not in existing_sheets:
                logger.info(f"🔧 {sheet_name} を作成します")

                # シート追加リクエスト
                requests.append({"addSheet": {"properties": {"title": sheet_name}}})

                created_sheets.append((sheet_name, headers))
            else:
                logger.info(f"✅ {sheet_name} は既に存在します")

        # バッチでシート作成
        if requests:
            body = {"requests": requests}
            # response = (
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
            logger.info(f"✅ {len(requests)}個のシートを作成しました")

            # ヘッダー書き込み
            for sheet_name, headers in created_sheets:
                try:
                    service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=f"{sheet_name}!A1",
                        valueInputOption="RAW",
                        body={"values": [headers]},
                    ).execute()

                    logger.info(f"✅ {sheet_name} ヘッダー書き込み完了")
                except Exception as e:
                    logger.warning(f"⚠️ {sheet_name} ヘッダー書き込み失敗: {e}")
        else:
            logger.info("ℹ️ すべての必須シートが既に存在します")

        return True

    except Exception as e:
        logger.error(f"❌ シート作成エラー: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """メイン実行"""
    print("=" * 60)
    print("📊 Google Sheetsシート強制作成")
    print("=" * 60)

    success = create_sheets_via_api()

    if success:
        print("\n✅ シート作成完了")
        print("💡 システムを再起動してください")
        return 0
    else:
        print("\n❌ シート作成失敗")
        print("💡 以下を確認してください:")
        print("   1. SPREADSHEET_IDが正しいか")
        print("   2. サービスアカウントに編集権限があるか")
        print("   3. 認証ファイルが正しいか")
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    exit(main())
