"""
修正版GoogleSheetsManager - authenticated属性追加
"""

import os
import gspread
from google.oauth2.service_account import Credentials
import logging
from datetime import datetime


class GoogleSheetsManager:
    def __init__(self, credentials_path=None):
        self.credentials_path = credentials_path
        self.authenticated = False  # authenticated属性を追加
        self.client = None
        self.sheet = None
        self.setup_logging()

        # 自動認証試行
        self.authenticate()

    def setup_logging(self):
        """ロギング設定"""
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def authenticate(self):
        """Google Sheets API認証"""
        try:
            # 資格情報ファイルのパスを決定
            if self.credentials_path and os.path.exists(self.credentials_path):
                creds_path = self.credentials_path
            elif os.path.exists("credentials.json"):
                creds_path = "credentials.json"
            elif os.path.exists("configuration/service_account.json"):
                creds_path = "configuration/service_account.json"
            else:
                self.logger.warning("❌ No credentials file found")
                self.logger.info("📝 Expected locations:")
                self.logger.info("   1. Set GOOGLE_CREDENTIALS_PATH env var")
                self.logger.info("   2. ./credentials.json")
                self.logger.info("   3. ./configuration/service_account.json")
                self.authenticated = False
                return False

            # スコープ設定
            SCOPES = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]

            # 認証
            credentials = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
            self.client = gspread.authorize(credentials)
            self.authenticated = True
            self.logger.info("✅ Google Sheets認証成功")
            return True

        except Exception as e:
            self.logger.error(f"❌ 認証エラー: {e}")
            self.authenticated = False
            return False

    def get_sheet_data(self, sheet_name):
        """シートデータを取得"""
        if not self.authenticated:
            self.logger.warning(f"⚠️ 認証されていないため、ダミーデータを返します: {sheet_name}")
            return self._get_dummy_data(sheet_name)

        try:
            worksheet = self.sheet.worksheet(sheet_name)
            return worksheet.get_all_records()
        except Exception as e:
            self.logger.error(f"❌ シートデータ取得エラー ({sheet_name}): {e}")
            return []

    def read_sheet(self, sheet_name):
        """シートを読み込む - 互換性のためのメソッド"""
        try:
            return self.get_sheet_data(sheet_name)
        except Exception as e:
            self.logger.error(f"⚠️ シート読み込みエラー ({sheet_name}): {e}")
            return []

    def _get_dummy_data(self, sheet_name):
        """テスト用のダミーデータを返す"""
        dummy_data = {
            "task_execution_log": [
                {"timestamp": "2024-01-01", "task": "テストタスク", "status": "success"}
            ],
            "retry_log": [{"timestamp": "2024-01-01", "error": "テストエラー", "retry_count": 1}],
            "context_log": [{"timestamp": "2024-01-01", "context": "テストコンテキスト"}],
            "feedback_queue": [{"timestamp": "2024-01-01", "feedback": "テストフィードバック"}],
            "agent_registry": [{"name": "TestAgent", "status": "active"}],
        }
        return dummy_data.get(sheet_name, [])

    def open_spreadsheet(self, spreadsheet_id):
        """スプレッドシートを開く"""
        if not self.authenticated:
            self.logger.warning("⚠️ 認証されていないため、スプレッドシートを開けません")
            return False

        try:
            self.sheet = self.client.open_by_key(spreadsheet_id)
            self.logger.info("✅ スプレッドシートを開きました")
            return True
        except Exception as e:
            self.logger.error(f"❌ スプレッドシートオープンエラー: {e}")
            return False


# グローバルインスタンス
_sheets_manager = None


def get_sheets_manager(credentials_path=None):
    """シングルトンなSheetsManagerを取得"""
    global _sheets_manager
    if _sheets_manager is None:
        _sheets_manager = GoogleSheetsManager(credentials_path)
    return _sheets_manager


if __name__ == "__main__":
    # テスト
    manager = GoogleSheetsManager()
    print(f"認証状態: {manager.authenticated}")
    test_data = manager.read_sheet("task_execution_log")
    print(f"テストデータ: {len(test_data)}件")
