#!/usr/bin/env python3
"""
Google Sheets Manager - 環境変数統一版
変更理由: GOOGLE_SERVICE_ACCOUNT_FILE に統一して.envと整合
"""

import os
import sys
from pathlib import Path
from typing import Optional, List
import logging

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 環境変数読み込み
try:
    from dotenv import load_dotenv

    env_paths = [project_root / ".env", Path.cwd() / ".env"]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path, override=True)
            break
except ImportError:
    print("⚠️ python-dotenvをインストール中...")
    import subprocess

    subprocess.run([sys.executable, "-m", "pip", "install", "python-dotenv", "--break-system-packages"], check=True)
    from dotenv import load_dotenv

    load_dotenv(project_root / ".env", override=True)

# Google APIライブラリ
try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
except ImportError:
    print("⚠️ Google APIライブラリをインストール中...")
    import subprocess

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "google-api-python-client",
            "google-auth-httplib2",
            "google-auth-oauthlib",
            "--break-system-packages",
        ],
        check=True,
    )
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build


class GoogleSheetsManager:
    """Google Sheetsマネージャー（環境変数統一版）"""

    def __init__(self, spreadsheet_id: Optional[str] = None):
        self.logger = logging.getLogger(__name__)

        # 環境変数から取得（統一名称）
        self.spreadsheet_id = spreadsheet_id or os.getenv("SPREADSHEET_ID")
        self.service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "configuration/service_account.json")

        self._validate_config()
        self.service = self._initialize_service()

    def _validate_config(self):
        """設定検証"""
        errors = []

        if not self.spreadsheet_id:
            errors.append("SPREADSHEET_ID が未設定")

        service_account_path = Path(self.service_account_file)
        if not service_account_path.exists():
            # プロジェクトルートからの相対パスも試す
            alt_path = project_root / self.service_account_file
            if alt_path.exists():
                self.service_account_file = str(alt_path)
            else:
                errors.append(f"認証ファイルが見つかりません: {self.service_account_file}")

        if errors:
            self.logger.error("🚨 設定エラー:")
            for error in errors:
                self.logger.error(f"   • {error}")
            self.logger.error("\n💡 .envファイルを確認してください:")
            self.logger.error(f"   SPREADSHEET_ID={os.getenv('SPREADSHEET_ID', '未設定')}")
            self.logger.error(f"   GOOGLE_SERVICE_ACCOUNT_FILE={os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', '未設定')}")
            raise ValueError(f"{len(errors)}件の設定エラー")

    def _initialize_service(self):
        """Google Sheets API初期化"""
        try:
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            credentials = Credentials.from_service_account_file(self.service_account_file, scopes=scopes)
            return build("sheets", "v4", credentials=credentials)
        except Exception as e:
            self.logger.error(f"❌ API初期化エラー: {e}")
            raise

    def read_range(self, range_name: str) -> List[List[str]]:
        """範囲読み取り"""
        try:
            result = (
                self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=range_name).execute()
            )
            return result.get("values", [])
        except Exception as e:
            self.logger.error(f"❌ 読み取りエラー: {e}")
            raise

    def write_range(self, range_name: str, values: List[List[str]]):
        """範囲書き込み"""
        try:
            body = {"values": values}
            return (
                self.service.spreadsheets()
                .values()
                .update(spreadsheetId=self.spreadsheet_id, range=range_name, valueInputOption="RAW", body=body)
                .execute()
            )
        except Exception as e:
            self.logger.error(f"❌ 書き込みエラー: {e}")
            raise

    def append_rows(self, range_name: str, values: List[List[str]]):
        """行追加"""
        try:
            body = {"values": values}
            return (
                self.service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption="RAW",
                    insertDataOption="INSERT_ROWS",
                    body=body,
                )
                .execute()
            )
        except Exception as e:
            self.logger.error(f"❌ 追加エラー: {e}")
            raise


# エイリアス
EnterpriseSheetsManager = GoogleSheetsManager

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🧪 GoogleSheetsManager テスト")
    try:
        manager = GoogleSheetsManager()
        print(f"✅ 初期化成功: {manager.spreadsheet_id[:20]}...")
    except Exception as e:
        print(f"❌ エラー: {e}")
