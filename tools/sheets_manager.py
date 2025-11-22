"""
GoogleSheetsManager v3.1 - configuration/service_account.json 対応版
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, List

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleSheetsManager:
    """Google Sheets API マネージャー v3.1"""

    def __init__(self, spreadsheet_id: str = None):
        """初期化"""

        # スプレッドシートID取得
        self.spreadsheet_id = spreadsheet_id or os.getenv("SPREADSHEET_ID")

        if not self.spreadsheet_id:
            logger.error("❌ SPREADSHEET_ID が設定されていません")
            raise ValueError("SPREADSHEET_ID が未設定です")

        logger.info(f"✅ スプレッドシートID: {self.spreadsheet_id[:30]}...")

        # 認証情報の取得
        credentials = self._get_credentials()

        if credentials:
            try:
                self.service = build("sheets", "v4", credentials=credentials)
                logger.info("✅ Google Sheets API 接続成功")
            except Exception as e:
                logger.error(f"❌ Google Sheets API 接続失敗: {e}")
                raise
        else:
            logger.error("❌ 認証情報が取得できませんでした")
            raise ValueError("認証情報が取得できません")

    def _get_credentials(self):
        """認証情報の取得"""
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

        # 優先順位1: configuration/service_account.json
        config_path = Path("configuration/service_account.json")
        if config_path.exists():
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    str(config_path), scopes=SCOPES
                )
                logger.info("✅ configuration/service_account.json から認証")
                return credentials
            except Exception as e:
                logger.warning(f"⚠️ configuration/service_account.json 読み込み失敗: {e}")

        # 優先順位2: credentials.json
        creds_file = Path("credentials.json")
        if creds_file.exists():
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    str(creds_file), scopes=SCOPES
                )
                logger.info("✅ credentials.json から認証")
                return credentials
            except Exception as e:
                logger.warning(f"⚠️ credentials.json 読み込み失敗: {e}")

        # 優先順位3: 環境変数
        creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        if creds_json:
            try:
                creds_dict = json.loads(creds_json)
                credentials = service_account.Credentials.from_service_account_info(
                    creds_dict, scopes=SCOPES
                )
                logger.info("✅ 環境変数から認証")
                return credentials
            except Exception as e:
                logger.warning(f"⚠️ 環境変数からの認証失敗: {e}")

        logger.error("❌ 認証情報が見つかりません")
        return None

    def read_range(self, range_name: str) -> List[List[Any]]:
        """指定範囲のデータ読み取り"""
        try:
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=range_name)
                .execute()
            )

            values = result.get("values", [])
            logger.info(f"✅ 読み取り成功: {range_name} ({len(values)}行)")
            return values

        except HttpError as e:
            logger.error(f"❌ スプレッドシート読み取りエラー: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ 予期しないエラー: {e}")
            raise

    def append_rows(self, range_name: str, values: List[List[Any]]) -> bool:
        """データ行の追加"""
        try:
            body = {"values": values}

            result = (
                self.service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                    body=body,
                )
                .execute()
            )

            logger.info(f"✅ 追加成功: {range_name} ({len(values)}行)")
            return True

        except HttpError as e:
            logger.error(f"❌ スプレッドシート書き込みエラー: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 予期しないエラー: {e}")
            return False

    def update_range(self, range_name: str, values: List[List[Any]]) -> bool:
        """指定範囲のデータ更新"""
        try:
            body = {"values": values}

            result = (
                self.service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption="USER_ENTERED",
                    body=body,
                )
                .execute()
            )

            logger.info(f"✅ 更新成功: {range_name}")
            return True

        except HttpError as e:
            logger.error(f"❌ スプレッドシート更新エラー: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 予期しないエラー: {e}")
            return False


if __name__ == "__main__":
    print("🧪 GoogleSheetsManager v3.1 動作確認\n")

    try:
        sheets = GoogleSheetsManager()
        print("✅ 初期化成功\n")

        print("📊 pm_tasks!A1:K10 の読み取りテスト")
        data = sheets.read_range("pm_tasks!A1:K10")

        if data:
            print(f"✅ 取得行数: {len(data)}\n")

            print("ヘッダー:")
            if len(data) > 0:
                for i, header in enumerate(data[0]):
                    print(f"  列{chr(65+i)}({i}): {header}")

            print("\nステータス列の確認:")
            status_idx = 4  # E列
            pending_count = 0
            for row_idx, row in enumerate(data[1:], start=2):
                if len(row) > status_idx:
                    status = str(row[status_idx]).strip()
                    if status.lower() == "pending":
                        pending_count += 1
                        if pending_count <= 3:
                            desc = row[2] if len(row) > 2 else ""
                            print(f"  行{row_idx}: {desc[:50]}... (status: {status})")

            print(f"\n📋 pending タスク数: {pending_count}件")
        else:
            print("⚠️ データが取得できませんでした")

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
