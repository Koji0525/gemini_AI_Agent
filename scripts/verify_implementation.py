#!/usr/bin/env python3
"""
実装確認ツール - 全項目を自動チェック
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from wordpress.wp_dev.wp_rest_client import WordPressRESTClient
from configuration.wp_config_loader import WordPressConfigLoader


def main():
    print("🔍 M&Aポータル実装確認")
    print("=" * 70)

    config_loader = WordPressConfigLoader()
    config = config_loader.load_config()

    import requests

    checks = []

    # 1. カスタム投稿タイプ
    print("\n📋 カスタム投稿タイプ確認...")
    try:
        url = f"{config['wp_api_base']}/types/ma_company"
        resp = requests.get(url, auth=(config["wp_user"], config["wp_pass"]), timeout=10)
        if resp.status_code == 200:
            print("   ✅ ma_company 登録済み")
            checks.append(True)
        else:
            print("   ❌ ma_company 未登録")
            checks.append(False)
    except:
        print("   ❌ チェック失敗")
        checks.append(False)

    # 2. タクソノミー
    print("\n🏷️ タクソノミー確認...")
    try:
        url = f"{config['wp_api_base']}/taxonomies/ma_industry"
        resp = requests.get(url, auth=(config["wp_user"], config["wp_pass"]), timeout=10)
        if resp.status_code == 200:
            print("   ✅ ma_industry 登録済み")
            checks.append(True)
        else:
            print("   ❌ ma_industry 未登録")
            checks.append(False)
    except:
        print("   ❌ チェック失敗")
        checks.append(False)

    # 3. デモデータ
    print("\n📊 デモデータ確認...")
    try:
        url = f"{config['wp_api_base']}/ma_company"
        resp = requests.get(url, auth=(config["wp_user"], config["wp_pass"]), timeout=10)
        if resp.status_code == 200:
            count = len(resp.json())
            if count >= 5:
                print(f"   ✅ {count}件の企業データ")
                checks.append(True)
            else:
                print(f"   ⚠️ {count}件のみ（5件推奨）")
                checks.append(False)
        else:
            print("   ❌ データ取得失敗")
            checks.append(False)
    except:
        print("   ❌ チェック失敗")
        checks.append(False)

    # 結果
    print("\n" + "=" * 70)
    success_rate = sum(checks) / len(checks) * 100
    print(f"📊 実装完了率: {success_rate:.0f}%")

    if all(checks):
        print("✅ 全ての項目が正常です！")
        return 0
    else:
        print("⚠️ 一部未完了の項目があります")
        return 1


if __name__ == "__main__":
    sys.exit(main())
