#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
環境診断・修復スクリプト
Playwrightとライブラリのインストール状況を確認・修復します
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path

def run_command(command, description):
    """コマンドを実行して結果を表示"""
    print(f"\n🔧 {description}")
    print(f"   実行中: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print(f"   ✅ 成功")
            if result.stdout.strip():
                print(f"   出力: {result.stdout.strip()[:200]}")
        else:
            print(f"   ❌ エラー (終了コード: {result.returncode})")
            if result.stderr.strip():
                print(f"   エラー詳細: {result.stderr.strip()}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"   ❌ タイムアウト（5分経過）")
        return False
    except Exception as e:
        print(f"   ❌ 実行エラー: {e}")
        return False

def check_python_environment():
    """Python環境の確認"""
    print("=" * 60)
    print("  Python環境診断")
    print("=" * 60)
    
    print(f"Python バージョン: {sys.version}")
    print(f"Python パス: {sys.executable}")
    print(f"作業ディレクトリ: {os.getcwd()}")
    
    # pip の確認
    run_command("pip --version", "pip バージョン確認")

def install_libraries():
    """必要なライブラリを順次インストール"""
    print("\n" + "=" * 60)
    print("  必要なライブラリのインストール")
    print("=" * 60)
    
    # 基本ライブラリのインストール
    libraries = [
        "playwright",
        "gspread", 
        "oauth2client",
        "google-auth",
        "google-auth-oauthlib",
        "aiohttp"
    ]
    
    for lib in libraries:
        print(f"\n📦 {lib} をインストール中...")
        success = run_command(f"pip install {lib} --upgrade", f"{lib} インストール")
        
        if not success:
            print(f"   ⚠️ {lib} のインストールに失敗しました")
            # 代替方法を試行
            run_command(f"pip install {lib} --user --upgrade", f"{lib} ユーザーインストール")

def install_playwright_browsers():
    """Playwright ブラウザのインストール"""
    print("\n" + "=" * 60)
    print("  Playwright ブラウザのインストール")
    print("=" * 60)
    
    # まずPlaywright本体が正しくインストールされているか確認
    try:
        import playwright
        print(f"✅ Playwright バージョン: {playwright.__version__}")
    except ImportError:
        print("❌ Playwrightがインストールされていません")
        return False
    
    # システム情報を表示
    print(f"OS: {os.name}")
    print(f"アーキテクチャ: {sys.platform}")
    
    # ブラウザインストールを実行（より詳細なログ出力）
    commands = [
        "python -m playwright install chromium",
        "playwright install chromium --with-deps",
        "python -m playwright install chromium --with-deps"
    ]
    
    for command in commands:
        print(f"\n🌐 ブラウザインストール試行: {command}")
        success = run_command(command, "Chromium ブラウザインストール")
        
        if success:
            print("✅ ブラウザインストール成功")
            break
        else:
            print("❌ インストール失敗、次の方法を試行...")
    
    # インストール後の確認
    check_playwright_installation()

def check_playwright_installation():
    """Playwright インストール状況の確認"""
    print("\n" + "=" * 60)
    print("  Playwright インストール確認")
    print("=" * 60)
    
    try:
        # Playwrightの動作テスト
        from playwright.sync_api import sync_playwright
        
        print("📱 ブラウザ起動テスト中...")
        with sync_playwright() as p:
            # ブラウザ一覧を表示
            browsers = ['chromium', 'firefox', 'webkit']
            for browser_name in browsers:
                try:
                    browser = getattr(p, browser_name)
                    browser_instance = browser.launch(headless=True)
                    browser_instance.close()
                    print(f"   ✅ {browser_name}: 起動成功")
                except Exception as e:
                    print(f"   ❌ {browser_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Playwright テスト失敗: {e}")
        return False

def test_import_all():
    """すべての必要なライブラリのインポートテスト"""
    print("\n" + "=" * 60)
    print("  ライブラリインポートテスト")
    print("=" * 60)
    
    test_libraries = {
        'playwright': 'playwright',
        'gspread': 'gspread',
        'oauth2client': 'oauth2client.service_account',
        'google.auth': 'google.auth',
        'aiohttp': 'aiohttp'
    }
    
    all_success = True
    
    for lib_name, import_name in test_libraries.items():
        try:
            module = importlib.import_module(import_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"   ✅ {lib_name}: {version}")
        except ImportError as e:
            print(f"   ❌ {lib_name}: {e}")
            all_success = False
        except Exception as e:
            print(f"   ⚠️ {lib_name}: {e}")
    
    return all_success

def check_network_and_permissions():
    """ネットワーク接続と権限の確認"""
    print("\n" + "=" * 60)
    print("  ネットワーク・権限確認")
    print("=" * 60)
    
    # 管理者権限の確認（Windows）
    if os.name == 'nt':
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        print(f"管理者権限: {'あり' if is_admin else 'なし'}")
        
        if not is_admin:
            print("💡 Playwrightのインストールに管理者権限が必要な場合があります")
    
    # ネットワーク接続確認
    import urllib.request
    test_urls = [
        "https://playwright.azureedge.net/",
        "https://pypi.org/",
        "https://github.com/"
    ]
    
    for url in test_urls:
        try:
            urllib.request.urlopen(url, timeout=10)
            print(f"   ✅ {url}")
        except Exception as e:
            print(f"   ❌ {url}: {e}")

def create_fixed_main_script():
    """修正されたメインスクリプトを作成"""
    print("\n" + "=" * 60)
    print("  修正されたスクリプトの作成")
    print("=" * 60)
    
    fixed_script = '''import asyncio
import sys
import os
from pathlib import Path

# より柔軟なライブラリチェック
def check_and_install_libraries():
    """必要なライブラリの確認とインストール"""
    required_packages = [
        'playwright',
        'gspread', 
        'oauth2client',
        'google-auth',
        'aiohttp'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'google-auth':
                __import__('google.auth')
            elif package == 'oauth2client':
                __import__('oauth2client.service_account')
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"以下のライブラリをインストールしてください:")
        print(f"pip install {' '.join(missing_packages)}")
        print("python -m playwright install chromium")
        
        # 自動インストールを試行
        import subprocess
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, check=True)
            subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], check=True)
            print("ライブラリのインストールが完了しました。")
        except subprocess.CalledProcessError:
            print("自動インストールに失敗しました。手動でインストールしてください。")
            return False
    
    return True

# ライブラリチェック実行
if not check_and_install_libraries():
    input("Enterキーを押して終了...")
    sys.exit(1)

# ここから通常のスクリプト内容
print("ライブラリチェック完了。メインプログラムを実行中...")

# 元のgemini_automation.pyの内容をここに続ける
'''
    
    script_path = Path("gemini_automation_fixed.py")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(fixed_script)
    
    print(f"✅ 修正スクリプトを作成しました: {script_path}")

def main():
    """メイン診断・修復処理"""
    print("=" * 60)
    print("  Gemini自動化 環境診断・修復ツール")
    print("=" * 60)
    
    # Step 1: Python環境確認
    check_python_environment()
    
    # Step 2: ライブラリインストール
    install_libraries()
    
    # Step 3: Playwrightブラウザインストール
    install_playwright_browsers()
    
    # Step 4: インポートテスト
    import_success = test_import_all()
    
    # Step 5: ネットワーク・権限確認
    check_network_and_permissions()
    
    # Step 6: 修正スクリプト作成
    create_fixed_main_script()
    
    # 最終結果
    print("\n" + "=" * 60)
    print("  診断結果")
    print("=" * 60)
    
    if import_success:
        print("🎉 すべてのライブラリが正常にインストールされました！")
        print("   gemini_automation.py を実行できます")
    else:
        print("⚠️ いくつかのライブラリに問題があります")
        print("   手動で以下を実行してください:")
        print("   pip install playwright gspread oauth2client google-auth aiohttp")
        print("   python -m playwright install chromium")
    
    print("\n💡 トラブルシューティングのヒント:")
    print("   - 管理者権限でコマンドプロンプトを実行")
    print("   - ウイルス対策ソフトを一時的に無効化")
    print("   - 企業ネットワークの場合、プロキシ設定を確認")
    
    input("\n何かキーを押して終了...")

if __name__ == "__main__":
    main()
'''