#!/usr/bin/env python3
"""
WordPress設定ローダー
変更理由: Phase 10.2 - WordPress認証情報の確実な読み込み
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager


class WordPressConfigLoader:
    """WordPress設定の確実な読み込み"""

    def __init__(self):
        self.sheets_manager = GoogleSheetsManager()
        self.config = {}

    def load_config(self) -> Dict:
        """
        WordPress設定を読み込む
        優先順位: 環境変数 > 設定シート > デフォルト
        """
        print("🔧 WordPress設定を読み込み中...")

        # 1. 環境変数から読み込み
        wp_url = os.getenv("WP_URL")
        wp_user = os.getenv("WP_USER")
        wp_pass = os.getenv("WP_PASS")

        # 2. 設定シートから読み込み（環境変数がない場合）
        if not all([wp_url, wp_user, wp_pass]):
            sheet_config = self._load_from_sheet()

            wp_url = wp_url or sheet_config.get("wp_url")
            wp_user = wp_user or sheet_config.get("wp_user")
            wp_pass = wp_pass or sheet_config.get("wp_pass")

        self.config = {
            "wp_url": wp_url,
            "wp_user": wp_user,
            "wp_pass": wp_pass,
            "wp_api_base": f"{wp_url}/wp-json/wp/v2" if wp_url else None,
        }

        # 設定の検証
        self._validate_config()

        return self.config

    def _load_from_sheet(self) -> Dict:
        """設定シートから読み込み"""
        try:
            data = self.sheets_manager.read_range("configuration_db")

            if not data or len(data) <= 1:
                print("⚠️ configuration_db シートが空です")
                return {}

            headers = data[0]
            config = {}

            # key-value形式を想定
            for row in data[1:]:
                if len(row) >= 2:
                    key = row[0]
                    value = row[1]

                    if key in ["wp_url", "wp_user", "wp_pass"]:
                        config[key] = value

            return config

        except Exception as e:
            print(f"⚠️ 設定シート読み込みエラー: {e}")
            return {}

    def _validate_config(self):
        """設定の妥当性を検証"""
        missing = []

        for key in ["wp_url", "wp_user", "wp_pass"]:
            if not self.config.get(key):
                missing.append(key)

        if missing:
            print(f"⚠️ 不足している設定: {', '.join(missing)}")
            print("\n設定方法:")
            print("  1. .env ファイルに追加:")
            print("     WP_URL=https://your-site.com")
            print("     WP_USER=admin")
            print("     WP_PASS=your-app-password")
            print("")
            print("  2. または configuration_db シートに追加")

            return False

        print("✅ WordPress設定: 正常")
        print(f"   URL: {self.config['wp_url']}")
        print(f"   USER: {self.config['wp_user']}")

        return True


def main():
    """テスト実行"""
    loader = WordPressConfigLoader()
    config = loader.load_config()

    print("\n📊 読み込まれた設定:")
    for key, value in config.items():
        if "pass" in key.lower():
            print(f"   {key}: {'*' * len(value) if value else 'None'}")
        else:
            print(f"   {key}: {value}")


if __name__ == "__main__":
    main()
