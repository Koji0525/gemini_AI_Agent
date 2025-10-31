"""
環境設定確認スクリプト
"""

import os
from dotenv import load_dotenv

load_dotenv()


def check_environment():
    """環境変数をチェック"""
    print("🔍 環境設定チェック")
    print("=" * 50)

    required_vars = ["WP_URL", "WP_USER", "WP_PASS"]
    all_ok = True

    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: 設定済み")
        else:
            print(f"❌ {var}: 未設定")
            all_ok = False

    print("=" * 50)

    if all_ok:
        print("🎉 すべての環境変数が設定されています")
    else:
        print("⚠️ 不足している環境変数があります")

    return all_ok


def check_playwright():
    """Playwright設定をチェック"""
    print("\n🔍 Playwright設定チェック")
    print("=" * 50)

    try:
        from playwright.async_api import async_playwright

        print("✅ Playwright インポート成功")

        # ブラウザパスを確認
        import subprocess

        result = subprocess.run(["which", "playwright"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Playwright CLI 利用可能")
        else:
            print("❌ Playwright CLI が見つかりません")

        return True
    except Exception as e:
        print(f"❌ Playwright チェック失敗: {e}")
        return False


if __name__ == "__main__":
    env_ok = check_environment()
    playwright_ok = check_playwright()

    if env_ok and playwright_ok:
        print("\n🎉 環境チェック完了 - すべて正常")
    else:
        print("\n⚠️ 環境に問題があります")
