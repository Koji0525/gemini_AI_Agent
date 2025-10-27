#!/usr/bin/env python3
"""
プロジェクト全体の設定ローダー - 一元管理
v1.3 - キー名統一版
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional


class ConfigLoader:
    """プロジェクト全体の設定を一元管理"""

    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._load_config()
        return cls._instance

    @classmethod
    def _load_config(cls):
        """設定を読み込み"""
        env_path = "/workspaces/gemini_AI_Agent/.env"
        load_dotenv(env_path)

        service_account = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        spreadsheet = os.getenv("SPREADSHEET_ID")

        cls._config = {
            # Google Sheets設定（複数のキー名に対応）
            "spreadsheet_id": spreadsheet,
            "SPREADSHEET_ID": spreadsheet,
            "service_account_file": service_account,
            "SERVICE_ACCOUNT_FILE": service_account,  # ← 追加
            "GOOGLE_APPLICATION_CREDENTIALS": service_account,
            "pm_sheet_name": os.getenv("PM_SHEET_NAME", "pm_tasks"),
            "PM_SHEET_NAME": os.getenv("PM_SHEET_NAME", "pm_tasks"),
            "settings_sheet_name": os.getenv("SETTINGS_SHEET_NAME", "setting"),
            "progress_sheet_name": "progress_dashboard",
            "goals_sheet_name": "project_goal",
            # WordPress設定
            "wp_url": os.getenv("WP_URL"),
            "WP_URL": os.getenv("WP_URL"),
            "wp_user": os.getenv("WP_USER"),
            "WP_USER": os.getenv("WP_USER"),
            "wp_pass": os.getenv("WP_PASS"),
            "WP_PASS": os.getenv("WP_PASS"),
            # プロジェクト設定
            "project_root": os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "debug_mode": os.getenv("DEBUG_MODE", "False").lower() == "true",
            "max_retries": int(os.getenv("MAX_RETRIES", "3")),
            "timeout": int(os.getenv("TIMEOUT", "300")),
        }

    def __getattr__(self, name: str) -> Any:
        """属性アクセスでも設定値を取得可能に"""
        if name.startswith("_"):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        return self._config.get(name)

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """設定値を取得"""
        if cls._config is None:
            cls._load_config()
        return cls._config.get(key, default)

    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """すべての設定を取得"""
        if cls._config is None:
            cls._load_config()
        return cls._config.copy()

    @classmethod
    def get_sheets_config(cls) -> Dict[str, str]:
        """Google Sheets関連の設定を取得"""
        return {
            "spreadsheet_id": cls.get("spreadsheet_id"),
            "service_account_file": cls.get("service_account_file"),
            "pm_sheet_name": cls.get("pm_sheet_name"),
            "settings_sheet_name": cls.get("settings_sheet_name"),
        }

    @classmethod
    def get_wordpress_config(cls) -> Dict[str, str]:
        """WordPress関連の設定を取得"""
        return {"url": cls.get("wp_url"), "user": cls.get("wp_user"), "pass": cls.get("wp_pass")}

    @classmethod
    def validate_config(cls):
        """必須設定の検証"""
        required = ["spreadsheet_id", "service_account_file"]
        missing = [key for key in required if not cls.get(key)]
        if missing:
            raise ValueError(f"必須設定が見つかりません: {', '.join(missing)}")


# グローバルシングルトンインスタンス
config = ConfigLoader()


# ========================================
# 後方互換性のためのヘルパー関数
# ========================================


def get_config(key: Optional[str] = None, default: Any = None) -> Any:
    """
    設定値を取得

    Args:
        key: 設定キー。Noneの場合はConfigLoaderインスタンスを返す
        default: デフォルト値

    Returns:
        keyがNoneの場合: ConfigLoaderインスタンス
        keyが指定された場合: 対応する設定値
    """
    if key is None:
        return config
    return config.get(key, default)


def get_spreadsheet_id() -> str:
    """スプレッドシートIDを取得"""
    return config.get("spreadsheet_id")


def get_service_account_file() -> str:
    """サービスアカウントファイルパスを取得"""
    return config.get("service_account_file")


def get_env(key: str, default: Any = None) -> Any:
    """環境変数を直接取得"""
    return config.get(key, default)
