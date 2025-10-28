"""config_loader.py - 環境変数設定読み込みモジュール"""
import os
from dotenv import load_dotenv
from typing import Optional

# .envファイルを読み込み
load_dotenv()

class Config:
    """設定クラス"""
    
    # WordPress設定
    WP_URL = os.getenv("WP_URL", "http://localhost/wordpress")
    WP_USER = os.getenv("WP_USER", "admin")
    WP_PASS = os.getenv("WP_PASS", "password")
    
    # Google Sheets設定
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")
    CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "credentials.json")
    
    # Gemini AI設定
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # ブラウザ設定
    HEADLESS_MODE = os.getenv("HEADLESS_MODE", "True").lower() == "true"
    BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30000"))
    
    # システム設定
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    @classmethod
    def validate(cls) -> bool:
        """
        必須設定の検証
        
        Returns:
            検証結果
        """
        required_settings = [
            ("WP_URL", cls.WP_URL),
            ("WP_USER", cls.WP_USER),
            ("WP_PASS", cls.WP_PASS),
        ]
        
        missing = []
        for name, value in required_settings:
            if not value:
                missing.append(name)
        
        if missing:
            print(f"❌ 必須設定が不足しています: {', '.join(missing)}")
            return False
        
        print("✅ 必須設定が検証されました")
        return True
    
    @classmethod
    def show_current_settings(cls):
        """現在の設定を表示"""
        print("🔧 現在の設定:")
        print(f"  WordPress URL: {cls.WP_URL}")
        print(f"  WordPress User: {cls.WP_USER}")
        print(f"  WordPress Pass: {'*' * len(cls.WP_PASS) if cls.WP_PASS else '未設定'}")
        print(f"  Spreadsheet ID: {cls.SPREADSHEET_ID or '未設定'}")
        print(f"  Gemini API Key: {'設定済み' if cls.GEMINI_API_KEY else '未設定'}")
        print(f"  ヘッドレスモード: {cls.HEADLESS_MODE}")
        print(f"  ログレベル: {cls.LOG_LEVEL}")

# グローバル設定インスタンス
config = Config()

# モジュール読み込み時に設定を検証
if __name__ == "__main__":
    config.show_current_settings()
    config.validate()
