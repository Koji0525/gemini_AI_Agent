#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最小限テストスクリプト - 個別にライブラリをテスト（修正版）
"""

import sys
print(f"Python: {sys.version}")
print(f"Path: {sys.executable}")
print("=" * 50)

# テスト1: Playwright
print("テスト1: Playwright")
try:
    import playwright
    # バージョン取得方法を修正
    try:
        version = playwright.__version__
    except AttributeError:
        try:
            from playwright._repo_version import version
        except ImportError:
            version = "バージョン情報なし"
    
    print(f"✅ Playwright インポート成功: {version}")
    
    # ブラウザテスト - Firefoxを使用（インストール済みのため）
    from playwright.sync_api import sync_playwright
    print("   ブラウザ起動テスト中...")
    with sync_playwright() as p:
        # Firefoxでテスト（インストール済み）
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        browser.close()
    print("   ✅ ブラウザ動作成功")
    
except ImportError as e:
    print(f"❌ Playwright インポートエラー: {e}")
except Exception as e:
    print(f"❌ Playwright 動作エラー: {e}")

print()

# テスト2: Google関連ライブラリ
print("テスト2: Google関連ライブラリ")
try:
    import google.auth
    print(f"✅ google-auth: {google.auth.__version__}")
except ImportError as e:
    print(f"❌ google-auth: {e}")

try:
    import gspread
    print(f"✅ gspread: {gspread.__version__}")
except ImportError as e:
    print(f"❌ gspread: {e}")

try:
    from oauth2client.service_account import ServiceAccountCredentials
    print("✅ oauth2client: OK")
except ImportError as e:
    print(f"❌ oauth2client: {e}")

print()

# テスト3: その他ライブラリ
print("テスト3: その他ライブラリ")
try:
    import aiohttp
    print(f"✅ aiohttp: {aiohttp.__version__}")
except ImportError as e:
    print(f"❌ aiohttp: {e}")

print()

# テスト4: Google Sheets接続テスト（簡易版）
print("テスト4: Google Sheets接続テスト")
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    from pathlib import Path
    
    service_account_file = Path("service_account.json")
    if service_account_file.exists():
        print("✅ service_account.json 存在")
        
        # 接続テスト
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(str(service_account_file), scope)
        gc = gspread.authorize(creds)
        
        # テストアクセス
        sheet = gc.open_by_key("14Kesp7vzsPqpNlU_t8RkDead18fRM2nMdlMWYAoKS6Q")
        print("✅ スプレッドシート接続成功")
        
        # シートチェック
        try:
            setting_sheet = sheet.worksheet("setting")
            print("✅ settingシート 存在")
        except:
            print("❌ settingシート 存在しない")
            
        try:
            prompt_sheet = sheet.worksheet("prompt")
            prompts = prompt_sheet.col_values(2)
            print(f"✅ promptシート 存在 ({len(prompts)} 行)")
        except:
            print("❌ promptシート 存在しない")
            
    else:
        print("⚠️ service_account.json が見つかりません（OAuth認証で実行予定）")
        
except Exception as e:
    print(f"❌ Google Sheets接続エラー: {e}")

print("=" * 50)
print("テスト完了")
input("Enterキーで終了...")