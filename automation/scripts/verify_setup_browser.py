"""
setup_browserメソッド修正確認スクリプト
"""

import sys
import os
import inspect

# プロジェクトルートをパスに追加
project_root = "/workspaces/gemini_AI_Agent"
sys.path.insert(0, project_root)

print("🔍 setup_browserメソッド修正確認")
print("=" * 50)

try:
    from browser_control.browser_controller import BrowserController

    print("✅ BrowserController インポート成功")

    # setup_browserメソッドのシグネチャ確認
    setup_browser_method = getattr(BrowserController, "setup_browser", None)
    if setup_browser_method:
        sig = inspect.signature(setup_browser_method)
        print(f"📋 setup_browserメソッドシグネチャ: {sig}")

        # 期待される引数を確認
        expected_params = ["self", "headless"]
        actual_params = list(sig.parameters.keys())

        if set(expected_params).issubset(set(actual_params)):
            print("✅ setup_browserメソッドは正しく修正されています")
            print(f"   期待される引数: {expected_params}")
            print(f"   実際の引数: {actual_params}")
        else:
            print("❌ setup_browserメソッドの修正が不完全です")
            print(f"   期待される引数: {expected_params}")
            print(f"   実際の引数: {actual_params}")
    else:
        print("❌ setup_browserメソッドが見つかりません")

except ImportError as e:
    print(f"❌ BrowserController インポート失敗: {e}")

# ファイルの内容も確認
print("\n🔍 ファイル内容確認:")
try:
    with open("browser_control/browser_controller.py", "r") as f:
        lines = f.readlines()

    setup_found = False
    headless_param_found = False

    for i, line in enumerate(lines):
        if "async def setup_browser" in line:
            setup_found = True
            print(f"✅ メソッド定義: 行 {i+1}: {line.strip()}")
            if "headless" in line:
                headless_param_found = True

        if setup_found and "chromium.launch" in line and "headless" in line:
            print(f"✅ chromium.launch呼び出し: 行 {i+1}: {line.strip()}")
            if "headless=headless" in line:
                print("   ⬆️ headlessパラメータが変数参照されています")
            else:
                print("   ⚠️ headlessパラメータが固定値の可能性があります")

    if not setup_found:
        print("❌ setup_browserメソッドが見つかりません")
    elif not headless_param_found:
        print("❌ setup_browserメソッドにheadless引数がありません")

except Exception as e:
    print(f"❌ ファイル読み込みエラー: {e}")

print("=" * 50)
print("🎉 確認完了")
