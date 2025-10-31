"""
インポートテストスクリプト - 修正版
"""

import sys
import os

print("🔍 インポートテスト開始 - 修正版")
print("=" * 50)

# 絶対パスでプロジェクトルートを追加
project_root = "/workspaces/gemini_AI_Agent"
sys.path.insert(0, project_root)
print(f"📁 プロジェクトルート: {project_root}")

# 現在のPythonパスを表示
print("🔍 現在のPythonパス:")
for i, path in enumerate(sys.path[:5]):  # 最初の5つだけ表示
    print(f"  {i+1}. {path}")

print("...")

# BrowserController テスト
try:
    from browser_control.browser_controller import BrowserController

    print("✅ BrowserController インポート成功")

    # 簡単なインスタンス化テスト
    try:
        browser = BrowserController()
        print("✅ BrowserController インスタンス化成功")
    except Exception as e:
        print(f"⚠️ BrowserController インスタンス化エラー: {e}")

except ImportError as e:
    print(f"❌ BrowserController インポート失敗: {e}")

# ConfigLoader テスト
try:
    from configuration.config_loader import ConfigLoader

    print("✅ ConfigLoader インポート成功")

    # 設定読み込みテスト
    try:
        config = ConfigLoader()
        wp_url = config.get("WP_URL")
        wp_user = config.get("WP_USER")
        print(f"📝 設定値: URL={wp_url}, USER={wp_user}")
    except Exception as e:
        print(f"⚠️ ConfigLoader インスタンス化エラー: {e}")

except ImportError as e:
    print(f"❌ ConfigLoader インポート失敗: {e}")

print("=" * 50)
print("🎉 インポートテスト完了")
