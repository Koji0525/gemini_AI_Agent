"""
インポートテストスクリプト
"""

import sys
import os

print("🔍 インポートテスト開始")
print("=" * 50)

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
print(f"📁 プロジェクトルート: {project_root}")

# BrowserController テスト
try:
    from browser_control.browser_controller import BrowserController

    print("✅ BrowserController インポート成功")
except ImportError as e:
    print(f"❌ BrowserController インポート失敗: {e}")

# ConfigLoader テスト
try:
    from configuration.config_loader import ConfigLoader

    print("✅ ConfigLoader インポート成功")

    # 設定読み込みテスト
    config = ConfigLoader()
    wp_url = config.get("WP_URL")
    wp_user = config.get("WP_USER")
    print(f"📝 設定値: URL={wp_url}, USER={wp_user}")
except ImportError as e:
    print(f"❌ ConfigLoader インポート失敗: {e}")
    # 代替パスを試す
    try:
        from config.config_loader import ConfigLoader

        print("✅ ConfigLoader インポート成功（代替パス）")
    except ImportError as e2:
        print(f"❌ 代替パスでもインポート失敗: {e2}")

print("=" * 50)
print("🎉 インポートテスト完了")
