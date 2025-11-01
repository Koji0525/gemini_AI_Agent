import os
import sys
from typing import Dict, Any


class EnhancedConfigLoader:
    """強化版設定ローダー - 24時間監視対応"""

    def __init__(self):
        self.config = {}
        self.load_config()

    def load_config(self):
        """設定を環境変数から読み込む"""
        try:
            self.config = {
                # WordPress設定
                "wp_url": os.getenv("WP_URL", "https://uzbek-ma.com"),
                "wp_username": os.getenv("WP_USERNAME", "uzbek"),
                "wp_password": os.getenv("WP_PASSWORD", "RkLU07FkrNpeiENdFx3swseJ"),
                "wp_api_url": os.getenv("WP_API_URL", "https://uzbek-ma.com/wp-json/wp/v2"),
                # 監視設定
                "monitor_interval": int(os.getenv("MONITOR_INTERVAL", "3600")),  # 1時間
                "error_check_interval": int(os.getenv("ERROR_CHECK_INTERVAL", "300")),  # 5分
                "max_retries": int(os.getenv("MAX_RETRIES", "3")),
                # 開発設定
                "auto_develop": os.getenv("AUTO_DEVELOP", "true").lower() == "true",
                "self_healing": os.getenv("SELF_HEALING", "true").lower() == "true",
                "continuous_improvement": os.getenv("CONTINUOUS_IMPROVEMENT", "true").lower() == "true",
                # 通知設定
                "notify_errors": os.getenv("NOTIFY_ERRORS", "true").lower() == "true",
                "notify_success": os.getenv("NOTIFY_SUCCESS", "false").lower() == "true",
                "log_level": os.getenv("LOG_LEVEL", "INFO"),
                # パス設定
                "project_root": "/workspaces/gemini_AI_Agent",
                "log_dir": "/workspaces/gemini_AI_Agent/uz-manda-portal/logs",
                "reports_dir": "/workspaces/gemini_AI_Agent/uz-manda-portal/reports",
            }

            print("✅ 設定を読み込みました")

        except Exception as e:
            print(f"❌ 設定読み込みエラー: {e}")
            self.set_defaults()

    def set_defaults(self):
        """デフォルト値を設定"""
        self.config = {
            "wp_url": "https://uzbek-ma.com",
            "wp_username": "uzbek",
            "wp_password": "RkLU07FkrNpeiENdFx3swseJ",
            "wp_api_url": "https://uzbek-ma.com/wp-json/wp/v2",
            "monitor_interval": 3600,
            "error_check_interval": 300,
            "max_retries": 3,
            "auto_develop": True,
            "self_healing": True,
            "continuous_improvement": True,
            "notify_errors": True,
            "notify_success": False,
            "log_level": "INFO",
            "project_root": "/workspaces/gemini_AI_Agent",
            "log_dir": "/workspaces/gemini_AI_Agent/uz-manda-portal/logs",
            "reports_dir": "/workspaces/gemini_AI_Agent/uz-manda-portal/reports",
        }

    def get(self, key: str, default: Any = None):
        """設定値を取得"""
        return self.config.get(key, default)

    def get_all(self):
        """全設定を取得"""
        return self.config.copy()


# グローバルインスタンス
config = EnhancedConfigLoader()

if __name__ == "__main__":
    print("📋 現在の設定:")
    for key, value in config.get_all().items():
        if "password" in key:
            print(f"  {key}: {'*' * 10}")
        else:
            print(f"  {key}: {value}")
