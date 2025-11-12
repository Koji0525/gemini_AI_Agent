"""
GoogleSheetsManager v2.1 - 環境変数対応版
実スプレッドシートIDを環境変数から読み込み
"""

import os
import json
from typing import List, Optional, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleSheetsManager:
    """
    Google Sheets API マネージャー v2.1

    主な変更点:
    - 環境変数 SPREADSHEET_ID からスプレッドシートIDを読み込み
    - 環境変数 GOOGLE_SHEETS_CREDENTIALS から認証情報を読み込み
    - フォールバック機能追加（credentials.json）
    """

    def __init__(self):
        """初期化: 認証とスプレッドシートID設定"""

        # 1. スプレッドシートID取得
        self.spreadsheet_id = os.getenv("SPREADSHEET_ID")

        if not self.spreadsheet_id or self.spreadsheet_id == "test_spreadsheet_id":
            logger.error("❌ SPREADSHEET_ID が設定されていません！")
            logger.error("環境変数 SPREADSHEET_ID に実際のスプレッドシートIDを設定してください")
            raise ValueError("SPREADSHEET_ID が未設定です")

        logger.info(f"✅ スプレッドシートID: {self.spreadsheet_id[:20]}...")

        # 2. 認証情報の取得
        credentials = self._get_credentials()

        # 3. Google Sheets API サービス構築
        try:
            self.service = build("sheets", "v4", credentials=credentials)
            logger.info("✅ Google Sheets API 接続成功")
        except Exception as e:
            logger.error(f"❌ Google Sheets API 接続失敗: {e}")
            raise

    def _get_credentials(self):
        """
        認証情報の取得

        優先順位:
        1. 環境変数 GOOGLE_SHEETS_CREDENTIALS (JSON文字列)
        2. credentials.json ファイル
        """
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

        # 方法1: 環境変数から
        creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        if creds_json:
            try:
                creds_dict = json.loads(creds_json)
                credentials = service_account.Credentials.from_service_account_info(
                    creds_dict, scopes=SCOPES
                )
                logger.info("✅ 環境変数から認証情報を読み込みました")
                return credentials
            except Exception as e:
                logger.warning(f"⚠️ 環境変数からの認証情報読み込み失敗: {e}")

        # 方法2: credentials.json ファイルから
        creds_file = "credentials.json"
        if os.path.exists(creds_file):
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    creds_file, scopes=SCOPES
                )
                logger.info("✅ credentials.json から認証情報を読み込みました")
                return credentials
            except Exception as e:
                logger.error(f"❌ credentials.json 読み込み失敗: {e}")
                raise

        # どちらも失敗
        logger.error("❌ 認証情報が見つかりません")
        logger.error("以下のいずれかを設定してください:")
        logger.error("  1. 環境変数 GOOGLE_SHEETS_CREDENTIALS")
        logger.error("  2. credentials.json ファイル")
        raise FileNotFoundError("認証情報が見つかりません")

    def read_range(self, range_name: str) -> List[List[Any]]:
        """
        指定範囲のデータ読み取り

        Args:
            range_name: シート範囲 (例: 'pm_tasks!A1:E10')

        Returns:
            データ行のリスト
        """
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
        """
        データ行の追加

        Args:
            range_name: シート名 (例: 'task_execution_log')
            values: 追加するデータ

        Returns:
            成功: True, 失敗: False
        """
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
        """
        指定範囲のデータ更新

        Args:
            range_name: シート範囲 (例: 'pm_tasks!E2:E5')
            values: 更新するデータ

        Returns:
            成功: True, 失敗: False
        """
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

    def batch_update(self, data: List[dict]) -> bool:
        """
        バッチ更新

        Args:
            data: 更新データのリスト

        Returns:
            成功: True, 失敗: False
        """
        try:
            body = {"data": data, "valueInputOption": "USER_ENTERED"}

            result = (
                self.service.spreadsheets()
                .values()
                .batchUpdate(spreadsheetId=self.spreadsheet_id, body=body)
                .execute()
            )

            logger.info(f"✅ バッチ更新成功: {len(data)}件")
            return True

        except HttpError as e:
            logger.error(f"❌ バッチ更新エラー: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 予期しないエラー: {e}")
            return False


# 動作確認用
if __name__ == "__main__":
    print("🧪 GoogleSheetsManager v2.1 動作確認\n")

    try:
        sheets = GoogleSheetsManager()
        print("✅ 初期化成功")

        # pm_tasks の最初の10行を取得
        print("\n📊 pm_tasks の読み取りテスト")
        data = sheets.read_range("pm_tasks!A1:E10")

        if data:
            print(f"取得行数: {len(data)}")
            print("\nヘッダー:")
            print(data[0] if len(data) > 0 else "なし")

            print("\nデータサンプル（最初の3行）:")
            for row in data[1:4]:
                print(f"  {row}")
        else:
            print("⚠️ データが取得できませんでした")

    except Exception as e:
        print(f"❌ エラー: {e}")
