#!/usr/bin/env python3
"""環境変数チェッカー（統一版）"""

import os
import sys
from pathlib import Path

# dotenv読み込み
try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass


def check_environment():
    project_root = Path(__file__).parent.parent

    print("🔍 環境設定チェック")
    print("=" * 60)

    issues = []

    # .env確認
    env_path = project_root / ".env"
    print(f"{'✅' if env_path.exists() else '❌'} .envファイル: {env_path}")

    # 必須変数（統一名称）
    print("\n📋 必須環境変数:")

    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    if spreadsheet_id:
        print(f"   ✅ SPREADSHEET_ID: {spreadsheet_id[:15]}...")
    else:
        issues.append("SPREADSHEET_ID 未設定")
        print(f"   ❌ SPREADSHEET_ID: 未設定")

    service_account = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "configuration/service_account.json")
    service_account_path = project_root / service_account
    print(f"\n🔑 認証情報ファイル:")
    if service_account_path.exists():
        print(f"   ✅ {service_account_path}")
    else:
        issues.append(f"認証ファイル未配置: {service_account_path}")
        print(f"   ❌ {service_account_path}")

    # パッケージ確認
    print(f"\n📦 必須パッケージ:")
    try:
        import dotenv

        print(f"   ✅ python-dotenv")
    except ImportError:
        issues.append("python-dotenv 未インストール")
        print(f"   ❌ python-dotenv")

    try:
        import googleapiclient

        print(f"   ✅ google-api-python-client")
    except ImportError:
        issues.append("google-api-python-client 未インストール")
        print(f"   ❌ google-api-python-client")

    # サマリー
    print("\n" + "=" * 60)
    if issues:
        print(f"❌ {len(issues)}件の問題:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    else:
        print("✅ 環境設定は正常です")
        return True


if __name__ == "__main__":
    sys.exit(0 if check_environment() else 1)
