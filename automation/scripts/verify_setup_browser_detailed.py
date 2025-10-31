"""
setup_browserメソッド詳細修正確認
"""

import sys
import os
import inspect

# プロジェクトルートをパスに追加
project_root = "/workspaces/gemini_AI_Agent"
sys.path.insert(0, project_root)

print("🔍 setup_browserメソッド詳細修正確認")
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

        if "headless" in actual_params:
            print("✅ setup_browserメソッドにheadless引数があります")

            # デフォルト値を確認
            headless_param = sig.parameters["headless"]
            print(f"   headless引数のデフォルト値: {headless_param.default}")
        else:
            print("❌ setup_browserメソッドにheadless引数がありません")

    else:
        print("❌ setup_browserメソッドが見つかりません")

except ImportError as e:
    print(f"❌ BrowserController インポート失敗: {e}")

# ファイル内容の詳細確認
print("\n🔍 ファイル内容詳細確認:")
try:
    with open("browser_control/browser_controller.py", "r") as f:
        content = f.read()

    # setup_browserメソッドの定義を検索
    import re

    method_pattern = r"async def setup_browser\([^)]*\) -> None:"
    match = re.search(method_pattern, content)

    if match:
        method_def = match.group(0)
        print(f"✅ メソッド定義: {method_def}")

        # headless引数があるか確認
        if "headless" in method_def:
            print("✅ メソッド定義にheadless引数があります")
        else:
            print("❌ メソッド定義にheadless引数がありません")

        # chromium.launchのheadlessパラメータを確認
        if "headless=headless" in content:
            print("✅ chromium.launchでheadless変数を使用しています")
        elif "headless=True" in content:
            print("⚠️ chromium.launchでheadless固定値を使用しています")
        else:
            print("❌ chromium.launchのheadlessパラメータが見つかりません")

    else:
        print("❌ setup_browserメソッドの定義が見つかりません")

except Exception as e:
    print(f"❌ ファイル読み込みエラー: {e}")

print("=" * 50)
print("🎉 詳細確認完了")
