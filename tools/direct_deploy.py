#!/usr/bin/env python3
"""
直接デプロイツール - デプロイシステムをバイパス
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()


def direct_deploy():
    """functions_additions_complete.phpを直接WordPressに送信"""

    # 設定読み込み
    wp_url = os.getenv("WP_URL")
    wp_user = os.getenv("WP_USER")
    wp_pass = os.getenv("WP_PASS")

    if not all([wp_url, wp_user, wp_pass]):
        print("❌ 環境変数が設定されていません")
        return False

    # ソースファイル読み込み
    source_file = Path("wordpress_projects/ma_portal/functions_additions_complete.php")

    if not source_file.exists():
        print(f"❌ ソースファイルが見つかりません: {source_file}")
        return False

    with open(source_file, "r", encoding="utf-8") as f:
        php_code = f.read()

    print(f"✅ ソースファイル読み込み: {len(php_code)} 文字")

    # REST API経由で送信
    api_url = f"{wp_url}/wp-json/custom/v1/update-functions"

    try:
        response = requests.post(api_url, json={"code": php_code}, auth=(wp_user, wp_pass), timeout=30)

        if response.status_code == 200:
            print("✅ デプロイ成功！")
            return True
        else:
            print(f"❌ デプロイ失敗: {response.status_code}")
            print(f"エラー: {response.text[:500]}")
            return False

    except Exception as e:
        print(f"❌ エラー: {e}")
        return False


if __name__ == "__main__":
    success = direct_deploy()
    sys.exit(0 if success else 1)
