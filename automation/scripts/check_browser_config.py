"""
ブラウザ設定詳細確認スクリプト
"""

import sys
import os

# プロジェクトルートをパスに追加
project_root = "/workspaces/gemini_AI_Agent"
sys.path.insert(0, project_root)

try:
    from browser_control.browser_controller import BrowserController

    print("✅ BrowserController インポート成功")

    # メソッドシグネチャを確認
    import inspect

    print("\n🔍 BrowserControllerのメソッドシグネチャ:")

    methods_to_check = ["setup_browser", "save_wordpress_cookies"]
    for method_name in methods_to_check:
        if hasattr(BrowserController, method_name):
            method = getattr(BrowserController, method_name)
            sig = inspect.signature(method)
            print(f"  - {method_name}{sig}")
        else:
            print(f"  - {method_name}: メソッドが存在しません")

    # 簡単なインスタンス化テスト
    print("\n🔧 簡単なインスタンス化テスト:")
    try:
        browser = BrowserController()
        print("  ✅ BrowserControllerインスタンス化成功")

        # 非同期メソッドのテストは実行しない（セットアップが必要なため）
        print("  ⚠️  setup_browserメソッドは非同期実行が必要です")

    except Exception as e:
        print(f"  ❌ BrowserControllerインスタンス化失敗: {e}")

except ImportError as e:
    print(f"❌ BrowserController インポート失敗: {e}")

print("\n🎉 ブラウザ設定確認完了")
