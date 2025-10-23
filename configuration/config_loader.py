#!/usr/bin/env python3
"""
Configuration Loader
環境変数から設定を読み込むモジュール
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


def get_config(config_key: Optional[str] = None) -> Any:
    """
    環境変数から設定を取得する関数

    Args:
        config_key: 取得する設定キー（Noneの場合は全設定を返す）

    Returns:
        指定されたキーの値、またはすべての設定辞書
    """
    # .envファイルがあれば読み込む
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    # 基本設定
    config = {
        # Google Sheets設定
        "SPREADSHEET_ID": os.getenv("SPREADSHEET_ID", ""),
        "SERVICE_ACCOUNT_FILE": os.getenv("SERVICE_ACCOUNT_FILE", "service_account.json"),
        "PM_SHEET_NAME": os.getenv("PM_SHEET_NAME", "PM"),
        "SETTINGS_SHEET_NAME": os.getenv("SETTINGS_SHEET_NAME", "setting"),
        # WordPress設定
        "WP_URL": os.getenv("WP_URL", ""),
        "WP_USER": os.getenv("WP_USER", ""),
        "WP_PASS": os.getenv("WP_PASS", ""),
        # Gemini API設定
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
        # システム設定
        "MAX_RETRIES": int(os.getenv("MAX_RETRIES", "3")),
        "TIMEOUT": int(os.getenv("TIMEOUT", "300")),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        # ディスプレイ設定
        "DISPLAY": os.getenv("DISPLAY", ":1"),
        # パス設定
        "PROJECT_ROOT": str(Path(__file__).parent.parent),
        "LOGS_DIR": os.getenv("LOGS_DIR", "logs"),
        "OUTPUT_DIR": os.getenv("OUTPUT_DIR", "agent_outputs"),
    }

    # 特定のキーが要求された場合
    if config_key:
        return config.get(config_key, None)

    # すべての設定を返す
    return config


def validate_config() -> Dict[str, bool]:
    """必須設定項目の検証"""
    config = get_config()

    validation_results = {
        "spreadsheet_id": bool(config["SPREADSHEET_ID"]),
        "service_account": Path(config["SERVICE_ACCOUNT_FILE"]).exists(),
        "gemini_api_key": bool(config["GEMINI_API_KEY"]),
    }

    return validation_results


def get_sheets_config() -> Dict[str, str]:
    """Google Sheets関連の設定を取得"""
    return {
        "spreadsheet_id": get_config("SPREADSHEET_ID"),
        "service_account_file": get_config("SERVICE_ACCOUNT_FILE"),
        "pm_sheet_name": get_config("PM_SHEET_NAME"),
        "settings_sheet_name": get_config("SETTINGS_SHEET_NAME"),
    }


def get_wp_config() -> Dict[str, str]:
    """WordPress関連の設定を取得"""
    return {
        "url": get_config("WP_URL"),
        "user": get_config("WP_USER"),
        "password": get_config("WP_PASS"),
    }


def get_system_config() -> Dict[str, Any]:
    """システム関連の設定を取得"""
    return {
        "max_retries": get_config("MAX_RETRIES"),
        "timeout": get_config("TIMEOUT"),
        "log_level": get_config("LOG_LEVEL"),
        "display": get_config("DISPLAY"),
        "project_root": get_config("PROJECT_ROOT"),
        "logs_dir": get_config("LOGS_DIR"),
        "output_dir": get_config("OUTPUT_DIR"),
    }


# 後方互換性のためのエイリアス
load_config = get_config


if __name__ == "__main__":
    """設定の検証とテスト"""
    print("=== Configuration Loader Test ===")
    print()

    config = get_config()
    print("📋 現在の設定:")
    for key, value in config.items():
        if any(sensitive in key.lower() for sensitive in ["pass", "key", "token"]):
            display_value = "*" * 8 if value else "(未設定)"
        else:
            display_value = value if value else "(未設定)"
        print(f"  {key}: {display_value}")

    print()
    print("🔍 設定検証:")
    validation = validate_config()
    for item, is_valid in validation.items():
        status = "✅" if is_valid else "❌"
        print(f"  {status} {item}")

    print()
    print("✅ テスト完了")
