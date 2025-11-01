#!/usr/bin/env python3
"""
WordPress設定確認スクリプト
"""

import requests
import base64
import os


def check_wordpress_setup():
    print("🔍 WordPress設定確認")
    print("=" * 40)

    wp_url = os.getenv("WP_URL")
    username = os.getenv("WP_USERNAME")
    password = os.getenv("WP_PASSWORD")

    if not all([wp_url, username, password]):
        print("❌ 環境変数が不足しています")
        return False

    api_url = f"{wp_url.rstrip('/')}/wp-json/wp/v2"
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {"Content-Type": "application/json", "Authorization": f"Basic {auth}"}

    # 1. 基本接続確認
    print("1. 🔌 基本接続確認...")
    try:
        response = requests.get(f"{api_url}/types", headers=headers, timeout=10)
        if response.status_code == 200:
            print("   ✅ WordPress REST API接続成功")
        else:
            print(f"   ❌ 接続失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 接続エラー: {e}")
        return False

    # 2. 利用可能な投稿タイプ確認
    print("2. 📝 投稿タイプ確認...")
    try:
        response = requests.get(f"{api_url}/types", headers=headers)
        if response.status_code == 200:
            post_types = response.json()
            print(f"   ✅ 投稿タイプ数: {len(post_types)}")
            for pt_name, pt_info in post_types.items():
                print(f"      - {pt_name}: {pt_info.get('name', 'N/A')}")
                if "rest_base" in pt_info:
                    print(f"        RESTエンドポイント: {pt_info['rest_base']}")
        else:
            print(f"   ❌ 投稿タイプ取得失敗: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 投稿タイプ確認エラー: {e}")

    # 3. カスタム投稿タイプ確認
    print("3. 🏢 カスタム投稿タイプ確認...")
    cpt_endpoints = ["ma_company", "ma-companies", "companies"]
    found_cpt = False

    for endpoint in cpt_endpoints:
        try:
            response = requests.get(f"{api_url}/{endpoint}", headers=headers, params={"per_page": 1})
            if response.status_code == 200:
                print(f"   ✅ CPTエンドポイント発見: {endpoint}")
                found_cpt = True
                break
        except:
            continue

    if not found_cpt:
        print("   ❌ カスタム投稿タイプが見つかりません")
        print("   💡 functions.phpにCPT定義を追加してください")

    # 4. タクソノミー確認
    print("4. 🏷️ タクソノミー確認...")
    try:
        response = requests.get(f"{api_url}/taxonomies", headers=headers)
        if response.status_code == 200:
            taxonomies = response.json()
            print(f"   ✅ タクソノミー数: {len(taxonomies)}")
            for tax_name, tax_info in taxonomies.items():
                print(f"      - {tax_name}: {tax_info.get('name', 'N/A')}")
        else:
            print(f"   ❌ タクソノミー取得失敗: {response.status_code}")
    except Exception as e:
        print(f"   ❌ タクソノミー確認エラー: {e}")

    return True


if __name__ == "__main__":
    check_wordpress_setup()
