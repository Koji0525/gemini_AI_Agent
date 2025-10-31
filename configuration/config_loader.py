"""
設定ファイル読み込みモジュール - 修正版
"""

import os
import json
from typing import Any, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class ConfigLoader:
    """設定読み込みクラス"""

    def __init__(self):
        self.config = {}
        self.load_config()

    def load_config(self):
        """設定を読み込む"""
        try:
            # 環境変数から設定を読み込み
            self.config = {
                "wp_url": os.getenv("WP_URL"),
                "wp_user": os.getenv("WP_USER"),
                "wp_pass": os.getenv("WP_PASS"),
                "spreadsheet_id": os.getenv("SPREADSHEET_ID"),
                "google_credentials": os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json"),
            }
        except Exception as e:
            print(f"❌ 設定読み込みエラー: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """設定値を取得"""
        return self.config.get(key, default)

    def get_all(self) -> Dict:
        """全設定を取得"""
        return self.config.copy()


# シングルトンインスタンス
config_loader = ConfigLoader()


def get_config(key: str = None, default: Any = None) -> Any:
    """設定を取得する関数"""
    if key is None:
        return config_loader.get_all()
    return config_loader.get(key, default)
