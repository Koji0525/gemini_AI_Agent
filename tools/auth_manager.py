#!/usr/bin/env python3
"""
統一認証マネージャー - システム全体の認証を一元管理

環境変数、設定ファイル、デフォルト値の優先順位を統一
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AuthConfig:
    """認証設定"""

    service_account_file: str
    spreadsheet_id: str
    scopes: list
    fallback_strategies: list


class UnifiedAuthManager:
    """統一認証マネージャー"""

    def __init__(self):
        self.config = self._load_auth_config()
        self.authenticated_services = {}

    def _load_auth_config(self) -> AuthConfig:
        """認証設定を読み込み"""

        # サービスアカウントファイルのパスを解決
        service_account_file = self._resolve_service_account_path()

        # スプレッドシートIDを解決
        spreadsheet_id = self._resolve_spreadsheet_id()

        return AuthConfig(
            service_account_file=service_account_file,
            spreadsheet_id=spreadsheet_id,
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"],
            fallback_strategies=[
                "service_account",
                "environment_variables",
                "default_credentials",
                "interactive_login",
            ],
        )

    def _resolve_service_account_path(self) -> str:
        """サービスアカウントファイルのパスを解決"""
        possible_paths = [
            # 環境変数
            os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE"),
            # 標準的なパス
            "config/service_account.json",
            "configuration/service_account.json",
            "service_account.json",
            # バックアップパス
            "_BACKUP/service_account.json",
        ]

        for path in possible_paths:
            if path and Path(path).exists():
                print(f"✅ サービスアカウントファイル発見: {path}")
                return path

        # ファイルが存在しない場合は作成を試みる
        default_path = "config/service_account.json"
        print(f"⚠️  サービスアカウントファイルが見つかりません。作成します: {default_path}")

        # 設定ディレクトリを作成
        Path("config").mkdir(exist_ok=True)

        # テンプレートファイルを作成
        template = {
            "type": "service_account",
            "project_id": "your-project-id",
            "private_key_id": "your-private-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY\\n-----END PRIVATE KEY-----\\n",
            "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
            "client_id": "your-client-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com",
        }

        with open(default_path, "w") as f:
            json.dump(template, f, indent=2)

        print(f"📝 テンプレートファイルを作成しました: {default_path}")
        print("🔧 実際のサービスアカウント情報で置き換えてください")

        return default_path

    def _resolve_spreadsheet_id(self) -> str:
        """スプレッドシートIDを解決"""
        possible_sources = [
            # 環境変数
            os.getenv("SPREADSHEET_ID"),
            # 設定ファイル（将来実装）
            # デフォルト値（サンプル）
            "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
        ]

        for source in possible_sources:
            if source:
                print(f"✅ スプレッドシートID発見: {source}")
                return source

        raise ValueError("スプレッドシートIDが見つかりません")

    def validate_authentication(self) -> Dict[str, Any]:
        """認証設定を検証"""
        results = {
            "service_account_file": {
                "path": self.config.service_account_file,
                "exists": Path(self.config.service_account_file).exists(),
                "readable": (
                    os.access(self.config.service_account_file, os.R_OK)
                    if Path(self.config.service_account_file).exists()
                    else False
                ),
            },
            "spreadsheet_id": {
                "value": self.config.spreadsheet_id,
                "valid": bool(self.config.spreadsheet_id and len(self.config.spreadsheet_id) > 10),
            },
            "environment": {
                "GOOGLE_SERVICE_ACCOUNT_FILE": os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE"),
                "SPREADSHEET_ID": os.getenv("SPREADSHEET_ID"),
            },
        }

        return results

    def get_google_sheets_config(self) -> Dict[str, Any]:
        """Google Sheets設定を取得"""
        return {
            "service_account_file": self.config.service_account_file,
            "spreadsheet_id": self.config.spreadsheet_id,
            "scopes": self.config.scopes,
        }

    def generate_setup_guide(self) -> str:
        """セットアップガイドを生成"""
        guide = [
            "🔐 Google Sheets 認証セットアップガイド",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "📋 現在の状態:",
            f"  サービスアカウントファイル: {self.config.service_account_file}",
            f"  スプレッドシートID: {self.config.spreadsheet_id}",
            "",
            "🚀 セットアップ手順:",
            "1. Google Cloud Consoleでサービスアカウントを作成",
            "2. サービスアカウントキー（JSON）をダウンロード",
            f"3. ダウンロードしたファイルを {self.config.service_account_file} に配置",
            "4. スプレッドシートをサービスアカウントと共有",
            "5. 環境変数を設定:",
            f"   export GOOGLE_SERVICE_ACCOUNT_FILE={self.config.service_account_file}",
            f"   export SPREADSHEET_ID={self.config.spreadsheet_id}",
            "",
            "🔧 トラブルシューティング:",
            "• ファイルパスを確認: ls -la config/",
            "• 環境変数を確認: env | grep GOOGLE",
            "• スプレッドシートの共有設定を確認",
            "",
        ]

        return "\n".join(guide)


# グローバルインスタンス
auth_manager = UnifiedAuthManager()


def get_auth_config() -> Dict[str, Any]:
    """認証設定を取得"""
    return auth_manager.get_google_sheets_config()


def validate_auth() -> Dict[str, Any]:
    """認証を検証"""
    return auth_manager.validate_authentication()


def get_setup_guide() -> str:
    """セットアップガイドを取得"""
    return auth_manager.generate_setup_guide()


if __name__ == "__main__":
    # 認証状態を表示
    print("🔐 認証状態チェック")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    validation = validate_auth()

    print("📊 検証結果:")
    for category, details in validation.items():
        print(f"  {category}:")
        for key, value in details.items():
            status = "✅" if value else "❌"
            print(f"    {status} {key}: {value}")

    print()
    print(get_setup_guide())
