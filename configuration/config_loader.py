"""
設定ファイル読み込みヘルパー
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

def get_spreadsheet_id() -> str:
    """スプレッドシートIDを取得"""
    return os.getenv("SPREADSHEET_ID", "")

def get_service_account_file() -> str:
    """サービスアカウントファイルパスを取得"""
    return os.getenv("SERVICE_ACCOUNT_FILE", "configuration/service_account.json")

