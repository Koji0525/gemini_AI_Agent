#!/usr/bin/env python3
"""
BrowserControllerの実際のメソッドを確認
"""
import sys
import os

# プロジェクトルートを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from browser_control.browser_controller import BrowserController
import inspect


def check_browser_controller():
    """BrowserControllerのメソッド一覧を表示"""

    print("=" * 60)
    print("🔍 BrowserController メソッド一覧")
    print("=" * 60)
    print()

    # すべてのメソッドを取得
    methods = [method for method in dir(BrowserController) if not method.startswith("_")]

    print(f"�� 公開メソッド数: {len(methods)}")
    print()

    # カテゴリ別に分類
    async_methods = []
    sync_methods = []
    properties = []

    for method_name in methods:
        method = getattr(BrowserController, method_name)

        if inspect.iscoroutinefunction(method):
            async_methods.append(method_name)
        elif callable(method):
            sync_methods.append(method_name)
        else:
            properties.append(method_name)

    # 表示
    print("【非同期メソッド（async）】")
    for method in sorted(async_methods):
        print(f"  - {method}")

    print()
    print("【同期メソッド】")
    for method in sorted(sync_methods):
        print(f"  - {method}")

    print()
    print("【プロパティ/属性】")
    for prop in sorted(properties):
        print(f"  - {prop}")

    print()
    print("=" * 60)
    print("💡 重要なメソッド")
    print("=" * 60)
    print()

    # 初期化関連
    if "initialize" in async_methods:
        print("✅ initialize() - 非同期初期化メソッドあり")
    elif "start" in async_methods:
        print("✅ start() - 非同期開始メソッドあり")
    elif "launch" in async_methods:
        print("✅ launch() - 非同期起動メソッドあり")
    else:
        print("⚠️  非同期初期化メソッドが見つかりません")
        print("   代替案: __init__() を使用")

    # クリーンアップ関連
    if "cleanup" in async_methods:
        print("✅ cleanup() - クリーンアップメソッドあり")
    elif "close" in async_methods:
        print("✅ close() - クローズメソッドあり")

    print()


if __name__ == "__main__":
    check_browser_controller()
